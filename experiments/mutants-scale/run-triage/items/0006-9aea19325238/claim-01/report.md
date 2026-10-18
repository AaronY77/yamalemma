# syn-757a85433c32-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing Ico with Icc should change the validity condition for some inputs; for example, at n = 4 and k = 3, a permutation can produce the values 2, 1, 3, 2, whose range is [1, 4) but not [1, 4].

## Source

Item fingerprint: `11fdcb4828c6ddc8a5956da2385035f494ca0a1b3ba2d207c5b6aa81991c59ea`
Source: syn-757a85433c32.lean

## Formal claim

```lean
∃ (grid : (n : ℕ) → ℕ → Fin n → Fin n → ℤ) (valid : ℕ → ℕ → Prop), ¬ (((∀ n k i j, grid n k i j = i.succ + j.succ - k) ∧ (∀ n k, valid n k ↔ 0 < n ∧ 0 < k ∧
      ∃ (f : Fin n → Fin n), f.Injective ∧
        Set.range (fun i => grid n k i (f i)) = Set.Ico (1 : ℤ) n)) ↔ ((∀ n k i j, grid n k i j = i.succ + j.succ - k) ∧ (∀ n k, valid n k ↔ 0 < n ∧ 0 < k ∧
      ∃ (f : Fin n → Fin n), f.Injective ∧
        Set.range (fun i => grid n k i (f i)) = Set.Icc (1 : ℤ) n)))
```

## Bridge obligations

- schema: Verify that the edited range condition captures the informal requirement, including its demand for all n distinct numbers, and check the resulting solution set. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited hypotheses was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Lean.Parser.Tactic.dsimp
  Evidence ID: `c1a15348d3191e09b985ef2cde178b8036eab6176bd4131b34dd8cafcfff73bd`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: validated
  Evidence ID: `c4e21e6fb32279f3e3e7a6a28734ef3a54894dd09214c5a05550f0ffd018f6ef`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
