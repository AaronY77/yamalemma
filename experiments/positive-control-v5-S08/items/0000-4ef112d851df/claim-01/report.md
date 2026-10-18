# S08-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Arbitrary S and g should permit the source conclusion to hold when its convergence antecedent fails, while the intended conjunction fails.

## Source

Item fingerprint: `3c4f992625fa5d2234b66442a8cee29223315b02d6ca4d64df744053554d0752`
Source: putnam_1982_b5.lean

## Formal claim

```lean
open Set Function Filter Topology Polynomial Real in
∃ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ), (∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
(∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T) ∧ ¬ ((∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) ∧ ContinuousOn g T)
```

## Bridge obligations

- schema: Check that the conjunction accurately translates the informal demand for convergence to g and continuity; then assess the discrepancy under hT and hS, which this separation probe omits. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped and the intended statement was proposed by a model; both need review. (discharged: False)

## Evidence

- confirm: probe.lean:1:18: error(lean.unknownIdentifier): Unknown identifier `Tendsto`

probe.lean:1:105: error: Tactic `rcases` failed: `x✝ : ?m.63` is not an inductive datatype

  Evidence ID: `e9678f39b5e5ccc0eb32ed7294d5e22d8facb2ca2f424bef91f477f667e9c6c6`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: validated
  Evidence ID: `bd8eee7b4a59b5a266212222a6a173a6155d72ce39afd24bef507a3268eff4ed`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
