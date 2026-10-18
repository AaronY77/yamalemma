# Reproducible evaluation and interpretation review

The tool can run experiments, but no held-out performance claim has been established. The original twelve snippets, seven demonstrations, and legacy certificates are development fixtures. Do not relabel them as unseen tests or assume an untouched item is clean.

## Intake and label review

Build the dataset from review packets instead of writing labels by hand next to pipeline results:

```bash
uv run yamalemma intake-export items.json --split heldout --batch heldout-1 --output review/heldout-1
```

`items.json` is the output of `ingest`. Each reviewable item becomes one packet under `packets/` containing its source span, declaration, whole source file, docstring, informal statement and unsupported-syntax reasons. Packets contain no labels and no model or audit output; the export rejects records that carry pipeline fields and items whose content changed after ingestion. Unsupported items are listed under `excluded`. A held-out batch also excludes items without a pinned benchmark revision. The split is fixed for the whole batch at export time. The group defaults to the source file; pass `--groups` with a JSON object mapping item IDs to broader provenance groups when variants of one problem live in different files. The output directory must not already exist.

Reviewers fill in a copy of `responses-template.json`. A response may leave `label` empty, which records the item as `unlabeled`. A `defect` or `control` label needs `reviewer`, `label_basis`, `source_reference` naming the official problem source, and `independent_of_outputs: true`. That last field is the reviewer's own declaration that they did not consult Yamalemma or model output; the program records it but cannot verify it.

```bash
uv run yamalemma intake-collect review/heldout-1/manifest.json --responses heldout-1-responses.json --output heldout-1-dataset.json
```

Collection rechecks the manifest and every packet hash, rejects responses for unknown packets, duplicates, mismatched items and attempts to change the split, and writes a dataset in the format below without overwriting an existing file. Every exported item appears in the dataset; unanswered items stay `unlabeled`. Concatenate datasets from separate batches before `freeze`, which rejects duplicate items and provenance groups that cross splits.

## Freeze before running

Prepare a JSON list of dataset records. Each record has:

```json
{
  "item_fingerprint": "actual fingerprint from ingestion",
  "label": "defect",
  "split": "heldout",
  "group": "shared problem or defect-family provenance",
  "reviewer": "actual independent reviewer",
  "label_basis": "reviewed defect or control rationale",
  "provenance": "pinned source and review reference"
}
```

This is a format illustration, not a usable label. Labels are `defect`, `control`, or `unlabeled`; splits are `development` or `heldout`. A labeled entry requires review provenance. A provenance group cannot occur in both splits. Use groups broad enough to keep variants of the same issue together. Label review should be independent of the pipeline outputs being scored.

Freeze two or more configurations before generating results:

```bash
uv run yamalemma freeze reviewed-dataset.json --config reader=configs/sol-reader.toml --config triage=configs/sol-triage.toml --output experiments/protocol.json
```

The destination must not already exist. The protocol hashes every configuration and records dataset identities, splits, scoring semantics, and a contamination caveat. Its hashes detect accidental edits; they are not a signature or independent timestamp service.

Prepare `heldout-items.json` containing exactly the ingested held-out records referenced by the protocol, then run both configurations against the same items:

```bash
uv run yamalemma evaluate heldout-items.json --protocol experiments/protocol.json --name reader --config configs/sol-reader.toml --output experiments/reader
uv run yamalemma evaluate heldout-items.json --protocol experiments/protocol.json --name triage --config configs/sol-triage.toml --output experiments/triage
```

These commands can incur hosted charges. Each run still has its configured limits. A missing response, incomplete reader, unsupported source, or exhausted budget remains part of the recorded outcome. Evaluating with a changed configuration or item set fails rather than silently changing the experiment. Add `--offline` to reproduce existing responses without new generation.

## Interpret formal evidence separately

An `EVIDENCE-CHECKED` verdict proves the precise formal claim. Confirming the reported discrepancy additionally requires explicit interpretation review. A review list contains entries with these fields:

```json
{
  "claim_fingerprint": "fingerprint of the exact claim object",
  "method": "human",
  "reviewer": "actual reviewer",
  "obligation": "exact obligation string from the claim",
  "justification": "why this formal evidence supports the discrepancy in the original problem"
}
```

Provide an entry for every bridge obligation you actually discharge. Do not copy a template as a completed sign-off. Claim fingerprints use `yamalemma.domain.fingerprint`. Apply a real review with:

```bash
uv run yamalemma review-audit path/to/audit.json --reviews interpretation-reviews.json --output path/to/reviewed-audit.json
```

This rechecks the proofs before recomputing findings. It preserves the original audit; the reviewed file has its own hash. When scoring reviewed reports, make a separate summary JSON whose `report` paths identify those reviewed files. Keep the raw run summary as well. The tool records a reviewer's supplied identity and rationale; it cannot authenticate a human's identity or judgment.

## Score meaning and correction direction

Without claim-level human judgments, item-level precision/recall are only proxies based on reviewed item labels. A random suspicion about an item with a different known defect can still count as an item hit. Do not report that number as validated claim precision.

Independent post-run judgments can evaluate the exact emitted claim and optional correction draft. Supply a JSON list:

```json
{
  "audit_hash": "hash from the exact audit being scored",
  "claim_fingerprint": "fingerprint of its claim",
  "reviewer": "independent evaluator",
  "justification": "review against the original mathematical problem and evidence scope",
  "meaning": "correct",
  "direction": "unreviewed"
}
```

Meaning is `correct`, `incorrect`, or `uncertain`. Direction is `correct`, `incorrect`, or `unreviewed`; a direction judgment requires a recorded fix. This evaluation judgment is separate from an interpretation sign-off: one determines the pipeline finding, while an independent assessment measures whether that finding is correct.

```bash
uv run yamalemma score experiments/protocol.json experiments/triage/summary.json --name triage --config configs/sol-triage.toml --judgments independent-judgments.json --output experiments/triage/reviewed-scores.json
```

Scores include item counts and missing reports, reader item recall, confirmed item precision/recall, recall retained, formal attempt coverage, checked and unresolved claims, internal errors, bridge counts, reviewed claim precision, model calls and reuse, elapsed time, known costs and unknown-cost counts. Correction-direction accuracy is calculated only over explicitly reviewed directions. Undefined ratios are JSON null. Cost per confirmed item is null when costs are unknown or there are no confirmed items.

Bridge categories describe interpretation obligations, not an automatic hierarchy of evidence strength. Unreviewed and uncertain claims are excluded from reviewed precision denominators and must be reported alongside coverage. A held-out study must report its actual reviewed sample size, uncertainty, selection process, and likely public-data contamination; the tool does not manufacture statistical assurance from a small sample.

## Local drafts

```bash
uv run yamalemma draft path/to/claim/report.json --output drafts/issue.md
```

This writes a local reproduction draft. It neither opens an issue nor sends a message. Fix elaboration alone cannot establish correction direction or semantic faithfulness. Review official problem sources and evidence scope before proposing a public correction.
