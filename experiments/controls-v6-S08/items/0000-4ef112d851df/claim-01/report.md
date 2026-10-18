# S08-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

A separation witness should satisfy the source conclusion but not the edited conclusion.

## Source

Item fingerprint: `3c4f992625fa5d2234b66442a8cee29223315b02d6ca4d64df744053554d0752`
Source: putnam_1982_b5.lean

## Formal claim

```lean
open Set Function Filter Topology Polynomial Real in
∃ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ), (∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
(∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T) ∧ ¬ ((∀ x ∈ T, ∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
((∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T))
```

## Bridge obligations

- schema: Separation drops hT and hS, so this tests only the logical form. It remains to check that unconditional convergence is the intended obligation for the recursively defined sequence. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped; the edit only regroups the source text, and a reviewer must confirm the regrouped statement expresses the original problem. (discharged: False)

## Evidence

- confirm: probe.lean:1:33: error(lean.unknownIdentifier): Unknown identifier `Tendsto`

probe.lean:1:144: error(lean.unknownIdentifier): Unknown identifier `atTop`

probe.lean:1:259: error(lean.unknownIdentifier): Unknown identifier `atTop`

probe.lean:1:326: error(lean.unknownIdentifier): Unknown identifier `Tendsto`

probe.lean:1:420: error: Tactic `rcases` failed: `x✝ : ?m.124` is not an inductive datatype

  Evidence ID: `6e4a0cb6a960cad27f44b0436c5a68b1c8eba88c3a4c072a39bfb7cffda040a7`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: probe.lean:1:213: error(lean.unknownIdentifier): Unknown constant `Filter.eventually_lt_nhds`

  Evidence ID: `7cab79973a698d0ffe0e280c4895074e91467d7b0581ec5938c49563275fe7d9`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
