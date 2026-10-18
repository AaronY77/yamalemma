# syn-e39722b71bad-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the original proposition is provable using the specified polynomial and S = ∅.

## Source

Item fingerprint: `6d84703657bcd39536b43b6ab63146dbff19b59daf53bc9ac5fc762bda546010`
Source: syn-e39722b71bad.lean

## Formal claim

```lean
Not (∀ (y : ℝ → ℝ)
(hy : y = fun x ↦ 2 * x ^ 4 + 7 * x ^ 3 + 3 * x - 5)
(S : Finset ℝ), (Collinear ℝ {P : Fin 2 → ℝ | P 0 ∈ S ∧ P 1 = y (P 0)} → (∑ x ∈ S, x) / 4 = putnam_1977_a1_solution))
```

## Bridge obligations

- intrinsic: Confirm that S is intended to represent exactly four distinct points; this counterexample does not assess the theorem with that condition added. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
