import copy
import tempfile
import unittest
from pathlib import Path

from test_next_models import configuration
from yamalemma.domain import fingerprint
from yamalemma.evaluation import freeze_protocol, score


class EvaluationTests(unittest.TestCase):
    def dataset(self):
        return [{'item_fingerprint': 'a', 'label': 'defect', 'split': 'heldout', 'group': 'history-a',
                 'reviewer': 'fixture reviewer', 'label_basis': 'synthetic test label', 'provenance': 'fixture'},
                {'item_fingerprint': 'b', 'label': 'control', 'split': 'heldout', 'group': 'history-b',
                 'reviewer': 'fixture reviewer', 'label_basis': 'synthetic test label', 'provenance': 'fixture'}]

    def test_freeze_is_immutable_and_groups_do_not_leak(self):
        config = configuration()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'protocol.json'
            freeze_protocol(self.dataset(), {'baseline': config, 'triage': config}, path)
            with self.assertRaises(FileExistsError):
                freeze_protocol(self.dataset(), {'baseline': config, 'triage': config}, path)
            rows = self.dataset()
            rows[1].update(group='history-a', split='development')
            with self.assertRaisesRegex(ValueError, 'leaks'):
                freeze_protocol(rows, {'baseline': config, 'triage': config}, Path(directory) / 'other.json')

    def test_no_unreviewed_clean_labels(self):
        rows = self.dataset()
        rows[1]['reviewer'] = ''
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                freeze_protocol(rows, {'one': configuration(), 'two': configuration()}, Path(directory) / 'protocol.json')

    def test_missing_and_zero_finding_denominators(self):
        config = configuration()
        with tempfile.TemporaryDirectory() as directory:
            protocol = freeze_protocol(self.dataset(), {'one': config, 'two': config}, Path(directory) / 'protocol.json')
            result = score(protocol, [], 'one', config)
            self.assertEqual(result['missing_reports'], 2)
            self.assertEqual(result['reader_item_recall'], 0)
            self.assertIsNone(result['confirmed_item_precision'])
            self.assertIsNone(result['cost_per_confirmed_item'])

    def test_results_must_be_bound_before_execution(self):
        config = configuration()
        with tempfile.TemporaryDirectory() as directory:
            protocol = freeze_protocol(self.dataset(), {'one': config, 'two': config}, Path(directory) / 'protocol.json')
            report = {'item_fingerprint': 'a', 'config_fingerprint': fingerprint(config), 'protocol_fingerprint': 'different'}
            report['hash'] = fingerprint(report)
            with self.assertRaisesRegex(ValueError, 'before running'):
                score(protocol, [report], 'one', config)

    def test_changed_protocol_rejected(self):
        config = configuration()
        with tempfile.TemporaryDirectory() as directory:
            protocol = freeze_protocol(self.dataset(), {'one': config, 'two': config}, Path(directory) / 'protocol.json')
            protocol['dataset'][0]['label'] = 'control'
            with self.assertRaises(ValueError):
                score(protocol, [], 'one', config)

    def test_claim_and_direction_metrics_require_exact_review(self):
        config = configuration()
        claim = {'id': 'synthetic', 'bridges': [{'type': 'parse'}]}
        with tempfile.TemporaryDirectory() as directory:
            protocol = freeze_protocol(self.dataset(), {'one': config, 'two': config}, Path(directory) / 'protocol.json')
            report = {'item_fingerprint': 'a', 'config_fingerprint': fingerprint(config), 'protocol_fingerprint': protocol['fingerprint'],
                      'reader_claims': [{}], 'claims': [{'claim': claim, 'adjudication': {'evidence_verdict': 'EVIDENCE-CHECKED', 'finding_status': 'confirmed'},
                                                       'evidence': [{}], 'fix': {'candidate': {'direction': 'unknown'}}}],
                      'status': 'reviewed', 'unknown_cost_calls': 1}
            report['hash'] = fingerprint(report)
            result = score(protocol, [report], 'one', config)
            self.assertIsNone(result['reviewed_confirmed_claim_precision'])
            self.assertIsNone(result['direction_accuracy'])
            self.assertIsNone(result['cost_per_confirmed_item'])
            judgment = {'audit_hash': report['hash'], 'claim_fingerprint': fingerprint(claim), 'reviewer': 'synthetic fixture reviewer',
                        'justification': 'Synthetic metric test only.', 'meaning': 'incorrect', 'direction': 'incorrect'}
            result = score(protocol, [report], 'one', config, [judgment])
            self.assertEqual(result['reviewed_confirmed_claim_precision'], 0)
            self.assertEqual(result['direction_accuracy'], 0)
            self.assertEqual(result['by_bridge']['parse']['reviewed_precision'], 0)
            self.assertEqual(result['formal_attempt_coverage'], 1)
            judgment['audit_hash'] = 'changed'
            with self.assertRaisesRegex(ValueError, 'exact audit claim'):
                score(protocol, [report], 'one', config, [judgment])
