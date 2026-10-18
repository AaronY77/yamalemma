import unittest

from yamalemma.axiom_policy import (
    AxiomPolicyResult,
    assess_axioms,
)


class AxiomPolicyTests(unittest.TestCase):
    def test_missing_report_is_unreadable(self):
        result = assess_axioms(None)
        expected = AxiomPolicyResult(
            status="unreadable",
            forbidden_axioms=(),
        )
        self.assertEqual(result, expected)

    def test_empty_report_is_allowed(self):
        result = assess_axioms(())
        expected = AxiomPolicyResult(
            status="allowed",
            forbidden_axioms=(),
        )
        self.assertEqual(result, expected)

    def test_standard_axioms_are_allowed(self):
        result = assess_axioms(
            ("propext", "Classical.choice", "Quot.sound")
        )
        expected = AxiomPolicyResult(
            status="allowed",
            forbidden_axioms=(),
        )
        self.assertEqual(result, expected)

    def test_sorry_is_forbidden(self):
        result = assess_axioms(("propext", "sorryAx"))
        expected = AxiomPolicyResult(
            status="forbidden",
            forbidden_axioms=("sorryAx",),
        )
        self.assertEqual(result, expected)

    def test_unknown_axiom_is_forbidden(self):
        result = assess_axioms(("MyProject.assumption",))
        expected = AxiomPolicyResult(
            status="forbidden",
            forbidden_axioms=("MyProject.assumption",),
        )
        self.assertEqual(result, expected)

    def test_forbidden_names_are_unique_and_sorted(self):
        result = assess_axioms(
            ("sorryAx", "MyProject.assumption", "sorryAx")
        )
        expected = AxiomPolicyResult(
            status="forbidden",
            forbidden_axioms=("MyProject.assumption", "sorryAx"),
        )
        self.assertEqual(result, expected)