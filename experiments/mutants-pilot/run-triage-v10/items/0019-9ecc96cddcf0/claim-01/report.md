# syn-7f0810fc7777-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing the hypothesis with positivity only for n > 0 admits f n = n while the original hypothesis does not.

## Source

Item fingerprint: `3411e80714985be59712c3be8d6ccc0adb26addd5fc6ca1c50f2b512abb2ba50`
Source: syn-7f0810fc7777.lean

## Formal claim

```lean
open Topology Filter in
∃ (f : ℕ → ℕ), ((∀ n > 0, f n > 0) ∧ (StrictMonoOn f (Set.Ici 1)) ∧ (f 2 = 2) ∧ (∀ m n, m > 0 → n > 0 → IsRelPrime m n → f (m * n) = f m * f n)) ∧ ¬ ((∀ n, f n > 0) ∧ (StrictMonoOn f (Set.Ici 1)) ∧ (f 2 = 2) ∧ (∀ m n, m > 0 → n > 0 → IsRelPrime m n → f (m * n) = f m * f n))
```

## Bridge obligations

- instance: Confirm that the informal sequence is indexed only by positive integers; this distinction does not by itself invalidate the conclusion for the functions retained by the formal hypotheses. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `7283f109e5f8a29b42a8d0dcaf63405e2f8ab719b323b883c5a917ce1530c026`
  Axioms: ['propext']
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
