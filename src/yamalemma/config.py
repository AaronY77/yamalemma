import copy
import math
import tomllib
from urllib.parse import urlparse


def load_config(path):
    with open(path, 'rb') as stream:
        return validate_config(tomllib.load(stream))


def validate_config(value):
    config = copy.deepcopy(value)
    if set(config) - {'models', 'stages', 'limits'}:
        raise ValueError('unknown configuration section')
    models = config.get('models', {})
    if not isinstance(models, dict):
        raise ValueError('models must be a table of role profiles')
    if 'reader' not in models or 'writer' not in models:
        raise ValueError('reader and writer model profiles are required')
    for role, model in models.items():
        if not isinstance(model, dict):
            raise ValueError('each model profile must be a table')
        if set(model) - {'provider', 'model', 'endpoint', 'key_env', 'reasoning', 'max_output_tokens',
                         'timeout', 'context_length', 'think', 'input_usd_per_million', 'output_usd_per_million',
                         'pricing_date', 'pricing_source', 'revision'}:
            raise ValueError(f'unknown model setting for {role}')
        if model.get('provider') not in ('openai', 'ollama') or not model.get('model'):
            raise ValueError(f'invalid model profile: {role}')
        model.setdefault('max_output_tokens', 2048)
        model.setdefault('timeout', 180)
        model.setdefault('context_length', 4096)
        if type(model['context_length']) is not int or not 512 <= model['context_length'] <= 8192:
            raise ValueError('local context length must be between 512 and 8192')
        if 'think' in model and type(model['think']) is not bool:
            raise ValueError('think must be a boolean in this implementation')
        if type(model['max_output_tokens']) is not int or not 32 <= model['max_output_tokens'] <= 16384:
            raise ValueError('max_output_tokens must be between 32 and 16384')
        if not isinstance(model['timeout'], (int, float)) or not math.isfinite(model['timeout']) or not 1 <= model['timeout'] <= 600:
            raise ValueError('model timeout must be between 1 and 600 seconds')
        if model['provider'] == 'openai':
            if model.get('endpoint', 'https://api.openai.com/v1/responses') != 'https://api.openai.com/v1/responses':
                raise ValueError('OpenAI requests must use the official Responses endpoint')
            model.setdefault('key_env', 'OPENAI_API_KEY')
            for rate in ('input_usd_per_million', 'output_usd_per_million'):
                if type(model.get(rate)) not in (int, float) or not math.isfinite(model[rate]) or model[rate] <= 0:
                    raise ValueError('hosted profiles require positive explicit pricing estimates')
            if not model.get('pricing_date') or not model.get('pricing_source'):
                raise ValueError('hosted profiles require pricing provenance')
        else:
            endpoint = urlparse(model.get('endpoint', 'http://127.0.0.1:11434'))
            if endpoint.scheme != 'http' or endpoint.hostname not in ('localhost', '127.0.0.1', '::1') or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
                raise ValueError('local model endpoint must be loopback HTTP without credentials')
    stages = config.setdefault('stages', {})
    if set(stages) - {'backtranslation', 'second_reader', 'triage', 'fixes'}:
        raise ValueError('unknown pipeline stage')
    for name, default in [('backtranslation', False), ('second_reader', False), ('triage', True), ('fixes', False)]:
        stages.setdefault(name, default)
        if type(stages[name]) is not bool:
            raise ValueError('stage switches must be booleans')
    for stage, roles in [('backtranslation', ('backtranslator', 'comparator')), ('second_reader', ('second_reader',)), ('fixes', ('fixer',))]:
        if stages[stage] and any(role not in models for role in roles):
            raise ValueError(f'{stage} requires corresponding model profiles')
    limits = config.setdefault('limits', {})
    defaults = {'max_repairs': 3, 'max_claims': 3, 'max_calls': 30, 'max_cost_usd': 2.0, 'max_input_bytes': 30000}
    if set(limits) - set(defaults):
        raise ValueError('unknown run limit')
    for name, default in defaults.items():
        limits.setdefault(name, default)
        if type(limits[name]) not in (int, float) or not math.isfinite(limits[name]) or limits[name] < 0:
            raise ValueError('run limits must be finite and nonnegative')
    if type(limits['max_repairs']) is not int or limits['max_repairs'] > 3:
        raise ValueError('at most three repairs are allowed')
    for name, maximum in [('max_claims', 20), ('max_calls', 10000), ('max_input_bytes', 200000)]:
        if type(limits[name]) is not int or not 1 <= limits[name] <= maximum:
            raise ValueError(f'invalid {name}')
    return config
