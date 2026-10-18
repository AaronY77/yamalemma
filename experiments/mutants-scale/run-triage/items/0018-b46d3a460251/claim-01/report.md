# syn-d7d5b61f161c-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source and edited propositions differ for a group and function that fail the triple-product condition and admit no left translate that is a homomorphism.

## Source

Item fingerprint: `a9c72f6e447fa0289e215f3e48285494a728cb6f7d5d66e6dd6870bde809945e`
Source: syn-d7d5b61f161c.lean

## Formal claim

```lean
open Filter Topology in
∃ (G : Type) (_inst1 : Group G) (φ : G → G), ¬ ((∃ a : G, let ψ := fun g => a * φ g; ∀ x y : G, ψ (x * y) = ψ x * ψ y) ↔ ((∀ g₁ g₂ g₃ h₁ h₂ h₃ : G, g₁ * g₂ * g₃ = 1 → h₁ * h₂ * h₃ = 1 → φ g₁ * φ g₂ * φ g₃ = φ h₁ * φ h₂ * φ h₃) → ∃ a : G, let ψ := fun g => a * φ g; ∀ x y : G, ψ (x * y) = ψ x * ψ y))
```

## Bridge obligations

- schema: Exhibit a specific group and function for which the omitted condition fails and the unconditioned conclusion is false; check that the added condition exactly translates the informal assumption. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
