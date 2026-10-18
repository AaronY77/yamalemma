# syn-ab6711b5535c-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

There is a function satisfying the original odd-indexed hypothesis but not the edited hypothesis with the even-indexed rule.

## Source

Item fingerprint: `48c2fa161ad4bc9e07ac9d8c1e45a54b5d157d99e6d47d81ba63c7590543f9c6`
Source: syn-ab6711b5535c.lean

## Formal claim

```lean
open Function Set in
∃ (c : ℕ → ℤ), ¬ (((c 1 = 1) ∧ (∀ n : ℕ, n > 0 → c (2 * n + 1) = (-1) ^ n * c n)) ↔ ((c 1 = 1) ∧ ((∀ n : ℕ, n > 0 → c (2 * n + 1) = (-1) ^ n * c n) ∧ (∀ n : ℕ, n > 0 → c (2 * n) = c n))))
```

## Bridge obligations

- schema: Establish that omitting the even-indexed recurrence can change the value of the sum, not merely the class of admissible functions. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: probe.lean:1:453: error: No goals to be solved

  Evidence ID: `2825eade4559f06895ebba911fbee167f821f12b729769788ca20b02d746e2af`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`
- confirm: validated
  Evidence ID: `9e2138d3307e5f8d76bce4b0d7eb82644dca965e7b72fa6b2daf787a12f7d40b`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
