# Jamie Dev Style Signals

Use this reference when the user asks for recommendations that align with their established `~/dev` project conventions.

## Scan command

```bash
bash Infrastructure/scripts/profile-dev-repos.sh --root ~/dev
```

This script inspects `.git` projects and reports:
- control-plane marker prevalence (`AGENTS.md`, preflight/verify wrappers, environment contracts, CI parity files);
- strongest scaffold-signal repos;
- package-manager and lockfile distribution (`npm`, `pnpm`, `yarn`);
- Python `uv` adoption signals.

## Baseline sample (April 11, 2026 snapshot)

These values came from a scan over `~/dev` in this workspace:
- git repos discovered: `20`
- `AGENTS.md`: `17`
- `.codex/environments/environment.toml`: `18`
- `Infrastructure/scripts/codex-preflight/codex-preflight.sh`: `15`
- `Infrastructure/scripts/validation-and-linting/verify-work.sh`: `5`
- `.harness/ci-required-checks.json`: `9`
- `Infrastructure/harness.contract.json`: `11`
- `Docs/agents/tooling.md`: `12`
- package manager declarations found in nested `package.json`: `pnpm=7`, `npm=1`
- lockfiles found across `~/dev`: `package-lock.json=13`, `pnpm-lock.yaml=6`, `yarn.lock=0`
- Python markers across `~/dev`: `pyproject.toml=5`, `uv.lock=3`

## Interpretation rules

- High `AGENTS.md` prevalence means instruction precedence is usually intentional:
  Start with `AGENTS.md` chain mapping before any remediation recommendation.
- High environment-contract and preflight prevalence means wrapper-first governance is normal:
  Prefer canonical wrapper entrypoints over ad hoc one-off commands.
- Mixed npm and pnpm lockfiles across the workspace means manager policy is repo-scoped, not global:
  In each target repo, infer policy from `packageManager`, lockfile, and CI scripts before recommending commands.
- `verify-work.sh` present in fewer repos than `codex-preflight.sh` means not every repo has the same layered depth:
  Do not force strict tier unless risk signals justify it.
- Moderate `uv` adoption means Python guidance should be explicit:
  Prefer `uv run --python 3.12` and lockfile-aware flows when Python tooling is in scope.

## How to cite in recommendations

When style scan is used, add one short note in output:

`Style profile source: Infrastructure/scripts/profile-dev-repos.sh --root ~/dev (repo_count=<n>, marker summary included)`
