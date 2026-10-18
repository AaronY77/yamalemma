import unittest

from yamalemma.lints import lint_candidate, lint_claim, lint_conclusion, witness_binders


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


def binder(kind, names, type_node):
    opening, closing = {'explicitBinder': ('(', ')'), 'implicitBinder': ('{', '}')}[kind]
    label = ' '.join(names)
    return node(f'Lean.Parser.Term.{kind}', f'{opening}{label} : {type_node["text"]}{closing}', node(f'«{opening}»', opening),
                node('null', label, *[ident(name) for name in names]),
                node('null', f': {type_node["text"]}', node('«:»', ': '), type_node), node('null', ''), node(f'«{closing}»', closing))


def s08_binders():
    groups = [binder('explicitBinder', ['T'], node('Lean.Parser.Term.app', 'Set ℝ', ident('Set'))),
              binder('explicitBinder', ['hT'], node('«term_=_»', 'T = Ioi c', ident('T'), ident('Ioi'), ident('c'))),
              binder('explicitBinder', ['S'], node('Lean.Parser.Term.arrow', 'ℝ → ℕ → ℝ')),
              binder('explicitBinder', ['hS'], node('Lean.Parser.Term.app', 'P S T', ident('P'), ident('S'), ident('T'))),
              binder('explicitBinder', ['g'], node('Lean.Parser.Term.arrow', 'ℝ → ℝ'))]
    return node('null', ' '.join(group['text'] for group in groups), *groups)


def uses(*names):
    return node('Lean.Parser.Term.app', ' '.join(names), *[ident(name) for name in names])


def synthetic_item(tree):
    conclusion = tree['text']
    return {'id': 'SYNTHETIC-S08', 'fingerprint': 'synthetic', 'conclusion': conclusion,
            'signature_source': f'(T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ) : {conclusion}',
            'expected_type': f'∀ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ), {conclusion}',
            'context': {'opens': ['open Filter Topology']}}


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

    def test_witnesses_keep_binders_the_conclusion_uses(self):
        witnesses = witness_binders(s08_binders(), uses('T', 'S', 'x', 'L', 'g'))
        self.assertEqual(witnesses['binders'], '(T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ)')
        self.assertEqual(witnesses['names'], ['T', 'S', 'g'])
        self.assertEqual(witnesses['dropped'], ['(hT : T = Ioi c)', '(hS : P S T)'])

    def test_witnesses_keep_binders_needed_by_kept_types(self):
        groups = [binder('implicitBinder', ['n'], node('termℕ', 'ℕ')),
                  binder('explicitBinder', ['hn'], node('«term_<_»', '0 < n', ident('n'))),
                  binder('explicitBinder', ['f'], node('Lean.Parser.Term.arrow', 'Fin n → ℝ', ident('Fin'), ident('n')))]
        witnesses = witness_binders(node('null', '', *groups), uses('f'))
        self.assertEqual(witnesses['binders'], '(n : ℕ) (f : Fin n → ℝ)')
        self.assertEqual(witnesses['dropped'], ['(hn : 0 < n)'])

    def test_strong_finding_becomes_a_regrouping_separation_claim(self):
        tree = s08()
        finding = lint_conclusion(tree, tree['text'])[0]
        finding['witnesses'] = witness_binders(s08_binders(), uses('T', 'S', 'g'))
        claim = lint_claim(synthetic_item(tree), finding, 1)
        self.assertEqual(claim['claim_source'], 'lint')
        self.assertEqual(claim['type'], 'precedence')
        self.assertEqual(claim['edit']['kind'], 'regrouping')
        self.assertEqual(claim['bridges'][0]['type'], 'schema')
        self.assertTrue(claim['proposition'].startswith('open Filter Topology in\n∃ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ), ('))
        self.assertIn('theorem binders the conclusion uses', claim['transformations'][0])

    def test_weak_or_unwitnessed_findings_do_not_become_claims(self):
        tree = forall_in('x', 'T', forall_in('x', 'U', app('P x')))
        self.assertEqual(lint_candidate(lint_conclusion(tree, tree['text'])[0])[1], 'only strong findings become claims')
        finding = lint_conclusion(s08(), s08()['text'])[0]
        finding['witnesses'] = {'binders': '', 'names': [], 'dropped': []}
        with self.assertRaises(ValueError):
            lint_claim(synthetic_item(s08()), finding, 1)


if __name__ == '__main__':
    unittest.main()
