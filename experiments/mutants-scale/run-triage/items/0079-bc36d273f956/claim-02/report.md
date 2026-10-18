# syn-2a8117305278-2

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Adding the f derivative equation changes the hypothesis for some differentiable functions.

## Source

Item fingerprint: `863858d6aad1561b55e7c501e930a69ee92e7c29287e72f3c56a1f458ba87c30`
Source: syn-2a8117305278.lean

## Formal claim

```lean
open Topology MvPolynomial Filter Set in
∃ (f g h : ℝ → ℝ) (a b : ℝ), ¬ (((0 ∈ Ioo a b) ∧ (DifferentiableOn ℝ f (Ioo a b) ∧ DifferentiableOn ℝ g (Ioo a b) ∧ DifferentiableOn ℝ h (Ioo a b)) ∧ ((∀ x ∈ Ioo a b, deriv g x = (f x) * (g x)^2 * (h x) + 4 / ((f x) * (h x))) ∧ g 0 = 1) ∧ ((∀ x ∈ Ioo a b, deriv h x = 3 * (f x) * (g x) * (h x)^2 + 1 / ((f x) * (g x))) ∧ h 0 = 1)) ↔ ((0 ∈ Ioo a b) ∧ (DifferentiableOn ℝ f (Ioo a b) ∧ DifferentiableOn ℝ g (Ioo a b) ∧ DifferentiableOn ℝ h (Ioo a b)) ∧ ((∀ x ∈ Ioo a b, deriv g x = (f x) * (g x)^2 * (h x) + 4 / ((f x) * (h x))) ∧ g 0 = 1 ∧ (∀ x ∈ Ioo a b, deriv f x = 2 * (f x)^2 * (g x) * (h x) + 1 / ((g x) * (h x)))) ∧ ((∀ x ∈ Ioo a b, deriv h x = 3 * (f x) * (g x) * (h x)^2 + 1 / ((f x) * (g x))) ∧ h 0 = 1)))
```

## Bridge obligations

- schema: Verify that this formal derivative equation matches the informal one. A local hypothesis difference alone does not establish a counterexample to the full conclusion. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: probe.lean:1:41: error: unsolved goals
⊢ ∃ x, (((-1) < x) ∧ (x < 1))

  Evidence ID: `e7b31b34ea03c208de9d1ea989f162c6a0d17d6067b7af58428c27e04c219a63`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: validated
  Evidence ID: `5f5ded6b267da9232ead36ceb7db61d34960ce7a6d28aa2ecb85ecc8a87c45fd`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
