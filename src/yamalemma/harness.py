import re
import json
import hashlib
from pathlib import Path

from yamalemma.axiom_policy import assess_axioms
from yamalemma.ingest import wrap
from yamalemma.domain import file_hash, fingerprint, make_probe, validate_claim


POLICY_VERSION = 'kernel-type-and-axioms-v1'
BLOCKED = re.compile(r'\b(?:run_tac|run_elab|elab|macro|syntax|initialize|unsafe|implemented_by|extern|native_decide|eval_expr|eval_term)\b|#')


def environment_record(project):
    files = ['lean-toolchain', 'lakefile.toml', 'lake-manifest.json', 'Yamalemma/Worker.lean']
    record = {name: file_hash(project / name) for name in files}
    record['policy'] = POLICY_VERSION
    record['toolchain'] = (project / 'lean-toolchain').read_text().strip()
    record['implementation'] = {name: file_hash(Path(__file__).parent / name)
                                for name in ('harness.py', 'worker.py', 'ingest.py', 'domain.py', 'axiom_policy.py',
                                             'adjudicate.py', 'templates.py', 'precheck.py', 'report.py', 'storage.py',
                                             'proof_syntax.json')}
    record['fingerprint'] = fingerprint(record)
    return record


def validate_item(item, project):
    item_body = {k: v for k, v in item.items() if k != 'fingerprint'}
    if fingerprint(item_body) != item['fingerprint']:
        raise ValueError('source item was changed after fingerprinting')
    if hashlib.sha256(item['raw_source'].encode()).hexdigest() != item['source_sha256']:
        raise ValueError('source bytes do not match the recorded source hash')
    expected = {'toolchain': (project / 'lean-toolchain').read_text().strip(),
                'manifest_sha256': file_hash(project / 'lake-manifest.json')}
    if item.get('environment') != expected:
        raise ValueError('source item environment differs from the verification environment')


def render_target(worker, item, proposition):
    if BLOCKED.search(proposition):
        return {'status': 'policy_rejected', 'error': 'unsupported executable syntax in target'}
    allowed = json.loads((Path(__file__).parent / 'proof_syntax.json').read_text())
    context = item.get('context', {})
    return worker.request({'action': 'render', 'expected': proposition, 'allowed_syntax': allowed,
                           'context': context.get('declarations', []), 'namespace': context.get('namespace', ''),
                           'scopes': context.get('scopes', [])})


def check_probe(worker, item, claim, probe, store=None):
    validate_claim(claim)
    validate_item(item, worker.project)
    if claim['item_fingerprint'] != item['fingerprint']:
        raise ValueError('claim source binding mismatch')
    expected_probe = make_probe(claim, probe['polarity'], probe['proof'], probe['template'])
    if probe != expected_probe:
        raise ValueError('probe target or source binding was changed')
    environment = environment_record(worker.project)
    result = {
        'claim_fingerprint': fingerprint(claim), 'item_fingerprint': item['fingerprint'],
        'polarity': probe['polarity'], 'expected': probe['expected'],
        'probe': probe, 'environment': environment, 'scope': claim['scope'],
        'accepted': False, 'type_matches': False, 'axiom_policy': 'unreadable',
    }
    context = item.get('context', {})
    supports = context.get('declarations', [])
    terms = [probe['proof'], probe['expected']] + [support[key] for support in supports for key in ('type', 'value')]
    if item.get('unsupported'):
        response = {'status': 'unsupported', 'error': '; '.join(item['unsupported'])}
    elif any(BLOCKED.search(term) for term in terms):
        response = {'status': 'policy_rejected', 'error': 'unsupported executable syntax in proof slot'}
    else:
        allowed = json.loads((Path(__file__).parent / 'proof_syntax.json').read_text())
        opens = [] if probe['proof'].lstrip().startswith('@(') else context.get('opens', [])
        result['proof_opens'] = opens
        response = worker.request({'action': 'check', 'expected': probe['expected'], 'proof': wrap(probe['proof'], opens),
                                   'allowed_syntax': allowed, 'context': supports, 'namespace': context.get('namespace', ''),
                                   'scopes': context.get('scopes', [])})
    result['attempt'] = response
    if response.get('status') == 'checked' and response.get('type_matches') is True:
        axioms = response.get('axioms')
        if isinstance(axioms, list) and all(isinstance(name, str) and name for name in axioms):
            decision = assess_axioms(tuple(axioms))
            result.update(type_matches=True, axioms=axioms, axiom_policy=decision.status,
                          forbidden_axioms=list(decision.forbidden_axioms), actual_type=response['actual_type'])
            result['accepted'] = decision.status == 'allowed'
    result['reason'] = 'validated' if result['accepted'] else response.get('error', result['axiom_policy'])
    result['id'] = fingerprint(result)
    if store:
        key = store.put(result)
        store.event({'event': 'probe', 'artifact_key': key, 'evidence_id': result['id'], 'accepted': result['accepted']})
    return result
