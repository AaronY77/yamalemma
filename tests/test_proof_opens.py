import hashlib
import tempfile
import unittest
from pathlib import Path

from yamalemma.domain import fingerprint, make_claim, make_probe
from yamalemma.harness import check_probe


class FakeWorker:
    def __init__(self, project):
        self.project = project
        self.requests = []

    def request(self, payload, timeout=None):
        self.requests.append(payload)
        return {'status': 'checked', 'type_matches': True, 'axioms': [], 'actual_type': payload['expected']}


class ProofOpenTests(unittest.TestCase):
    def test_proof_is_checked_under_the_item_opens(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory)
            (project / 'lean-toolchain').write_text('leanprover/lean4:v0.0.0')
            (project / 'lake-manifest.json').write_text('{}')
            (project / 'Yamalemma').mkdir()
            (project / 'Yamalemma' / 'Worker.lean').write_text('')
            (project / 'lakefile.toml').write_text('')
            source = 'theorem t : True := trivial'
            item = {'id': 't', 'raw_source': source, 'source_sha256': hashlib.sha256(source.encode()).hexdigest(),
                    'context': {'opens': ['open Filter Topology'], 'declarations': [], 'namespace': '', 'scopes': []},
                    'environment': {'toolchain': 'leanprover/lean4:v0.0.0',
                                    'manifest_sha256': hashlib.sha256(b'{}').hexdigest()}}
            item['fingerprint'] = fingerprint(item)
            claim = make_claim(item, 'c', 'True', 'synthetic', 'scope', 'synthetic', 'parse', 'synthetic obligation')
            worker = FakeWorker(project)
            result = check_probe(worker, item, claim, make_probe(claim, 'confirm', 'by trivial'))
            explicit = check_probe(worker, item, claim, make_probe(claim, 'confirm', '@(open Filter Topology in\ntrivial)'))
        self.assertEqual(worker.requests[0]['proof'], 'open Filter Topology in\nby trivial')
        self.assertEqual(result['probe']['proof'], 'by trivial')
        self.assertEqual(result['proof_opens'], ['open Filter Topology'])
        self.assertTrue(result['accepted'])
        self.assertEqual(worker.requests[1]['proof'], '@(open Filter Topology in\ntrivial)')
        self.assertEqual(explicit['proof_opens'], [])


if __name__ == '__main__':
    unittest.main()
