# syn-50f0e0b13de5-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source proposition is false because no single k / n can satisfy the inequalities for both m = 1 and m = 1992; the reordered quantifiers express the intended condition.

## Source

Item fingerprint: `a6aed16afbe2972f17674f8644043c8ac666ad637d26946b00245ff636e3e752`
Source: syn-50f0e0b13de5.lean

## Formal claim

```lean
¬ ((IsLeast
    {n : ℕ | 0 < n ∧
      ∃ k : ℤ, ∀ m ∈ Set.Ioo (0 : ℤ) (1993), (m / 1993 < (k : ℝ) / n) ∧ ((k : ℝ) / n < (m + 1) / 1994) }
    putnam_1993_b1_solution) ↔ (IsLeast
    {n : ℕ | 0 < n ∧
      ∀ m ∈ Set.Ioo (0 : ℤ) (1993), ∃ k : ℤ, (m / 1993 < (k : ℝ) / n) ∧ ((k : ℝ) / n < (m + 1) / 1994) }
    putnam_1993_b1_solution))
```

## Bridge obligations

- schema: Test that the original and edited IsLeast propositions differ, and review that the edited quantifier order matches the informal problem. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
