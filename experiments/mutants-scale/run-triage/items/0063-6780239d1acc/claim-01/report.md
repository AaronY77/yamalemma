# syn-b30af69a0072-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing the strict inequalities with non-strict ones should admit degenerate intervals excluded by the original hypothesis.

## Source

Item fingerprint: `f28d19c8a952d2ad0625003a44b21a06bba23846ae0fcb84d449261d0e0069c2`
Source: syn-b30af69a0072.lean

## Formal claim

```lean
open Matrix Function in
∃ (IsFiniteAP : Set ℤ → Prop) (q r : ℤ) (A B : Fin 2 → ℝ) (T : Set ℤ) (S : Set ℤ), ((∀ s,
      IsFiniteAP s ↔ ∃ n : ℕ, ∃ a d : ℤ, 0 < d ∧ s = {a + i * d | i : Fin n}) ∧ (q > 0) ∧ (A 0 ≤ A 1 ∧ B 0 ≤ B 1) ∧ (T = {x : ℤ | ∃ b m : ℤ, (b : ℝ) ∈ Set.Icc (B 0) (B 1) ∧ x = b + m * q}) ∧ (S = {a : ℤ | (a : ℝ) ∈ Set.Icc (A 0) (A 1) ∧ r * a ∈ T}) ∧ ((A 1 - A 0) * (B 1 - B 0) < q)) ∧ ¬ ((∀ s,
      IsFiniteAP s ↔ ∃ n : ℕ, ∃ a d : ℤ, 0 < d ∧ s = {a + i * d | i : Fin n}) ∧ (q > 0) ∧ (A 0 < A 1 ∧ B 0 < B 1) ∧ (T = {x : ℤ | ∃ b m : ℤ, (b : ℝ) ∈ Set.Icc (B 0) (B 1) ∧ x = b + m * q}) ∧ (S = {a : ℤ | (a : ℝ) ∈ Set.Icc (A 0) (A 1) ∧ r * a ∈ T}) ∧ ((A 1 - A 0) * (B 1 - B 0) < q))
```

## Bridge obligations

- instance: Check whether ‘intervals’ in the intended problem includes singleton intervals; if nondegenerate intervals were intended, this is not a discrepancy. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `86beb81e44333fdff05a1f5da4c646e03c13658112fddcf33a280ac7ebb82f41`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
