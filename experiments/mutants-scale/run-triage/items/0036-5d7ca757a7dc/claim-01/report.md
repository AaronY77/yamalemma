# syn-e282f0bb3421-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the formal proposition is provable by constructing a qualifying set that excludes 3 and using leastness to show that 3 ∉ S.

## Source

Item fingerprint: `5f104a9c78875d93f2a8b375bce03f277292caf9c3896b733f243faa0d0ad6f9`
Source: syn-e282f0bb3421.lean

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

- intrinsic: Construct and verify a qualifying set excluding 3, then check that `IsLeast` places S inside it. Confirm that the supplied answer set indeed omits 3. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
