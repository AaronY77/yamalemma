# syn-2a8117305278-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Adding f 0 = 1 changes the hypothesis for some functions.

## Source

Item fingerprint: `863858d6aad1561b55e7c501e930a69ee92e7c29287e72f3c56a1f458ba87c30`
Source: syn-2a8117305278.lean

## Formal claim

```lean
open Topology MvPolynomial Filter Set in
∃ (f g h : ℝ → ℝ) (a b : ℝ), ¬ (((0 ∈ Ioo a b) ∧ (DifferentiableOn ℝ f (Ioo a b) ∧ DifferentiableOn ℝ g (Ioo a b) ∧ DifferentiableOn ℝ h (Ioo a b)) ∧ ((∀ x ∈ Ioo a b, deriv g x = (f x) * (g x)^2 * (h x) + 4 / ((f x) * (h x))) ∧ g 0 = 1) ∧ ((∀ x ∈ Ioo a b, deriv h x = 3 * (f x) * (g x) * (h x)^2 + 1 / ((f x) * (g x))) ∧ h 0 = 1)) ↔ ((0 ∈ Ioo a b) ∧ (DifferentiableOn ℝ f (Ioo a b) ∧ DifferentiableOn ℝ g (Ioo a b) ∧ DifferentiableOn ℝ h (Ioo a b)) ∧ ((∀ x ∈ Ioo a b, deriv g x = (f x) * (g x)^2 * (h x) + 4 / ((f x) * (h x))) ∧ g 0 = 1 ∧ f 0 = 1) ∧ ((∀ x ∈ Ioo a b, deriv h x = 3 * (f x) * (g x) * (h x)^2 + 1 / ((f x) * (g x))) ∧ h 0 = 1)))
```

## Bridge obligations

- schema: Check the counterexample against the exact Lean operations and verify the proposed formula's value at zero. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
