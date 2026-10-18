# syn-90e69125e704-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing < with ≤ changes H_def for a set containing boundary points and makes the hypercube closed.

## Source

Item fingerprint: `396dc9d6dad9ccecf468a8de84a1311e1c7fe286d59ffb3d98e37a7cabd18267`
Source: syn-90e69125e704.lean

## Formal claim

```lean
open Metric Filter Topology Set Nat in
∃ (H : Set (EuclideanSpace ℝ (Fin 4))) (contains : ℝ → Prop), ¬ (((H = {P : EuclideanSpace ℝ (Fin 4) | ∀ i : Fin 4, |P i| < 1 / 2}) ∧ (∀ r, contains r ↔
      ∃ᵉ (A : AffineSubspace ℝ (EuclideanSpace ℝ (Fin 4))) (C ∈ A),
        Module.finrank ℝ A.direction = 2 ∧
        sphere C r ∩ A ⊆ H)) ↔ ((H = {P : EuclideanSpace ℝ (Fin 4) | ∀ i : Fin 4, |P i| ≤ 1 / 2}) ∧ (∀ r, contains r ↔
      ∃ᵉ (A : AffineSubspace ℝ (EuclideanSpace ℝ (Fin 4))) (C ∈ A),
        Module.finrank ℝ A.direction = 2 ∧
        sphere C r ∩ A ⊆ H)))
```

## Bridge obligations

- schema: Check that the informal use of “hypercube” intends the closed cube, and establish separately that the stated radius is attained there but not in the open cube. A difference between the definitions alone does not establish that the original proposition is false. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `a3b3c26cbc1eac5236dbc102be3a39aadfbcc469f1060e0c09092bc64fb6cbcc`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
