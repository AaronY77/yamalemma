# S11-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Review the quantifier order against the proposed uniform formulation. Equivalence may still be provable because a uniform identity might exist; that result alone would not resolve the translation question.

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
    (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n) ↔ (open Nat Topology Filter in
∀ (n : ℕ) (npos : n > 0)
  (avals : ℕ → (ℕ → Fin n → ℝ) → Prop)
  (havals : ∀ N a, avals N a ↔ ∀ (i : Fin N) (j : Fin n), (a i j = -1 ∨ a i j = 0 ∨ a i j = 1)),
  ∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin n → ℝ),
    avals N a ∧
    ∀ (x : Fin n → ℝ),
      (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n)
```

## Bridge obligations

- translated: Confirm that “identically” requires N, c, and a to be independent of x. Do not treat a proof of equivalence, or of the uniform theorem, as evidence that the original quantifier order matches the wording. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: <input>:1:37: expected end of input
  Evidence ID: `49b164ac56453d1a8fbd81fe308ecf900363808b6de7f01726abeaf2d0198afb`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- confirm: <input>:1:36: expected end of input
  Evidence ID: `783b6c157d3cd4552dad80dfde6cd60b9ef3fd9e4708d0dda18e6ad8eea8d430`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: <input>:1:9: expected end of input
  Evidence ID: `f19a89a5ddb15e168288000f235ba0db7b49843757d7fe38f03483a9f7ec8227`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`
- refute: <input>:1:15: expected end of input
  Evidence ID: `2f9b57326b94e96d07d89ad69377d7291fbdc91d624edb20b1ad89d95a6932d5`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
