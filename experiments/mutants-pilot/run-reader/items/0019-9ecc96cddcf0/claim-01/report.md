# syn-7f0810fc7777-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The hypothesis-separation test finds an admissible function excluded solely because f 0 = 0.

## Source

Item fingerprint: `3411e80714985be59712c3be8d6ccc0adb26addd5fc6ca1c50f2b512abb2ba50`
Source: syn-7f0810fc7777.lean

## Formal claim

```lean
open Topology Filter in
∃ (f : ℕ → ℕ), ((∀ n > 0, f n > 0) ∧ (StrictMonoOn f (Set.Ici 1)) ∧ (f 2 = 2) ∧ (∀ m n, m > 0 → n > 0 → IsRelPrime m n → f (m * n) = f m * f n)) ∧ ¬ ((∀ n, f n > 0) ∧ (StrictMonoOn f (Set.Ici 1)) ∧ (f 2 = 2) ∧ (∀ m n, m > 0 → n > 0 → IsRelPrime m n → f (m * n) = f m * f n))
```

## Bridge obligations

- instance: Confirm that the informal sequence begins at n = 1 rather than n = 0; otherwise positivity at zero may be intended. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
