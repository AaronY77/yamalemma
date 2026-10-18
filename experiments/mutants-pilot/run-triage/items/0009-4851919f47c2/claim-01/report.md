# syn-ab6711b5535c-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the stated theorem is provable: choose admissible sequences with c 2012 = 1 that differ only at the free even-indexed value c 2014. The summand at n = 2012 changes, so both sums cannot equal the fixed answer.

## Source

Item fingerprint: `48c2fa161ad4bc9e07ac9d8c1e45a54b5d157d99e6d47d81ba63c7590543f9c6`
Source: syn-ab6711b5535c.lean

## Formal claim

```lean
Not (open Function Set in
∀ (c : ℕ → ℤ)
(hc1 : c 1 = 1)
(hcodd : ∀ n : ℕ, n > 0 → c (2 * n + 1) = (-1) ^ n * c n), (∑ n : Set.Icc 1 2013, c n * c (n.1 + 2)) = putnam_2013_b1_solution)
```

## Bridge obligations

- intrinsic: Construct the two sequences in Lean, verify hc1 and hcodd, and show their sums differ. This tests the missing rule; it does not by itself establish the intended sum. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
