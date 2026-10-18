# syn-de94f0fc5642-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation of the full proposition is provable by constructing a sequence satisfying the base cases and recurrence, then showing that 182 is not odd.

## Source

Item fingerprint: `64f3dc19dd18cb0f7f8f2e09e5d4444d32ef7ee11682afb3136403711a055232`
Source: syn-de94f0fc5642.lean

## Formal claim

```lean
Not (∀ (a : ℕ → ℤ)
(abase : a 0 = 1 ∧ a 1 = 2)
(arec : ∀ n ≥ 2, a n = 4 * a (n - 1) - a (n - 2)), Odd putnam_2015_a2_solution ∧ putnam_2015_a2_solution.Prime ∧ ((putnam_2015_a2_solution : ℤ) ∣ a 2015))
```

## Bridge obligations

- intrinsic: Verify that the supplied declaration evaluates to 182 and that a sequence satisfying the recurrence exists, so the universal proposition is not merely vacuous. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Lean.calcTactic
  Evidence ID: `556f2a90aebcd60078013eceea26819e050ec1f5bfffa9a088df6678fd0bb00f`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: probe.lean:1:459: error: No goals to be solved

  Evidence ID: `d58b049c12cf14337610992d6e7fed71480520948c3e4139ec494b9085d86c81`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
