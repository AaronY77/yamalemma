# syn-1793ef0c8de1-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source and edited hypotheses differ at k = n; the missing endpoint may also permit a counterexample to the full proposition.

## Source

Item fingerprint: `ba50c473c6e3f0a65ac8c7f07763ff3f0c7641ad5e4d6b918444732565cfb143`
Source: syn-1793ef0c8de1.lean

## Formal claim

```lean
∃ (m n : ℕ) (a : ℕ → ℤ) (G : Type) (_inst3 : Group G) (g h : G), ¬ (((m > 0 ∧ n > 0) ∧ (Nat.gcd m n = 1) ∧ (∀ k : Set.Ico 1 n, a k = Int.floor (m * k / (n : ℝ)) - Int.floor (m * ((k : ℤ) - 1) / (n : ℝ))) ∧ (((List.Ico 1 (n + 1)).map (fun k : ℕ => g * h ^ (a k))).prod = 1)) ↔ ((m > 0 ∧ n > 0) ∧ (Nat.gcd m n = 1) ∧ (∀ k : Set.Ico 1 (n + 1), a k = Int.floor (m * k / (n : ℝ)) - Int.floor (m * ((k : ℤ) - 1) / (n : ℝ))) ∧ (((List.Ico 1 (n + 1)).map (fun k : ℕ => g * h ^ (a k))).prod = 1)))
```

## Bridge obligations

- schema: Verify the interval endpoint and floor calculation in Lean, and instantiate a nonabelian group with an involution g that does not commute with h to establish the claimed effect on the full proposition. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `db4067645296cdc7622d3637b31ef5b4c6c0003419284a324c7198bb0fb2b1a6`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
