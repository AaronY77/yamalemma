# syn-5a34626db4db-1

Evidence verdict: **EVIDENCE-CHECKED**
Finding status: **unconfirmed**

Scope: source-bound formal probe; interpretation pending

The original and edited IsLeast propositions disagree for the specified P and f.

## Source

Item fingerprint: `ac489ddc08d79e8a9c2fbc5db0723caec1cb74c9af885ed01dfe29631723eabc`
Source: syn-5a34626db4db.lean

## Formal claim

```lean
open Topology Filter Set Polynomial Function in
∃ (P : ℝ × ℝ × ℝ → Prop) (f : ℝ × ℝ × ℝ → ℝ), ¬ ((IsLeast {y | ∃ r s t, P (r, s, t) ∧ f (r, s, t) = y} putnam_1981_b2_solution) ↔ (IsLeast {y | ∃ r s t, P (r, s, t) ∧ f (r, s, t) = y} (12 - 8 * Real.sqrt 2)))
```

## Bridge obligations

- schema: Verify in Lean that the edited value is the global minimum, and review whether the named solution was intended to denote a different expression. A reviewer must establish that this formal proposition supports the stated discrepancy in the original problem. Only the edited conclusion was kept; Lean evidence shows that the edit changes its meaning on some instance, not that the source is wrong. A reviewer must confirm that the edited text is the intended reading and check it closely, since the edit adds or removes content. (discharged: False)

## Evidence

- confirm: probe.lean:1:151: error: don't know how to synthesize implicit argument `α`
  @Exists (?m.94 y) fun r => (∃ s t, (True ∧ (putnam_1981_b2_solution = y)))
context:
y : ℝ
⊢ Sort ?u.85

probe.lean:1:151: error: don't know how to synthesize implicit argument `α`
  @Exists (?m.95 y r) fun s => (∃ t, (True ∧ (putnam_1981_b2_solution = y)))
context:
y : ℝ
r : ?m.94 y
⊢ Sort ?u.87

probe.lean:1:151: error: don't know how to synthesize implicit argument `α`
  @Exists (?m.96 y r s) fun t => (True ∧ (putnam_1981_b2_solution = y))
context:
y : ℝ
r : ?m.94 y
s : ?m.95 y r
⊢ Sort ?u.89

probe.lean:1:159: error(lean.inferBinderTypeFailed): Failed to infer type of binder `t`

probe.lean:1:157: error(lean.inferBinderTypeFailed): Failed to infer type of binder `s`

probe.lean:1:155: error(lean.inferBinderTypeFailed): Failed to infer type of binder `r`

probe.lean:1:48: error: unsolved goals
⊢ ¬((IsLeast {y | (∃ r s t, (((fun x => True) (r, s, t)) ∧ (((fun x => putnam_1981_b2_solution) (r, s, t)) = y)))}
        putnam_1981_b2_solution) ↔
      (IsLeast {y | (∃ r s t, (((fun x => True) (r, s, t)) ∧ (((fun x => putnam_1981_b2_solution) (r, s, t)) = y)))}
        (12 - (8 * √2))))

  Evidence ID: `01f7104f71db96073fb0f66c65a2fcee075417e338fe57825b3205d68127526e`
  Axioms: unavailable
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`
- confirm: validated
  Evidence ID: `97e86e95af20c8182fc6014fd80050d3d66f361d9831cacfab427d7191ce51dc`
  Axioms: ['propext', 'Classical.choice', 'Quot.sound']
  Environment: `5e2c48888b4507bbe13276838167d0b3566a82a7cd7faed4eb484b3c3be56859`

The JSON report contains complete inputs, attempts, and provenance.
Formal evidence does not by itself establish faithfulness to the informal problem.
