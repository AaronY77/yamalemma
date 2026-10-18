# S08-lint-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

With the declaration hypotheses dropped, some witnesses satisfy the exact source conclusion but not the regrouped conclusion.

## Source

Item fingerprint: `3c4f992625fa5d2234b66442a8cee29223315b02d6ca4d64df744053554d0752`
Source: putnam_1982_b5.lean

## Formal claim

```lean
open Set Function Filter Topology Polynomial Real in
∃ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ), (∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
(∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T) ∧ ¬ ((∀ x ∈ T, ∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧ ((∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T))
```

## Bridge obligations

- schema: This claim comes from a deterministic parse lint, not from reading the informal problem. A reviewer must check against the informal problem that the regrouped conclusion is the intended reading. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped; the edit only regroups the source text, and a reviewer must confirm the regrouped statement expresses the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
