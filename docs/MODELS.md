# Model operation on this PC

All commands below run inside Ubuntu WSL from `~/projects/yamalemma`.

## Local model

The installed server is Ollama 0.40.6. The model is `deepseek-r1:7b`, Q4_K_M, approximately 4.68 GB, with digest `755ced02ce7befdb13b7ca74e1e4d08cddba4986afdb63a480f2c93d3140383f`. Installation metadata, downloaded archive, models, PID, and logs are under `~/.local/share/yamalemma`. It uses the GTX 1660 Ti with 6 GiB VRAM. The operating system may offload some work to CPU at larger contexts.

```bash
uv run yamalemma local-model start
uv run yamalemma local-model status
uv run yamalemma model-info
uv run yamalemma local-model stop
```

Starting does not create a system service. After WSL shuts down, start it again. The API binds to `127.0.0.1:11434`. The stop command checks that its saved PID belongs to this project's Ollama server before sending a termination signal.

The local profiles request `think = false`, deterministic temperature zero, one request at a time, and an 8,192-token context. This is not a guarantee of short or correct answers: the measured R1 responses still sometimes consumed their output budget. A conservative input-context check may return `context_limit` before generation. An explicit incomplete result is preferable to silently dropping part of the source. Large source contexts should use the hosted reader profile or a deliberately tested context/model change.

The small local model is useful for testing the complete connection and optional advisory stage. Its performance is not established by the installation. Run one item first:

```bash
uv run yamalemma ingest fixtures/exp5 --informal fixtures/putnam_informal.json --output .yamalemma/items.json
uv run yamalemma audit .yamalemma/items.json --item-id S12 --config configs/local.toml --output .yamalemma/local-audit
```

Inspect `summary.json`, each `items/*/audit.md` and `audit.json`, and per-claim `report.md`. Model calls include original prompts, schema, raw responses, usage, and statuses. These are development results, not new benchmark findings.

## Hosted API setup

The adapters use the official [Responses API with structured output](https://developers.openai.com/api/docs/guides/structured-outputs?api-mode=responses). The configured models follow the original design: [gpt-6-sol](https://developers.openai.com/api/docs/models/gpt-6-sol) with medium reasoning and [gpt-6-astra](https://developers.openai.com/api/docs/models/gpt-6-astra) with high reasoning. The configured standard uncached estimates are respectively $2/$10 and $10/$50 per million input/output tokens, with the source and lookup date recorded in TOML. Verify applicable billing rates before a paid study; availability depends on the account.

This PC is configured. Yamalemma reads `~/.config/yamalemma/openai-api-key` when `OPENAI_API_KEY` is unset. The directory has mode 700 and the key file has mode 600. Publicly readable files and symlinks are rejected. The key belongs to the Yamalemma API project, allows only Responses API access, and expires on November 16, 2026. It is outside Git and is not passed into the isolated Lean worker.

The API project has a $5 enforced monthly spend limit across its requests, and auto-recharge is off. OpenAI warns that enforcement is not instantaneous, so a small overshoot is possible. The per-run application caps remain in effect as well. A separate application-wide SQLite ledger now limits all hosted requests by this Linux user, across output folders and profiles. The application ledger does not reset monthly or when a key changes.

On another installation, or to override the stored key for the current Ubuntu terminal without putting it in shell history or a source file:

```bash
read -rsp "OpenAI API key: " OPENAI_API_KEY
printf '\n'
export OPENAI_API_KEY
```

Enter the key in that terminal. Do not paste it into a chat message. Then run:

```bash
uv run yamalemma audit .yamalemma/items.json --item-id S12 --config configs/hosted-smoke.toml --output .yamalemma/hosted-first
```

This is a paid call once a valid key is present. The first-test profile allows at most three calls, one claim, zero proof-repair retries, and a $0.25 conservative estimated reservation per output directory. Each request allows at most 4,096 output tokens. Requests that return errors still consume the call allowance. Restarting with the same output directory preserves the ledger. A new directory starts a separate run ledger but cannot restart the shared allowance. This PC's shared budget also permits only three total requests and $0.25 in reservations, and already includes the first two requests ($0.109124 reserved). These application limits count conservative reservations, not the provider's final charges.

The larger `hosted.toml` profile allows at most 30 calls and a $2 estimated reservation. The limit is across the whole run, not per item. Each claim can request both polarities and up to four proof attempts per polarity. A small budget may intentionally leave claims unresolved.

Reservations use a conservative input-byte estimate plus output allowance at configured prices. A timeout retains its reservation because the remote provider might still have performed work. Actual usage is separately recorded when returned. This mechanism cannot override provider billing or guarantee that a listed price remains current. Set an account-side budget as appropriate for a broader experiment.

Remove the terminal credential after use if desired:

```bash
unset OPENAI_API_KEY
```

## Shared hosted budget

```bash
uv run yamalemma budget-status
```

The ledger lives at `~/.local/state/yamalemma/hosted-budget.sqlite3`, outside the checkout. On a new installation, `uv run yamalemma budget-init` creates a three-request/$0.25 allowance. Initialization refuses an existing ledger rather than resetting usage. This PC is already initialized with the earlier two paid requests included. Missing, corrupt, locked, or exhausted ledgers block new hosted requests. Local Ollama calls and cache replay do not consume this allowance.

For a deliberately approved future spending scope, `budget-limit` accepts required `--max-calls` and `--max-cost-usd` arguments. Those values are absolute cumulative ceilings, not additional allowances. It retains all consumed calls and reservations, and rejects ceilings below current usage. No automatic reset or refill occurs. Do not delete the ledger to obtain a new allowance.

SQLite transactions reserve capacity before network access, including when separate processes use different output folders. Failed requests, timeouts, and interruption after reservation retain capacity because the provider may have performed work. Microdollar integer accounting rounds reservations upward and ceilings downward. The run-specific limits continue to apply as well. If either cap is reached, the application returns an operational status without making a request.

The ledger applies to this user's installation, not another PC or Linux account, and cannot prevent its owner from modifying the application or ledger. Keep the provider-side project limit as an independent control. The ledger records request hashes and reservation amounts, never API keys or prompts.

Changing provider code changes the implementation fingerprint. Old model caches are preserved but may produce `replay_miss` under the new implementation; exact historical replay requires the corresponding implementation. This does not reset either budget or silently permit a paid replacement when `--offline` is set.

## Profiles

| Profile | Reader | Back-translation | Proof triage | Second reader |
| --- | --- | --- | --- | --- |
| `local.toml` | DeepSeek | DeepSeek | DeepSeek writer | No |
| `hosted-smoke.toml` | Sol | No | Sol writer, no repairs | No |
| `hosted.toml` | Sol | No | Sol writer | No |
| `sol-reader.toml` | Sol | No | No | No |
| `sol-backtranslation.toml` | Sol | DeepSeek | No | No |
| `sol-triage.toml` | Sol | DeepSeek | Sol writer | No |
| `sol-second-reader.toml` | Sol | DeepSeek | Sol writer | Astra |
| `frontier-reader.toml` | Astra | No | No | No |
| `frontier-backtranslation.toml` | Astra | DeepSeek | No | No |
| `frontier-triage.toml` | Astra | DeepSeek | Astra writer | No |
| `frontier-second-reader.toml` | Astra | DeepSeek | Astra writer | Sol |

Fix generation is disabled by default. The hosted profiles contain a fixer role; setting `fixes = true` enables drafts only for evidence-checked claims. Changing settings requires a fresh run directory, and any frozen evaluation must use the configuration frozen before execution.

## Replay and common outcomes

Repeat the exact audit command with `--offline` and the same output directory. The cached prompts and responses are checked against their hashes, and Lean checks run again. No network request is made, including the local-model revision lookup. Completed responses are also reusable in ordinary online mode. Failed calls are recorded and reused only in offline mode; an online rerun may try them again within the remaining ledger budget.

`replay_miss` means no response exists for that exact request. `missing_credentials`, `model_revision_mismatch`, `local_model_unavailable`, `input_limit`, `context_limit`, `budget_exhausted`, `shared_budget_exhausted`, `shared_budget_unavailable`, `refused`, `truncated`, `invalid_json`, `invalid_schema`, and transport/provider errors are operational outcomes. None means that a mathematical proposition is false. A successful empty reader result means no claim detected, not certified faithfulness.

Run only one full Lean audit or regression suite at a time on this PC. Mathlib imports and local inference together use substantial WSL memory. The implementation does not change the user's WSL memory allocation.

Ollama protocol and installation references: [chat API](https://docs.ollama.com/api/chat), [Linux installation](https://docs.ollama.com/linux), [DeepSeek R1 7B model](https://ollama.com/library/deepseek-r1:7b).
