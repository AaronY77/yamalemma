# syn-d9d182ea5aef-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

With the counting-function hypothesis dropped, some functions satisfy the pointwise bounds but admit no uniform C.

## Source

Item fingerprint: `f85de908f6bbd5082ae2c95217294eb954eb40cc5f675452dd0057c65defdd00`
Source: syn-d9d182ea5aef.lean

## Formal claim

```lean
open Set Nat Function in
∃ (f : ℕ → ℕ), ((∀ n : ℕ, ∃ C : ℝ, n ≥ 2 → n ^ (n ^ 2 / 2 - C * n) * Real.exp (-(n ^ 2) / 4) ≤ f n ∧ f n ≤ n ^ (n ^ 2 / 2 + C * n) * Real.exp (-(n ^ 2) / 4))) ∧ ¬ ((∃ C : ℝ, ∀ n : ℕ, n ≥ 2 → n ^ (n ^ 2 / 2 - C * n) * Real.exp (-(n ^ 2) / 4) ≤ f n ∧ f n ≤ n ^ (n ^ 2 / 2 + C * n) * Real.exp (-(n ^ 2) / 4)))
```

## Bridge obligations

- schema: Separation drops hf and therefore shows only a logical-form difference; it does not establish that the counting function lacks a uniform bound. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped; the edit reorders source tokens without adding or removing any, and a reviewer must confirm the reordered statement expresses the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
