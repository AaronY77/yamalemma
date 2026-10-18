import unittest

import jsonschema

from yamalemma.prompts import CLAIM_SCHEMA, edit_kind, prepare_claim


def item(conclusion='x = x → x ≤ 1 ∧ x ≥ 0'):
    return {'id': 'synthetic', 'fingerprint': 'synthetic-item', 'signature_source': f'(x : ℕ) : {conclusion}',
            'expected_type': f'∀ (x : ℕ), {conclusion}', 'conclusion': conclusion, 'binders': '(x : ℕ)',
            'context': {'namespace': '', 'declarations': [], 'opens': ['open Nat']}}


def candidate(**changes):
    value = {'type': 'precedence', 'location': 'x = x', 'explanation': 'Synthetic fixture.',
             'prediction': 'Synthetic separation.', 'probe_kind': 'separation', 'comparison': None,
             'witnesses': '(x : ℕ)', 'edit_from': 'x ≤ 1 ∧ x ≥ 0', 'edit_to': '(x ≤ 1) ∧ (x ≥ 0)',
             'bridge': 'schema', 'obligation': 'Synthetic obligation.'}
    value.update(changes)
    return value


class SeparationTests(unittest.TestCase):
    def test_target_uses_the_exact_conclusion_and_the_declared_edit(self):
        claim = prepare_claim(item(), candidate(edit_from='x = x → x ≤ 1', edit_to='(x = x → x ≤ 1)'), 1)
        self.assertEqual(claim['proposition'],
                         'open Nat in\n∃ (x : ℕ), (x = x → x ≤ 1 ∧ x ≥ 0) ∧ ¬ ((x = x → x ≤ 1) ∧ x ≥ 0)')
        self.assertEqual(claim['edit']['kind'], 'regrouping')
        self.assertEqual(claim['bridges'][0]['type'], 'schema')
        self.assertIn('only regroups', claim['bridges'][0]['obligation'])

    def test_rewrites_are_flagged_and_free_comparisons_rejected(self):
        claim = prepare_claim(item(), candidate(edit_from='x ≤ 1 ∧ x ≥ 0', edit_to='x ≤ 1'), 1)
        self.assertEqual(claim['edit']['kind'], 'rewrite')
        self.assertIn('may come from the rewrite', claim['bridges'][0]['obligation'])
        with self.assertRaisesRegex(ValueError, 'declared edit'):
            prepare_claim(item(), candidate(comparison='x ≤ 1'), 1)

    def test_edit_must_match_once_and_change_the_text(self):
        for changes in ({'edit_from': 'absent'}, {'edit_from': 'x'}, {'edit_to': 'x ≤ 1 ∧ x ≥ 0'},
                        {'witnesses': None}, {'edit_from': None}, {'edit_to': None}):
            with self.assertRaises(ValueError):
                prepare_claim(item(), candidate(**changes), 1)

    def test_other_templates_reject_separation_fields(self):
        with self.assertRaisesRegex(ValueError, 'only separation'):
            prepare_claim(item(), candidate(probe_kind='statement'), 1)
        plain = candidate(probe_kind='statement', witnesses=None, edit_from=None, edit_to=None)
        self.assertEqual(prepare_claim(item(), plain, 1)['proposition'], item()['expected_type'])

    def test_edit_kinds(self):
        self.assertEqual(edit_kind('a ∧ b → c', '(a ∧ b) → c'), 'regrouping')
        self.assertEqual(edit_kind('∀ x, ∃ y, p x y', '∃ y, ∀ x, p x y'), 'reordering')
        self.assertEqual(edit_kind('a ∧ b → c', 'a ∧ c'), 'rewrite')

    def test_reader_schema_requires_the_new_fields(self):
        jsonschema.validate(candidate(), CLAIM_SCHEMA)
        for key in ('witnesses', 'edit_from', 'edit_to'):
            value = candidate()
            del value[key]
            with self.assertRaises(jsonschema.ValidationError):
                jsonschema.validate(value, CLAIM_SCHEMA)


if __name__ == '__main__':
    unittest.main()
