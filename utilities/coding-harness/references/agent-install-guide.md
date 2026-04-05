# Agent install guide — @brainwav/coding-harness in a consumer project

> **For AI agents.** Follow every step in order. Stop and surface blockers rather
> than guessing. Do not claim success without command evidence from the current repo.
> Machine-readable install spec: [`agent-install.json`](./agent-install.json)

## Table of Contents

- [Prerequisites: what must exist before you start](#prerequisites)
- [Phase 1: Auth and private registry](#phase-1-auth-and-private-registry)
- [Phase 2: Install harness globally](#phase-2-install-harness-globally)
- [Phase 3: Init scaffold](#phase-3-init-scaffold)
- [Phase 3b: Migrate away from GitHub Actions (if applicable)](#phase-3b-migrate-away-from-github-actions)
- [Phase 4: mise tool baseline](#phase-4-mise-tool-baseline)
- [Phase 5: CircleCI environment variables](#phase-5-circleci-environment-variables-and-github-secrets)
- [Phase 6: Branch protection](#phase-6-branch-protection)
- [Phase 7: CodeRabbit setup](#phase-7-coderabbit-setup)
- [Phase 8: Memory layer bootstrap](#phase-8-memory-layer-bootstrap)
- [Phase 9: Validate end-to-end](#phase-9-validate-end-to-end)
- [What harness init scaffolds (file inventory)](#what-harness-init-scaffolds)
- [What is enforced, adaptable, and optional](#what-is-enforced-adaptable-and-optional)
- [Capability boundaries](#capability-boundaries)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

Confirm these exist before starting. If any are missing, surface the gap and stop.

| Requirement | Check command | Required |
|---|---|---|
| `node` ≥ 24 | `node --version` | ✅ mandatory |
| `pnpm` ≥ 10 | `pnpm --version` | ✅ mandatory |
| `git` | `git --version` | ✅ mandatory |
| `jq` | `jq --version` | ✅ mandatory |
| `rg` (ripgrep) | `rg --version` | ✅ mandatory |
| `fd` | `fd --version` | ✅ mandatory |
| `mise` | `mise --version` | ✅ mandatory |
| `gh` CLI | `gh --version` | Required for branch-protect + GitHub steps |
| `NPM_TOKEN` env var | `printenv NPM_TOKEN \| wc -c` (must be > 1) | Required for private pkg auth |
| 1Password session | `op account list` | Required if secrets come from 1Password |

```bash
# Quick preflight — run this first
node --version && pnpm --version && git --version && jq --version && rg --version && fd --version && mise --version
printenv NPM_TOKEN | wc -c   # must print a number > 1
```

---

## Phase 1: Auth and private registry

harness is a **private** npm package. Auth must be wired before install.

```bash
# 1. Confirm token is present (do NOT print the value)
printenv NPM_TOKEN | wc -c

# 2. Wire token into ~/.npmrc
echo "//registry.npmjs.org/:_authToken=${NPM_TOKEN}" >> ~/.npmrc

# 3. Verify npm can authenticate
npm whoami

# 4. Confirm the package is reachable
npm view @brainwav/coding-harness dist-tags --json
```

If `npm whoami` fails, the session NPM_TOKEN is stale or invalid. Stop and instruct the
user to refresh their 1Password session or re-export the token.

---

## Phase 2: Install harness globally

```bash
# Preferred: managed via mise (pinned version, login-shell accessible)
mise install -g npm:@brainwav/coding-harness

# Fallback: direct npm global (same effect)
npm install -g @brainwav/coding-harness

# Verify
harness --version
harness --help
```

> **Do not** use `pnpm exec tsx src/cli.ts` in a consumer repo. That path is
> coding-harness development only. Generated `scripts/check-environment.sh` always
> expects the global `harness` binary.

---

## Phase 3: Init scaffold

The `harness init` command scaffolds all governance files. Follow this sequence:

```bash
# 3.1 — Dry run first (no writes — safe to always run)
harness init --dry-run

# Review the planned files. If anything looks wrong, STOP.

# 3.2 — Apply (CircleCI is the standard CI provider for this project)
harness init

# 3.3 — Verify scaffold applied
harness init --check-updates
```

> **CI provider:** `circleci` is the default. Do **not** pass `--ci circleci` here:
> the current CLI treats that extra positional argument as a target directory.
> CodeRabbit review is surfaced by the GitHub App check context (`CodeRabbit`);
> it is not a separate scaffolded CircleCI workflow file.

---

## Phase 3b: Migrate away from GitHub Actions

**Skip this phase if the project has no `.github/workflows/` directory.**

If the target repo already has GitHub Actions workflows, use the dedicated migration
command to remove them safely and cut over to CircleCI. This is a staged, reversible
process — do not manually delete workflow files.

```bash
# 3b.1 — Preview what will change (safe, no writes)
harness ci-migrate prepare --provider circleci --dry-run
```

Review the output. Confirm the listed `.github/workflows/` files will be removed and
that the CircleCI config is already present (from Phase 3). If anything looks wrong, STOP.

```bash
# 3b.2 — Apply the migration and create the recovery snapshot
harness ci-migrate prepare --provider circleci --apply

# 3b.3 — Verify migration is complete (uses the snapshot id from prepare output)
harness ci-migrate verify --snapshot <snapshot-id>

# 3b.4 — Commit the cutover once verification passes
harness ci-migrate commit --snapshot <snapshot-id>
```

**If something goes wrong:**

```bash
# Roll back to the pre-migration state
harness ci-migrate abort --snapshot <snapshot-id>
```

**What `ci-migrate` does:**
- Removes `.github/workflows/` CI job files that conflict with CircleCI
- Updates `harness.contract.json` `activeProvider` to `circleci`
- Updates `.harness/ci-required-checks.json` to CircleCI check names
- Creates a snapshot so rollback is always available
- Does **not** touch `.github/PULL_REQUEST_TEMPLATE.md`, `CODEOWNERS`, or `ISSUE_TEMPLATE/` — those are PR hygiene, not CI

> **Agent rule:** Never manually delete `.github/workflows/` files. Always use
> `harness ci-migrate` so the snapshot + rollback path is available.

**Key files every project MUST have after init:**

```
harness.contract.json               — governance contract (source of truth)
.harness/ci-required-checks.json    — required CI check list
.coderabbit.yaml                    — CodeRabbit review config (repo-scoped)
.circleci/config.yml                — All CI jobs (lint, test, security, release)
.github/PULL_REQUEST_TEMPLATE.md    — PR checklist
scripts/codex-preflight.sh          — agent preflight script (source at session start)
scripts/check-environment.sh        — harness env readiness script
.codex/environments/environment.toml — Codex action blocks
.mise.toml                          — pinned tool versions
Makefile                            — canonical task runner
prek.toml                           — pre-commit/pre-push hook config
```

---

## Phase 4: mise tool baseline

After init, harness scaffolds `.mise.toml` with required tool versions.
Install everything it pins:

```bash
# 4.1 — Trust the mise config (required first time)
mise trust .mise.toml

# 4.2 — Install all tools
mise install

# 4.3 — Verify key binaries are present
mise list
harness check-environment --json
```

**If `harness check-environment` reports missing binaries**, install them:

```bash
mise install -g cargo:prek
mise install -g npm:@brainwav/diagram
mise install -g npm:@argos-ci/cli
mise install -g npm:@mermaid-js/mermaid-cli
mise install -g npm:agentation
mise install -g npm:agentation-mcp
mise install -g npm:agent-browser
mise install -g npm:beautiful-mermaid
mise install -g npm:markdownlint-cli2
mise install -g npm:wrangler
```

Verify binaries are reachable in login shells (non-interactive PATH must be correct):

```bash
zsh -lc 'prek --version && diagram --version && mmdc --version'
```

---

## Phase 5: CircleCI environment variables and GitHub secrets

### CircleCI project environment variables

These are set in **CircleCI project settings → Environment Variables**.
Harness cannot create them — surface this to the user if any are missing.

| Variable | Purpose | Source |
|---|---|---|
| `NPM_TOKEN` | Install `@brainwav/coding-harness` in CI jobs | npm / 1Password |
| `GITHUB_PERSONAL_ACCESS_TOKEN` | `gh` CLI auth for review-gate, PR creation, branch ops | GitHub PAT |
| `LINEAR_API_KEY` | Linear issue sync job | Linear settings |

Check via CircleCI API:

```bash
# Replace <owner> and <repo>; requires CIRCLE_TOKEN env var
curl -s --request GET \
  --url "https://circleci.com/api/v2/project/github/<owner>/<repo>/envvar" \
  --header "Circle-Token: $CIRCLE_TOKEN" | jq '[.items[].name]'
```

> **No GitHub Actions secrets are required.** CI runs through CircleCI, and
> CodeRabbit enforcement is provided by the GitHub App check context (`CodeRabbit`).

---

## Phase 6: Branch protection

```bash
# Apply branch protection using the harness ecosystem profile
harness branch-protect \
  --token "$GITHUB_PERSONAL_ACCESS_TOKEN" \
  --owner <owner> \
  --repo <repo> \
  --ecosystem harness \
  --branch main
```

Required checks applied by `--ecosystem harness`:

```
pr-template, linear-gate, risk-policy-gate, dependency-scan,
orb-pinning, consistency-drift-health, docs-gate,
lint, typecheck, test, audit, check, memory, security-scan, CodeRabbit
```

> `dependency-scan` = Trivy SCA (replaces GitHub Actions `dependency-review`)
> `orb-pinning` = CircleCI orb version enforcement (replaces GitHub Actions `actions-pinning`)

Verify after applying:

```bash
harness check-authz \
  --contract harness.contract.json \
  --repo <owner>/<repo> \
  --branch main
```

---

## Phase 7: CodeRabbit setup

CodeRabbit provides automated PR review through the GitHub App check context.
This repository should use `.coderabbit.yaml` as the repo-local review source.

### 7.1 Verify repo-local config exists

```bash
test -f .coderabbit.yaml && echo "✅ config" || echo "❌ missing"
```

### 7.2 Verify CodeRabbit GitHub App installation

```bash
harness verify-coderabbit \
  --token "$GITHUB_PERSONAL_ACCESS_TOKEN" \
  --owner <owner> \
  --repo <repo>
```

If this fails: instruct the user to install the CodeRabbit GitHub App from
https://github.com/marketplace/coderabbitai and grant repository access.

---

## Phase 8: Memory layer bootstrap

Every harness-enabled repo uses a per-project memory file for agent learnings.

```bash
mkdir -p .harness/memory
test -f .harness/memory/LEARNINGS.md || cat > .harness/memory/LEARNINGS.md << 'EOF'
---
schema_version: 1
purpose: Per-project agent knowledge base — repo-specific gotchas and hard-won fixes.
scope: This repo only.
update_policy: |
  Append after any bug, tool failure, or extra-effort fix specific to this repo.
  Universal gotchas go in ~/.codex/instructions/Learnings.md instead.
  Do NOT delete entries. Append only.
  Format: **YYYY-MM-DD [Agent]:** <problem> → <fix>
---

# Learnings

Repo-specific agent knowledge base. Append-only.
EOF
```

Confirm `.harness/memory/LEARNINGS.md` is gitignored:

```bash
grep -q "\.harness/memory" .gitignore && echo "✅ gitignored" || echo "⚠️  add .harness/memory/ to .gitignore"
```

---

## Phase 9: Validate end-to-end

Run this validation ladder in order. Stop on first failure and report.

```bash
# 9.1 — Preflight (repo context, required binaries)
bash scripts/codex-preflight.sh --stack auto --mode required

# 9.2 — Environment check (mise tools, harness readiness)
harness check-environment --json

# 9.3 — Init idempotency (no pending updates)
harness init --check-updates

# 9.4 — Policy baseline
pnpm check   # or: npm run check

# 9.5 — CodeRabbit (if token available)
harness verify-coderabbit --token "$GITHUB_PERSONAL_ACCESS_TOKEN" --owner <owner> --repo <repo>

# 9.6 — Authorization (branch protection matches contract)
harness check-authz --contract harness.contract.json --repo <owner>/<repo> --branch main
```

All six steps must pass before the setup is complete.

---

## What harness init scaffolds

Full file inventory — all paths relative to repo root.

### Core governance

| File | Purpose |
|---|---|
| `harness.contract.json` | Governance contract — source of truth for all policy |
| `.harness/ci-required-checks.json` | Required CI check names |
| `memory.json` | Harness memory/state file |

### CodeRabbit AI review

| File | Purpose |
|---|---|
| `.coderabbit.yaml` | Repo-local CodeRabbit review configuration |

CodeRabbit review is provided by the GitHub App check context (`CodeRabbit`).
Use `harness verify-coderabbit` to validate setup from CLI.

### CI pipeline (CircleCI)

| File | Purpose |
|---|---|
| `.circleci/config.yml` | All CI: lint, typecheck, test, audit, security-scan, post-merge, auto-release, publish-npm |

### PR and contribution hygiene

| File | Purpose |
|---|---|
| `.github/PULL_REQUEST_TEMPLATE.md` | PR checklist |
| `.github/ISSUE_TEMPLATE/config.yml` | Issue template routing |
| `.github/CODEOWNERS` | Code ownership |
| `CONTRIBUTING.md` | Contribution guide |

### Scripts

| File | Purpose |
|---|---|
| `scripts/codex-preflight.sh` | Agent preflight — source at every session start |
| `scripts/check-environment.sh` | Harness env readiness check |
| `scripts/setup-git-hooks.js` | Git hook installer |
| `scripts/validate-commit-msg.js` | Commit message linter |
| `scripts/check-staged-secrets.sh` | Pre-commit secret scan |
| `scripts/check-doc-style.sh` | Doc style enforcer |
| `scripts/check-related-tests.sh` | Test coverage reminder |
| `scripts/check-semgrep-changed.sh` | Security scan on changed files |
| `scripts/refresh-diagram-context.sh` | Architecture diagram refresh |
| `scripts/check-diagram-freshness.sh` | Diagram staleness gate |
| `scripts/semgrep-pre-push.yml` | Semgrep config for pre-push |

### Tooling config

| File | Purpose |
|---|---|
| `.mise.toml` | Pinned tool versions (node, pnpm, python, uv, prek, diagram, etc.) |
| `biome.json` | Formatter/linter config (TypeScript projects) |
| `.gitleaks.toml` | Secret scanning config |
| `prek.toml` | Pre-commit/pre-push hook config |
| `Makefile` | Canonical task runner |
| `.diagramrc` | Diagram generation config |

### Codex agent environment

| File | Purpose |
|---|---|
| `.codex/environments/environment.toml` | Codex action blocks (auto-generated from package.json scripts) |

---

## What is enforced, adaptable, and optional

Use this table to decide whether to touch a file. When in doubt, check the column.

### Enforced — harness owns these files

`harness init --update` will overwrite these with the latest template. Do not
hand-edit them — changes will be lost on the next update. Use harness commands to
change the values they encode (for example `harness branch-protect` for required checks).

| File | Owned by |
|---|---|
| `harness.contract.json` | `harness init` \u2014 source of truth for all policy |
| `.harness/ci-required-checks.json` | `harness init` \u2014 required check list |
| `memory.json` | `harness init` \u2014 harness state file |
| `.circleci/config.yml` | `harness init` \u2014 full CI pipeline |
| `scripts/check-environment.sh` | `harness init` \u2014 generated from tooling baseline |
| `.codex/environments/environment.toml` | `harness init` \u2014 **only safe to edit if not harness-autogenerated** |

### Adaptable — harness writes a starter, you own it after

These are written once by `harness init` but treated as project-owned after that.
`harness init --update` will **not** overwrite them unless you pass `--force`.

| File | What to customise |
|---|---|
| `.coderabbit.yaml` | Adjust review routing, scopes, and repository-specific review behavior |
| `.github/CODEOWNERS` | Set actual owners for this repo |
| `.github/PULL_REQUEST_TEMPLATE.md` | Add project-specific checklist items |
| `CONTRIBUTING.md` | Add project-specific contribution guidance |
| `Makefile` | Add project-specific tasks |
| `biome.json` | Tune lint/format rules for this project |
| `prek.toml` | Add/remove hooks for this project |
| `.mise.toml` | Pin additional tools needed by this project |
| `.gitleaks.toml` | Add project-specific secret scan exclusions |
| `scripts/codex-preflight.sh` | Add project-specific preflight checks |

### Optional tooling — install only if the project needs it

These are **not** scaffolded by `harness init`. Install with `mise install -g` if the
project uses them. `harness check-environment` will surface which are missing.

| Tool | Install command | When needed |
|---|---|---|
| `@brainwav/diagram` | `mise install -g npm:@brainwav/diagram` | Architecture diagram generation |
| `@argos-ci/cli` | `mise install -g npm:@argos-ci/cli` | Visual regression CI |
| `@mermaid-js/mermaid-cli` (`mmdc`) | `mise install -g npm:@mermaid-js/mermaid-cli` | Mermaid diagram rendering |
| `agentation` | `mise install -g npm:agentation` | Agentation annotation CLI |
| `agentation-mcp` | `mise install -g npm:agentation-mcp` | Agentation MCP server |
| `agent-browser` | `mise install -g npm:agent-browser` | Deterministic browser automation |
| `beautiful-mermaid` | `mise install -g npm:beautiful-mermaid` | Styled diagram output |
| `markdownlint-cli2` | `mise install -g npm:markdownlint-cli2` | Docs linting |
| `wrangler` | `mise install -g npm:wrangler` | Cloudflare Workers deploy |
| `prek` | `mise install -g cargo:prek` | Pre-commit/pre-push hooks (required for hooks to run) |

---

## Capability boundaries

Harness **can** do automatically:
- Scaffold all governance files (`harness init`)
- Verify repository state (`check-environment`, `check-authz`, `verify-coderabbit`)
- Apply branch protection via GitHub API (`harness branch-protect`)
- Generate Codex environment action blocks from package.json scripts
- Run policy gates (lint, typecheck, test, audit, docs-gate, risk-policy-gate)

Harness **cannot** do — requires user action:
- Create or rotate GitHub tokens/PATs or CircleCI environment variables
- Install the CodeRabbit GitHub App on a repository
- Create GitHub repository secrets or CircleCI project vars (agent can check; user must set)
- Bypass branch protection or required review checks
- Safely overwrite user-customized `.codex/environments/environment.toml` without explicit approval

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `npm install -g` fails with 403 | `NPM_TOKEN` expired or missing | Re-export from 1Password; verify `npm whoami` |
| `harness` not found after install | PATH missing `~/.local/bin` or mise shims | Add to `~/.zprofile`: `export PATH="$HOME/.local/bin:$(mise shims path):$PATH"` |
| `mise install` hangs | FIFO env file issue | Use `op run -- mise install` or source env file directly |
| `harness check-environment` reports missing binaries | Tool not installed | Run `mise install -g <tool>` for each missing binary |
| `harness verify-coderabbit` fails | CodeRabbit App not installed on repo | User must install from github.com/marketplace/coderabbitai |
| Branch protection not applying | PAT missing `repo` + `admin:repo_hook` scopes | Re-generate PAT with required scopes |
| Preflight script fails | Old or corrupted `scripts/codex-preflight.sh` in target repo | Use the existing-repo flow: `harness init --check-updates`, `harness upgrade --dry-run`, then `harness upgrade`. Use `harness init --update` only if tracked baseline files are missing and need re-scaffold |
| CircleCI can't authenticate to npm | `NPM_TOKEN` missing from CircleCI project env vars | Set in CircleCI project settings → Environment Variables |
| CI fails on `npm pack` / missing `dist/` | Build not run before pack | Verify `.circleci/config.yml` has build step before pack |
