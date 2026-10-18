# syn-76d8765ffb26-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the proposition is provable by constructing a least qualifying set and using 12 to contradict the claimed equality.

## Source

Item fingerprint: `797747201b55747c345d243eb2fb92bb13cff3dae0fea497e06f2e5899c5e090`
Source: syn-76d8765ffb26.lean

## Formal claim

```lean
Not (∀ (IsQualifying : Set ℤ → Prop)
    (IsQualifying_def : ∀ S, IsQualifying S ↔
      (∀ n ∈ S, 0 < n) ∧
      2 ∈ S ∧
      (∀ n > 0, n ^ 2 ∈ S → n ∈ S) ∧
      (∀ n ∈ S, (n + 5) ^ 2 ∈ S))
    (S : Set ℤ)
    (hS : IsLeast IsQualifying S), Sᶜ ∩ {n | 0 < n} = putnam_2017_a1_solution)
```

## Bridge obligations

- intrinsic: Verify in Lean that a least qualifying set exists and that the declared solution contains 12; then check the intended answer rather than inferring its full form from this counterexample. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
