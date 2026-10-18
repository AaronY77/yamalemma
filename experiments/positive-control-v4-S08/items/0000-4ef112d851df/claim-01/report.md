# S08-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

A proof of the proposition could assume this convergence rather than establish it.

## Source

Item fingerprint: `3c4f992625fa5d2234b66442a8cee29223315b02d6ca4d64df744053554d0752`
Source: putnam_1982_b5.lean

## Formal claim

```lean
open Set Function Filter Topology Polynomial Real in
∀ (T : Set ℝ)
(hT : T = Ioi (Real.exp (Real.exp 1)))
(S : ℝ → ℕ → ℝ)
(hS : ∀ x ∈ T, S x 0 = (Real.exp 1) ∧ ∀ n : ℕ, S x (n + 1) = Real.logb (S x n) x)
(g : ℝ → ℝ), ∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
(∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T
```

## Bridge obligations

- parse: Confirm the implication's scope in Lean and whether the intended theorem requires convergence as a conclusion. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: forbidden
  Evidence ID: `806c26ced3d89b825e6a214239d610c0483724c1cc8558990613f73e85191592`
  Axioms: ['propext', 'sorryAx', 'Classical.choice', 'Quot.sound']
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: unsupported proof syntax: Lean.Parser.Term.completion
  Evidence ID: `ee1d411e3d5fe1669509086e34beb9170f65f7183e0c1050014050a505cb5dde`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
