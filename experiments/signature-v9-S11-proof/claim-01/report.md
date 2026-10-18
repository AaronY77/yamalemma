# S11-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

With the declaration hypotheses dropped, a separation test should find an admissibility predicate for which the source conclusion holds at a particular x but no fixed N, c, and a work for every x.

## Source

Item fingerprint: `2c1b637189f2f1cc788905c43e58144426cfc0e4d4ba93fd83eac108c17d2770`
Source: putnam_2004_a4.lean

## Formal claim

```lean
open Nat Topology Filter in
∃ (n : ℕ) (x : Fin n → ℝ) (avals : ℕ → (ℕ → Fin n → ℝ) → Prop), (∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin n → ℝ),
    avals N a ∧
    (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n) ∧ ¬ (∃ (N : ℕ) (c : Fin N → ℚ) (a : ℕ → Fin n → ℝ),
    avals N a ∧
    ∀ x : Fin n → ℝ, (∏ i : Fin n, x i) = ∑ i : Fin N, c i * (∑ j : Fin n, a i j * x j) ^ n)
```

## Bridge obligations

- schema: The separation drops npos and havals and establishes only a difference in logical form. Review whether “expressed identically” requires uniform coefficients; this probe does not show a failure for the benchmark’s admissibility predicate. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped; the edit quantifies part of the conclusion over a theorem binder, which the outer witness of the same name no longer constrains there, and a reviewer must confirm the moved scope expresses the original problem. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `a80eed04ce26e71318a41ecf2c622f23c1776db731015500edcb2687d6f44a20`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `667e7bb8b6bcbf355eae6e4b85d0e5e36eec97cd3c2fe44d4ff7f9589d37f708`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
