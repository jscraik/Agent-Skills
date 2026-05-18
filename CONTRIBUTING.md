# Contributing

## Table of Contents

- [Minimum workflow contract](#minimum-workflow-contract)
- [Why this workflow exists](#why-this-workflow-exists)
- [Branching and PR rule](#branching-and-pr-rule)
- [Branch name policy](#branch-name-policy)
- [Required pre-merge gates](#required-pre-merge-gates)
- [Required tooling baseline](#required-tooling-baseline)
- [Repo-local verification wrapper](#repo-local-verification-wrapper)
- [Repo-local harness wrapper](#repo-local-harness-wrapper)
- [Recommended security scanner baseline](#recommended-security-scanner-baseline)
- [Review artifacts requirement](#review-artifacts-requirement)
- [Credential-safe evidence snippets](#credential-safe-evidence-snippets)
- [Branch protection recommendation](#branch-protection-recommendation)

## Minimum workflow contract

- Branch off `main` for every change.
- No direct push to `main`.
- Pull request required for every merge.
- Required checks must pass before merge.
- CodeRabbit + Codex review artifacts are required before merge.
- The coding agent must not approve its own PR; review must be independent.
- No third-party directory, marketplace, mirror, sponsorship, or promotional links without maintainer approval.
- Merge only after all gates pass.
- Delete branch/worktree after merge.

## Why this workflow exists

This workflow keeps delivery auditable, reversible, and consistent even for solo development.

## Branching and PR rule

1. Create a dedicated branch/worktree for each task:
   - Agent-created branch: `git switch -c codex/<short-description>`
   - Agent-created worktree: `git worktree add ../tmp-worktree -b codex/<short-description>`
   - Human-authored branch prefixes (when not using `codex/`): `feat/`, `fix/`, `docs/`, `refactor/`, `chore/`, `test/`
2. Keep commits small and focused.
3. Open a PR to merge into `main`.
4. Do not merge until checks, reviews, and checklist items are complete.
5. After merge, delete the remote branch and remove local worktree/branch.

## Branch name policy

- Use lower-case, kebab-case slugs.
- Agent-created branches must use `codex/<short-description>`.
- Human-authored branches may use: `feat/`, `fix/`, `docs/`, `refactor/`, `chore/`, `test/`.
- Avoid `main`-like names and do not include secrets or issue-pii.

## Required pre-merge gates

- `./bin/ask repo validate`
- Run package-level checks only inside verified package roots with their own
  `package.json` and lockfile.
- Do not run `npm run check` at the repository root; this repository has no
  root package manager install step.
- Treat package-manager repair commands in repo-template or consumer-repo
  sections as scoped to repositories that actually contain that package root.
- Keep any task-specific memory or artifact validation tied to the owning
  package, skill, or wrapper command instead of adding root package-manager
  gates.

## Required tooling baseline

Harness-managed repositories should keep this baseline available locally before claiming the repo is ready:

- `prek`
- `diagram`
- `mise`
- `vale`
- `argos`
- `cosign`
- `cloudflared`
- `vitest`
- `ruff`
- `eslint`
- `agent-browser`
- `agentation` (backed by the `agentation-mcp` CLI)
- `mermaid-cli` (via the `mmdc` CLI)
- `markdownlint-cli2`
- `wrangler`
- `beautiful-mermaid`
- `semgrep`
- `semver`
- `trivy`
- `rsearch` (arXiv research)
- `wsearch` (Wikidata search)

Recommended policy:

- Pin repo-managed tooling in `.mise.toml` where possible.
- Treat `scripts/codex-preflight.sh` as required project bootstrap infrastructure.
- Treat `CODESTYLE.md` and `scripts/validate-codestyle.sh` as required repo-local contract files.
- Keep `CODESTYLE.md` as a real repo-local file in generated repositories even when the harness authoring source is maintained globally.
- Scaffold `scripts/codex-enforced` and `scripts/codex-learn` together with preflight so repo-local wrappers own repo-local state.
- Keep `preflight_repo` in `required` mode by default; only relax mode (`optional` or `off`) when the project documents why.
- Adjust preflight binary/path lists per project scope instead of deleting the script.
- Keep repo-scoped telemetry and learned overrides under `.harness/memory/`, and global telemetry under `~/.codex/`.
- Treat `scripts/verify-work.sh` as the canonical repo-facing verification command and keep it wired to repo-local preflight defaults.
- Treat `scripts/validate-codestyle.sh` as the fail-closed codestyle gate and require exact proof-of-pass in change summaries and PRs.
- Treat `scripts/prepare-worktree.sh` as required first-push bootstrap for freshly created worktrees so local hooks run with dependencies and canonical hook wiring.
- Treat `scripts/check-environment.sh` as the local readiness gate for required tooling.
- Block merge or promotion work when a required CLI is missing rather than silently skipping the corresponding validation lane.
- For repositories with explicit `ui` / `chatgpt_apps_sdk` capabilities or matching dependency signals, install `@brainwav/design-system-guidance` and treat its absence as a readiness failure.

## Repo-local verification wrapper

- `harness init` scaffolds `scripts/verify-work.sh` as the canonical repo-local verification entrypoint.
- The wrapper always runs `scripts/codex-preflight.sh` in `required` Local Memory mode with scaffold-safe path and binary expectations.
- `scripts/validate-codestyle.sh` is the canonical fail-closed codestyle gate and is reused by `verify-work`, local hooks, and downstream repo docs.
- Repo-local launches should prefer `./scripts/codex-enforced` so preflight failures are recorded into repo-scoped learn state.
- Use `./scripts/codex-learn analyze` and `./scripts/codex-learn apply` to inspect repo-scoped failure patterns and write override files into `.harness/memory/`.
- Use `bash scripts/validate-codestyle.sh --fast` during iteration for focused codestyle validation.
- Use `bash scripts/validate-codestyle.sh` before handoff for the fail-closed codestyle bundle.
- Use `bash scripts/verify-work.sh` for the broader verification bundle.
- Use `bash scripts/verify-work.sh --fast` for preflight + codestyle fast lane coverage.
- Before the first push from a fresh worktree, run `bash scripts/prepare-worktree.sh`.

## Repo-local harness wrapper

- `harness init` also scaffolds `scripts/harness-cli.sh` for repositories that want a repo-local wrapper around the published CLI package.
- The wrapper resolves `@brainwav/coding-harness/dist/cli.js` from the current repository before running any harness command.
- If the wrapper cannot resolve the package, treat that as local install/bootstrap drift rather than a harness command failure.
- In a consumer repository with a root `package.json` and lockfile, repair from
  that repo root with:
  - `npm install`
  - `npm install --save-dev @brainwav/coding-harness`
- After repair in that verified package root, rerun:
  - `bash scripts/harness-cli.sh <command>`
  - `npm exec harness -- <command>`

## Recommended security scanner baseline

For repositories that use Harness, recommend installing these scanners as project prerequisites:

- Gitleaks
- Trivy
- Semgrep

Recommended policy:

- Keep scanner binaries available in local development environments and CI runners.
- Run scanner checks in CI on pull requests and pushes to protected branches.
- Treat scanner findings as merge blockers unless explicitly waived with rationale.

## Review artifacts requirement

Each PR must include:

- CodeRabbit review artifact (URL, report, or comment reference).
- Codex review artifact (URL, report, or comment reference).
- Confirmation that reviewer agent is independent from coding agent.

If a required review artifact is missing, block merge until it is added or explicitly waived by repository policy.

## Credential-safe evidence snippets

- Never use command substitution in commit messages, PR bodies, or evidence notes for secrets.
- Do **not** use `$(gh auth token)` (or similar) inside `git commit -m ...` / `gh pr create --body ...`.
- Use placeholders in text output:
  - ✅ `$GITHUB_TOKEN`
  - ✅ `${GITHUB_TOKEN}`
  - ❌ expanded token values
- If a token value is ever exposed in commit/PR text, treat it as compromised: rotate/revoke, rewrite history where applicable, and document remediation in the issue/PR.

## Branch protection recommendation

Configure GitHub branch protection (or rulesets) on `main`:

- Bootstrap baseline via harness:
  - `harness branch-protect --owner <owner> --repo <repo>`
- Token resolution for `branch-protect`:
  - `--token <PAT>` or env `GITHUB_TOKEN` / `GITHUB_PERSONAL_ACCESS_TOKEN`
- Require pull request before merge.
- Allow `0` required reviewers for solo-maintainer repositories.
- Dismiss stale approvals when new commits are pushed.
- Require conversation resolution before merge.
- Restrict branch deletions.
- Block force pushes.
- Require linear history.
- Require status checks:
  - `pr-template`
  - `linear-gate`
  - `risk-policy-gate`
  - `dependency-scan`
  - `orb-pinning`
  - `consistency-drift-health`
  - `docs-gate`
  - `lint`
  - `typecheck`
  - `test`
  - `audit`
  - `check`
  - `memory`
  - `security-scan`
  - `CodeRabbit`
- Require branches to be up to date before merge.
- Require code quality results with severity `all`.
- In public repositories, require `CodeQL` code scanning results with `high_or_higher` security alerts and `errors` alerts thresholds.
- Allow merge commits, squash merges, and rebase merges.
- Require workflows to pin third-party actions to full commit SHAs.
- Configure required checks workflows to run on both `pull_request` and `merge_group` when using merge queue.
- Block direct pushes to `main`.
