# S03-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

There is an instance satisfying the edited hypotheses but not the source hypotheses.

## Source

Item fingerprint: `9a6983a5f72efd399e8d38c73f2891f35257bb73adeeb48410fd8135988ebaf8`
Source: putnam_2016_a5.lean

## Formal claim

```lean
open Polynomial Filter Topology Real Set Nat List in
∃ (G : Type) (_inst1 : Group G) (Gfin : Fintype G) (g h : G) (S : Set G), ((Subgroup.closure {g, h} = ⊤) ∧ (Odd (orderOf g)) ∧ (S = {g * h, g⁻¹ * h, g * h⁻¹, g⁻¹ * h⁻¹})) ∧ ¬ ((Subgroup.closure {g, h} = ⊤ ∧ ¬Subgroup.closure {g} = ⊤ ∧ ¬Subgroup.closure {h} = ⊤) ∧ (Odd (orderOf g)) ∧ (S = {g * h, g⁻¹ * h, g * h⁻¹, g⁻¹ * h⁻¹}))
```

## Bridge obligations

- instance: Exhibit a finite group and elements with g of odd order that jointly generate G while at least one generates G alone; this tests the hypothesis discrepancy, not whether the conclusion fails. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Lean.Parser.Tactic.simpArgs
  Evidence ID: `1e9b41cc3a6089d4e4baf0c832352c373aeae2f35bf50d4166bbadc35c0304b6`
  Axioms: unavailable
  Environment: `667e7bb8b6bcbf355eae6e4b85d0e5e36eec97cd3c2fe44d4ff7f9589d37f708`
- confirm: validated
  Evidence ID: `fba98141250021a06901e2d86d92e8c5e44158092ca2a9f6395eb894f3b87f6e`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `667e7bb8b6bcbf355eae6e4b85d0e5e36eec97cd3c2fe44d4ff7f9589d37f708`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
