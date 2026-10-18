import tempfile
import unittest
from pathlib import Path

from yamalemma.adjudicate import adjudicate
from yamalemma.domain import fingerprint, make_claim, make_probe
from yamalemma.storage import ArtifactStore


class DomainTests(unittest.TestCase):
    def setUp(self):
        self.item = {'raw_source': 'example : True := by trivial'}
        self.item['fingerprint'] = fingerprint(self.item)
        self.claim = make_claim(self.item, 'test', 'True', 'a test claim', 'vacuous', 'test scope', 'intrinsic', 'review meaning')

    def evidence(self, polarity, accepted=True):
        probe = make_probe(self.claim, polarity, 'by trivial')
        return dict(probe, accepted=accepted, type_matches=True, axiom_policy='allowed', id=polarity)

    def test_polarities_share_one_claim(self):
        self.assertEqual(make_probe(self.claim, 'refute', 'by trivial')['expected'], 'Not (True)')

    def test_verdicts(self):
        for polarities, expected in [((), 'UNRESOLVED'), (('confirm',), 'EVIDENCE-CHECKED'),
                                     (('refute',), 'REFUTED'), (('confirm', 'refute'), 'INTERNAL-ERROR')]:
            with self.subTest(polarities=polarities):
                result = adjudicate(self.claim, [self.evidence(p) for p in polarities])
                self.assertEqual(result['evidence_verdict'], expected)
                self.assertEqual(result['finding_status'], 'unconfirmed')

    def test_failed_execution_is_not_refutation(self):
        result = adjudicate(self.claim, [self.evidence('refute', False)])
        self.assertEqual(result['evidence_verdict'], 'UNRESOLVED')

    def test_wrong_claim_is_rejected(self):
        evidence = self.evidence('confirm')
        evidence['claim_fingerprint'] = 'wrong'
        with self.assertRaises(ValueError):
            adjudicate(self.claim, [evidence])

    def test_incomplete_validation_is_rejected(self):
        evidence = self.evidence('confirm')
        evidence['axiom_policy'] = 'forbidden'
        with self.assertRaises(ValueError):
            adjudicate(self.claim, [evidence])

    def test_human_review_is_explicit_and_claim_bound(self):
        review = {'claim_fingerprint': fingerprint(self.claim), 'obligation': 'review meaning',
                  'method': 'human', 'reviewer': 'test reviewer', 'justification': 'test justification'}
        result = adjudicate(self.claim, [self.evidence('confirm')], [review])
        self.assertEqual(result['finding_status'], 'confirmed')
        review['claim_fingerprint'] = 'other'
        self.assertEqual(adjudicate(self.claim, [self.evidence('confirm')], [review])['finding_status'], 'unconfirmed')

    def test_artifact_corruption_is_detected(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ArtifactStore(directory)
            key = store.put(self.claim)
            self.assertEqual(store.get(key), self.claim)
            (Path(directory) / 'objects' / f'{key}.json').write_text('{}')
            with self.assertRaises(ValueError):
                store.get(key)
