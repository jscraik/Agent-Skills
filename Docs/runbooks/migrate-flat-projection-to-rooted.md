# Migrate Flat Projection To Rooted

## Preconditions

- `python3 bin/ask skills sync --projection rooted --dry-run --json` passes.
- `python3 bin/ask skills handles --check --json` passes.
- `python3 bin/ask skills handles --check-command-handles --json` passes.
- `python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection flat --json` passes.
  (This validates the current flat baseline before migration; `--projection` defaults to `flat` in `check_context_budget.py`.)
- At least one workout has a passing scorecard.
- `.skillsets/**` is generated, provenance-rich, and validated.
- `.agents/skills/<handle>/SKILL.md` generated command handles exist for every
  command-visible latent module.

## Dry Run

```bash
python3 bin/ask skills sync --scope workspace --projection rooted --dry-run --json
```

Confirm:

- `projection_mode` is `rooted`;
- `validation_status` is `pass`;
- root skill-set count is at or below 10;
- full latent workflow bodies are not planned as first-level runtime output;
- generated command handles are planned only as thin pointers.

## Apply

```bash
python3 bin/ask skills sync --scope workspace --projection rooted --json
```

Then validate rooted budget:

```bash
python3 bin/ask skills handles --check --json
python3 bin/ask skills handles --check-command-handles --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection rooted --json
bash Infrastructure/scripts/validate_all.sh --ephemeral
```

## User Relink

```bash
python3 bin/ask skills sync --scope user --projection rooted --json
```

Confirm user projection applied successfully:

```bash
python3 bin/ask skills sync --scope user --projection rooted --dry-run --json
```

## Acceptance Gates

Do not collapse these gates into one proof:

1. Resolver gate: `python3 bin/ask skills resolve <handle> --json` returns one
   canonical `source_path`.
2. Command-surface gate: `python3 bin/ask skills handles --check --json` passes
   and `.skillsets/command-surface.json` is generated from rooted manifests.
3. Runtime-handle gate: `python3 bin/ask skills handles --check-command-handles
--json` passes and `.agents/skills/<handle>/SKILL.md` exists.
4. Workspace sync gate: `python3 bin/ask skills sync --scope workspace
--projection rooted --json` succeeds.
5. User sync gate: `python3 bin/ask skills sync --scope user --projection rooted
--json` succeeds.
6. Live invocation gate: a fresh Codex runtime can mention `$<handle>` without
   loading unrelated latent workflow bodies.

Reviewer handles are resolved through `python3 bin/ask reviewers resolve
<handle> --json`, not through `ask skills resolve`.

## Rollback

Run the full validation gate before rollback while the workspace projection is
still rooted:

```bash
bash Infrastructure/scripts/validate_all.sh --ephemeral
```

Then rollback to flat projection:

```bash
python3 bin/ask skills sync --scope workspace --projection flat --json
python3 Infrastructure/scripts/validation-and-linting/check_context_budget.py --projection flat --json
```

The full gate checks rooted first-level runtime entries, so flat rollback is
validated separately with the flat context-budget check.
