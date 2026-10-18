# S11-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The original proposition may be provable without producing uniform witnesses. An equivalence proof would show that this quantifier difference does not change the mathematical result, but would not remove the translation question.

## Source

Item fingerprint: `2c1b637189f2f1cc788905c43e58144426cfc0e4d4ba93fd83eac108c17d2770`
Source: putnam_2004_a4.lean

## Formal claim

```lean
(open Nat Topology Filter in
∀ (n : ℕ) (npos : n > 0)
  (x : Fin n → ℝ)
  (avals : ℕ → (ℕ → Fin n → ℝ) → Prop)
  (havals : ∀ N a, avals N a ↔ ∀ (i : Fin N) (j : Fin n), (a i j = -1 ∨ a i j = 0 ∨ a i j = 1)), ∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin n → ℝ),
    avals N a ∧
    (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n) ↔ (∀ (n : ℕ), n > 0 → ∀ (avals : ℕ → (ℕ → Fin n → ℝ) → Prop), (∀ (N : ℕ) (a : ℕ → Fin n → ℝ), avals N a ↔ ∀ (i : Fin N) (j : Fin n), (a i j = -1 ∨ a i j = 0 ∨ a i j = 1)) → ∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin n → ℝ), avals N a ∧ ∀ (x : Fin n → ℝ), (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n)
```

## Bridge obligations

- translated: Review whether “expressed identically” requires N, c, and a to be independent of x; mathematical equivalence alone would not settle that translation choice. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
