# Validation Lanes

Apply only the lanes touched by your recommendation.

## Workspace style-profile lane

Use when recommendations should match the user's established repo conventions:

```bash
bash Infrastructure/scripts/profile-dev-repos.sh --root ~/dev
```

Pass criteria:
- command succeeds;
- output includes `style_scan.repo_count=`;
- output includes marker counts and `top_repos` block.

## Shared governance lane

Use when repositories expose these wrappers:

```bash
bash Infrastructure/scripts/codex-preflight.sh --stack auto --mode required
bash Infrastructure/scripts/verify-work.sh --fast
```

## npm lane

Use when policy explicitly selects npm (not pnpm/yarn). If style-profile shows mixed managers in `~/dev`, confirm target-repo policy before enforcing npm commands:

```bash
npm ci
npm run check --if-present
npm run test --if-present
```

Drift checks:

```bash
git diff -- package.json package-lock.json
```

Contract reminders:
- `npm ci` for deterministic automation installs
- do not hand-edit `package-lock.json`

## Bash lane

```bash
shellcheck -x path/to/script.sh
bash -n path/to/script.sh
```

Contract reminders:
- declare the right interpreter (`bash` vs `sh`)
- use strict mode for non-trivial Bash scripts
- quote variable expansion unless deliberate splitting is required

## uv Python lane

```bash
uv run --python 3.12 pytest
uv run --python 3.12 ruff check
```

Dependency operations:

```bash
uv add <pkg>
uv add --dev <pkg>
uv lock
```

Contract reminders:
- keep `uv.lock` synchronized with dependency changes
- avoid manual virtualenv activation for canonical runs

## External dependency/docs lane

Use when recommendations depend on drift-prone library behavior:
- route to `context7` workflow for current library docs grounding.
