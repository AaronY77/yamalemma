# syn-f4f2356e8d2c-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The original fadd formula and the edited formula should disagree for these functions: the f equation holds, while the g equation fails, for example at x = y = 1.

## Source

Item fingerprint: `0da57b0939dd4a051ecece421e05c9ceedbaa01821a729ee316fcf1324c4a8e1`
Source: syn-f4f2356e8d2c.lean

## Formal claim

```lean
open Filter Topology in
∃ (f g : ℝ → ℝ), ¬ (((¬∃ c, f = Function.const ℝ c ∨ g = Function.const ℝ c) ∧ (Differentiable ℝ f ∧ Differentiable ℝ g) ∧ (∀ x y, f (x + y) = f x * f y - g x * g y)) ↔ ((¬∃ c, f = Function.const ℝ c ∨ g = Function.const ℝ c) ∧ (Differentiable ℝ f ∧ Differentiable ℝ g) ∧ ((∀ x y, f (x + y) = f x * f y - g x * g y) ∧ (∀ x y, g (x + y) = f x * g y + g x * f y))))
```

## Bridge obligations

- schema: Verify the proposed functions and the failed conclusion in Lean, and confirm that the added equation is the intended translation of the informal assumption. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Mathlib.Meta.FunProp.funPropTacStx
  Evidence ID: `a12cb43a3811ad25c5f0f766ea49e8e9c40d9976b92c9a3f81f3e9b8bf9cc6b8`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: validated
  Evidence ID: `a78d2089ce194fb4046a968ae2e39b6ce0ca6362383006d46dc22bc05d572a5a`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
