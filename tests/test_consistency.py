import json
import tempfile
import unittest
from pathlib import Path

from test_next_models import configuration, response
from test_next_pipeline import ROOT, candidate
from yamalemma.consistency import cluster_samples, consistency_summary
from yamalemma.config import validate_config
from yamalemma.ingest import ingest_source
from yamalemma.models import ModelClient
from yamalemma.pipeline import audit_item
from yamalemma.worker import LeanWorker


ITEM = {'conclusion': '∀ x ∈ T, (P x) ∧ (Q x) → R'}


def claim(claim_type, location, probe_kind='statement', edit_from=None, edit_to=None):
    return {'type': claim_type, 'location': location, 'probe_kind': probe_kind, 'edit_from': edit_from, 'edit_to': edit_to}


REGROUP = claim('precedence', 'R', 'separation', '∀ x ∈ T, (P x) ∧ (Q x) → R', '(∀ x ∈ T, P x) ∧ ((Q x) → R)')
REWRITE = claim('wrong_strength', 'R', 'separation', '→ R', '∧ R')


class ConsistencyTests(unittest.TestCase):
    def test_majority_cluster_prefers_regrouping_over_rewrite(self):
        found, summary = consistency_summary(ITEM, [[REWRITE], [REGROUP], [claim('scope', 'T')]], ['completed'] * 3)
        self.assertEqual(found, [REGROUP])
        self.assertEqual(summary['kept_clusters'], 1)
        self.assertEqual(summary['clusters'][0]['support'], 2)
        self.assertEqual(summary['clusters'][0]['representative_edit_kind'], 'regrouping')
        self.assertEqual(summary['cluster_agreement_rate'], 0.5)
        self.assertTrue(summary['item_agreement'])

    def test_single_sample_suspicion_is_dropped(self):
        found, summary = consistency_summary(ITEM, [[claim('domain', 'x')], [], []], ['completed'] * 3)
        self.assertEqual(found, [])
        self.assertFalse(summary['item_agreement'])
        self.assertEqual(summary['samples_with_claims'], 1)

    def test_claims_within_one_sample_do_not_support_each_other(self):
        clusters = cluster_samples(ITEM, [[claim('domain', 'x'), claim('domain', 'y')], [], []])
        self.assertTrue(all(cluster['support'] == 1 for cluster in clusters))

    def test_no_claims_anywhere(self):
        found, summary = consistency_summary(ITEM, [[], [], []], ['completed'] * 3)
        self.assertEqual(found, [])
        self.assertIsNone(summary['cluster_agreement_rate'])
        self.assertTrue(summary['item_agreement'])

    def test_reader_samples_limit_is_optional_and_bounded(self):
        config = configuration()
        self.assertNotIn('reader_samples', validate_config(config)['limits'])
        config['limits']['reader_samples'] = 9
        with self.assertRaises(ValueError):
            validate_config(config)


class SampledPipelineTests(unittest.TestCase):
    def test_three_samples_use_separate_cache_keys_and_keep_the_majority_claim(self):
        config = configuration()
        config['limits'].update(max_calls=20, reader_samples=3)
        config['stages']['triage'] = False
        replies = iter([[candidate()], [], [candidate()]])
        def transport(url, body, headers, timeout):
            return response({'claims': next(replies), 'summary': 'synthetic'})
        with LeanWorker(ROOT / 'lean') as worker, tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'source.lean'
            path.write_text('import Mathlib\ntheorem sample (n : Nat) (h : n < 0) : n = 1 := by omega\n')
            item = ingest_source(worker, path)[0]
            client = ModelClient(config, Path(directory) / 'models', transport=transport)
            result = audit_item(worker, client, item, config, Path(directory) / 'audit')
            self.assertEqual(len({call['request_key'] for call in result['model_calls']}), 3)
            self.assertEqual(len(result['reader_claims']), 1)
            self.assertEqual(result['reader_consistency']['reader']['clusters'][0]['support'], 2)
            replay = ModelClient(config, Path(directory) / 'models', offline=True, transport=lambda *args: self.fail('network used'))
            again = audit_item(worker, replay, item, config, Path(directory) / 'replay')
            self.assertEqual(again['reader_claims'], result['reader_claims'])


if __name__ == '__main__':
    unittest.main()
