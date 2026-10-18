# S08-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

With T = {0} and S x n = (n : ℝ), the source conclusion holds because its convergence antecedent is false; the edited conclusion fails because it requires a limit at 0.

## Source

Item fingerprint: `3c4f992625fa5d2234b66442a8cee29223315b02d6ca4d64df744053554d0752`
Source: putnam_1982_b5.lean

## Formal claim

```lean
open Set Function Filter Topology Polynomial Real in
∃ (T : Set ℝ) (S : ℝ → ℕ → ℝ) (g : ℝ → ℝ); take T = {0}, S = fun _ n => (n : ℝ), and g = fun _ => 0, (∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
(∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T) ∧ ¬ (∀ x ∈ T, (∃ L : ℝ, Tendsto (S x) atTop (𝓝 L)) ∧
((∀ x ∈ T, Tendsto (S x) atTop (𝓝 (g x))) → ContinuousOn g T))
```

## Bridge obligations

- schema: This separation drops hT and hS and demonstrates only a difference in logical form. Review whether the recursive sequence under the actual hypotheses converges, and whether making convergence an assertion matches the intended theorem. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped; the edit only regroups the source text, and a reviewer must confirm the regrouped statement expresses the original problem. (discharged: False)

## Evidence

- confirm: <input>:2:41: expected ','
  Evidence ID: `1dccb18a88d133eaa98f54303400b216efd6b955658d4ddd7fca270ca961e8bc`
  Axioms: unavailable
  Environment: `57a48d2a3ecea56d48365c16866166619348ec5cc1bb7017f1eec92ef6b0df8b`
- confirm: <input>:2:41: expected ','
  Evidence ID: `b42615e2f3de955d34dedef89fd5d3db8bf6a7bb6b28d6a371f815315d9a0569`
  Axioms: unavailable
  Environment: `57a48d2a3ecea56d48365c16866166619348ec5cc1bb7017f1eec92ef6b0df8b`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
