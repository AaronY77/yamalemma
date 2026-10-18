# syn-d9d182ea5aef-2

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Extending the stated bounds to n = 1 makes them impossible: the lower bound is positive and the upper bound is exp(-1/4) < 1, so neither possible natural-number value of f 1 can satisfy both.

## Source

Item fingerprint: `f85de908f6bbd5082ae2c95217294eb954eb40cc5f675452dd0057c65defdd00`
Source: syn-d9d182ea5aef.lean

## Formal claim

```lean
open Set Nat Function in
∃ (f : ℕ → ℕ), ((∀ n : ℕ, ∃ C : ℝ, n ≥ 2 → n ^ (n ^ 2 / 2 - C * n) * Real.exp (-(n ^ 2) / 4) ≤ f n ∧ f n ≤ n ^ (n ^ 2 / 2 + C * n) * Real.exp (-(n ^ 2) / 4))) ∧ ¬ ((∀ n : ℕ, ∃ C : ℝ, n ≥ 1 → n ^ (n ^ 2 / 2 - C * n) * Real.exp (-(n ^ 2) / 4) ≤ f n ∧ f n ≤ n ^ (n ^ 2 / 2 + C * n) * Real.exp (-(n ^ 2) / 4)))
```

## Bridge obligations

- schema: Separation drops hf. The informal statement appears to need a restriction to n ≥ 2 or another adjustment at n = 1; this probe does not show the formal theorem is false. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped and the edit adds or removes content; the separation may come from the rewrite rather than the suspected error, so a reviewer must check the edited statement closely. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
