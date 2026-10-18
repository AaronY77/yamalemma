# syn-3b9811e13b78-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The two inequalities can differ when the ratio equals √3. Whether that equality is attainable by six distinct planar points remains to be checked.

## Source

Item fingerprint: `8c79802ec4ed7c11f339051dd5c2c0801af072a6200ef4b53ec4b48db30a2369`
Source: syn-3b9811e13b78.lean

## Formal claim

```lean
∃ (A : Finset (EuclideanSpace ℝ (Fin 2))) (dists : Set ℝ), ¬ (((sSup dists / sInf dists > Real.sqrt 3)) ↔ ((sSup dists / sInf dists ≥ Real.sqrt 3)))
```

## Bridge obligations

- schema: Determine whether equality can occur under the six-point hypotheses; a difference for arbitrary distance sets alone does not establish a defect in this theorem. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `cab9c1615ac9f5b59815729c0e2e69da8391f8e91e41427711f0fe033b40623b`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
