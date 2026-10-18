# S07-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The comparison may be provable despite the difference in the property required of a particular g. If so, this is a wording mismatch rather than a defect in the theorem.

## Source

Item fingerprint: `1528552df523a16bb84efc2862a4fb1c0bd47ebad7c9f291cbff1866394483fb`
Source: putnam_1986_a5.lean

## Formal claim

```lean
(∀ (n : ℕ) (hn : 1 ≤ n)
  (f : Fin n → ((Fin n → ℝ) → ℝ))
  (hf : ∀ i, ContDiff ℝ 2 (f i))
  (C : Fin n → Fin n → ℝ)
  (hf' : ∀ i j : Fin n, ∀ x : Fin n → ℝ, fderiv ℝ (f i) x (Pi.single j 1) - fderiv ℝ (f j) x (Pi.single i 1) = C i j), ∃ g : (Fin n → ℝ) → ℝ, ∀ i : Fin n, IsLinearMap ℝ (λ x ↦ f i x + fderiv ℝ g x (Pi.single i 1))) ↔ ((∀ (n : ℕ) (hn : 1 ≤ n) (f : Fin n → ((Fin n → ℝ) → ℝ)) (hf : ∀ i, ContDiff ℝ 2 (f i)) (C : Fin n → Fin n → ℝ) (hf' : ∀ i j : Fin n, ∀ x : Fin n → ℝ, fderiv ℝ (f i) x (Pi.single j 1) - fderiv ℝ (f j) x (Pi.single i 1) = C i j), ∃ g : (Fin n → ℝ) → ℝ, ∀ i : Fin n, IsLinearMap ℝ (fun x => f i x + fderiv ℝ g x (Pi.single i 1))) ↔ (∀ (n : ℕ) (hn : 1 ≤ n) (f : Fin n → ((Fin n → ℝ) → ℝ)) (hf : ∀ i, ContDiff ℝ 2 (f i)) (C : Fin n → Fin n → ℝ) (hf' : ∀ i j : Fin n, ∀ x : Fin n → ℝ, fderiv ℝ (f i) x (Pi.single j 1) - fderiv ℝ (f j) x (Pi.single i 1) = C i j), ∃ g : (Fin n → ℝ) → ℝ, ∀ i : Fin n, ∃ (a₀ : ℝ) (a : Fin n → ℝ), ∀ x : Fin n → ℝ, f i x + fderiv ℝ g x (Pi.single i 1) = a₀ + ∑ j : Fin n, a j * x j))
```

## Bridge obligations

- translated: Review the affine-form comparison against the informal definition, and determine whether the existential choice of g makes the two full propositions equivalent. A difference between the predicates for a fixed g alone would not establish a defect. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
