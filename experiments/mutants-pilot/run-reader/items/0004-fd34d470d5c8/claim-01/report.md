# syn-50f4fb0719b4-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

A separation should be possible with k = 1 and a triangle PQR whose area is twice that of ABC: the source equality then holds, while the edited equality does not.

## Source

Item fingerprint: `0fefeadbfcd0f88ff4ed62046c7e72ebaabb9e8dd4d4f7513dc475f81ce3ef1a`
Source: syn-50f4fb0719b4.lean

## Formal claim

```lean
open MeasureTheory in
∃ (A B C P Q R : EuclideanSpace ℝ (Fin 2)) (k : ℝ), ((volume (convexHull ℝ {P, Q, R})).toReal / (volume (convexHull ℝ {A, B, C})).toReal = (k - 1)^2 / k^2 + k + 1) ∧ ¬ ((volume (convexHull ℝ {P, Q, R})).toReal / (volume (convexHull ℝ {A, B, C})).toReal = (k - 1)^2 / (k^2 + k + 1))
```

## Bridge obligations

- schema: This separation drops the segment and intersection hypotheses, so it establishes a difference in logical form, not by itself a counterexample to the full proposition. Verify the intended denominator against the informal problem and, separately, check the full hypotheses if testing the original proposition. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped; the edit only regroups the source text, and a reviewer must confirm the regrouped statement expresses the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
