# S08-2

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

A proof could use the assumed convergence to identify g with the sequence limits, without constructing g or proving that it is a limit function.

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

- parse: Check the parsed scope of this antecedent and whether the informal wording intends g to be constructed rather than assumed to have the limit property. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Lean.Parser.Term.completion
  Evidence ID: `632fbb3ea331d6a1c84a319fa2ad331c089e1f48ada2aa47506f56178881f67b`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: unsupported proof syntax: Lean.Parser.Term.completion
  Evidence ID: `b3152a7558b8b38d2ce9d1eac3cba03f7e655b9f74e855567c5e5f39c5038e2e`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: <input>:1:24: expected end of input
  Evidence ID: `b673aae34b26c25506f9010c5fa7072e99d11b9d3fb3290096cd82a87c144fd1`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: <input>:1:60: expected end of input
  Evidence ID: `7408170b7e157e930c80466ac05813cafc9dd6e39fd0414d8d212a23e7425d44`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
