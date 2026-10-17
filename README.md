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

These checks have been run manually. The automated verification
runner has not yet been implemented.