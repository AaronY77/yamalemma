import unittest

from yamalemma.consistency import consistency_summary
from yamalemma.prompts import binder_move, declared_edit_kind, prepare_claim
from yamalemma.signature import split_hypotheses


def group(names, type_text, uses=(), instance=False):
    return {'names': list(names), 'type': type_text, 'uses': list(uses), 'text': '', 'instance': instance}


GROUPS = [group(['G'], 'Type*'), group([], 'Group G', ['G', 'Group'], instance=True), group(['g', 'h'], 'G', ['G']),
          group(['ghgen'], 'closure {g, h} = ⊤ ∧ ¬closure {g} = ⊤', ['closure', 'g', 'h']),
          group(['godd'], 'Odd (orderOf g)', ['Odd', 'orderOf', 'g'])]
SIGNATURE = dict(split_hypotheses(GROUPS, {'x', 'G', 'g'}), status='found')
SYNTHETIC = {'id': 'SYNTHETIC-HYP', 'fingerprint': 'synthetic', 'conclusion': '∀ x : G, P x g',
             'binders': '(G : Type*) [Group G] (g h : G) (ghgen : closure {g, h} = ⊤ ∧ ¬closure {g} = ⊤) (godd : Odd (orderOf g))',
             'signature_source': '(G : Type*) [Group G] (g h : G) (ghgen : closure {g, h} = ⊤ ∧ ¬closure {g} = ⊤) (godd : Odd (orderOf g)) : ∀ x : G, P x g',
             'expected_type': '∀ (G : Type*) [Group G] (g h : G), ∀ x : G, P x g', 'context': {'opens': []}}


def candidate(**fields):
    base = {'type': 'extra_hyp', 'location': '¬closure {g} = ⊤', 'explanation': 'synthetic', 'prediction': 'synthetic',
            'probe_kind': 'hypothesis_separation', 'comparison': None, 'witnesses': None,
            'edit_from': 'closure {g, h} = ⊤ ∧ ¬closure {g} = ⊤', 'edit_to': 'closure {g, h} = ⊤',
            'bridge': 'schema', 'obligation': 'synthetic'}
    return dict(base, **fields)


class SignatureSeparationTests(unittest.TestCase):
    def test_unreferenced_named_binders_are_hypotheses(self):
        self.assertEqual([row['names'] for row in SIGNATURE['hypotheses']], [['ghgen'], ['godd']])
        self.assertEqual(SIGNATURE['witnesses'], '(G : Type) (_inst1 : Group G) (g h : G)')

    def test_hypothesis_edit_builds_an_instance_separation(self):
        claim = prepare_claim(SYNTHETIC, candidate(), 1, SIGNATURE)
        self.assertEqual(claim['proposition'],
                         '∃ (G : Type) (_inst1 : Group G) (g h : G), ((closure {g, h} = ⊤) ∧ (Odd (orderOf g))) ∧ '
                         '¬ ((closure {g, h} = ⊤ ∧ ¬closure {g} = ⊤) ∧ (Odd (orderOf g)))')
        self.assertEqual(claim['bridges'][0]['type'], 'instance')
        self.assertEqual(claim['edit']['kind'], 'rewrite')
        self.assertEqual(claim['edit']['hypothesis'], ['ghgen'])
        self.assertIn('admissible in the original problem', claim['bridges'][0]['obligation'])

    def test_hypothesis_edit_must_hit_exactly_one_hypothesis(self):
        for fields in ({'edit_from': 'Q', 'edit_to': 'R'}, {'edit_from': 'g', 'edit_to': 'h'}, {'witnesses': '(G : Type)'}):
            with self.assertRaises(ValueError):
                prepare_claim(SYNTHETIC, candidate(**fields), 1, SIGNATURE)
        with self.assertRaises(ValueError):
            prepare_claim(SYNTHETIC, candidate(), 1, None)

    def test_conclusion_edits_still_reject_hypothesis_text(self):
        with self.assertRaises(ValueError):
            prepare_claim(SYNTHETIC, candidate(probe_kind='separation', witnesses='(G : Type)'), 1, SIGNATURE)

    def test_difference_on_a_hypothesis_keeps_only_the_hypotheses(self):
        claim = prepare_claim(SYNTHETIC, candidate(probe_kind='difference', edit_from='Odd (orderOf g)', edit_to='Even (orderOf g)',
                                                   location='Odd (orderOf g)'), 1, SIGNATURE)
        self.assertEqual(claim['proposition'],
                         '∃ (G : Type) (_inst1 : Group G) (g h : G), ¬ (((closure {g, h} = ⊤ ∧ ¬closure {g} = ⊤) ∧ (Odd (orderOf g))) ↔ '
                         '((closure {g, h} = ⊤ ∧ ¬closure {g} = ⊤) ∧ (Even (orderOf g))))')
        self.assertEqual(claim['edit']['part'], 'hypotheses')
        self.assertEqual(claim['bridges'][0]['type'], 'schema')
        self.assertIn('not that the source is wrong', claim['bridges'][0]['obligation'])

    def test_difference_on_the_conclusion_drops_the_hypotheses(self):
        claim = prepare_claim(SYNTHETIC, candidate(probe_kind='difference', edit_from='P x g', edit_to='P g x', location='P x g'), 1, SIGNATURE)
        self.assertTrue(claim['proposition'].endswith('¬ ((∀ x : G, P x g) ↔ (∀ x : G, P g x))'))
        self.assertEqual(claim['edit']['part'], 'conclusion')
        self.assertEqual(claim['edit']['kind'], 'reordering')

    def test_difference_rejects_witnesses_and_edits_outside_formulas(self):
        for fields in ({'witnesses': '(G : Type)'}, {'edit_from': '(G : Type*)', 'edit_to': '(G : Type)'}, {'edit_from': 'Q', 'edit_to': 'R'}):
            with self.assertRaises(ValueError):
                prepare_claim(SYNTHETIC, candidate(probe_kind='difference', location='godd', **fields), 1, SIGNATURE)

    def test_quantifying_over_a_theorem_binder_is_a_binder_move(self):
        item = {'binders': '(n : ℕ)\n  (x : Fin n → ℝ)', 'conclusion': '∃ N, P N ∧ Q x'}
        self.assertTrue(binder_move(item, 'Q x', '∀ x : Fin n → ℝ, Q x'))
        self.assertTrue(binder_move(item, 'Q x', '∀ (x : Fin n → ℝ), Q x'))
        self.assertFalse(binder_move(item, 'Q x', '∀ x : ℝ, Q x'))
        self.assertFalse(binder_move(item, 'Q x', '∀ x : Fin n → ℝ, Q x ∧ R'))
        separation = {'probe_kind': 'separation', 'edit_from': 'Q x', 'edit_to': '∀ x : Fin n → ℝ, Q x'}
        self.assertEqual(declared_edit_kind(item, separation), 'binder_move')

    def test_consistency_prefers_a_binder_move_over_a_rewrite(self):
        item = {'binders': '(x : ℝ)', 'conclusion': '∃ N, P N ∧ Q x'}
        move = {'type': 'scope', 'location': 'Q x', 'probe_kind': 'separation', 'edit_from': 'Q x', 'edit_to': '∀ x : ℝ, Q x'}
        rewrite = {'type': 'scope', 'location': 'P N', 'probe_kind': 'separation', 'edit_from': 'P N', 'edit_to': 'R N'}
        found, _ = consistency_summary(item, [[rewrite], [move], []], ['completed'] * 3)
        self.assertEqual(found, [move])


if __name__ == '__main__':
    unittest.main()
