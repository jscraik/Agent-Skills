# Migrate Flat Projection To Rooted

## Preconditions

- `python3 bin/ask skills sync --projection rooted --dry-run --json` passes.
- `python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --json` passes.
- At least one workout has a passing scorecard.
- `.skillsets/**` is generated, provenance-rich, and validated.

## Dry Run

```bash
python3 bin/ask skills sync --scope workspace --projection rooted --dry-run --json
```

Confirm:

- `projection_mode` is `rooted`;
- `validation_status` is `pass`;
- root skill-set count is at or below 10;
- no individual latent skill is planned as first-level runtime output.

## Apply

```bash
python3 bin/ask skills sync --scope workspace --projection rooted --json
```

Then validate rooted budget:

```bash
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted --json
bash Infrastructure/scripts/validate_all.sh --ephemeral
```

## User Relink

```bash
python3 bin/ask skills sync --scope user --projection rooted --json
```

## Rollback

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --json
```

Run the full validation gate before rollback while the workspace projection is
still rooted. The full gate checks rooted first-level runtime entries, so flat
rollback is validated separately with the flat context-budget check.
