# S05-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

For arbitrary F, the source conclusion can hold while the conclusion with the informal bounds fails.

## Source

Item fingerprint: `716c49b25b680f88cd2893cf9aa548e198ccca95f577f65832b0c38777ae4b94`
Source: putnam_1983_a3.lean

## Formal claim

```lean
∃ (p : ℕ) (F : ℕ → ℕ); p = 3; F = fun n => if n = 0 then 1 else n, (∀ a ∈ Finset.Icc 1 p, ∀ b ∈ Finset.Icc 1 p, a ≠ b → ¬(F a ≡ F b [MOD p])) ∧ ¬ (∀ a ∈ Finset.Ico 0 p, ∀ b ∈ Finset.Ico 0 p, a ≠ b → ¬(F a ≡ F b [MOD p]))
```

## Bridge obligations

- schema: This separation drops the hypotheses, so it establishes only a difference in the quantified domains. Check whether the two conclusions are equivalent for the specified polynomial F, in particular because F p is congruent to F 0 modulo p. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped and the edit adds or removes content; the separation may come from the rewrite rather than the suspected error, so a reviewer must check the edited statement closely. (discharged: False)

## Evidence

- confirm: <input>:1:21: expected ','
  Evidence ID: `56d7f3a9a3080027bb32bb3fdcce1ccd20cb430c507d191ec81ed2afd8e3c113`
  Axioms: unavailable
  Environment: `8e10e1cf79fd2863ceb1ab1fc6e5e225c00a66c1607c736c290d880bbbf88588`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
