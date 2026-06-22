# Migrate Flat Projection To Rooted

## Status

Rooted runtime projection mode is retired. Do not run `--projection rooted`.
The current supported projection modes are `flat` and `hybrid`; use `flat`
for normal workspace and user sync unless a current SDK command explicitly asks
for `hybrid`.

## Current Commands

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
python3 bin/ask skills sync --scope user --projection flat --json
python3 bin/ask skills handles --check --json
```

## Legacy Metadata

Some `.skillsets/**` and context-budget fixtures still use rooted terminology
as compatibility metadata. Maintain those with the dedicated manifest generator
and context-budget validator; do not use the removed `skills sync --projection
rooted` command.

```bash
python3 Infrastructure/scripts/lifecycle-and-sync/generate_skillset_manifests.py --write --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted --json
```
