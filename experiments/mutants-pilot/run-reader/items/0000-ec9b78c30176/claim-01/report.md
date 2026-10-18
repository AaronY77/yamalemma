# syn-e35966fad0ef-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the original proposition is provable if no conspiratorial subset of 1 through 15 has 11 elements.

## Source

Item fingerprint: `75225dc43ffa20e3274ae26c1d4aea2d17248b9ee39943c2b6b23855739ab5eb`
Source: syn-e35966fad0ef.lean

## Formal claim

```lean
Not (open Set in
∀ (conspiratorial : Set ℤ → Prop)
    (hconspiratorial : ∀ S, conspiratorial S ↔ ∀ a ∈ S, ∀ b ∈ S, ∀ c ∈ S, (a > 0 ∧ b > 0 ∧ c > 0) ∧ ((a ≠ b ∧ b ≠ c ∧ a ≠ c) → (Int.gcd a b > 1 ∨ Int.gcd b c > 1 ∨ Int.gcd a c > 1))), IsGreatest {k | ∃ S, S ⊆ Ico 1 16 ∧ conspiratorial S ∧ S.encard = k} putnam_1974_a1_solution)
```

## Bridge obligations

- intrinsic: Verify the maximum for 1 through 15 and confirm that the intended range includes 16. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
