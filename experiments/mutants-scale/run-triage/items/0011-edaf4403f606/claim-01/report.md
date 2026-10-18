# syn-0e86094e63da-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing the index set with `Set.Ici 1` changes the proposition: the edited sum includes the nonzero n = 1 term.

## Source

Item fingerprint: `0d0451694e273cfa996171f00c9704d5bff231185d456b9ebcf768cacee7bf9a`
Source: syn-0e86094e63da.lean

## Formal claim

```lean
open Topology Filter Polynomial Set in
¬ ((∑' n : Set.Ioi 1, ((2 : ℝ) ^ (round (Real.sqrt n)) + (2 : ℝ) ^ (-round (Real.sqrt n))) / 2 ^ (n : ℝ) = putnam_2001_b3_solution) ↔ (∑' n : Set.Ici 1, ((2 : ℝ) ^ (round (Real.sqrt n)) + (2 : ℝ) ^ (-round (Real.sqrt n))) / 2 ^ (n : ℝ) = putnam_2001_b3_solution))
```

## Bridge obligations

- schema: Verify that the informal lower limit is inclusive and that `round (Real.sqrt n)` implements the intended nearest-integer convention. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
