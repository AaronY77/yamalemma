# syn-e35966fad0ef-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing `Ico 1 16` with `Icc 1 16` changes the conclusion for some predicates. The remaining obligation is to check the maximum under `hconspiratorial`.

## Source

Item fingerprint: `75225dc43ffa20e3274ae26c1d4aea2d17248b9ee39943c2b6b23855739ab5eb`
Source: syn-e35966fad0ef.lean

## Formal claim

```lean
open Set in
∃ (conspiratorial : Set ℤ → Prop), ¬ ((IsGreatest {k | ∃ S, S ⊆ Ico 1 16 ∧ conspiratorial S ∧ S.encard = k} putnam_1974_a1_solution) ↔ (IsGreatest {k | ∃ S, S ⊆ Icc 1 16 ∧ conspiratorial S ∧ S.encard = k} putnam_1974_a1_solution))
```

## Bridge obligations

- schema: Verify that the inclusive range matches the informal wording and determine whether excluding 16 changes the greatest attainable cardinality for the predicate defined by hconspiratorial. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: probe.lean:1:164: error: unsolved goals
T : Set ℤ := {6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}
⊢ {6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16}.encard = 11

  Evidence ID: `17bdf62cba1a86114a7a4f9fb025101b8061fb73e13b2ab39c0349b8f97afb3f`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`
- confirm: unsupported proof syntax: coeNotation
  Evidence ID: `5f71b198be0a9562fbe37cf8a2feb6b9865d6a9d508ee3ac88625ce70be203c4`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
