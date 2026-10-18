# syn-cc5f46db1a58-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source and edited hypotheses differ for some S, including the negative rationals.

## Source

Item fingerprint: `dc8a4a4f8cc8494b5599351502848cdcb889292c367c4d0827af1888ba0602b2`
Source: syn-cc5f46db1a58.lean

## Formal claim

```lean
∃ (S : Set ℚ), ¬ (((∀ a ∈ S, ∀ b ∈ S, a + b ∈ S) ∧ (∀ r : ℚ, (r ∈ S ∨ -r ∈ S ∨ r = 0) ∧ ¬(r ∈ S ∧ -r ∈ S) ∧ ¬(r ∈ S ∧ r = 0) ∧ ¬(-r ∈ S ∧ r = 0))) ↔ ((∀ a ∈ S, ∀ b ∈ S, a + b ∈ S ∧ a * b ∈ S) ∧ (∀ r : ℚ, (r ∈ S ∨ -r ∈ S ∨ r = 0) ∧ ¬(r ∈ S ∧ -r ∈ S) ∧ ¬(r ∈ S ∧ r = 0) ∧ ¬(-r ∈ S ∧ r = 0))))
```

## Bridge obligations

- schema: Verify that the added conjunct expresses the informal multiplication requirement and that the negative-rational instance satisfies the remaining formal hypothesis. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: probe.lean:1:923: error: unsolved goals
S : Set ℚ := {r | (r < 0)}
h :
  ((∀ a ∈ S, (∀ b ∈ S, ((a + b) ∈ S))) ∧
      (∀ (r : ℚ),
        (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧
          (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0))))))) ↔
    ((∀ a ∈ S, (∀ b ∈ S, (((a + b) ∈ S) ∧ ((a * b) ∈ S)))) ∧
      (∀ (r : ℚ),
        (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧
          (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0)))))))
hadd : ∀ a ∈ S, (∀ b ∈ S, ((a + b) ∈ S))
hsign :
  ∀ (r : ℚ),
    (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧ (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0)))))
⊢ (-1) ∈ S

probe.lean:1:942: error: unsolved goals
S : Set ℚ := {r | (r < 0)}
h :
  ((∀ a ∈ S, (∀ b ∈ S, ((a + b) ∈ S))) ∧
      (∀ (r : ℚ),
        (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧
          (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0))))))) ↔
    ((∀ a ∈ S, (∀ b ∈ S, (((a + b) ∈ S) ∧ ((a * b) ∈ S)))) ∧
      (∀ (r : ℚ),
        (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧
          (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0)))))))
hadd : ∀ a ∈ S, (∀ b ∈ S, ((a + b) ∈ S))
hsign :
  ∀ (r : ℚ),
    (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧ (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0)))))
⊢ (-1) ∈ S

probe.lean:1:0: error: unsolved goals
S : Set ℚ := {r | (r < 0)}
h :
  ((∀ a ∈ S, (∀ b ∈ S, ((a + b) ∈ S))) ∧
      (∀ (r : ℚ),
        (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧
          (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0))))))) ↔
    ((∀ a ∈ S, (∀ b ∈ S, (((a + b) ∈ S) ∧ ((a * b) ∈ S)))) ∧
      (∀ (r : ℚ),
        (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧
          (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0)))))))
hadd : ∀ a ∈ S, (∀ b ∈ S, ((a + b) ∈ S))
hsign :
  ∀ (r : ℚ),
    (((r ∈ S) ∨ (((-r) ∈ S) ∨ (r = 0))) ∧ (¬((r ∈ S) ∧ ((-r) ∈ S)) ∧ (¬((r ∈ S) ∧ (r = 0)) ∧ ¬(((-r) ∈ S) ∧ (r = 0)))))
hm : ((-2) ∈ S) ∧ (1 ∈ S)
⊢ False

  Evidence ID: `bf9668f3edf57c770b1f7cf4dd30fda1cc30a7d357da93661b300dfe244daad3`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: validated
  Evidence ID: `2109f998cdfe390a06472940819738bddc6c1f23a77cd90cfe74b40d052ad5bc`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
