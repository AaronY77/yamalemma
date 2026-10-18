# Yamalemma findings, October 17–18, 2026

A summary of every live run, its result, and the fixes it led to, from the first recorded hosted runs (prompt v3) to the blinded 40 + 40 mutant study (prompt v10). Full details, tables and caveats are in `docs/RESULTS_2026-10-17.md`; section references below point there. Prompts v1 and v2 predate the results record, so no measured results exist for them.

All costs are estimates from response usage and configured pricing, not invoices. "Lean-checked" means the Lean kernel accepted a proof of the harness-built claim under the axiom policy. It certifies that formal claim, not that the benchmark is wrong. A finding is confirmed only after a person discharges the claim's interpretation obligation, and no finding has been confirmed yet.

## Headline

On a blinded, pre-registered set of 40 synthetic single-edit defects and their 40 unmodified originals (section 3j):

| Level | Mutants flagged (n = 40) | Unmodified originals flagged (n = 40) |
| --- | --- | --- |
| Reader suspicion (GPT-6 Sol) | 34/40, 85% (95% CI 71–93%) | 5/40, 13% (6–26%) |
| Lean-checked evidence | 19/40, 48% (33–63%) | 1/40, 3% (0–13%) |
| Deterministic lint only | 0/40 | 0/40 |

- **Filtering.** The harness kept 19 of 34 reader suspicions on mutants (56%) and 1 of 5 on originals (20%).
- **What the evidence proves.** Of the 19 Lean-checked mutants, 3 are proofs that the formal statement itself is false. The other 16 prove that the reader's proposed correction changes the statement's meaning at the flagged spot.
- **The flagged original.** It is 2012 A4: Lean accepted that its strict hypothesis `A 0 < A 1 ∧ B 0 < B 1` excludes degenerate intervals, which the informal "intervals on the real line" arguably allows. It may be a real minor issue and is pending review. "Original" means unmodified, not verified faithful.
- **Scope.** These are planted single-edit defects in public statements the model has likely seen. They do not measure recall on real benchmark errors.

Progress on the same kind of measurement:

| Stage | Lean-checked defects |
| --- | --- |
| v3–v4 positive controls (S08, S11) | 0 of 2 known defects, across 3 runs each |
| Mutant pilot, prompt v9 | 0/10 mutants |
| Same pilot items, prompt v10 (development check) | 4/10 mutants |
| Fresh 40 + 40 study, prompt v10 | 19/40 mutants, 1/40 originals |
| Known development defects | 4 Lean-checked: S08 (1982 B5) by reader and by lint, S03 (2016 A5), S11 (2004 A4) |

## Timeline of runs and results

### Held-out pool and first pilot (October 17)

- **Held-out selection** (section 1). 40 PutnamBench problems at `a635813`, seeded by the commit, excluding 21 development problems. Without answer substitution 22 were blocked, 21 of them by hidden-answer placeholders. With `--benchmark-answers`, 21 answers were substituted and 38 are checkable. Review packets are exported to `review/heldout-a635813`. **No labels exist yet**, and no model or lint has been run on these 40.
- **Five-problem pilot**, unlabeled and outside the 40 (section 2). Both arms completed 5/5 with 0 claims, for $0.042.

### Positive controls, prompts v3 and v4 (section 3)

- **v3, runs 1 and 2.** The reader raised a claim on S08 and S11 in every run, but S08's claim type varied. No evidence was accepted: proof fields held prose or `by sorry`. S08 used 10 calls ($0.137) and S11 6 calls ($0.098).
- **v4 (writer abstention).** The writer declined explicitly in all four directions. S08 used 5 calls ($0.032) and S11 4 calls ($0.037).
- **Lesson.** Whole-statement probes asked the writer to solve Putnam problems.

### Separation probes, prompts v5 to v8 (sections 3b–3d)

- **v5, free-form intended statement.** The first Lean-checked claim on S08 (6 calls, $0.065) was proved against a mis-stated reading, so it was not evidence of the defect. This showed the risk of a misformalized invalidation.
- **v6, edit guard.** The reader gives one exact substring edit, which the harness classifies as regrouping, reordering or rewrite. S08's regrouping edit matched the known fix and was Lean-checked after 3 repairs ($0.071). The clean controls S05 and S07 drew spurious suspicions that Lean filtered out; S12 drew none.
- **v7.** Proofs are now checked under the item's `open` declarations.
- **v8.** Witnesses must be binders only, and targets are elaborated before any proof call. S08 was checked on the first attempt (5 calls, $0.041), but with a rewrite edit a reviewer should reject.
- **Run-to-run variation.** Across 4 full S08 runs, the reader produced the correct regrouping twice.

### Deterministic lint (October 17)

- On the 12 development snippets it flags only S08. On 632 PutnamBench problems (all but the held-out 40) it flags only `putnam_1982_b5`. Precision on this pattern is 1/1, and it covers one bug class.

### #1b: lint-derived claims (section 3e)

- A strong lint finding becomes a regrouping separation claim with no reader call. Witnesses are derived from the parse tree.
- **Free:** the claim builds and elaborates on S08 and 1982 B5, and the earlier proof replays and is accepted in both Lean environments.
- **Paid:** S08 was Lean-checked on the first writer attempt (2 calls, $0.039).

### #2: reader self-consistency, k = 3 (section 3f)

- Run on S08 and S05 (6 calls, $0.093). S08 was flagged in 3/3 samples, but always with rewrite edits. The spurious S05 suspicion recurred in 2/3 samples and survived the majority rule.
- **Not recommended.** Reader errors are correlated across samples, and sampling triples reader cost.

### #3: signature-level separation, prompt v9 (section 3g)

- `hypothesis_separation` edits one hypothesis type, and conclusion edits that only quantify over an existing theorem binder are classified `binder_move`.
- **Free:** my hand-written S03 and S11 claims elaborate and my hand proofs are accepted.
- **Paid, S03:** the reader proposed the same hypothesis edit, Lean-checked after 1 repair (4 calls, $0.061), with a trivial-group witness.
- **Paid, S11:** the reader proposed the same binder move, and the writer proved it on the first attempt (3 calls in total, $0.031).

### #5: fix-history pairs (section 3h)

- 143 before/after pairs from upstream statement-changing commits since June 2025, with the held-out 40 excluded. 33 come from fix-like commits.
- At first 10 fix-like pairs were usable. 22 were blocked by Yamalemma's own syntax allowlist, not by the toolchain.
- After the allowlist was widened and the change check started comparing answer definitions, **31 of 33** were usable. The two still blocked are `putnam_2025_b4`, where the `#{…}` finset notation trips the `#` filter (a false positive), and `putnam_2022_a4`, whose statement has unresolved metavariables.

### Blinded mutant pilot, 10 + 10 (section 3i)

- **Design.** One parse-tree edit per problem across 7 types, neutral shuffled IDs, a separate key, and the informal statement and docstring left unchanged. Free Lean checks place each mutant in an equivalence bucket. Pre-registered as protocol `9667189c`.
- **Prompt v9.** Reader suspicion 9/10 mutants, 1/10 originals. Lean-checked 0/10 mutants. 7 of 9 claims used whole-statement probes, which need Putnam-level counterexamples, and 3 of 9 proof attempts were blocked by the allowlist.
- **Prompt v10** (development check, since the change was made after seeing these items). The new `difference` probe raised Lean-checked mutants to 4/10, with 1/10 originals flagged.
- **Label caveats.** The 1963 A2 original's `f 0 > 0` requirement may be a real issue, and its mutant, `f n ≥ 0`, may not be a defect at all.

### Blinded mutant study, 40 + 40 (section 3j)

- Fresh problems disjoint from the pilot, protocol `46aba078` frozen before any paid call, arm B only. 80/80 reports, 174 hosted calls, $2.22.
- **Results.** See the headline table above. By type, as reader → Lean-checked:

| Type | n | Reader | Lean-checked |
| --- | --- | --- | --- |
| Missing hypothesis | 8 | 8 | 7 |
| Boundary | 8 | 6 | 5 |
| Wrong answer | 8 | 8 | 3 |
| Domain | 7 | 6 | 2 |
| Precedence | 4 | 2 | 2 |
| Extra hypothesis | 3 | 2 | 0 |
| Scope | 2 | 2 | 0 |

- **Equivalence buckets.** 6 mutants proved different (all wrong answers): reader 6/6, Lean-checked 2/6. 34 undetermined: reader 28/34, Lean-checked 17/34. None proved equivalent.
- **Probe use.** Of 41 claims: `difference` 25 (15 checked), `negated_statement` 7 (3), `hypothesis_separation` 7 (2), `separation` 2 (0).
- **Wrong answers.** Three wrong-answer mutants were checked. In one (1984 B1) Sol refuted the mutated statement on the actual objects.
- **Allowlist.** 7 of 37 proof attempts were still blocked: `fun_prop`, `set_option`, `dsimp`, `convert` and `calc`. `set_option` should stay blocked.

## Fixes and improvements, in order

| # | Change | Effect |
| --- | --- | --- |
| 1 | Writer abstention schema (v4) | Explicit declines instead of prose parsed as proofs; per-control cost cut by up to about 4×. |
| 2 | Source-bound `separation` template (v5) | First Lean-checked claim, which exposed the intended-statement risk. |
| 3 | Edit guard and edit classification (v6) | Model-written intended statements replaced by one exact edit; regrouping, reordering and rewrite are distinguished. |
| 4 | Proofs checked under the item's `open` declarations (v7) | Removed name-resolution failures. |
| 5 | Witness binders only, target elaboration before proof calls (v8) | No writer calls on targets that cannot elaborate. |
| 6 | Deterministic precedence lint | 1/1 precision on its pattern, with no model needed. |
| 7 | Lint-derived claims (#1b) | Lean-checked S08 evidence with no reader call. |
| 8 | Optional reader sampling (#2) | Built and measured; not recommended. |
| 9 | `hypothesis_separation` and `binder_move` (v9, #3) | Covers extra-hypothesis and binder-scope defects; S03 and S11 Lean-checked. |
| 10 | Fix-history pair builder (#5) | 31 usable real-defect pairs. |
| 11 | Allowlist widening, 349 → 400 → 404 kinds (reviewed) | Notation and `simp` arguments, then `change`, parenthesized `rcases`, `![…]` and `↑`. |
| 12 | Blinded mutant generator, `synthetic` protocol split, three-level scorer with Wilson intervals | Pre-registered synthetic evaluation without human labels. |
| 13 | `difference` probe (v10) | The model supplies only an edit; Lean checks a witness of disagreement. 0/10 → 4/10 on the pilot items. |
| 14 | Dependent hypothesis formulas | Hypotheses with tactic blocks, such as `by omega`, keep earlier hypotheses in scope. |

## Bugs found and fixed

- A variable named `text` shadowed the `text()` helper during answer substitution.
- `source_sha256` hashed the original file instead of the substituted text, so substituted items were rejected.
- Writer declines were parsed as proofs and sent for repair.
- Statement-level probes asked the writer for full Putnam solutions.
- Proofs were not checked under the item's `open` declarations.
- Targets with prose in the witness field cost writer calls before failing.
- `Type*` witnesses could not be instantiated with a concrete type. Witnesses now use `Type`.
- The fix-pair change check ignored answer definitions, so real answer fixes looked unchanged.
- Harness-built hypothesis conjunctions dropped earlier hypotheses from scope.

## Spending

| Period | Estimated cost |
| --- | --- |
| October 17 runs (sections 1–3d) | about $0.93 |
| #1b, #2, #3 checks (October 18) | about $0.23 |
| Mutant pilot, both arms, prompt v9 | $0.731 |
| Mutant pilot, arm B, prompt v10 | $0.495 |
| Mutant study 40 + 40, arm B | $2.221 |
| **Total** | **about $4.60** |

The shared ledger stands at 368 of 500 calls and $21.35 of $32.00 reserved, under approved limits. Reservations are conservative and never refunded. The provider's $5 monthly cap bounds actual spending, and about $4.60 of it is used in October.

## Limitations and open items

- **No human labels.** The held-out 40 are unlabeled, so precision and recall on real benchmark defects are not measured.
- **Synthetic labels describe construction, not ground truth.** Two "originals" (1963 A2, 2012 A4) drew Lean-checked claims that may be real minor issues, and one mutant (1963 A2) may not be a defect.
- **Most `difference` evidence is schema-level.** It shows that a proposed correction changes meaning; confirming a defect needs review.
- **Weak types.** Scope (0/2) and extra-hypothesis (0/3) mutants were never Lean-checked in the 40 + 40 study. When both versions of a scope swap are true, no instance can separate them.
- **Free equivalence checks are limited.** They can prove difference only for answer changes, so most mutants are undetermined.
- **Contamination.** PutnamBench is public and likely in training data.
- **Small samples.** All intervals are wide, and the comparisons are descriptive.

## Next steps

1. Review the two possible benchmark issues, 2012 A4 and 1963 A2, and record the judgments.
2. Label the held-out 40, then run the paired study for real-defect precision and recall.
3. Build review packets for the 31 fix-history pairs and measure recall on real defects.
4. Optionally allowlist `fun_prop`, `dsimp`, `convert` and `calc`, but not `set_option`.
5. Any further paid work waits for November 1 or a higher provider cap.
