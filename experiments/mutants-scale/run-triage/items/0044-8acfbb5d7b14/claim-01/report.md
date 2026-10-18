# syn-a51d88c1b0df-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The proposition with 480/49 in place of putnam_2018_a3_solution holds, while the original does not.

## Source

Item fingerprint: `71709329bd74a52cebf962a360b25a170003997dfbbd20ea55dd01d3c43289fd`
Source: syn-a51d88c1b0df.lean

## Formal claim

```lean
¬ ((IsGreatest
      {∑ i, Real.cos (3 * x i) | (x : Fin 10 → ℝ) (hx : ∑ i, Real.cos (x i) = 0)}
      putnam_2018_a3_solution) ↔ (IsGreatest
      {∑ i, Real.cos (3 * x i) | (x : Fin 10 → ℝ) (hx : ∑ i, Real.cos (x i) = 0)}
      (480 / 49 : ℝ)))
```

## Bridge obligations

- schema: Prove that every admissible sum is at most 480/49, and verify that the indicated cosine values are realizable by real angles. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence


The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
