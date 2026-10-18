import hashlib
import json
from pathlib import Path


BRIDGES = {'intrinsic', 'parse', 'instance', 'schema', 'translated'}
CLAIM_TYPES = {'vacuous', 'precedence', 'scope', 'extra_hyp', 'missing_hyp', 'domain',
               'coercion_junk', 'wrong_answer', 'wrong_strength', 'docstring_mismatch'}


def fingerprint(value):
    data = json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':')).encode()
    return hashlib.sha256(data).hexdigest()


def file_hash(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def require_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f'{field} must be a nonempty string')
    return value


def validate_claim(claim):
    for key in ('id', 'item_fingerprint', 'prediction', 'proposition', 'scope', 'explanation'):
        require_text(claim.get(key), key)
    if claim.get('type') not in CLAIM_TYPES:
        raise ValueError('unsupported claim type')
    bridges = claim.get('bridges')
    if not isinstance(bridges, list) or not bridges:
        raise ValueError('claims require explicit bridge obligations')
    for bridge in bridges:
        if bridge.get('type') not in BRIDGES:
            raise ValueError('unsupported bridge type')
        require_text(bridge.get('obligation'), 'bridge obligation')
    return claim


def make_claim(item, claim_id, proposition, prediction, claim_type, scope, bridge_type, obligation):
    claim = {
        'schema_version': 1, 'id': claim_id, 'item_fingerprint': item['fingerprint'],
        'proposition': proposition, 'prediction': prediction, 'explanation': prediction,
        'type': claim_type, 'scope': scope,
        'bridges': [{'type': bridge_type, 'obligation': obligation}],
    }
    return validate_claim(claim)


def make_probe(claim, polarity, proof, template='proposition-v1'):
    validate_claim(claim)
    if polarity not in ('confirm', 'refute'):
        raise ValueError('polarity must be confirm or refute')
    require_text(proof, 'proof')
    proposition = claim['proposition']
    expected = proposition if polarity == 'confirm' else f'Not ({proposition})'
    return {
        'schema_version': 1, 'claim_fingerprint': fingerprint(claim),
        'item_fingerprint': claim['item_fingerprint'], 'polarity': polarity,
        'template': template, 'expected': expected, 'proof': proof,
    }


def save_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n')


def load_json(path):
    return json.loads(Path(path).read_text())
