import copy
import io
import json
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

from yamalemma.config import validate_config
from yamalemma.domain import fingerprint
from yamalemma.models import ModelClient, ModelError, parse_response
from yamalemma.prompts import PROOF_SCHEMA


def configuration(provider='ollama'):
    profile = {'provider': provider, 'model': 'test-model', 'max_output_tokens': 128, 'context_length': 8192}
    if provider == 'openai':
        profile.update(input_usd_per_million=2, output_usd_per_million=10,
                       pricing_date='test', pricing_source='test fixture', key_env='YAMALEMMA_TEST_KEY')
    return validate_config({'models': {'reader': dict(profile), 'writer': dict(profile)}, 'limits': {'max_cost_usd': 1, 'max_calls': 4}})


def response(data, provider='ollama'):
    if provider == 'openai':
        return {'status': 'completed', 'model': 'test-model', 'output': [{'type': 'message', 'content': [{'type': 'output_text', 'text': json.dumps(data)}]}],
                'usage': {'input_tokens': 100, 'output_tokens': 20}}
    return {'done': True, 'done_reason': 'stop', 'message': {'content': json.dumps(data)}, 'prompt_eval_count': 100, 'eval_count': 20}


class ModelTests(unittest.TestCase):
    def setUp(self):
        from yamalemma.budget import initialize_budget
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        setting = patch('yamalemma.budget.BUDGET_PATH', Path(directory.name) / 'budget.sqlite3')
        setting.start()
        self.addCleanup(setting.stop)
        initialize_budget(100, 100)

    def call(self, client, binding=None):
        return client.complete('writer', 'proof', [{'role': 'user', 'content': 'prove True'}], PROOF_SCHEMA, binding or {'source': 'fixed'})

    def test_strict_schema_rejects_wrong_fields(self):
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(configuration(), directory, transport=lambda *args: response({'proof': 'by trivial', 'target': 'False'}))
            self.assertEqual(self.call(client)['status'], 'invalid_schema')

    def test_refusal_and_truncation(self):
        refused = {'status': 'completed', 'output': [{'type': 'message', 'content': [{'type': 'refusal', 'refusal': 'no'}]}]}
        self.assertEqual(parse_response('openai', refused)[0], 'refused')
        self.assertEqual(parse_response('openai', {'status': 'incomplete'})[0], 'truncated')
        self.assertEqual(parse_response('ollama', {'done': True, 'done_reason': 'length'})[0], 'truncated')

    def test_invalid_json(self):
        raw = {'done': True, 'message': {'content': '```json not JSON```'}}
        self.assertEqual(parse_response('ollama', raw)[0], 'invalid_json')

    def test_replay_is_exact_and_never_calls_network(self):
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(configuration(), directory, transport=lambda *args: response({'proof': 'by trivial'}))
            first = self.call(client)
            replay = ModelClient(configuration(), directory, offline=True, transport=lambda *args: self.fail('network used'))
            cached = self.call(replay)
            self.assertEqual(cached['data'], first['data'])
            self.assertTrue(cached['reused'])
            self.assertEqual(cached['new_cost_usd'], 0)
            self.assertEqual(self.call(replay, {'source': 'changed'})['status'], 'replay_miss')

    def test_roles_do_not_share_an_independent_reader_call(self):
        config = configuration()
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(config, directory, transport=lambda *args: response({'proof': 'by trivial'}))
            messages = [{'role': 'user', 'content': 'test'}]
            one = client.complete('reader', 'reader', messages, PROOF_SCHEMA, {})
            two = client.complete('writer', 'reader', messages, PROOF_SCHEMA, {})
            self.assertNotEqual(one['request_key'], two['request_key'])
            self.assertFalse(two['reused'])

    def test_failed_response_can_be_replayed(self):
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(configuration(), directory, transport=lambda *args: {'done': True, 'done_reason': 'length'})
            self.assertEqual(self.call(client)['status'], 'truncated')
            replay = ModelClient(configuration(), directory, offline=True)
            self.assertEqual(self.call(replay)['status'], 'truncated')

    def test_corrupt_cache_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(configuration(), directory, transport=lambda *args: response({'proof': 'by trivial'}))
            self.call(client)
            path = next((Path(directory) / 'responses').glob('*.json'))
            record = json.loads(path.read_text())
            record['data']['proof'] = 'changed'
            path.write_text(json.dumps(record))
            with self.assertRaises(ValueError):
                self.call(client)

    def test_budget_exhaustion_prevents_calls(self):
        config = configuration('openai')
        config['limits']['max_cost_usd'] = 0
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(config, directory, transport=lambda *args: self.fail('network used'))
            self.assertEqual(self.call(client)['status'], 'budget_exhausted')

    def test_context_limit_prevents_silent_prompt_truncation(self):
        config = configuration()
        config['models']['writer']['context_length'] = 512
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(config, directory, transport=lambda *args: self.fail('network used'))
            self.assertEqual(self.call(client)['status'], 'context_limit')

    def test_local_revision_mismatch_prevents_generation(self):
        config = configuration()
        config['models']['writer']['revision'] = 'expected-digest'
        tags = io.BytesIO(json.dumps({'models': [{'name': 'test-model', 'digest': 'changed-digest'}]}).encode())
        with tempfile.TemporaryDirectory() as directory, patch('urllib.request.urlopen', return_value=tags):
            client = ModelClient(config, directory)
            self.assertEqual(self.call(client)['status'], 'model_revision_mismatch')
            self.assertEqual(client.call_count, 0)

    def test_persisted_call_limit(self):
        config = configuration()
        config['limits']['max_calls'] = 1
        with tempfile.TemporaryDirectory() as directory:
            self.call(ModelClient(config, directory, transport=lambda *args: response({'proof': 'by trivial'})))
            restarted = ModelClient(config, directory, transport=lambda *args: self.fail('network used'))
            self.assertEqual(self.call(restarted, {'source': 'new'})['status'], 'budget_exhausted')

    def test_missing_key_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {}, clear=True):
            result = self.call(ModelClient(configuration('openai'), directory, transport=lambda *args: self.fail('network used')))
            self.assertEqual(result['status'], 'missing_credentials')

    def test_key_not_written_and_usage_is_estimated(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'YAMALEMMA_TEST_KEY': 'private-sentinel'}):
            received = []
            def transport(url, body, headers, timeout):
                received.append((url, body, headers))
                return response({'proof': 'by trivial'}, 'openai')
            result = self.call(ModelClient(configuration('openai'), directory, transport=transport))
            self.assertEqual(result['status'], 'completed')
            self.assertEqual(result['cost_kind'], 'estimated_standard_uncached')
            self.assertEqual(received[0][2]['Authorization'], 'Bearer private-sentinel')
            self.assertTrue(received[0][1]['text']['format']['strict'])
            self.assertFalse(received[0][1]['store'])
            for path in Path(directory).rglob('*.json'):
                self.assertNotIn('private-sentinel', path.read_text())

    def test_unknown_usage_is_not_zero_cost(self):
        with tempfile.TemporaryDirectory() as directory, patch.dict('os.environ', {'YAMALEMMA_TEST_KEY': 'test'}):
            raw = response({'proof': 'by trivial'}, 'openai')
            del raw['usage']
            result = self.call(ModelClient(configuration('openai'), directory, transport=lambda *args: raw))
            self.assertIsNone(result['cost_usd'])
            self.assertGreater(result['reserved_usd'], 0)

    def test_rate_limit_and_malformed_provider_response(self):
        with tempfile.TemporaryDirectory() as directory:
            def transport(*args):
                raise urllib.error.HTTPError('http://localhost', 429, 'rate limit', {}, None)
            client = ModelClient(configuration(), directory, transport=transport)
            self.assertEqual(self.call(client)['status'], 'rate_limited')
            client.transport = lambda *args: []
            self.assertEqual(self.call(client)['status'], 'provider_error')

    def test_config_rejects_extra_repairs_remote_local_and_secrets(self):
        config = configuration()
        for key, value in [('max_repairs', 4), ('max_cost_usd', float('inf'))]:
            bad = copy.deepcopy(config)
            bad['limits'][key] = value
            with self.assertRaises(ValueError):
                validate_config(bad)
        config['models']['reader']['endpoint'] = 'http://remote.example'
        with self.assertRaises(ValueError):
            validate_config(config)
        config = configuration()
        config['models']['reader']['api_key'] = 'secret'
        with self.assertRaises(ValueError):
            validate_config(config)
