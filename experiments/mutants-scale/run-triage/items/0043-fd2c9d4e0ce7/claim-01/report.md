# syn-ccfdae00f7a0-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing `Finset.Iio n` with `Finset.Iic n` changes the existence proposition from false to true if a sequence satisfying the intended condition exists.

## Source

Item fingerprint: `39fb59d83b089dcd6eaee6b5129c8780175f45020639677504b3f18c95b414e7`
Source: syn-ccfdae00f7a0.lean

## Formal claim

```lean
open Filter Polynomial Topology Nat in
¬ (((∃ a : ℕ → ℝ, (∀ i, a i ≠ 0) ∧
      (∀ n ≥ 1, (∑ i ∈ Finset.Iio n, a i • X ^ i : Polynomial ℝ).roots.toFinset.card = n)) ↔
    putnam_1990_b5_solution) ↔ ((∃ a : ℕ → ℝ, (∀ i, a i ≠ 0) ∧
      (∀ n ≥ 1, (∑ i ∈ Finset.Iic n, a i • X ^ i : Polynomial ℝ).roots.toFinset.card = n)) ↔
    putnam_1990_b5_solution))
```

## Bridge obligations

- schema: Verify that the inclusive sum matches the intended polynomial and establish whether a sequence satisfying all the intended root conditions exists. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
