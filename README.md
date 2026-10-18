# Yamalemma

Yamalemma audits whether formal Lean 4 benchmark statements, mainly PutnamBench, faithfully express their informal problems. An LLM reader compares the informal problem with the exact Lean statement and proposes testable discrepancy claims. The harness, not the model, turns each claim into a Lean proposition built from the exact source text plus at most one declared edit. A proof writer tries to prove that proposition or its negation. A sandboxed Lean kernel worker checks each proof. A rules-only adjudicator then assigns `EVIDENCE-CHECKED`, `REFUTED`, `UNRESOLVED` or `INTERNAL-ERROR`. Lean certifies the formal claim, not the finding. A finding counts as confirmed only after a person discharges the claim's recorded interpretation obligation.

## Architecture

```
informal problem + exact Lean statement
        │
        ▼
reader (LLM) ──► discrepancy claims: type, location, probe, one edit
        │
        ▼
harness ──► Lean proposition built from the source text, the declared edit and parse-tree witnesses;
        │   elaborated before any proof call
        ▼
writer (LLM) ──► proof or explicit abstention, for the claim and for its negation, with bounded repair
        │
        ▼
sandboxed kernel worker ──► elaborates the proof against the fixed expected type, adds it as a kernel
        │                   declaration, collects its axioms
        ▼
rules-only adjudicator ──► EVIDENCE-CHECKED / REFUTED / UNRESOLVED / INTERNAL-ERROR, plus open review obligations
```

- **Probes.** `statement`, `negated_statement`, `vacuity`, `equivalence`, `separation`, `hypothesis_separation` and `difference`. Under `difference`, the reader supplies only an edit. The harness keeps the edited formula and asks Lean for an instance on which the source and edited formulas disagree. Each edit is classified as `regrouping`, `reordering`, `binder_move` or `rewrite`, and rewrites carry a stronger review warning.
- **Lint.** A deterministic precedence lint (`yamalemma lint`) can build claims with no model call (`yamalemma lint-audit`).
- **Worker.** It runs under bubblewrap with no network, no home directory and no credentials, under `prlimit`, from a separate Lean project pinned to the benchmark's toolchain.
- **Axiom policy.** A proof is accepted only if its type matches the expected proposition and its axioms are a subset of `propext`, `Classical.choice` and `Quot.sound`. `sorryAx`, `Lean.ofReduceBool` (from `native_decide`) and custom axioms are rejected.
- **Syntax policy.** Executable syntax (`run_tac`, `elab`, `macro`, `#eval` and similar) is rejected before Lean runs. Targets and proofs must use syntax kinds from the reviewed allowlist `src/yamalemma/proof_syntax.json`.
- **Budget.** Hosted calls draw on a shared spending ledger with conservative per-call reservations. Model responses are cached by exact request, and Lean always re-checks.

## Quickstart

Requirements: Linux or WSL, `uv`, Elan, bubblewrap and util-linux `prlimit`.

```bash
cd ~/projects/yamalemma
uv sync
(cd lean && lake exe cache get)
uv run yamalemma doctor
uv run python -m unittest discover -s tests
uv run yamalemma demo
```

For PutnamBench, use the matching environment in `lean-putnambench/` (Lean v4.33.1, Mathlib `0df444a`) and a checkout pinned at `a635813`:

```bash
(cd lean-putnambench && lake update && lake exe cache get)
uv run yamalemma doctor --lean-project lean-putnambench
uv run yamalemma lint experiments/sweep-items.json --lean-project lean-putnambench --output lint.json
```

Hosted runs need an API key, either in `OPENAI_API_KEY` or in a private file outside the repository, plus an initialized ledger (`uv run yamalemma budget-init`). Check the remaining allowance with `uv run yamalemma budget-status`. The mutant study can be reproduced with `yamalemma mutate`, `yamalemma freeze`, `yamalemma evaluate`, `yamalemma score-mutants` and `yamalemma mutant-restoration`; section 3j of the results lists the exact inputs.

## Evaluation

A blinded, pre-registered mutation study (protocol `46aba078`, frozen before any paid call):
- **Items.** 40 PutnamBench problems at `a635813`, outside the held-out 40 and the 21 development problems.
- **Mutants.** One parse-tree edit each, across 7 defect types.
- **Blinding.** Neutral shuffled IDs and a separate key; informal statements and docstrings unchanged.
- **Configuration.** GPT-6 Sol reader and writer, prompt v10, 1 repair, at most 2 claims per item.

Rates are given with Wilson 95% intervals.

| Level | Mutants flagged (n = 40) | Unmodified originals flagged (n = 40) |
| --- | --- | --- |
| Reader suspicion | 34/40, 85% (71–93%) | 5/40, 13% (6–26%) |
| Reader suspicion at the mutated text | 32/40, 80% (65–90%) | — |
| Lean-checked evidence | 19/40, 48% (33–63%) | 1/40, 3% (0–13%) |
| Lean-checked evidence at the mutated text | 18/40, 45% (31–60%) | — |
| Deterministic lint only | 0/40 (0–9%) | 0/40 (0–9%) |

The Lean check kept 19 of 34 reader suspicions on mutants (56%, 40–71%) and 1 of 5 on originals (20%, 4–62%).

| Mutation type | n | Reader suspicion | Lean-checked |
| --- | --- | --- | --- |
| Missing hypothesis | 8 | 8 | 7 |
| Boundary (`<` ↔ `≤`) | 8 | 6 | 5 |
| Wrong answer | 8 | 8 | 3 |
| Domain (interval kind) | 7 | 6 | 2 |
| Precedence | 4 | 2 | 2 |
| Extra hypothesis | 3 | 2 | 0 |
| Scope (∀/∃ swap) | 2 | 2 | 0 |

Restoration: the result of applying each Lean-checked claim's edit to its mutant.

| Outcome | Claims (of 19) |
| --- | --- |
| Restores the original text exactly | 7 |
| Restores a statement proved equivalent to the original (free Lean check) | 4 |
| At the mutated text, not shown to restore the original | 4 |
| Not at the mutated text | 1 |
| Mutated statement refuted directly, no edit | 3 |

Run cost: 174 hosted calls and about $2.22 estimated, with 80 of 80 reports and no internal errors. A 10 + 10 pilot first returned 0/10 Lean-checked mutants. That traced the bottleneck to probe design and led to the `difference` probe.

## Limitations

- **The defects are synthetic.** They are single local edits, and the numbers measure detection of planted defects, not recall on real benchmark errors.
- **Possible memorization.** PutnamBench is public and likely in the model's training data. In one case the reader reproduced the benchmark's exact answer.
- **Most evidence shows a change of meaning, not a defect.** A Lean-checked `difference` or separation claim proves that the proposed correction changes the statement's meaning at that spot, usually with the other hypotheses dropped. It does not prove that the benchmark is wrong. Only `negated_statement` evidence (3 of the 19) proves the formal statement false.
- **No human labels.** The held-out 40 are unlabeled, so precision and recall on real defects are not measured. No finding has been confirmed by review.
- **The flagged originals are pending review.** "Original" means unmodified, not verified faithful. The flagged originals, 2012 A4 in the study and 1963 A2 in the pilot, may be genuine minor issues and await human judgment.
- **Small samples.** All intervals are wide, and the comparisons are descriptive.

## Documentation

- [docs/findings.md](docs/findings.md): a summary of every run, result, fix and cost.
- [docs/RESULTS_2026-10-17.md](docs/RESULTS_2026-10-17.md): detailed results, sections 1–3j.
- [docs/STUDY_PLAN.md](docs/STUDY_PLAN.md): the held-out paired study design.
- [docs/EVALUATION.md](docs/EVALUATION.md): frozen protocols, label intake and scoring.
- [docs/IMPLEMENTATION.md](docs/IMPLEMENTATION.md): architecture details, trust assumptions and deviations.
- [docs/MODELS.md](docs/MODELS.md): model profiles, local back-translation and the hosted budget.

## Result meanings

Execution status, axiom-policy status, evidence verdict and finding status are separate:
- **Execution:** success, failure, timeout or launch error.
- **Axiom policy:** allowed, forbidden or unreadable.
- **Evidence:** `EVIDENCE-CHECKED` (the claim was proved), `REFUTED` (its negation was proved), `UNRESOLVED`, or `INTERNAL-ERROR` (both polarities accepted).
- **Finding:** confirmed only when the evidence is checked and every bridge obligation has been discharged by a person.

Compilation failure, timeouts, forbidden axioms, unsupported syntax and abstentions never count as refutation.

## Tests

```bash
uv run python -m unittest discover -s tests
```

The suite includes policy, adjudication, artifact integrity, real Lean checks, malformed output, target and source changes, sandbox visibility, timeout restart, the mutant generator, scoring and the synthetic protocol split. Some tests load Mathlib and take 1–2 minutes. `lean/fixtures/runner_invalid.lean` and `axiom_policy_cases.lean` fail on purpose to test rejection.
