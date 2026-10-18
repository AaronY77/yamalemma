# syn-00d1fab97dba-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The original hypothesis holds for the zero-polynomial family, while the edited hypothesis does not.

## Source

Item fingerprint: `2a58cc051e1883bf04c5529e4cd50e9a55d0ab67c29a39a36323145f6f4d1f8e`
Source: syn-00d1fab97dba.lean

## Formal claim

```lean
open Set Filter Topology Real Polynomial Function in
∃ (f : ℕ -> Polynomial ℕ), ¬ (((∀ n ≥ 1, (f n).eval 0 = 0) ∧ (∀ n : ℕ, derivative (f (n + 1)) = (n + 1) * (Polynomial.comp (f n) (X + 1)))) ↔ ((f 0 = 1 ∧ ∀ n ≥ 1, (f n).eval 0 = 0) ∧ (∀ n : ℕ, derivative (f (n + 1)) = (n + 1) * (Polynomial.comp (f n) (X + 1)))))
```

## Bridge obligations

- schema: Verify that the zero-polynomial family satisfies the derivative hypothesis and that its factorization differs from putnam_1985_b2_solution; confirm that f 0 = 1 is the intended polynomial identity. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `526cd769abd86aa5a7a352bc4d13d0c72ec0b95aad26e52f2d7185bf966210d0`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
