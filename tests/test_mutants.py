import tempfile
import unittest
from pathlib import Path

from yamalemma.evaluation import freeze_protocol
from yamalemma.mutants import answer_edits, apply_edit, boundary_edits, domain_edits, restoration, score_mutants, wilson


def leaf(kind, raw, text, identifier=None):
    start = raw.index(text.encode())
    return {'kind': kind, 'text': text, 'identifier': identifier, 'start': start, 'end': start + len(text.encode()), 'children': []}


SOURCE = b'theorem t (x : Nat) : 0 < x \xe2\x88\xa7 x \xe2\x88\x88 Set.Icc 0 1 := sorry'


class OperatorTests(unittest.TestCase):
    def test_boundary_swaps_only_the_operator_token(self):
        comparison = {'kind': '«term_<_»', 'children': [leaf('num', SOURCE, '0'), leaf('«<»', SOURCE, '<'), leaf('ident', SOURCE, 'x', 'x')]}
        edits = boundary_edits([comparison], SOURCE)
        self.assertEqual(len(edits), 1)
        self.assertEqual(apply_edit(SOURCE, edits[0]).decode(), 'theorem t (x : Nat) : 0 ≤ x ∧ x ∈ Set.Icc 0 1 := sorry')

    def test_domain_swaps_the_interval_kind_and_keeps_its_namespace(self):
        edits = domain_edits([leaf('ident', SOURCE, 'Set.Icc', 'Set.Icc')], SOURCE)
        self.assertEqual(apply_edit(SOURCE, edits[0]).decode(), 'theorem t (x : Nat) : 0 < x ∧ x ∈ Set.Ico 0 1 := sorry')

    def test_wrong_answer_bumps_a_numeral_in_the_answer_comment(self):
        raw = 'abbrev s_solution : ℕ := sorry\n-- {2, 13}\ntheorem s : s_solution = 2 := sorry\n'.encode()
        edits = answer_edits(raw)
        self.assertEqual([edit['detail'] for edit in edits], ['answer numeral 2 to 3', 'answer numeral 13 to 14'])
        self.assertIn('-- {3, 13}', apply_edit(raw, edits[0]).decode())


def report(fingerprint, reader_claims=(), checked=()):
    claims = [{'claim': claim, 'adjudication': {'evidence_verdict': 'EVIDENCE-CHECKED'}} for claim in checked]
    return {'item_fingerprint': fingerprint, 'reader_claims': list(reader_claims), 'claims': claims, 'model_calls': [],
            'new_cost_usd': 0, 'elapsed_seconds': 0, 'rejected_candidates': []}


class ScoringTests(unittest.TestCase):
    def test_wilson_interval(self):
        self.assertEqual(wilson(0, 10), [0.0, 0.278])
        self.assertIsNone(wilson(0, 0))

    def test_three_levels_and_buckets_are_scored_separately(self):
        mutation = {'operator': 'boundary', 'replacement': '≤', 'detail': '< to ≤'}
        key = [{'item_fingerprint': 'o1', 'role': 'original', 'operator': None, 'mutation': None, 'equivalence': None},
               {'item_fingerprint': 'm1', 'role': 'mutant', 'operator': 'boundary', 'mutation': mutation, 'equivalence': {'bucket': 'undetermined'}},
               {'item_fingerprint': 'm2', 'role': 'mutant', 'operator': 'boundary', 'mutation': mutation, 'equivalence': {'bucket': 'proved_equivalent'}}]
        suspicion = {'type': 'domain', 'location': '0 ≤ x'}
        reports = [report('o1', [{'type': 'scope', 'location': 'y'}]), report('m1', [suspicion], [suspicion]), report('m2')]
        result = score_mutants(key, {'triage': reports}, [{'item_fingerprint': 'o1', 'findings': []}])
        levels = result['arms']['triage']
        self.assertEqual(levels['reader_suspicion']['false_alarm_on_originals']['hits'], 1)
        self.assertEqual(levels['evidence_checked']['false_alarm_on_originals']['hits'], 0)
        self.assertEqual(levels['evidence_checked_located']['detection_undetermined']['hits'], 1)
        self.assertEqual(levels['reader_suspicion']['detection_proved_equivalent']['hits'], 0)
        self.assertEqual(levels['reader_suspicion']['detection_proved_different']['n'], 0)


class RestorationTests(unittest.TestCase):
    def test_exact_restoration_and_refutations_are_counted_without_lean(self):
        mutation = {'operator': 'boundary', 'replacement': '≤', 'detail': '< to ≤'}
        key = [{'item_fingerprint': 'o1', 'group': 'g1', 'role': 'original', 'operator': None, 'mutation': None},
               {'item_fingerprint': 'm1', 'group': 'g1', 'role': 'mutant', 'operator': 'boundary', 'mutation': mutation},
               {'item_fingerprint': 'o2', 'group': 'g2', 'role': 'original', 'operator': None, 'mutation': None},
               {'item_fingerprint': 'm2', 'group': 'g2', 'role': 'mutant', 'operator': 'boundary', 'mutation': mutation}]
        items = [{'fingerprint': 'o1', 'signature_source': '(x : ℕ) : 0 < x', 'expected_type': '∀ (x : ℕ), 0 < x'},
                 {'fingerprint': 'm1', 'signature_source': '(x : ℕ) : 0 ≤ x', 'expected_type': '∀ (x : ℕ), 0 ≤ x'},
                 {'fingerprint': 'o2', 'signature_source': ': 1 < 2', 'expected_type': '1 < 2'},
                 {'fingerprint': 'm2', 'signature_source': ': 1 ≤ 2', 'expected_type': '1 ≤ 2'}]
        restoring = {'id': 'c1', 'template_kind': 'difference', 'type': 'domain', 'location': '0 ≤ x', 'edit': {'from': '0 ≤ x', 'to': '0 < x'}}
        refuting = {'id': 'c2', 'template_kind': 'negated_statement', 'type': 'domain', 'location': '1 ≤ 2', 'edit': None}
        reports = [report('m1', checked=[restoring]), report('m2', checked=[refuting]), report('o1')]
        summary, rows = restoration(None, key, items, reports)
        self.assertEqual((summary['restores_exact_text'], summary['no_edit'], summary['checked_claims']), (1, 1, 2))
        self.assertTrue(all(row['located'] for row in rows))


class SyntheticSplitTests(unittest.TestCase):
    def row(self, **fields):
        base = {'item_fingerprint': 'a', 'label': 'defect', 'split': 'synthetic', 'synthetic': True, 'group': 'g',
                'construction': 'operator', 'label_basis': 'synthetic defect', 'provenance': 'commit'}
        return dict(base, **fields)

    def test_synthetic_rows_need_construction_not_a_reviewer(self):
        with tempfile.TemporaryDirectory() as directory:
            protocol = freeze_protocol([self.row(), self.row(item_fingerprint='b', label='control')],
                                       {'a': {'x': 1}, 'b': {'x': 2}}, Path(directory) / 'protocol.json')
            self.assertEqual(len(protocol['dataset']), 2)
            for bad in (self.row(construction=None), self.row(synthetic=False), self.row(split='heldout')):
                with self.assertRaises(ValueError):
                    freeze_protocol([bad], {'a': {'x': 1}, 'b': {'x': 2}}, Path(directory) / 'bad.json')


if __name__ == '__main__':
    unittest.main()
