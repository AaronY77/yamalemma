# syn-a16c5b11639a-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The hypotheses with 0 < S replaced by True are satisfiable, while the original hypotheses are not.

## Source

Item fingerprint: `9eed377371c15cf0fc92cdd2f55908c9060bc4a143312192d6b1f1e774fa2d5b`
Source: syn-a16c5b11639a.lean

## Formal claim

```lean
open Filter Topology Set in
∃ (d : ℕ → ℕ) (S : ℤ), ((True) ∧ (d = fun n : ℕ => ∑ i : Fin (Nat.digits 2 n).length, (Nat.digits 2 n)[i]!) ∧ (S = ∑ k : Icc 1 2020, ((-1 : ℤ)^(d k))*(k : ℤ)^3)) ∧ ¬ ((0 < S) ∧ (d = fun n : ℕ => ∑ i : Fin (Nat.digits 2 n).length, (Nat.digits 2 n)[i]!) ∧ (S = ∑ k : Icc 1 2020, ((-1 : ℤ)^(d k))*(k : ℤ)^3))
```

## Bridge obligations

- instance: Verify the sign of the specified finite sum in Lean and confirm that the informal problem imposes no positivity condition on S. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source conclusion was dropped; the witnesses show only that the edited hypotheses admit an instance the source hypotheses exclude. A reviewer must confirm that this instance is admissible in the original problem and that the edit adds or removes nothing else, since it changes content. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Lean.Parser.Tactic.set_option
  Evidence ID: `dd141813cf6af1ed8a996572b3f0b876f4efdb9ea897b55e416c95d8e1125376`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- refute: probe.lean:1:60: error: maximum recursion depth has been reached
use `set_option maxRecDepth <num>` to increase limit
use `set_option diagnostics true` to get diagnostic information

  Evidence ID: `b765bd1c32657858e461ff9e8e4b47e15cd6f852a67f9686e1ac8c5064c1c542`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- refute: unsupported proof syntax: Lean.Parser.Tactic.set_option
  Evidence ID: `4a4231d7a670cdd788b00f047de1e956d53613593b8c15868475c3e2789b0e86`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
