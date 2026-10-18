# Yamalemma implementation and design decisions

## What each component does

`runner.py` preserves the original trusted-file execution interface. It records command, exit code, elapsed time, and output. `axiom_report.py` and `axiom_policy.py` preserve the learner-built parser and allowlist decision. The CLI can display their result, but this text route does not produce structured checked evidence.

`worker.py` owns a single persistent Lean process. `lean/Yamalemma/Worker.lean` is the trusted bridge. It imports the pinned Mathlib environment once. Each request runs from the original environment and a fresh elaborator state. A previously checked declaration is never available to a later candidate. Timeout or protocol failure kills the worker; the next request starts a new worker.

`domain.py` defines the JSON contracts, fingerprints, and probe construction. `ingest.py` obtains syntax trees and byte spans from Lean, rather than extracting Lean declarations with regular expressions. `templates.py` builds small proposition, vacuity, equivalence, separation, expression-equality, and counterexample templates. The expected proposition is owned by the prepared claim; a candidate proof cannot replace it.

`harness.py` verifies claim/source/probe identities, enforces supported syntax, invokes Lean, checks the structured response, applies the axiom policy, and emits evidence. `adjudicate.py` assigns deterministic verdicts. `storage.py` stores immutable JSON objects under content hashes and appends local events. `report.py` exports Markdown and JSON with scope and outstanding bridge obligations. `demo.py` provides the seven hand-filled development cases.

`precheck.py` renders elaborated statements, tries bounded contradictory-hypothesis probes, and emits advisory patterns for finite indices, natural arithmetic, division, limits, and totalized operations. Failure of a vacuity proof does not establish satisfiability. A lint is not a defect verdict.

## Trusted mathematical boundary

The structured worker parses one expected type and one proof term. A proof slot is not accepted as a sequence of top-level commands. It elaborates the type, checks that it is a proposition, elaborates the proof at that type, resolves metavariables, checks definitional type equality, and adds a theorem declaration through Lean's kernel with import trust level zero. It then obtains transitive axioms directly from the environment, including dependencies of the theorem type.

Expected types and inferred types can pretty-print differently while being definitionally equal. The original expected source and both renderings are retained. The policy does not use textual equality of pretty-printed types.

The proof/type syntax allowlist is a fixed package artifact derived from the reviewed historical development fixtures, original twelve development statements, and fixed harness templates. Unsupported syntax fails closed. Executable elaborator features are also blocked before requests. The allowlist is not expanded from a candidate's own contents. The keyword check is supplementary; it is not the kernel validation mechanism.

This implementation trusts the installed Lean/Mathlib binaries, cached dependency artifacts, bridge, Python harness, and fixed syntax policy. It does not defend against an attacker who can alter the local application or trusted dependency installation. It is not a replacement for independent security review before offering execution as a public service.

## Operating-system boundary

The structured worker runs in bubblewrap with separate user, PID, mount, network, and other namespaces. The toolchain and dependency tree are mounted read-only. The application source, home contents, Windows mounts, and host credentials are not exposed. The environment is cleared. Temporary writes stay inside the sandbox. File-descriptor, output, input, file-size, heartbeat, and wall-clock limits are enforced.

The address-space allowance is 64 GiB because Lean maps a large quantity of Mathlib artifacts. This is a virtual-address limit, not a 64 GiB RAM allocation and not a strict resident-memory guarantee. The WSL VM's own memory/swap limits still apply. Only one worker is used. This avoids changing the user's WSL configuration or requiring a privileged service.

The old `run` command deliberately remains a trusted-local-fixture tool and is not sandboxed. Generated candidates must use the structured harness. Worker subprocesses do not receive API credentials. Provider calls occur in the Python parent outside this worker.

## Source extraction and supported scope

The extractor preserves original UTF-8 source, byte ranges, declaration/signature text, docstrings, informal text when supplied, imports, and source hashes. It uses Lean's parsed syntax tree, including parser scope updates for `open`, namespaces, and sections. It does not execute the benchmark's theorem proofs.

Supported declarations currently use theorem binders, ordinary `:=` proof bodies, and simple supporting definitions. Referenced definitions and earlier helper theorems are selected from the parsed source and checked in dependency order in the fresh request environment. Their names and namespaces are retained so tactics such as `unfold` retain their meaning. The target theorem itself is never installed as support. Anonymous examples are not dependencies. Supporting definitions are not imported as axioms. Source answer placeholders and admitted helpers are identified and left unresolved unless a reviewed transformation supplies the intended content.

Binder closure is recorded explicitly. The fixed expected type retains the source binder annotations; proof-binder `Type*` annotations are inferred from that type to avoid introducing unrelated fresh universe parameters. Windows CRLF line endings are normalized only for parsing, with parser spans mapped back to the original UTF-8 bytes. The stored source and source hash always describe the original bytes.

Local notation declarations, complex recursive definitions, unsupported section variables, non-Mathlib imports, and source toolchain mismatches require explicit extension. They must not silently become faithful/clean results. The adapter does not claim to cover every possible Lean source file. It is a Putnam-oriented adapter with explicit supported forms.

Source snapshots are not automatically attributed to upstream HEAD. The twelve Exp5 snippets retain their source snapshot as provenance. The separately preserved `pr_files` statements may be proposed fixes. A clean repository revision is recorded only when it can be verified; otherwise content hashes identify the snapshot.

## Evidence versus findings

Confirming and refuting probes are P and Not P for the same claim fingerprint, expected assumptions, and source item. Compilation failure, timeout, forbidden axioms, unsupported syntax, and missing evidence never count as refutation. Both accepted polarities produce INTERNAL-ERROR and block confirmation.

Bridge categories are metadata describing remaining interpretation obligations, not automatic strength rankings. Human review must identify the exact claim, obligation, reviewer, and justification. Human interpretation is not presented as a kernel theorem. The demonstration creates no human sign-offs and therefore no confirmed findings.

The E4/E5/E6 development cases record these corrections:

- S03 checks the selected cyclic-group property; all informal admissibility conditions remain explicit review obligations.
- S06 checks the formalized docstring claim and leaves correction direction to official-source review.
- S08 concerns an abstracted conclusion. B82_weaker does not satisfy the original recurrence and domain assumptions.
- S09 records substitution of the positive-natural answer and treats length-one games separately.
- S11 is a schema separation. It does not imply a truth-value difference for the actual product.
- S10 and S12 refute the specific natural-number indexing predictions, not every possible issue in those benchmark items. The n=0 determinant example is not a witness for all original hypotheses.

## Deliberate implementation choices and deviations

The original plan suggested a third-party Lean REPL or wrapper. This implementation uses a small project-owned JSON worker because the required operations are narrowly defined: parse source, render an expected proposition, and check a constrained proof. It retains the planned persistent import reuse and clean candidate state while avoiding another independently versioned package. The cost is that this bridge must be maintained when Lean changes.

The original teaching parser remains, but acceptance no longer depends on `#print axioms` text. This is a strengthening of the planned trust boundary: arbitrary printed lines cannot establish that the expected theorem was checked.

The implementation uses validated dictionaries and ordinary functions for most records, retaining the existing dataclasses where useful. It does not impose pervasive type annotations or a schema framework. Runtime validation still exists at boundaries. New implementation code contains no comments; design explanations live here.

The extraction strategy closes binders and reconstructs only referenced supporting declarations, checking their types and values rather than importing an entire benchmark file with admitted proofs. These transformations are recorded. Unsupported forms remain unresolved. Broadening source support must preserve parser-based extraction, target-proof exclusion, and environment pins.

Lean acceptance results are always rechecked during replay. Environment fingerprints include the relevant bridge, Python implementation, policy file, toolchain, and dependency lock. Replay refuses a changed environment. Model responses have a separate exact-request cache; caching a model answer never skips Lean validation.

Execution confinement is implemented and tested on this WSL installation, but no claim of a fully audited hostile-code service is made. Strong resident-memory control through delegated cgroups is not configured. Unsupported proof syntax is intentionally conservative.

## Models and orchestration

`config.py` validates TOML profiles, stage switches, and run limits. `models.py` implements the OpenAI Responses API and Ollama chat API using Python's standard HTTP library. `jsonschema` validates their structured outputs. This small dependency is used at the external model boundary; ordinary records and functions remain elsewhere. A provider refusal, partial response, malformed JSON, invalid schema, missing credential, budget exhaustion, or transport failure is not a mathematical verdict.

`prompts.py` owns versioned prompts and four model-accessible templates: the exact statement, its negation, False under its declaration binders, and equivalence to a closed proposed translation. Other hand-authored library templates remain available. Reader claims must anchor to a literal source-signature span. Proposed translations always carry a translation-review obligation. Limiting the automated templates is deliberate: it avoids allowing a model to invent arbitrary transformed targets while still covering the main verification path. More sophisticated instance and separation automation needs reviewed template extensions.

`pipeline.py` performs preliminary checks, optional Lean-only back-translation and comparison, the main reader, an optional independent reader, claim preparation, and proof checks. The back-translator receives no main informal problem or target proof. Its supporting declarations may contain their own mathematical names and content. The comparator sees its paraphrase and the informal text. Comparator output feeds the reader, never the writer directly. The second reader does not see the first reader's answer; its distinct role is part of the cache key.

Each formal claim has confirm and refute polarities. Each polarity allows one initial proof and at most three repairs. Repairs receive the preceding proof and at most 2,000 characters of its first diagnostic; complete diagnostics remain in evidence records. Refusal or truncation stops that polarity instead of pretending a valid proof was returned. The writer is instructed to return a complete Lean term, including `by` for tactic proofs. This remains an instruction, not an acceptance shortcut.

Model cache keys bind the role, model and settings, prompt and schema, exact stage payload, source item, source environment, configuration, prompt version, implementation hashes, and optional frozen protocol. Timing-only precheck metadata is excluded from prompts so it cannot invalidate an otherwise identical replay. Raw provider responses, token usage, elapsed time, status, and cost estimates are stored. Keys are headers only and are never deliberately serialized. Local model digests are checked before uncached generation. Replay retains the identity of the original cached response; it does not claim a newly installed model generated it.

Concurrent CLI audits using the same output directory are rejected with a Linux file lock. A persisted ledger reserves calls and conservative estimated costs before network access. It survives process interruption. This is an application budget, not a contractual billing limit. Token usage missing from a hosted response has unknown cost, never zero cost. Cache reuse incurs zero new API cost while retaining original cost metadata. Local API fees are recorded as zero, excluding electricity and hardware costs.

Local prompts are bounded by input bytes and a conservative context estimate that includes reserved output. Requests that might overrun the configured context are rejected rather than allowing the server to silently discard source text. Because byte counts overestimate tokens, this can reject a prompt that the model would actually fit. This choice favors explicit incomplete outcomes over hidden loss of source context.

## Shared spending boundary

`budget.py` adds a per-user SQLite ledger outside run folders. Every uncached hosted request must reserve both its run allowance and its shared allowance before network access. An immediate SQLite transaction serializes reservations across processes; counters survive restarts and failures. Cache hits, offline misses, and local inference do not consume the hosted ledger. Missing or invalid shared state fails closed. `budget-init` cannot overwrite existing state, `budget-status` reads it, and `budget-limit` changes only cumulative ceilings while preserving usage.

This extends the earlier per-output-folder cap to meet the final application's spending-limit requirement. It uses the Python standard library and keeps the user's three-request/$0.25 scope, importing the two prior requests rather than resetting the budget. Reservations are conservative configured-price estimates, not actual billing records. A crash between shared reservation and run-ledger persistence may conservatively consume unused capacity; it cannot create additional shared allowance. The provider project limit remains an independent control. This is a local-user boundary, not protection against the owner intentionally changing files or against calls from other installations.

## Correction and evaluation tooling

`fixes.py` produces optional closed-statement candidates and checks their elaboration using the same syntax boundary. Elaboration does not prove that a correction matches the intended problem. Every draft retains pending review and `faithfulness_certified: false`. Correction direction is also provisional. Issue drafts are local Markdown only.

`evaluation.py` freezes dataset identities, reviewed labels, provenance groups, split assignments, and configurations before execution. Related provenance groups cannot cross the development/held-out boundary. Reports must carry the frozen protocol fingerprint from the time of the run. Missing runs, incomplete readers, unreviewed data, undefined ratios, unknown costs, and internal errors are represented explicitly. Item-level detection is only a proxy: any suspicion on a known-defect item does not establish that the right defect was found. Optional independent judgments bound to exact audit and claim hashes provide reviewed claim precision and correction-direction accuracy. Review fields record provenance; the program cannot authenticate that a named person actually reviewed something.

`intake.py` exports label-free, source-bound review packets from ingested items and collects reviewer responses into the frozen-protocol dataset format. Packets carry no model or audit output, held-out batches require a pinned benchmark revision, the split is fixed per batch at export, and labeled responses must name a reviewer, basis, official source and an independence declaration. The declaration is recorded, not authenticated.

`selection.py` selects a deterministic held-out sample from a clean pinned benchmark checkout, excluding the listed development problems, and records file hashes that `ingest --selection` rechecks. `ingest --benchmark-answers` replaces an admitted answer placeholder with the answer written in the benchmark comment directly after it, records the transformation, and leaves the reviewer to confirm that answer against the official solution. It also lists upstream statement-changing commits as candidate material for a fix-history stratum. `lean-putnambench/` is a second pinned Lean environment matching PutnamBench's toolchain; it reuses the same worker source. The study plan is in STUDY_PLAN.md.

Eight explicit profiles cover two hosted tiers with reader-only, added back-translation, added proof triage, and added independent-reader stages. No held-out labels or successful hosted results were fabricated. Historical fixtures remain development-only. A real new-target study should follow frozen evaluation and a defined paid-run scope.

## Local installation and remaining evidence

Ollama and DeepSeek R1 7B were installed in the user's WSL home, without a system-wide service. The server binds to loopback, disables cloud use, and loads at most one model/request concurrently. The official archive checksum and model digest are recorded. The requested DeepSeek model was chosen for the local integration; this does not validate its quality against the alternative non-thinking models discussed in the design.

The software through evaluation is implemented, but an empirical project is not complete merely because its tools exist. Authenticated hosted reader and proof-writer checks now pass. Remaining evidence includes independently reviewed held-out labels, paired ablation runs, and review of correction direction against original problem sources. API credentials and genuine human interpretation judgments cannot be invented by the implementation. The first two hosted calls used an estimated $0.00693. There have been no remote pushes, public posts, or fabricated human approvals. `credentials.py` adds environment-first loading of a private owner-only key file outside the repository; custom key environment variables do not fall back to the default file. The restricted key and provider-side $5 monthly hard limit are local account setup, not credentials distributed with the package.
