# S08-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

For a nonempty T, a constant-zero S, and a constant-one g, the source conclusion holds because convergence to g is false; replacing the implication with a conjunction makes it false.

## Source

Item fingerprint: `3c4f992625fa5d2234b66442a8cee29223315b02d6ca4d64df744053554d0752`
Source: putnam_1982_b5.lean

## Formal claim

```lean
open Set Function Filter Topology Polynomial Real in
∃ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ), (∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
(∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T) ∧ ¬ (∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
(∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) ∧ ContinuousOn g T)
```

## Bridge obligations

- schema: This separation drops hT and hS and shows only a difference in logical form. Review whether the recursive sequence admits a limit function under those hypotheses, and whether the intended theorem should assert existence of such a g rather than quantify over an arbitrary one. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped and the edit adds or removes content; the separation may come from the rewrite rather than the suspected error, so a reviewer must check the edited statement closely. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
