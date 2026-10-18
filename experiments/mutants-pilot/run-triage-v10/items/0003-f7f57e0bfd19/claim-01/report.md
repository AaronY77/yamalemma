# syn-1cb7b9ddc669-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The hypothesis and its corrected version differ at p = 5. Confirming the six-sequence count in Lean would establish that this difference affects the theorem.

## Source

Item fingerprint: `4b04ac8b73e28a902e2ed3bc93d56ed0c12fe4a64babcb4ee5ac843ce47d968c`
Source: syn-1cb7b9ddc669.lean

## Formal claim

```lean
open Polynomial in
∃ (p f : ℕ), ¬ (((Nat.Prime p ∧ p ≥ 5) ∧ (f = {a : ℕ → (ZMod p) | ∀ n : ℕ, a n ≠ 0 ∧ a n * a (n + 2) = 1 + a (n + 1)}.ncard)) ↔ ((Nat.Prime p ∧ p > 5) ∧ (f = {a : ℕ → (ZMod p) | ∀ n : ℕ, a n ≠ 0 ∧ a n * a (n + 2) = 1 + a (n + 1)}.ncard)))
```

## Bridge obligations

- schema: Verify in Lean that the set in hf has ncard 6 when p = 5, and that its sequences correspond to those in the informal problem. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `d89b0911922a028b47e0a5e3aef6677b63b088b43c1d5ba7538b535a88aeb3dc`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
