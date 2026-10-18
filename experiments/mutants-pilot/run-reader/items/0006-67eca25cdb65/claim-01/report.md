# syn-40e8cf55497c-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

There is an X equal to the stated closed square that satisfies the edited hypothesis but not hX.

## Source

Item fingerprint: `0a2548d07dfd1672e87083e4dfd7e61bd8f8945fa6c6e0fe1441aae461ab4a7b`
Source: syn-40e8cf55497c.lean

## Formal claim

```lean
open RingHom Set Nat in
∃ (X : Set (ℝ × ℝ)) (room : (ℝ × ℝ) → ℝ), ((X = Set.prod (Icc 0 1) (Icc 0 1)) ∧ (room = fun (a,b) ↦ min (min a (1 - a)) (min b (1 - b)))) ∧ ¬ ((X = Set.prod (Ico 0 1) (Icc 0 1)) ∧ (room = fun (a,b) ↦ min (min a (1 - a)) (min b (1 - b))))
```

## Bridge obligations

- instance: This tests a mismatch in the permitted sets X, not a difference in the final answer. Check whether continuity makes the excluded edge immaterial to the proposition. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
