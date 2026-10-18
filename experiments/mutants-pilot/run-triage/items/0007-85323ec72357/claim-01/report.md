# syn-f3452fbc1660-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The proposition can be proved by choosing C separately for each p, for example from ‖p.eval 0‖ and its positive integral when p has degree 1999. Such a proof would not establish a uniform constant.

## Source

Item fingerprint: `b058707a4cb2c8e7034d5b14575e6e050e0b942215da2e12a92da7211b4a7baa`
Source: syn-f3452fbc1660.lean

## Formal claim

```lean
open Filter Topology Metric in
∀ p : Polynomial ℝ, ∃ C : ℝ, p.degree = 1999 → ‖p.eval 0‖ ≤ C * ∫ x in (-1)..1, ‖p.eval x‖
```

## Bridge obligations

- parse: Check whether the informal problem intends C to be independent of p. A proof using a p-dependent C demonstrates the scope difference, but does not show that the uniform bound is false. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
