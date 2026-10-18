# syn-3e9238add05f-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

There are f, a, and b for which the interval-local differentiability conditions hold but hdiff does not.

## Source

Item fingerprint: `e317ced369888bb1810deaa0a4a1615093c304ca23067e5ae7e3eec49f114d49`
Source: syn-3e9238add05f.lean

## Formal claim

```lean
∃ (f : ℝ → ℝ) (a b : ℝ), ((∀ x ∈ Set.Icc a b, DifferentiableAt ℝ f x ∧ DifferentiableAt ℝ (deriv f) x) ∧ (∀ x ∈ Set.Icc a b, |f x| ≤ 1) ∧ (∀ x ∈ Set.Ico a b, |(iteratedDeriv 2 f) x| ≤ 1) ∧ (b - a ≥ 2)) ∧ ¬ ((Differentiable ℝ f ∧ (Differentiable ℝ (deriv f))) ∧ (∀ x ∈ Set.Icc a b, |f x| ≤ 1) ∧ (∀ x ∈ Set.Ico a b, |(iteratedDeriv 2 f) x| ≤ 1) ∧ (b - a ≥ 2))
```

## Bridge obligations

- instance: Check whether the informal problem intends differentiability only on the interval, and whether ambient derivatives at its endpoints are the appropriate translation. The proposed test establishes a difference in hypotheses, not a counterexample to the conclusion. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
