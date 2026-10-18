# syn-404110731c82-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source and edited propositions disagree: the source fails at n = a = b = 0, while the corrected coordinates should satisfy the forward implication.

## Source

Item fingerprint: `98c078fdec18822c0f7e0c19bbaf34722c718a34f7e2fdb04f0fdc3898876ff1`
Source: syn-404110731c82.lean

## Formal claim

```lean
open Polynomial in
∃ (nab nxy : (ℤ × ℤ × ℤ) → Prop), ¬ (((∀ n a b : ℤ, nab (n, a, b) → nxy (n, putnam_1975_a1_solution.1 (a, b), putnam_1975_a1_solution.2 (a, b))) ∧
∀ n : ℤ, (∃ x y : ℤ, nxy (n, x, y)) → ∃ a b : ℤ, nab (n, a, b)) ↔ ((∀ n a b : ℤ, nab (n, a, b) → nxy (n, (a + b + 1), putnam_1975_a1_solution.2 (a, b))) ∧
∀ n : ℤ, (∃ x y : ℤ, nxy (n, x, y)) → ∃ a b : ℤ, nab (n, a, b)))
```

## Bridge obligations

- schema: Check that the edited full proposition holds, including its converse, and that a + b + 1 is the intended requested coordinate. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `b1957a0c9c45148e8a02bff7d79621a3114ea2b00148af82def53ea8ea6521da`
  Axioms: ['propext']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
