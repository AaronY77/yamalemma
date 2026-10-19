# Yamalemma

Yamalemma audits whether formal Lean 4 benchmark statements, mainly PutnamBench, faithfully express their informal problems. A language-model reader proposes discrepancy claims, the harness turns each claim into a Lean proposition built from the exact source text, and a sandboxed Lean kernel checks the evidence.

## Results

Blinded, pre-registered mutation study: 40 PutnamBench statements, each with one planted single-edit defect, plus their 40 unmodified originals (95% Wilson intervals).

| Level | Mutants flagged (n = 40) | Unmodified originals flagged (n = 40) |
| --- | --- | --- |
| Reader suspicion | 34/40, 85% (71–93%) | 5/40, 13% (6–26%) |
| Lean-checked evidence | 19/40, 48% (33–63%) | 1/40, 3% (0–13%) |
| Deterministic lint only | 0/40, 0% (0–9%) | 0/40, 0% (0–9%) |

"Lean-checked" means the Lean kernel accepted a proof of the harness-built claim under the axiom policy. Usually the claim is that a proposed correction changes the statement's meaning. It is not by itself a confirmed defect.

- [FINDINGS.md](FINDINGS.md): every run, result, fix and cost, with the per-type and restoration tables.
- [docs/RESULTS_2026-10-17.md](docs/RESULTS_2026-10-17.md): detailed results and caveats.

## How it works

```
informal problem + exact Lean statement
        │
        ▼
reader (model) ──► discrepancy claims: type, location, probe, one declared edit
        │
        ▼
harness ──► Lean proposition from the source text, the edit and parse-tree witnesses; elaborated first
        │
        ▼
writer (model) ──► proof or explicit abstention, for the claim and its negation, with bounded repair
        │
        ▼
sandboxed kernel worker ──► checks the proof against the fixed expected type and collects axioms
        │
        ▼
rules-only adjudicator ──► EVIDENCE-CHECKED / REFUTED / UNRESOLVED / INTERNAL-ERROR
```

- **Probes:**
  - `statement`, `negated_statement`, `vacuity` and `equivalence` test the whole statement.
  - `separation`, `hypothesis_separation` and `difference` test one declared edit.
  - Under `difference`, the reader supplies only an edit, and Lean must find an instance on which the source and edited formulas disagree.
  - Edits are classified as regrouping, reordering, binder move or rewrite.
- **Lint:** a deterministic precedence lint can build claims with no model call.
- **Worker:** it runs under bubblewrap with no network or credentials, under resource limits, in a Lean project pinned to the benchmark's toolchain.
- **Axiom policy:** only `propext`, `Classical.choice` and `Quot.sound` are allowed. `sorryAx`, `native_decide` and custom axioms are rejected.
- **Syntax policy:** executable syntax is refused, and targets and proofs must use reviewed syntax kinds (`src/yamalemma/proof_syntax.json`).
- **Budget:** hosted calls draw on a shared spending ledger. Model responses are cached by exact request, and Lean always re-checks.
- **Findings:** a finding is confirmed only after a person discharges the claim's recorded interpretation obligation.

## Quickstart

Requirements: Linux or WSL, `uv`, Elan, bubblewrap and util-linux `prlimit`.

```bash
uv sync
(cd lean && lake exe cache get)
uv run yamalemma doctor
uv run python -m unittest discover -s tests
uv run yamalemma demo
```

For PutnamBench, use the matching environment in `lean-putnambench/` (Lean v4.33.1, Mathlib `0df444a`) with a checkout pinned at `a635813`:

```bash
(cd lean-putnambench && lake update && lake exe cache get)
uv run yamalemma doctor --lean-project lean-putnambench
uv run yamalemma lint experiments/sweep-items.json --lean-project lean-putnambench --output lint.json
```

Hosted runs need an API key, either in `OPENAI_API_KEY` or in a private file outside the repository, plus an initialized ledger (`uv run yamalemma budget-init`). The mutation study can be reproduced with `mutate`, `freeze`, `evaluate`, `score-mutants` and `mutant-restoration`. Section 3j of the results lists the exact inputs. Further documentation is in `docs/`: implementation, models, evaluation protocol and study plan.

## Limitations

- Synthetic defects. Results are on planted single-edit mutations of public statements the models have likely seen. They do not measure recall on real benchmark errors.
- Evidence is not confirmation. Lean checks a formal claim, usually that a proposed correction changes meaning. A person must confirm any defect. The two flags on unmodified statements (2012 A4, 1963 A2) are pending human review.
- No human labels yet for the held-out 40 or the 31 fix-history pairs.
- Small samples. Intervals are wide, and back-translation's contribution was not measured.
