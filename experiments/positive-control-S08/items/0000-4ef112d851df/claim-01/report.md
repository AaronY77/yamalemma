# S08-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

A proof of the stated proposition could use the assumed convergence to g to establish continuity without proving convergence from hS. Such a proof alone would not establish the informal problem's convergence claim.

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

- parse: Confirm that the informal request requires convergence as an unconditional conclusion, with g defined by those limits, rather than only continuity conditional on convergence. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Lean.Parser.Term.completion
  Evidence ID: `8b177084d77a5aad68b16ea0ede1a2c7086bbe6c7a9f372094a742814a2e6436`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: unsupported proof syntax: Lean.Parser.Term.completion
  Evidence ID: `a58d195fdc55c830d2bd40b8e6f2da201a84c395cdb6c3fb3356e87edd012dee`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: <input>:1:71: expected end of input
  Evidence ID: `ba6173165f8f8342d5dfffc6c2070f76a5cf8b1949188b7b6e62e7dca74e4bfb`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: forbidden
  Evidence ID: `05b0e60385ba5b85d105100e55030746741b02cf8efb6eb2bf2b00efefbd0372`
  Axioms: ['propext', 'sorryAx', 'Classical.choice', 'Quot.sound']
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
