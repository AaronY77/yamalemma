# syn-d903d831ef02-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

A function that is zero at a positive index satisfies the source formula but not the edited formula when those formulas are tested in isolation.

## Source

Item fingerprint: `918a10923a29558f4946872a409de844964690f6f372b30db282d0b1bc88a494`
Source: syn-d903d831ef02.lean

## Formal claim

```lean
open Topology Filter in
∃ (f : ℕ → ℕ), ¬ (((∀ n, f n ≥ 0) ∧ (StrictMonoOn f (Set.Ici 1)) ∧ (f 2 = 2) ∧ (∀ m n, m > 0 → n > 0 → IsRelPrime m n → f (m * n) = f m * f n)) ↔ ((∀ n > 0, f n > 0) ∧ (StrictMonoOn f (Set.Ici 1)) ∧ (f 2 = 2) ∧ (∀ m n, m > 0 → n > 0 → IsRelPrime m n → f (m * n) = f m * f n)))
```

## Bridge obligations

- schema: Check whether strict monotonicity, `f 2 = 2`, and coprime multiplicativity imply positivity at every positive index. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- refute: probe.lean:1:251: error: unsolved goals
f : ℕ → ℕ
hf :
  ¬(((∀ (n : ℕ), ((f n) ≥ 0)) ∧
        ((StrictMonoOn f (Set.Ici 1)) ∧
          (((f 2) = 2) ∧
            (∀ (m n : ℕ), ((m > 0) → ((n > 0) → ((IsRelPrime m n) → ((f (m * n)) = ((f m) * (f n)))))))))) ↔
      ((∀ n > 0, ((f n) > 0)) ∧
        ((StrictMonoOn f (Set.Ici 1)) ∧
          (((f 2) = 2) ∧ (∀ (m n : ℕ), ((m > 0) → ((n > 0) → ((IsRelPrime m n) → ((f (m * n)) = ((f m) * (f n)))))))))))
left✝ : ∀ (n : ℕ), ((f n) ≥ 0)
hs : StrictMonoOn f (Set.Ici 1)
h2 : (f 2) = 2
hm : ∀ (m n : ℕ), ((m > 0) → ((n > 0) → ((IsRelPrime m n) → ((f (m * n)) = ((f m) * (f n))))))
n : ℕ
hn : n > 0
⊢ IsRelPrime 1 2

  Evidence ID: `42596193fb9e8178e1d7b31025d5de9faae9666479ad4dbc54f88d7f3bc7edb1`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`
- refute: probe.lean:1:254: error: failed to synthesize
  Decidable (IsRelPrime 1 2)

Hint: Additional diagnostic information may be available using the `set_option diagnostics true` command.

  Evidence ID: `c2ddee21982c0f5a0815c9202b2c9af5636b204534f34a3b8887de04a89ebba3`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
