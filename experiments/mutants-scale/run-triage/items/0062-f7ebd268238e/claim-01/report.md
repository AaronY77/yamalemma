# syn-050e70d822dc-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The edited interval-local hypothesis admits some functions excluded by the original global hypothesis.

## Source

Item fingerprint: `f207f3aa5c96cb6f6b82beb9686504c39c9575dcc35fbdc6c55f6e54592afd60`
Source: syn-050e70d822dc.lean

## Formal claim

```lean
∃ (f : ℝ → ℝ) (a b : ℝ), ((∀ x ∈ Set.Icc a b, DifferentiableAt ℝ f x ∧ DifferentiableAt ℝ (deriv f) x) ∧ (∀ x ∈ Set.Icc a b, |f x| ≤ 1) ∧ (∀ x ∈ Set.Icc a b, |(iteratedDeriv 2 f) x| ≤ 1) ∧ (b - a ≥ 2)) ∧ ¬ ((Differentiable ℝ f ∧ (Differentiable ℝ (deriv f))) ∧ (∀ x ∈ Set.Icc a b, |f x| ≤ 1) ∧ (∀ x ∈ Set.Icc a b, |(iteratedDeriv 2 f) x| ≤ 1) ∧ (b - a ≥ 2))
```

## Bridge obligations

- instance: Check whether the informal problem implicitly intends global twice differentiability; the separation test alone does not settle that interpretation. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
