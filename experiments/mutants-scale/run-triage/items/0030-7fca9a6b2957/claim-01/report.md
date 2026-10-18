# syn-eaa7b3f60eeb-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source conclusion fails at q = 0 under the defining hypothesis; changing the bound to q > 0 removes that counterexample.

## Source

Item fingerprint: `2fab713487a9e5e5fe09b988b4035748a4384741b13973f4616d0e151c611fcc`
Source: syn-eaa7b3f60eeb.lean

## Formal claim

```lean
open Topology MvPolynomial Filter Set in
∃ (isquotprodprimefact : ℚ → Prop), ¬ ((∀ q : ℚ, q ≥ 0 → isquotprodprimefact q) ↔ (∀ q : ℚ, q > 0 → isquotprodprimefact q))
```

## Bridge obligations

- schema: Check that the finite factorial products are positive, so the defining predicate excludes zero, and separately verify the intended claim for positive rationals. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `a8e7e53fa7194f5fac45882a89f799e7941fc7ef08fe3d715b401250a7b9d650`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
