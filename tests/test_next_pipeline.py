import copy
import json
import tempfile
import unittest
from pathlib import Path

from test_next_models import configuration, response
from yamalemma.domain import fingerprint
from yamalemma.ingest import ingest_source
from yamalemma.models import ModelClient
from yamalemma.pipeline import audit_item, review_audit
from yamalemma.prompts import prepare_claim, backtranslation_messages
from yamalemma.worker import LeanWorker
from yamalemma.fixes import propose_fix


ROOT = Path(__file__).resolve().parents[1]


def candidate():
    return {'type': 'vacuous', 'location': 'n < 0', 'explanation': 'Impossible natural-number assumption.',
            'prediction': 'The declaration assumptions imply False.', 'probe_kind': 'vacuity', 'comparison': None,
            'bridge': 'intrinsic', 'obligation': 'Review whether the original problem permits these inputs.'}


class PipelineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worker = LeanWorker(ROOT / 'lean')
        cls.worker.start()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.lean'
            path.write_text('import Mathlib\ntheorem sample (n : Nat) (h : n < 0) : n = 1 := by omega\n')
            cls.item = ingest_source(cls.worker, path, informal='PRIVATE_INFORMAL_SENTINEL')[0]

    @classmethod
    def tearDownClass(cls):
        cls.worker.close()

    def test_real_lean_repair_and_replay(self):
        config = configuration()
        config['limits']['max_calls'] = 20
        counts = {'confirm': 0, 'refute': 0}
        def transport(url, body, headers, timeout):
            if 'claims' in body['format']['properties']:
                return response({'claims': [candidate()], 'summary': 'One discrepancy candidate.'})
            payload = json.loads(body['messages'][1]['content'])
            polarity = 'refute' if payload['expected'].startswith('Not (') else 'confirm'
            counts[polarity] += 1
            proof = 'by omega' if polarity == 'confirm' and counts[polarity] > 1 else 'by rfl'
            return response({'proof': proof})
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(config, Path(directory) / 'models', transport=transport)
            result = audit_item(self.worker, client, self.item, config, Path(directory) / 'audit')
            self.assertEqual(counts, {'confirm': 2, 'refute': 4})
            self.assertEqual(result['claims'][0]['adjudication']['evidence_verdict'], 'EVIDENCE-CHECKED')
            self.assertEqual(result['claims'][0]['adjudication']['finding_status'], 'unconfirmed')
            replay = ModelClient(config, Path(directory) / 'models', offline=True, transport=lambda *args: self.fail('network used'))
            again = audit_item(self.worker, replay, self.item, config, Path(directory) / 'replay')
            self.assertEqual(again['claims'][0]['adjudication']['evidence_verdict'], 'EVIDENCE-CHECKED')
            self.assertTrue(all(call['reused'] for call in again['model_calls']))
            self.assertEqual(again['new_cost_usd'], 0)

    def test_local_differences_do_not_bypass_reader(self):
        config = configuration()
        config['stages']['backtranslation'] = True
        for role in ('backtranslator', 'comparator'):
            config['models'][role] = dict(config['models']['reader'])
        captured = []
        def transport(url, body, headers, timeout):
            captured.append(body)
            fields = body['format']['properties']
            if 'paraphrase' in fields:
                self.assertNotIn('PRIVATE_INFORMAL_SENTINEL', json.dumps(body))
                return response({'paraphrase': 'A proposition with contradictory assumptions.'})
            if 'differences' in fields:
                return response({'differences': ['A possible contradiction.']})
            if 'claims' in fields:
                return response({'claims': [], 'summary': 'No supported discrepancy found.'})
            self.fail('local differences bypassed the reader')
        with tempfile.TemporaryDirectory() as directory:
            result = audit_item(self.worker, ModelClient(config, Path(directory) / 'models', transport=transport),
                                self.item, config, Path(directory) / 'audit')
            self.assertEqual(len(captured), 3)
            self.assertEqual(result['claims'], [])
            self.assertTrue(result['no_claim_detected'])

    def test_refusal_is_not_no_claim_or_refutation(self):
        config = configuration()
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(config, Path(directory) / 'models', transport=lambda *args: {'done': True, 'done_reason': 'length'})
            result = audit_item(self.worker, client, self.item, config, Path(directory) / 'audit')
            self.assertEqual(result['status'], 'reader_incomplete')
            self.assertFalse(result['no_claim_detected'])
            self.assertEqual(result['claims'], [])

    def test_invalid_source_location_never_reaches_writer(self):
        config = configuration()
        bad = candidate()
        bad['location'] = 'not present'
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(config, Path(directory) / 'models', transport=lambda *args: response({'claims': [bad], 'summary': 'test'}))
            result = audit_item(self.worker, client, self.item, config, Path(directory) / 'audit')
            self.assertEqual(len(result['rejected_candidates']), 1)
            self.assertEqual(len(client.calls), 1)

    def test_template_preserves_exact_source_and_marks_translation(self):
        value = candidate()
        value.update(probe_kind='equivalence', comparison='True')
        claim = prepare_claim(self.item, value, 1)
        self.assertIn(self.item['expected_type'], claim['proposition'])
        self.assertEqual(claim['bridges'][0]['type'], 'translated')
        value.update(probe_kind='statement')
        with self.assertRaises(ValueError):
            prepare_claim(self.item, value, 1)

    def test_elaborated_fix_is_not_a_faithfulness_certificate(self):
        config = configuration()
        config['models']['fixer'] = dict(config['models']['writer'])
        claim = prepare_claim(self.item, candidate(), 1)
        with tempfile.TemporaryDirectory() as directory:
            client = ModelClient(config, directory, transport=lambda *args: response({
                'statement': 'True', 'explanation': 'Synthetic candidate, not a reviewed correction.', 'direction': 'unknown'}))
            result = propose_fix(self.worker, client, self.item, claim, {})
            self.assertEqual(result['status'], 'elaborated')
            self.assertFalse(result['faithfulness_certified'])
            self.assertEqual(result['review_status'], 'pending')

    def test_review_rechecks_and_rejects_changed_audit(self):
        config = configuration()
        config['limits']['max_calls'] = 20
        def transport(url, body, headers, timeout):
            if 'claims' in body['format']['properties']:
                return response({'claims': [candidate()], 'summary': 'test'})
            payload = json.loads(body['messages'][1]['content'])
            return response({'proof': 'by rfl' if payload['expected'].startswith('Not (') else 'by omega'})
        with tempfile.TemporaryDirectory() as directory:
            result = audit_item(self.worker, ModelClient(config, Path(directory) / 'models', transport=transport), self.item, config, Path(directory) / 'audit')
            claim = result['claims'][0]['claim']
            review = {'claim_fingerprint': fingerprint(claim), 'method': 'human', 'reviewer': 'explicit test fixture reviewer',
                      'obligation': claim['bridges'][0]['obligation'], 'justification': 'Synthetic test sign-off; not a real benchmark review.'}
            reviewed = review_audit(self.worker, result, [review])
            self.assertEqual(reviewed['finding_status'], 'confirmed')
            result['status'] = 'tampered'
            with self.assertRaises(ValueError):
                review_audit(self.worker, result, [review])
