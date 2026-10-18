# syn-dafe0fd397bd-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Changing the threshold to n ≥ 1 makes the bound fail at n = 1 for the specified f.

## Source

Item fingerprint: `d3bd198c70e608177cf1664d70c763fc74cb0762b34fcc1529811714b8f71afb`
Source: syn-dafe0fd397bd.lean

## Formal claim

```lean
open Set Nat Function in
∃ (f : ℕ → ℕ), ¬ (((∃ C : ℝ, ∀ n : ℕ, n ≥ 2 → n ^ (n ^ 2 / 2 - C * n) * Real.exp (-(n ^ 2) / 4) ≤ f n ∧ f n ≤ n ^ (n ^ 2 / 2 + C * n) * Real.exp (-(n ^ 2) / 4))) ↔ ((∃ C : ℝ, ∀ n : ℕ, n ≥ 1 → n ^ (n ^ 2 / 2 - C * n) * Real.exp (-(n ^ 2) / 4) ≤ f n ∧ f n ≤ n ^ (n ^ 2 / 2 + C * n) * Real.exp (-(n ^ 2) / 4))))
```

## Bridge obligations

- schema: Verify the n = 1 cardinality and determine whether the original n ≥ 2 conclusion holds for the specified f; the n = 1 failure alone does not establish a difference between the full quantified conclusions. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
