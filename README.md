# Yamalemma

A tool for auditing whether formal mathematics benchmark statements
faithfully represent their informal problems.

## Lean regression environment

- Lean: 4.35.0, selected by lean/lean-toolchain.
- Mathlib: exact commit pinned in lean/lakefile.toml.
- Resolved dependencies: lean/lake-manifest.json.

From the project root, reproduce the checks with:

```bash
cd lean
lake update
lake exe cache get
lake env lean fixtures/E5_audit.lean
lake env lean fixtures/E6_audit.lean
```

Both check commands must finish successfully without errors.
Their axiom reports may contain only:
propext, Classical.choice, and Quot.sound.
An empty axiom list is also acceptable.

## Fixtures and evidence scope

E5_controls.lean and E6_counterexamples.lean are copies of the
historical fixtures. The audit copies name anonymous examples and
print axiom dependencies.

E5 checks arithmetic interpretations and a determinant instance.
Its determinant witness covers only n = 0.

E6 checks counterexamples and excluded instances.
Connecting each formal result to a benchmark faithfulness finding
requires separate justification.

## Python execution runner

From the project root in Ubuntu/WSL:

```bash
uv sync
uv run yamalemma fixtures/E5_audit.lean
```

The command prints JSON containing the execution status, command,
working directory, elapsed time, exit code, stdout, and stderr.

The default timeout is 180 seconds. To choose another limit:

```bash
uv run yamalemma fixtures/E5_audit.lean --timeout 30
```

Execution statuses and CLI exit codes:

- success: 0
- failure: 1
- timeout: 124
- launch_error: 127

Run the regression tests with:

```bash
uv run python -m unittest discover -s tests -v
```

The tests cover successful execution, an invalid proof, timeout,
and launch failure. The runner_invalid.lean fixture deliberately
contains an invalid proof and is expected to fail.

This runner targets Ubuntu/WSL and trusted local fixtures.
A successful execution does not establish that the intended theorem
was checked or that its axiom dependencies satisfy our policy.
Those checks are not yet automated. This runner is not a security
sandbox for untrusted Lean code.