# syn-e35966fad0ef-1

Evidence verdict: **UNRESOLVED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

Replacing `Ico 1 16` with `Icc 1 16` changes the logical form of the conclusion for some predicates `conspiratorial`.

## Source

Item fingerprint: `75225dc43ffa20e3274ae26c1d4aea2d17248b9ee39943c2b6b23855739ab5eb`
Source: syn-e35966fad0ef.lean

## Formal claim

```lean
open Set in
∃ (conspiratorial : Set ℤ → Prop), (IsGreatest {k | ∃ S, S ⊆ Ico 1 16 ∧ conspiratorial S ∧ S.encard = k} putnam_1974_a1_solution) ∧ ¬ (IsGreatest {k | ∃ S, S ⊆ Icc 1 16 ∧ conspiratorial S ∧ S.encard = k} putnam_1974_a1_solution)
```

## Bridge obligations

- schema: Separation drops `hconspiratorial` and establishes only a logical-form difference. Separately verify the maxima under the stated definition of conspiratorial for 1 through 15 and 1 through 16. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. The source hypotheses were dropped and the edit adds or removes content; the separation may come from the rewrite rather than the suspected error, so a reviewer must check the edited statement closely. (discharged: False)

## Evidence

- confirm: unsupported proof syntax: Lean.Parser.Tactic.rcasesPat.paren
  Evidence ID: `41f113639928a63741cb1239bd2e282e598d6fa83b716a386c8ad90f44e00d41`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`
- confirm: probe.lean:1:281: error(lean.unknownIdentifier): Unknown constant `Set.encard_Ico`

probe.lean:1:243: error: unsolved goals
case refine_1.left.refine_2
⊢ (Ico 1 12).encard = 11

probe.lean:1:454: error(lean.unknownIdentifier): Unknown constant `Set.encard_Ico`

probe.lean:1:400: error: unsolved goals
case refine_1.right.inl
hsub : (Ico 1 12) ⊆ (Ico 1 16)
⊢ (Ico 1 12).encard ≤ 11

probe.lean:1:806: error(lean.unknownIdentifier): Unknown constant `Set.encard_Icc`

probe.lean:1:576: error: unsolved goals
case refine_2
h :
  IsGreatest {k | (∃ S ⊆ (Icc 1 16), (((fun S => ((S = (Ico 1 12)) ∨ (S = (Icc 1 16)))) S) ∧ (S.encard = k)))}
    ↑putnam_1974_a1_solution
hle : (Icc 1 16).encard ≤ 11
⊢ False

  Evidence ID: `fc49e0e7dce2e00b5bcd5834b219420d26468569c942655d1ee17d1aa6de9a67`
  Axioms: unavailable
  Environment: `50a77b70d932ea9dfb6e0fc44864ce9ca2e1884ea35b7e52530de752b62136d4`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
