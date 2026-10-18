# syn-73de1e58769b-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the stated IsLeast proposition is provable using this square as a feasible set of volume less than 5.

## Source

Item fingerprint: `7d57d9131454b8037926ea7b5c66bc88e97e8ceedb505fbf1c03b5a2b6b1a79e`
Source: syn-73de1e58769b.lean

## Formal claim

```lean
Not (open MeasureTheory in
IsLeast
    {y | ∃ S : Set (Fin 2 → ℝ),
      Convex ℝ S ∧
      (∃ p ∈ S, p 0 > 0 ∧ p 1 > 0 ∧ p 0 * p 1 = 1) ∧
      (∃ p ∈ S, p 0 < 0 ∧ p 1 < 0 ∧ p 0 * p 1 = 1) ∧
      (∃ p ∈ S, p 0 < 0 ∧ p 1 > 0 ∧ p 0 * p 1 = -1) ∧
      (∃ p ∈ S, p 0 > 0 ∧ p 1 < 0 ∧ p 0 * p 1 = -1) ∧
    volume S = y} putnam_2007_a2_solution)
```

## Bridge obligations

- instance: Verify the square’s volume and the four branch witnesses in the formal Fin 2 → ℝ representation. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
