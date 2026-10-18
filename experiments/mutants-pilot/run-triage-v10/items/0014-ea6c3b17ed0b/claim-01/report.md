# syn-e39722b71bad-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Adding S.card = 4 to the antecedent should make the source and edited propositions differ, with S = ∅ providing a test instance.

## Source

Item fingerprint: `6d84703657bcd39536b43b6ab63146dbff19b59daf53bc9ac5fc762bda546010`
Source: syn-e39722b71bad.lean

## Formal claim

```lean
∃ (y : ℝ → ℝ) (S : Finset ℝ), ¬ (((Collinear ℝ {P : Fin 2 → ℝ | P 0 ∈ S ∧ P 1 = y (P 0)} → (∑ x ∈ S, x) / 4 = putnam_1977_a1_solution)) ↔ ((S.card = 4 ∧ Collinear ℝ {P : Fin 2 → ℝ | P 0 ∈ S ∧ P 1 = y (P 0)} → (∑ x ∈ S, x) / 4 = putnam_1977_a1_solution)))
```

## Bridge obligations

- schema: Verify that cardinality four captures the informal requirement of four distinct curve points and that the empty graph set is collinear under the Lean definition. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: probe.lean:1:172: error: Type mismatch
  collinear_empty
has type
  ∀ (k : (Type ?u.112)) {V : (Type ?u.111)} (P : (Type ?u.110)) [inst : (DivisionRing k)] [inst_1 : (AddCommGroup V)]
    [inst_2 : (Module k V)] [inst_3 : (AddTorsor V P)], (Collinear k ∅)
but is expected to have type
  Collinear ℝ ∅

probe.lean:1:0: error: unsolved goals
hc : Collinear ℝ {P | (((P 0) ∈ ∅) ∧ ((P 1) = ((fun x => 0) (P 0))))}
⊢ Collinear ℝ ∅

  Evidence ID: `6adc4849649e3d2cae8b8da2f7b172217a2cfdb41f0069afd6a1719c7a7b02e2`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`
- confirm: probe.lean:1:0: error: unsolved goals
hc : Collinear ℝ {P | (((P 0) ∈ ∅) ∧ ((P 1) = ((fun x => 0) (P 0))))}
⊢ Collinear ℝ ∅

  Evidence ID: `abe72374de8db56f93693c0e0b31dfdf62957c69949c7b8a3edd5281136d1bfd`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
