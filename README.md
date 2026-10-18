# Yamalemma

Yamalemma is a local Python CLI and library for reviewing whether formal benchmark statements represent their informal mathematical problems. It includes source extraction, isolated Lean verification, model readers and writers, bounded repair, local back-translation, reproducible reports, explicit interpretation review, and evaluation tooling.

The software is implemented through the evaluation tooling. The first live hosted reader and proof-writer checks passed. A meaningful held-out experiment still requires independently reviewed labels and paired runs. The historical fixtures are development examples, not an accuracy benchmark.

## Environment

Run commands in Ubuntu/WSL from the project root:

```bash
cd ~/projects/yamalemma
uv sync
```

Python is selected by `.python-version`. Lean 4.35.0 and the exact Mathlib revision are recorded in `lean/lean-toolchain`, `lean/lakefile.toml`, and `lean/lake-manifest.json`.

The structured worker requires Linux, bubblewrap, and util-linux's `prlimit`. It has no unrestricted fallback. On this PC these tools are installed and tested. When provisioning another machine, install those system dependencies before using the worker.

To restore Lean dependencies:

```bash
cd lean
lake exe cache get
cd ..
```

If `uv` is missing in a new shell, run `source "$HOME/.local/bin/env"`. If calling Lake manually, run `source "$HOME/.elan/env"`. The Python runner also locates Lake under the current user's Elan installation.

## Commands

The original command remains available:

```bash
uv run yamalemma fixtures/E5_audit.lean
uv run yamalemma run fixtures/axiom_policy_cases.lean --theorem PolicyFixture.admitted
```

These run trusted fixture files. Their printed-report policy check is diagnostic, not the structured evidence acceptance path. Raw fixture execution is not sandboxed. Use only reviewed local fixtures with `run`.

The isolated worker and offline demonstration:

```bash
uv run yamalemma doctor
uv run yamalemma demo
```

The demonstration writes `.yamalemma/demo/summary.json`, one Markdown/JSON report per case, the hand-authored claims and probes, and content-addressed evidence artifacts. It covers five confirming formal claims and two refuted arithmetic predictions. Bridge obligations remain unconfirmed unless separately discharged.

Replay a report against the recorded implementation/environment:

```bash
uv run yamalemma replay .yamalemma/demo/S03/report.json
```

A changed environment causes replay to stop explicitly. Run a new audit to produce a report under the new environment.

Check a proof against a saved source-bound claim:

```bash
uv run yamalemma check --item .yamalemma/demo/S03/item.json --claim .yamalemma/demo/S03/claim.json --proof .yamalemma/demo/S03/proof.lean
```

Ingest the original twelve development snippets and run preliminary checks:

```bash
uv run yamalemma ingest fixtures/exp5 --informal fixtures/putnam_informal.json --output .yamalemma/items.json
uv run yamalemma precheck .yamalemma/items.json --output .yamalemma/prechecks.json
```

`fixtures/exp5` is extracted from a preserved historical blind-audit snapshot. Its manifest records the extraction and added Mathlib import. These are development examples, not a held-out evaluation set. `fixtures/putnam` contains separately preserved proposed statement snapshots from earlier work; it must not be mistaken for original upstream benchmark HEAD.

For an external benchmark checkout, point `ingest` at its Lean source directory. A supplied `--benchmark-commit` must match a clean source checkout. The adapter rejects mismatched toolchains instead of silently upgrading them. Source SHA-256 hashes remain the identity for local snapshots without a verified upstream revision.

## Result meanings

Execution status, axiom-policy status, evidence verdict, and finding status are distinct.

- Execution: success, failure, timeout, or launch error.
- Axiom policy: allowed, forbidden, or unreadable.
- Evidence: EVIDENCE-CHECKED, REFUTED, or UNRESOLVED. Contradictory accepted polarities trigger INTERNAL-ERROR.
- Finding: confirmed only after the evidence is checked and every bridge obligation is discharged.

The allowed axioms are `propext`, `Classical.choice`, and `Quot.sound`. `sorryAx` and all other axiom names are rejected. The structured worker checks the proof against the expected elaborated proposition, submits a theorem declaration to Lean's kernel, and collects dependencies from that declaration. A successful compilation alone is insufficient.

## Model pipeline

DeepSeek R1 7B is installed locally through Ollama on this PC. Start or inspect it with:

```bash
uv run yamalemma local-model start
uv run yamalemma local-model status
```

Run one development item with the local profile:

```bash
uv run yamalemma audit .yamalemma/items.json --item-id S12 --config configs/local.toml --output .yamalemma/local-audit
```

The profile pins the model digest. It is a local integration profile, not a claim that this small model is an effective Lean auditor. Invalid output, output truncation, context limits, and failed proofs remain visible. Only the reader's structured claims can reach the proof writer; local comparator suspicions are advisory.

For hosted models, configure `OPENAI_API_KEY` in the Ubuntu process environment and use `configs/hosted-smoke.toml` for the first test. Keep keys out of source files and chat messages. Each run has a persistent call limit and a conservative estimated cost budget, $0.25 and three calls for the first-test profile; larger profiles use $2. This PC now loads its restricted project key from a private file outside the repository when OPENAI_API_KEY is unset. The first two hosted requests succeeded at an estimated total cost of $0.00693. The OpenAI Yamalemma project also has an enforced $5 monthly limit; provider enforcement can lag slightly.

Reuse the same command and output directory with `--offline` to replay saved model responses without network calls. Lean checks run again. Changed source, configuration, prompt, implementation, or environment cannot silently reuse a different request. Use a new output directory after changing a configuration.

Detailed instructions, profiles, and limitations are in [MODELS.md](docs/MODELS.md). The frozen experiment and human review formats are in [EVALUATION.md](docs/EVALUATION.md).

## Tests

```bash
uv run python -m unittest discover -s tests -v
```

The suite includes pure-policy tests, adjudication, artifact integrity, actual Lean checks, malformed output, target/source changes, injection, state separation, sandbox visibility, and timeout restart. Some tests load Mathlib and therefore take longer than ordinary Python unit tests.

`lean/fixtures/runner_invalid.lean` intentionally fails. `axiom_policy_cases.lean` intentionally uses `sorry` and a custom axiom. They test rejection behavior and are not accepted evidence.

See [IMPLEMENTATION.md](docs/IMPLEMENTATION.md) for architecture, trust assumptions, and deviations. Work remains local; no reports or code have been published. Commands using a hosted configuration can incur API charges once credentials are configured.

## Shared API allowance

`uv run yamalemma budget-status` shows the remaining hosted allowance across all run folders. This PC retains the original three-request/$0.25 test cap with the two earlier requests already counted. A new installation must run `uv run yamalemma budget-init` before paid calls. The ledger never automatically resets. See [model operation](docs/MODELS.md) for explicit limit adjustment, failure handling, and the separate provider-side cap.
