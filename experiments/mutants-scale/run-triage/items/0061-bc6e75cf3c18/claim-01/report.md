# syn-6d01e4c56887-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The conclusion with the supplied constant differs from the conclusion using 3 * Real.sqrt 3 / 2.

## Source

Item fingerprint: `47c923d9442b17ead3250a8d313279c5b08b018d26fba5821f48d51ddc9150de`
Source: syn-6d01e4c56887.lean

## Formal claim

```lean
∃ (curve : Set (ℝ × ℝ)) (equilateral : Set (ℝ × ℝ) → Prop), ¬ (((∃! S : Set (ℝ × ℝ), S ⊆ curve ∧ equilateral S) ∧
  (∃ S : Set (ℝ × ℝ), S ⊆ curve ∧ equilateral S ∧ (MeasureTheory.volume (convexHull ℝ S)).toReal = putnam_2006_b1_solution)) ↔ ((∃! S : Set (ℝ × ℝ), S ⊆ curve ∧ equilateral S) ∧
  (∃ S : Set (ℝ × ℝ), S ⊆ curve ∧ equilateral S ∧ (MeasureTheory.volume (convexHull ℝ S)).toReal = (3 * Real.sqrt 3 / 2))))
```

## Bridge obligations

- schema: Verify the curve factorization, uniqueness of the triangle, and that Lean's volume of its convex hull has the stated area. A difference probe alone does not establish the intended numerical answer. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
