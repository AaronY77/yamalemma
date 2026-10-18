# syn-1c16ef8b95b0-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing > with ≥ permits equality cases that the formal conclusion excludes.

## Source

Item fingerprint: `fc0761ac403313041dcba2eaf5ca6a6cdc69937cb4527aeb6d0bcb3b7f1094ce`
Source: syn-1c16ef8b95b0.lean

## Formal claim

```lean
open Filter Topology Real in
∃ (SM : (n : ℕ) → Set (Matrix (Fin 3) (Fin n) ℤ)) (Srowsums : (n : ℕ) → Matrix (Fin 3) (Fin n) ℤ → Set ℤ) (sumsprog : (Set ℤ) → Prop), ¬ ((∃ n ≥ 1995, {M : (SM n) | sumsprog (Srowsums n M)}.encard > 4 * {M : (SM n) | (Srowsums n M).encard = 1}.encard) ↔ (∃ n ≥ 1995, {M : (SM n) | sumsprog (Srowsums n M)}.encard ≥ 4 * {M : (SM n) | (Srowsums n M).encard = 1}.encard))
```

## Bridge obligations

- schema: Check whether the intended formalization must match the non-strict bound; the stronger strict bound may still hold for the specified matrices. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `57875ebdb42f54636e66d2483d86ec26518a647bc214c69147729c368d18da2e`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- refute: probe.lean:1:44: error: Tactic `apply` failed: could not unify the type of `h`
  ∃ SM Srowsums sumsprog,
    ¬((∃ n ≥ 1995, ({M | (sumsprog (Srowsums n ↑M))}.encard > (4 * {M | ((Srowsums n ↑M).encard = 1)}.encard))) ↔
        (∃ n ≥ 1995, ({M | (sumsprog (Srowsums n ↑M))}.encard ≥ (4 * {M | ((Srowsums n ↑M).encard = 1)}.encard))))
with the goal
  False

h :
  ∃ SM Srowsums sumsprog,
    ¬((∃ n ≥ 1995, ({M | (sumsprog (Srowsums n ↑M))}.encard > (4 * {M | ((Srowsums n ↑M).encard = 1)}.encard))) ↔
        (∃ n ≥ 1995, ({M | (sumsprog (Srowsums n ↑M))}.encard ≥ (4 * {M | ((Srowsums n ↑M).encard = 1)}.encard))))
⊢ False

  Evidence ID: `2c6ac3f801c72caedb2183d8084dc75c18c935533f8cc2e81cc91bddd2f90542`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
