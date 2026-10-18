# syn-955642311c5f-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The negation is provable by taking f to be the stated factorial-sum function and evaluating the recurrence at n = 1.

## Source

Item fingerprint: `949aa095d7cbf112f1023ce52d55a7aad7bd38a06385455a304b934886981689`
Source: syn-955642311c5f.lean

## Formal claim

```lean
Not (open Topology Filter Nat in
∀ (f : ℕ → ℤ)
(hf : ∀ n > 0, f n = ∑ i : Set.Icc 1 n, ((i)! : ℤ)), let (P, Q) := putnam_1984_b1_solution; ∀ n ≥ 1, f (n + 2) = P.eval (n : ℝ) * f (n + 1) + Q.eval (n : ℝ) * f n)
```

## Bridge obligations

- instance: Verify in Lean the factorial-sum witness, the polynomial evaluations, and the integer-to-real coercions at n = 1. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence

- confirm: validated
  Evidence ID: `1bc463030aab6f8be17a7b3a273dd8a31c88770ef034f492c5cb8c421f2e09c9`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
