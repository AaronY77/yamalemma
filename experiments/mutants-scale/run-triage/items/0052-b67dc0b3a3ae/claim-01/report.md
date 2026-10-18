# syn-8ae48c240bf4-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

There is an instance satisfying the edited hypotheses but not the original hypotheses, with q = 1 and Nq = 0.

## Source

Item fingerprint: `3b569349246434b5e52c539158fe4726146b1934b1e5d78e978079f7efb318c8`
Source: syn-8ae48c240bf4.lean

## Formal claim

```lean
∃ (q : ℕ) (Nq : ℕ), ((True) ∧ (Odd q) ∧ (q > 0) ∧ (Nq = {a : ℕ | 0 < a ∧ a < (q : ℝ) / 4 ∧ Nat.gcd a q = 1}.encard)) ∧ ¬ ((0 < Nq) ∧ (Odd q) ∧ (q > 0) ∧ (Nq = {a : ℕ | 0 < a ∧ a < (q : ℝ) / 4 ∧ Nat.gcd a q = 1}.encard))
```

## Bridge obligations

- instance: Verify that q = 1 satisfies the stated count definition and that the informal problem includes this case; the separation establishes an excluded input, not that the equivalence is false there. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence

- confirm: probe.lean:1:111: warning: `Set.mem_setOf_eq` has been deprecated: Use `Set.mem_ofPred_eq` instead

probe.lean:1:0: error: unsolved goals
h : {a | ((0 < a) ∧ ((↑a < (1 / 4)) ∧ ((a.gcd 1) = 1)))} = ∅
⊢ 0 = {a | ((0 < a) ∧ (↑a < 4⁻¹))}.encard

  Evidence ID: `2abf7c28564af25bb486e9d52b7e7e864c3adf961ac13e45dee5c9d05f011d86`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: probe.lean:1:111: warning: `Set.mem_setOf_eq` has been deprecated: Use `Set.mem_ofPred_eq` instead

probe.lean:1:0: error: unsolved goals
h : {a | ((0 < a) ∧ ((↑a < (1 / 4)) ∧ ((a.gcd 1) = 1)))} = ∅
⊢ 0 = {a | ((0 < a) ∧ (↑a < 4⁻¹))}.encard

  Evidence ID: `91421565ce24e0490266742b551cda5e4e124efa01d670978a313e6712c2db7b`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
