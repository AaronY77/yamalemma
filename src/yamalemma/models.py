import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path

from jsonschema import Draft202012Validator

from yamalemma.domain import fingerprint, load_json, save_json
from yamalemma.credentials import load_key
from yamalemma.budget import BudgetError, reserve_hosted


class ModelError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, response, code, message, headers, newurl):
        raise ModelError('provider redirect rejected')


def post_json(url, body, headers, timeout):
    request = urllib.request.Request(url, data=json.dumps(body).encode(), headers={'Content-Type': 'application/json', **headers})
    with urllib.request.build_opener(NoRedirect).open(request, timeout=timeout) as response:
        data = response.read(8 * 1024 * 1024 + 1)
    if len(data) > 8 * 1024 * 1024:
        raise ModelError('model response exceeds 8 MiB')
    return json.loads(data)


def parse_response(provider, response):
    if not isinstance(response, dict):
        raise ModelError('provider response must be an object')
    if provider == 'openai':
        contents = [part for entry in response.get('output', []) if entry.get('type') == 'message' for part in entry.get('content', [])]
        usage = response.get('usage') or {}
        tokens = {'input': usage.get('input_tokens'), 'output': usage.get('output_tokens')}
        if any(part.get('type') == 'refusal' for part in contents):
            return 'refused', None, tokens
        if response.get('status') == 'incomplete':
            return 'truncated', None, tokens
        if response.get('status') != 'completed':
            return 'provider_error', None, tokens
        content = ''.join(part.get('text', '') for part in contents if part.get('type') == 'output_text')
    else:
        tokens = {'input': response.get('prompt_eval_count'), 'output': response.get('eval_count')}
        if response.get('done_reason') == 'length':
            return 'truncated', None, tokens
        if response.get('done') is not True or response.get('error'):
            return 'provider_error', None, tokens
        content = response.get('message', {}).get('content', '')
    try:
        return 'completed', json.loads(content), tokens
    except (ValueError, TypeError):
        return 'invalid_json', None, tokens


class ModelClient:
    def __init__(self, config, directory, offline=False, transport=None):
        self.config = config
        self.directory = Path(directory)
        self.offline = offline
        self.transport = transport or post_json
        self.calls = []
        self.spent = 0.0
        self.call_count = 0
        self.config_id = fingerprint(config)
        self.ledger_path = self.directory / 'ledger.json'
        if self.ledger_path.exists():
            ledger = load_json(self.ledger_path)
            if ledger['config_fingerprint'] != self.config_id:
                raise ValueError('this run directory belongs to a different configuration')
            self.spent = ledger['reserved_usd']
            self.call_count = ledger['calls']

    def complete(self, role, stage, messages, schema, binding):
        model = self.config['models'][role]
        request = {'version': 1, 'role': role, 'stage': stage, 'profile': model, 'messages': messages,
                   'schema': schema, 'binding': binding}
        key = fingerprint(request)
        cache = self.directory / 'responses' / f'{key}.json'
        if cache.exists():
            record = load_json(cache)
            if record.get('request') != request or record.get('hash') != fingerprint({k: v for k, v in record.items() if k != 'hash'}):
                raise ValueError('model response cache is corrupt or belongs to another request')
            if record['status'] == 'completed':
                Draft202012Validator(schema).validate(record['data'])
            if self.offline or record['status'] == 'completed':
                reused = dict(record, reused=True, new_cost_usd=0.0, original_record_hash=record['hash'])
                reused['hash'] = fingerprint({k: v for k, v in reused.items() if k != 'hash'})
                self.calls.append(reused)
                return reused
        record = {'request': request, 'request_key': key, 'status': 'pending', 'data': None,
                  'usage': {'input': None, 'output': None}, 'cost_usd': None, 'cost_kind': 'unknown',
                  'raw_response': None, 'reused': False}
        if self.offline:
            record['status'] = 'replay_miss'
            self.calls.append(record)
            return record
        if model['provider'] == 'ollama' and model.get('revision') and self.transport is post_json:
            try:
                endpoint = model.get('endpoint', 'http://127.0.0.1:11434').rstrip('/')
                with urllib.request.urlopen(endpoint + '/api/tags', timeout=5) as response:
                    installed = json.load(response)['models']
                actual = next((entry['digest'] for entry in installed if entry['name'] == model['model']), None)
                if actual != model['revision']:
                    record['status'] = 'model_revision_mismatch'
                    self.calls.append(record)
                    return record
                record['runtime_model_revision'] = actual
            except (OSError, ValueError, KeyError, TypeError):
                record['status'] = 'local_model_unavailable'
                self.calls.append(record)
                return record
        limits = self.config['limits']
        input_bytes = len(json.dumps({'messages': messages, 'schema': schema}, ensure_ascii=False).encode())
        if input_bytes > limits['max_input_bytes']:
            record['status'] = 'input_limit'
            self.calls.append(record)
            return record
        if model['provider'] == 'ollama' and input_bytes + model['max_output_tokens'] + 256 > model['context_length']:
            record['status'] = 'context_limit'
            self.calls.append(record)
            return record
        reserve = 0.0
        if model['provider'] == 'openai':
            reserve = ((input_bytes + 4096) * model['input_usd_per_million'] + model['max_output_tokens'] * model['output_usd_per_million']) / 1000000
        if self.call_count >= limits['max_calls'] or self.spent + reserve > limits['max_cost_usd']:
            record['status'] = 'budget_exhausted'
            self.calls.append(record)
            return record
        headers = {}
        if model['provider'] == 'openai':
            secret = load_key(model.get('key_env', 'OPENAI_API_KEY'))
            if not secret:
                record['status'] = 'missing_credentials'
                self.calls.append(record)
                return record
            headers['Authorization'] = 'Bearer ' + secret
            endpoint = 'https://api.openai.com/v1/responses'
            body = {'model': model['model'], 'input': messages, 'store': False,
                    'max_output_tokens': model['max_output_tokens'],
                    'text': {'format': {'type': 'json_schema', 'name': 'yamalemma', 'strict': True, 'schema': schema}}}
            if model.get('reasoning'):
                body['reasoning'] = {'effort': model['reasoning']}
        else:
            endpoint = model.get('endpoint', 'http://127.0.0.1:11434').rstrip('/') + '/api/chat'
            body = {'model': model['model'], 'messages': messages, 'stream': False, 'format': schema,
                    'options': {'num_ctx': model['context_length'], 'num_predict': model['max_output_tokens'], 'temperature': 0},
                    'keep_alive': '5m'}
            if 'think' in model:
                body['think'] = model['think']
        if model['provider'] == 'openai':
            try:
                receipt = reserve_hosted(reserve, key)
            except BudgetError:
                record['status'] = 'shared_budget_unavailable'
                self.calls.append(record)
                return record
            if receipt is None:
                record['status'] = 'shared_budget_exhausted'
                self.calls.append(record)
                return record
            record['shared_budget_reservation'] = receipt
        self.call_count += 1
        self.spent += reserve
        save_json(self.ledger_path, {'config_fingerprint': self.config_id, 'calls': self.call_count, 'reserved_usd': self.spent})
        started = time.monotonic()
        try:
            raw = self.transport(endpoint, body, headers, model['timeout'])
            status, data, usage = parse_response(model['provider'], raw)
            record.update(status=status, data=data, usage=usage, raw_response=raw)
            if status == 'completed':
                errors = list(Draft202012Validator(schema).iter_errors(data))
                if errors:
                    record.update(status='invalid_schema', data=None, error=errors[0].message[:1000])
            if model['provider'] == 'ollama':
                record.update(cost_usd=0.0, cost_kind='local_api_fee_only')
            elif all(type(usage.get(part)) is int and usage[part] >= 0 for part in ('input', 'output')):
                cost = (usage['input'] * model['input_usd_per_million'] + usage['output'] * model['output_usd_per_million']) / 1000000
                record.update(cost_usd=cost, cost_kind='estimated_standard_uncached')
        except urllib.error.HTTPError as error:
            record.update(status='rate_limited' if error.code == 429 else 'http_error', error=f'HTTP {error.code}')
        except (TimeoutError, urllib.error.URLError) as error:
            record.update(status='transport_error', error=type(error).__name__)
        except (OSError, ValueError, TypeError, AttributeError, ModelError) as error:
            record.update(status='provider_error', error=type(error).__name__)
        record['elapsed_seconds'] = time.monotonic() - started
        record['reserved_usd'] = reserve
        record['new_cost_usd'] = record['cost_usd']
        record['hash'] = fingerprint(record)
        save_json(self.directory / 'calls' / f'{self.call_count:06d}-{key}.json', record)
        save_json(cache, record)
        self.calls.append(record)
        return record
