# syn-6d1859450143-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

There is a sequence with a zero term for which the source summability hypothesis holds but the edited hypothesis does not.

## Source

Item fingerprint: `9578bb1c6fe7bfe1ecffb4985a927dea1106a825fc374abfbe3cd5861c951c4f`
Source: syn-6d1859450143.lean

## Formal claim

```lean
open Set Function Filter Topology in
∃ (a b : ℕ → ℕ), ¬ (((Summable fun n ↦ (1 : ℝ) / a n) ∧ (∀ n, b n = {k | a k ≤ n}.ncard)) ↔ (((Summable fun n ↦ (1 : ℝ) / a n) ∧ (∀ n : ℕ, 0 < a (n + 1))) ∧ (∀ n, b n = {k | a k ≤ n}.ncard)))
```

## Bridge obligations

- schema: Check that positivity from index 1 is the intended indexing convention. This probe tests a domain difference, not whether the original conclusion is false. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `0f7e10d4105c0cc785195ce3d3baa830a468f282376c6e21f2cc826b03e64c72`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
