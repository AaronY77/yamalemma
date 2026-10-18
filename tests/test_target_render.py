import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from test_next_models import configuration, response
from yamalemma.domain import fingerprint
from yamalemma.models import ModelClient
from yamalemma.pipeline import audit_item


class FakeWorker:
    def __init__(self, project):
        self.project = project
        self.requests = []

    def request(self, payload, timeout=None):
        self.requests.append(payload)
        if payload.get('action') == 'render':
            if ';' in payload['expected']:
                return {'status': 'failure', 'error': "<input>:2:41: expected ','"}
            return {'status': 'rendered', 'type': payload['expected']}
        return {'status': 'failure', 'error': 'not proved'}


def project(directory):
    root = Path(directory)
    root.mkdir()
    (root / 'lean-toolchain').write_text('leanprover/lean4:v0.0.0')
    (root / 'lake-manifest.json').write_text('{}')
    (root / 'lakefile.toml').write_text('')
    (root / 'Yamalemma').mkdir()
    (root / 'Yamalemma' / 'Worker.lean').write_text('')
    return root


def item():
    source = 'theorem t (x : ℕ) : x = x → x ≤ 1 ∧ x ≥ 0 := sorry'
    value = {'id': 't', 'raw_source': source, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
             'signature_source': '(x : ℕ) : x = x → x ≤ 1 ∧ x ≥ 0', 'expected_type': '∀ (x : ℕ), x = x → x ≤ 1 ∧ x ≥ 0',
             'conclusion': 'x = x → x ≤ 1 ∧ x ≥ 0', 'binders': '(x : ℕ)', 'informal': 'Synthetic fixture.', 'docstring': '',
             'context': {'opens': [], 'declarations': [], 'namespace': '', 'scopes': []},
             'environment': {'toolchain': 'leanprover/lean4:v0.0.0', 'manifest_sha256': hashlib.sha256(b'{}').hexdigest()}}
    value['fingerprint'] = fingerprint(value)
    return value


def candidate(witnesses):
    return {'type': 'precedence', 'location': 'x = x', 'explanation': 'Synthetic fixture.', 'prediction': 'Synthetic.',
            'probe_kind': 'separation', 'comparison': None, 'witnesses': witnesses,
            'edit_from': 'x = x → x ≤ 1', 'edit_to': '(x = x → x ≤ 1)', 'bridge': 'schema', 'obligation': 'Synthetic obligation.'}


class TargetRenderTests(unittest.TestCase):
    def run_audit(self, witnesses):
        config = configuration()
        config['stages']['triage'] = True
        roles = []

        def transport(url, body, headers, timeout):
            if 'claims' in body['format']['properties']:
                roles.append('reader')
                return response({'claims': [candidate(witnesses)], 'summary': 'Synthetic.'})
            roles.append('writer')
            return response({'proof': None, 'abstain_reason': 'synthetic decline'})

        with tempfile.TemporaryDirectory() as directory:
            worker = FakeWorker(project(Path(directory) / 'project'))
            client = ModelClient(config, Path(directory) / 'models', transport=transport)
            result = audit_item(worker, client, item(), config, Path(directory) / 'audit')
        return result, roles

    def test_unparsable_target_is_rejected_before_any_proof_call(self):
        result, roles = self.run_audit('(x : ℕ); take x = 0')
        self.assertEqual(roles, ['reader'])
        self.assertEqual(result['claims'], [])
        self.assertIn('target does not elaborate', result['rejected_candidates'][0]['reason'])

    def test_valid_target_reaches_the_writer(self):
        result, roles = self.run_audit('(x : ℕ)')
        self.assertEqual(roles, ['reader', 'writer', 'writer'])
        self.assertEqual(len(result['claims']), 1)
        self.assertEqual(result['rejected_candidates'], [])


if __name__ == '__main__':
    unittest.main()
