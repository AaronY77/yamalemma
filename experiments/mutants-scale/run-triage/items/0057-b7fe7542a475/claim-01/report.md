# syn-364343e1788b-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The source and edited conclusions disagree on an instance satisfying the matrix and product definitions.

## Source

Item fingerprint: `4eef82be6411520768f97b13ee277aafb60575746b23046127d99f16c5d4314e`
Source: syn-364343e1788b.lean

## Formal claim

```lean
∃ (n : ℕ) (a b : ℝ) (c : Fin n → ℝ) (A : Matrix (Fin n) (Fin n) ℝ) (p : ℝ → ℝ), ¬ (((A.det = ((b * p a - a * p b) / b - a))) ↔ ((A.det = ((b * p a - a * p b) / (b - a)))))
```

## Bridge obligations

- schema: Check the instance against hA and hp, and confirm that the informal fraction’s denominator is b - a. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `f57243c356581b165e67d7546c5bb583ba38e7a7864902a085d98c12c2f75ebf`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
