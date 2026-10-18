import unittest

from yamalemma.axiom_policy import assess_axioms
from yamalemma.axiom_report import find_axiom_report, parse_axiom_report


class AxiomReportTests(unittest.TestCase):
    def test_empty_dependencies(self):
        self.assertEqual(parse_axiom_report("'T' does not depend on any axioms", 'T'), ())

    def test_dependencies(self):
        self.assertEqual(parse_axiom_report("'T' depends on axioms: [propext, Custom.assumption]", 'T'),
                         ('propext', 'Custom.assumption'))

    def test_exact_target(self):
        output = "'Target_extra' does not depend on any axioms\n'Target' depends on axioms: [sorryAx]"
        self.assertEqual(parse_axiom_report(output, 'Target'), ('sorryAx',))

    def test_bad_reports_are_unreadable(self):
        for output in ('', 'warning', "'Other' depends on axioms: [propext]",
                       "'T' depends on axioms: [propext", "'T' depends on axioms: [propext,]",
                       "'T' depends on axioms: [bad name]", "'T' depends on axioms: [propext] junk",
                       "'T' does not depend on any axioms\n'T' depends on axioms: [sorryAx]",
                       "'T' depends on axioms: [propext,\nClassical.choice]"):
            with self.subTest(output=output):
                self.assertIsNone(parse_axiom_report(output, 'T'))
                self.assertEqual(assess_axioms(parse_axiom_report(output, 'T')).status, 'unreadable')


if __name__ == '__main__':
    unittest.main()
