# S08-1

Evidence verdict: **EVIDENCE-CHECKED**
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

- confirm: probe.lean:1:31: error(lean.unknownIdentifier): Unknown identifier `Tendsto`

probe.lean:1:134: error(lean.unknownIdentifier): Unknown identifier `atTop`

probe.lean:1:251: error(lean.unknownIdentifier): Unknown identifier `atTop`

probe.lean:1:427: error: Tactic `rcases` failed: `x✝ : ?m.139` is not an inductive datatype

  Evidence ID: `61f4e719b2a4204f06d125a5d0c2f598aedcb5c94f22145914410d3ad9e9d79e`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: probe.lean:1:203: error(lean.unknownIdentifier): Unknown constant `Set.isOpen_Iio.mem_nhds`

  Evidence ID: `f5f1b348a9b734c8856ffa113615325dd4fb7f0297210e701c4c1228bcbe6deb`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: validated
  Evidence ID: `8561ba056a7757e0b5c2ab71d73dca67b7cb5e7ef7d719915338e7911f902432`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
