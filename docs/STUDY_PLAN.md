# Held-out paired study plan

Status: proposed, not approved. Nothing here has been run against a hosted model, and no held-out label exists yet. The paid phase needs explicit approval of the budget change described below.

## 1. Benchmark revision and selection (step 3)

- Source: PutnamBench `lean4/src` at commit `a635813f5edf297d928f9bd5ef8324a26bdde09c` (October 6, 2026; 672 problems).
- Toolchain: PutnamBench uses `leanprover/lean4:v4.33.1` with Mathlib `0df444a360eaa60ab8c11dca51a86af692955474`, while the project worker in `lean/` is pinned to v4.35.0. `ingest` correctly refuses that mismatch, so held-out items are ingested and checked in the separate environment `lean-putnambench/`. It reuses the same `Worker.lean` byte for byte; a test enforces that. Items record the environment they were ingested under, and every later command must pass `--lean-project lean-putnambench`.
- Exclusions: `fixtures/development_problems.json` lists the 21 problems used in fixtures, development runs, earlier audit findings, issue drafts and fix PRs. Add any other problem inspected during development before selecting.
- Selection: `experiments/heldout-selection-a635813.json`, 40 problems chosen by SHA-256 rank of `seed:name` with the benchmark commit as seed, one provenance group per problem. It was generated before any pipeline run or review. The selection records each file's hash; `ingest --selection` refuses a checkout at another revision or with edited files.
- Contamination: PutnamBench is public and likely present in model training data, and earlier manual audit work read PutnamBench statements. Held-out here means unused for building or tuning Yamalemma, not unseen by any model or person. Every report must say this.

### Base-rate limitation

A random sample of current statements will contain few defects. Earlier manual work found roughly a dozen problems with errors among 672, and many recent upstream changes are refinements rather than truth-value changes. Forty random items can estimate false-alarm behaviour and reviewed claim precision, but they cannot estimate recall with useful precision.

The recommended enrichment is a second stratum built from upstream fix history: the statement before a maintainer fix as a defect candidate and the fixed statement as its paired control, sharing one provenance group. `yamalemma fix-history` lists candidate commits; since June 2025 it reports 20 statement-changing commits touching 150 problems, of which 122 were touched by fix-like commits. Ingesting a pre-fix statement written for an older toolchain needs a reviewed transformation adapter that is not built yet. A maintainer fix is evidence for review, not a label: both versions still go through independent review.

## 2. Review (step 4)

Set up the environment and benchmark checkout once:

```bash
cd ~/projects/yamalemma/lean-putnambench && lake update && lake exe cache get && cd ..
git clone https://github.com/trishullab/PutnamBench ~/benchmarks/PutnamBench && git -C ~/benchmarks/PutnamBench checkout a635813f5edf297d928f9bd5ef8324a26bdde09c
uv run yamalemma doctor --lean-project lean-putnambench
```

`lake update` must leave Mathlib at `0df444a3…` in the generated `lake-manifest.json`; check that before ingesting. If `doctor` fails because `Worker.lean` does not compile under v4.33.1, the worker needs a version-compatible variant, and the byte-equality test must then be replaced by a reviewed difference.

```bash
uv run yamalemma ingest ~/benchmarks/PutnamBench/lean4/src --lean-project lean-putnambench --selection experiments/heldout-selection-a635813.json --informal ~/benchmarks/PutnamBench/informal/putnam.json --benchmark-answers --output experiments/heldout-items-answers.json
uv run yamalemma intake-export experiments/heldout-items-answers.json --split heldout --batch heldout-a635813 --output review/heldout-a635813
```

PutnamBench hides every computed answer as `abbrev …_solution := sorry` followed by a one-line comment holding the answer; 346 of its 672 files use this form, and 21 of the 40 selected problems were blocked by it in the first ingest. `--benchmark-answers` substitutes the commented answer for the placeholder, records each substitution under `source_transformations` and in `transformations`, and keeps the original file hash. The substituted answer is the benchmark's claim, not ground truth: the reviewer must confirm it against the official solution, and a wrong answer is itself a defect label. If a substituted file no longer parses, the item falls back to the original source and stays blocked with the reason recorded.

A reviewer who has not seen any Yamalemma or model output labels each packet against the official problem statement, then `uv run yamalemma intake-collect review/heldout-a635813/manifest.json --responses heldout-responses.json --output review/heldout-a635813-dataset.json` produces the dataset. Unsupported items stay excluded and are reported. Model suggestions are not reviews.

## 3. Arms (step 5)

| Arm | Profile | Stages |
| --- | --- | --- |
| A | `configs/study-reader.toml` | GPT-6 Sol reader only |
| B | `configs/study-triage.toml` | local back-translation advisory, GPT-6 Sol reader, GPT-6 Sol proof triage |

The two profiles are identical except for enabled stages: at most two claims per item, one proof repair, 380 calls and $25.00 of reservations per run. Arm B changes two things at once, the back-translation advisory and proof triage, so a difference between arms cannot be attributed to either component alone. The independent second reader (GPT-6 Astra) is excluded: it costs five times as much per token and is not needed to answer the main question.

Primary measures, all reported with counts, coverage and missing items:

- reviewed confirmed-claim precision, from independent post-run judgments;
- false-alarm rate on reviewed controls (any confirmed claim on a control);
- reader item recall on reviewed defects, flagged as underpowered without the fix-history stratum;
- unresolved and internal-error rates, formal attempt coverage;
- calls, estimated cost and time per item.

Report Wilson 95% intervals for proportions and the paired discordant counts (items where only A or only B produced a confirmed claim). With 40 items these are descriptive; no significance claim is planned.

## 4. Cost

Measured so far: one reader call cost an estimated $0.005366 and one proof-writer call $0.001564. Each hosted call reserves `((input_bytes + 4096) × $2 + 4096 × $10) / 1,000,000`, about $0.055–0.065 for these items, and reservations are never refunded.

| | Arm A | Arm B | Total |
| --- | --- | --- | --- |
| Hosted calls, worst case | 40 | 40 × (1 reader + 2 claims × 2 polarities × 2 attempts) = 360 | 400 |
| Reservation, worst case | ≈ $2.60 | ≈ $23.40 | ≈ $26 |
| Expected actual cost | $0.20–0.80 | $0.40–2.40 | $0.60–3.20 |

Expected cost assumes most items yield zero or one claim; it is an estimate, not a measurement. The provider project's enforced $5 monthly limit bounds actual spending and could stop a run early, which would be recorded as missing items.

Required approval: raising the shared ledger, currently 3 calls / $0.25 with 2 calls and $0.109124 used, to `uv run yamalemma budget-limit --max-calls 430 --max-cost-usd 27`. Do not run this without explicit approval. A ten-item pilot of both arms under `--max-calls 110 --max-cost-usd 8` is a cheaper alternative that tests the full path before committing the rest.

## 5. Execution (step 6)

After labels are collected and the budget change is approved:

```bash
uv run yamalemma freeze review/heldout-a635813-dataset.json --config reader=configs/study-reader.toml --config triage=configs/study-triage.toml --output experiments/heldout-protocol.json
uv run yamalemma evaluate experiments/heldout-items-answers.json --lean-project lean-putnambench --protocol experiments/heldout-protocol.json --name reader --config configs/study-reader.toml --output experiments/heldout-reader
uv run yamalemma evaluate experiments/heldout-items-answers.json --lean-project lean-putnambench --protocol experiments/heldout-protocol.json --name triage --config configs/study-triage.toml --output experiments/heldout-triage
```

Run one evaluation at a time. Then collect independent judgments of each emitted claim and score each arm with `score --judgments`, as described in EVALUATION.md. Unlabeled items in the dataset are excluded from accuracy denominators by the scorer.
