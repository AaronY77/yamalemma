# S05-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Test equivalence with the proposition using the informal interval. Equivalence would show that this domain shift does not change the theorem.

## Source

Item fingerprint: `716c49b25b680f88cd2893cf9aa548e198ccca95f577f65832b0c38777ae4b94`
Source: putnam_1983_a3.lean

## Formal claim

```lean
(∀ (p : ℕ)
(F : ℕ → ℕ)
(poddprime : Odd p ∧ p.Prime)
(hF : ∀ n : ℕ, F n = ∑ i ∈ Finset.range (p - 1), (i + 1) * n ^ i), ∀ a ∈ Finset.Icc 1 p, ∀ b ∈ Finset.Icc 1 p, a ≠ b → ¬(F a ≡ F b [MOD p])) ↔ (∀ (p : ℕ) (F : ℕ → ℕ), (Odd p ∧ p.Prime) → (∀ n : ℕ, F n = ∑ i ∈ Finset.range (p - 1), (i + 1) * n ^ i) → ∀ a ∈ Finset.Icc 0 (p - 1), ∀ b ∈ Finset.Icc 0 (p - 1), a ≠ b → ¬(F a ≡ F b [MOD p]))
```

## Bridge obligations

- translated: Review whether the informal integer domain is faithfully represented by natural numbers from 0 through p−1. Even if that translation is accepted, determine whether polynomial periodicity makes the two quantified statements equivalent before treating the changed representatives as a defect. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
