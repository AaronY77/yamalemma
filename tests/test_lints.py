import unittest

from yamalemma.lints import lint_conclusion


def node(kind, text, *children, identifier=None):
    return {'kind': kind, 'text': text, 'identifier': identifier, 'children': list(children)}


def ident(name):
    return node('ident', name, identifier=name)


def paren(term):
    return node('Lean.Parser.Term.paren', f'({term["text"]})',
                node('Lean.Parser.Term.hygienicLParen', '(', node('«(»', '(')), term, node('«)»', ')'))


def forall_in(name, domain, body):
    return node('Lean.«term∀__,_»', f'∀ {name} ∈ {domain}, {body["text"]}',
                node('«∀»', '∀'), node('Lean.binderIdent', name, ident(name)),
                node('Lean.«binderPred∈_»', f'∈ {domain}', node('«∈»', '∈'), ident(domain)), node('«,»', ','), body)


def binary(kind, symbol, left, right):
    return node(kind, f'{left["text"]} {symbol} {right["text"]}', left, node(f'«{symbol}»', symbol), right)


def app(text):
    return node('Lean.Parser.Term.app', text)


def s08():
    exists = node('«term∃_,_»', '∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)', node('«∃»', '∃'),
                  node('Lean.explicitBinders', 'L : ℝ', node('Lean.binderIdent', 'L', ident('L'))), node('«,»', ','),
                  app('Tendsto (S x) atTop (𝓝 L)'))
    inner = forall_in('x', 'T', app('Tendsto (S x) atTop (𝓝 (g x))'))
    conjunction = binary('«term_∧_»', '∧', paren(exists), paren(inner))
    implication = binary('Lean.Parser.Term.arrow', '→', conjunction, app('ContinuousOn g T'))
    return forall_in('x', 'T', implication)


class LintTests(unittest.TestCase):
    def test_s08_precedence_is_flagged_with_the_regrouping_fix(self):
        tree = s08()
        findings = lint_conclusion(tree, tree['text'])
        self.assertEqual(len(findings), 1)
        finding = findings[0]
        self.assertEqual(finding['strength'], 'strong')
        self.assertEqual(finding['shadowed_binders'][0]['names'], ['x'])
        self.assertEqual(finding['suggested_edit']['kind'], 'regrouping')
        self.assertEqual(finding['suggested_edit']['edit_to'],
                         '(∀ x ∈ T, ∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧ '
                         '((∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T)')

    def test_plain_quantified_implication_is_not_flagged(self):
        tree = forall_in('x', 'T', binary('Lean.Parser.Term.arrow', '→', app('0 < x'), app('0 < x ^ 2')))
        self.assertEqual(lint_conclusion(tree, tree['text']), [])

    def test_unparenthesized_conjunction_is_not_flagged(self):
        tree = forall_in('x', 'T', binary('Lean.Parser.Term.arrow', '→',
                                          binary('«term_∧_»', '∧', app('0 < x'), app('x < 1')), app('x ^ 2 < 1')))
        self.assertEqual(lint_conclusion(tree, tree['text']), [])

    def test_shadowing_alone_is_weak(self):
        tree = forall_in('x', 'T', forall_in('x', 'U', app('P x')))
        findings = lint_conclusion(tree, tree['text'])
        self.assertEqual(findings[0]['strength'], 'weak')
        self.assertIsNone(findings[0]['captured_conjunction'])

    def test_names_inside_hypothesis_types_are_not_binders(self):
        hypothesis_type = paren(node('Lean.Parser.Term.forall', '∀ x, 0 < f x', node('«∀»', '∀'),
                                     node('Lean.binderIdent', 'x', ident('x')), node('«,»', ','), app('0 < f x')))
        hypothesis = node('Lean.Parser.Term.explicitBinder', f'(hf : {hypothesis_type["text"]})', node('«(»', '('),
                          node('null', 'hf', node('Lean.binderIdent', 'hf', ident('hf'))),
                          node('null', f': {hypothesis_type["text"]}', node('«:»', ':'), hypothesis_type), node('«)»', ')'))
        inner = node('Lean.«term∀__,_»', '∀ x > N, P x', node('«∀»', '∀'), node('Lean.binderIdent', 'x', ident('x')),
                     node('Lean.«binderPred>_»', '> N'), node('«,»', ','), app('P x'))
        tree = node('Lean.Parser.Term.forall', f'∀ f {hypothesis["text"]}, {inner["text"]}', node('«∀»', '∀'),
                    node('null', f'f {hypothesis["text"]}', node('Lean.binderIdent', 'f', ident('f')), hypothesis),
                    node('«,»', ','), inner)
        self.assertEqual(lint_conclusion(tree, tree['text']), [])


if __name__ == '__main__':
    unittest.main()
