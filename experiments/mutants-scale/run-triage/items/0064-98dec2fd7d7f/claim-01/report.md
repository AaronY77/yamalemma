# syn-ea8356135ed1-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source and edited conclusions disagree for k = 1, n 0 = 1, and zpoly z = 1 + z.

## Source

Item fingerprint: `bef1be5ddce9d514764dcd2f3a0c7330ca5cfb873eb29bf18441bd8c2cf9b2d7`
Source: syn-ea8356135ed1.lean

## Formal claim

```lean
open EuclideanGeometry Filter Topology Set MeasureTheory Metric in
∃ (k : ℕ) (n : Fin k → ℤ) (zpoly : ℂ → ℂ), ¬ ((∀ z : ℂ, z ∈ ball 0 (Real.sqrt 5 - 1/2) → zpoly z ≠ 0) ↔ (∀ z : ℂ, z ∈ ball 0 ((Real.sqrt 5 - 1)/2) → zpoly z ≠ 0))
```

## Bridge obligations

- schema: Confirm that the informal, typographically incomplete circle expression intends radius (√5 − 1)/2. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `e2ecb778928c8141204582da498ecb286f5fc061ee11342a30516fe655b3002b`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
