# S08-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

With the declaration hypotheses dropped, a nonempty T and an S that does not converge to g can satisfy the source conclusion but not the edited conclusion.

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

- schema: This separation tests logical form only: it drops hT and hS. Review whether convergence for the recursively defined sequence on the prescribed T is proved elsewhere, and whether the intended conclusion should instead assert the existence of a continuous limit function. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped and the edit adds or removes content; the separation may come from the rewrite rather than the suspected error, so a reviewer must check the edited statement closely. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `479c314c4916d31b3201d93920310b6e9fad0f821d098e0219fbb96df5183399`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `667e7bb8b6bcbf355eae6e4b85d0e5e36eec97cd3c2fe44d4ff7f9589d37f708`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
