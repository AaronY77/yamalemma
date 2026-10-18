import json
import tempfile
import unittest
from pathlib import Path

from yamalemma.demo import run_demo
from yamalemma.domain import make_claim, make_probe
from yamalemma.harness import check_probe
from yamalemma.ingest import ingest_source, ingest_putnam
from yamalemma.precheck import precheck
from yamalemma.worker import LeanWorker


ROOT = Path(__file__).resolve().parents[1]


class DevelopmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worker = LeanWorker(ROOT / 'lean')
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.worker.close()

    def test_seven_case_demo(self):
        with tempfile.TemporaryDirectory() as directory:
            results = run_demo(self.worker, ROOT, Path(directory))
            self.assertEqual([entry['verdict'] for entry in results], ['EVIDENCE-CHECKED'] * 5 + ['REFUTED'] * 2)
            self.assertTrue(all(entry['finding_status'] == 'unconfirmed' for entry in results))

    def test_twelve_source_statements_and_placeholders(self):
        items = ingest_putnam(self.worker, ROOT / 'fixtures/exp5')
        self.assertEqual(len(items), 12)
        unresolved = []
        for item in items:
            with self.subTest(item=item['id']):
                result = precheck(self.worker, item)
                if item['id'] in ('S01', 'S04', 'S09', 'S10'):
                    self.assertEqual(result['status'], 'unresolved')
                    self.assertIn('placeholder', result['reasons'][0])
                    unresolved.append(item['id'])
                else:
                    self.assertEqual(result['status'], 'completed', result)
        self.assertEqual(len(unresolved), 4)

    def test_original_certificates_and_intentional_failures(self):
        paths = [ROOT / f'fixtures/prior/{name}.lean' for name in ('E1b', 'E1c', 'E2', 'E4')]
        paths += [ROOT / f'lean/fixtures/{name}.lean' for name in ('E5_audit', 'E6_audit')]
        count = 0
        for path in paths:
            for item in ingest_source(self.worker, path):
                with self.subTest(theorem=item['id']):
                    claim = make_claim(item, item['id'], item['expected_type'], 'original certificate regression',
                                       'wrong_strength', 'original certificate proposition', 'translated',
                                       'This regression does not establish informal faithfulness.')
                    evidence = check_probe(self.worker, item, claim, make_probe(claim, 'confirm', item['proof']))
                    if item['id'].startswith('TC.'):
                        self.assertFalse(evidence['accepted'])
                    else:
                        self.assertTrue(evidence['accepted'], evidence['attempt'])
                    count += 1
        self.assertEqual(count, 52)
