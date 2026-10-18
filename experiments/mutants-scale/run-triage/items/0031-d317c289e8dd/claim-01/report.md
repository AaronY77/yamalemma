# syn-94b298c4387a-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The corrected hypotheses are satisfiable for a function that does not satisfy the source hypotheses.

## Source

Item fingerprint: `fa110c1c47da304fabea8ecf77d44d6dedc074919aa571498a6b7f5883073932`
Source: syn-94b298c4387a.lean

## Formal claim

```lean
open Polynomial in
∃ (f : ℝ → ℝ), ((ContDiff ℝ 2 f) ∧ (∀ x : ℝ, |f x| ≤ 1) ∧ ((f 0)^2 + (deriv f 0)^2 = 4)) ∧ ¬ ((ContDiff ℝ 2 f) ∧ (∀ x : ℝ, |f x| < 1) ∧ ((f 0)^2 + (deriv f 0)^2 = 4))
```

## Bridge obligations

- instance: Verify the proposed witness satisfies the Lean differentiability and derivative assumptions, and confirm that the informal non-strict bound is intended. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Mathlib.Tactic.convert
  Evidence ID: `8de2dc4bb2154b953aca619d66cc83df4d178dca00bd14e7145d59107354fb19`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: unsupported proof syntax: Mathlib.Meta.FunProp.funPropTacStx
  Evidence ID: `9c0cbc7d73eae6c2ecae140958994e89ec3551cdcbd460c2f64d47f1af8e33d8`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
