# syn-ab6711b5535c-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation should be provable: start with a function satisfying the informal recurrences and change only c(2014). The odd recurrence can still be satisfied by updating its later descendants. The summand at n=2012 changes because c(2012) is nonzero, while no other summand in the stated range changes. Thus both resulting sums cannot equal the fixed answer.

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

- intrinsic: Construct the functions and verify the odd recurrence and finite-sum difference in Lean; this is a suspected omission, not a confirmed counterexample. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
