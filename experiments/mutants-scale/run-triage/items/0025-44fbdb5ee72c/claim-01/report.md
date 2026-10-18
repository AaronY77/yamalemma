# syn-26dec54e3296-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the full proposition is provable by choosing an unconstrained `areadef3`.

## Source

Item fingerprint: `1ca007949a8ba8e4caefabb13fb838336dcacd925944ac10da57be6d20b4238f`
Source: syn-26dec54e3296.lean

## Formal claim

```lean
Not (open Function Set MeasureTheory in
∀ (m : ℕ)
(area2 : EuclideanSpace ℝ (Fin 2) → EuclideanSpace ℝ (Fin 2) → EuclideanSpace ℝ (Fin 2) → ℝ)
(area3 : EuclideanSpace ℝ (Fin 3) → EuclideanSpace ℝ (Fin 3) → EuclideanSpace ℝ (Fin 3) → ℝ)
(areadef2 : (Fin m → Fin m → Fin m → ℝ) → Prop)
(areadef3 : (Fin m → Fin m → Fin m → ℝ) → Prop)
(mge3 : m ≥ 3)
(harea2 : ∀ a b c, area2 a b c = (volume (convexHull ℝ {a, b, c})).toReal)
(harea3 : ∀ a b c, area3 a b c = (μH[2] (convexHull ℝ {a, b, c})).toReal)
(hareadef2 : ∀ a, areadef2 a ↔ ∀ A : Fin m → EuclideanSpace ℝ (Fin 2), (∑ i : Fin m, ∑ j : Fin m, ∑ k : Fin m, if (i < j ∧ j < k) then (a i j k * area2 (A i) (A j) (A k)) else 0) ≥ 0), ∀ a, areadef2 a → areadef3 a)
```

## Bridge obligations

- intrinsic: Check that the area functions and planar-definition hypothesis can be instantiated as described, and that the intended ℝ³ definition would exclude the constantly false predicate. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `79927e2fa356bb98a25a70ee0781b29fdae16ef1bc53cceb35293f517c113031`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
