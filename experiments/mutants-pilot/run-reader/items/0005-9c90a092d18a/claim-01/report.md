# syn-a3e3355f28e3-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the formal proposition is provable using this example, with mult chosen as the least nonzero derivative order at each point.

## Source

Item fingerprint: `2d799823568dbd39c3e89a99091a0462c1b5e6ba073d0341ea7dd773a88183c4`
Source: syn-a3e3355f28e3.lean

## Formal claim

```lean
Not (open Topology Filter Nat Set Function in
∀ (N : ℕ) (hN : N > 0)
  (a : Icc 1 N → ℝ)
  (f : ℝ → ℝ)
  (mult : (ℝ → ℝ) → ℝ → ℕ)
  (M : ℕ → ℕ)
  (haN : a ⟨N, by simp; omega⟩ ≠ 0)
  (hf : ∀ t, f t = ∑ j : Icc 1 N, a j * Real.sin (2 * Real.pi * j * t))
  (hmult : ∀ g : ℝ → ℝ, ∀ t : ℝ, (∃ c : ℕ, iteratedDeriv c g t ≠ 0) → (iteratedDeriv (mult g t) g t ≠ 0 ∧ ∀ k < (mult g t), iteratedDeriv k g t = 0))
  (hM : ∀ k, M k = ∑' t : Icc (0 : ℝ) 1, mult (iteratedDeriv k f) t), ((∀ i j : ℕ, i ≤ j → M i ≤ M j) ∧ Tendsto M atTop (𝓝 (2 * N))))
```

## Bridge obligations

- translated: Confirm that the informal zero count is intended to cover one period without counting its shared endpoint twice; the informal statement does not specify a counting interval. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
