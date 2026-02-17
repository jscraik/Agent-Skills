---
name: automate-github-issues
description: Use when the user asks to automate GitHub issue triage with parallel Jules agents; output a validated fleet setup and runbook for analyze, plan, dispatch, and merge.
---

# Automate GitHub Issues with Jules

## Philosophy
- Build a deterministic issue pipeline: analyze -> plan -> validate -> dispatch -> merge.
- Keep setup canonical for unreleased/greenfield repos; do not add compatibility shims unless explicitly requested.
- Prefer explicit validation gates before dispatching parallel agents.

## Triggers and usage
- The user wants automated GitHub issue triage and multi-agent implementation.
- The repo needs repeatable setup for fleet scripts plus GitHub Actions workflows.

## Required inputs
- Target repository path and default branch.
- Access to `JULES_API_KEY` and repository write permissions.
- Confirmation that `.github/workflows/` and `scripts/fleet/` can be created/updated.

## Expected deliverables
- Output contract schema_version: 1.0
- Fleet scripts under `scripts/fleet/`.
- Workflow templates under `.github/workflows/`.
- Environment template and setup checklist.
- Runbook notes for local execution and troubleshooting.

## Setup steps

### Step 1: Copy fleet scripts
Copy the entire `scripts/` directory from this skill to `scripts/fleet/` in the target repo:

```text
scripts/fleet/
├── fleet-analyze.ts
├── fleet-plan.ts
├── fleet-dispatch.ts
├── fleet-merge.ts
├── types.ts
├── prompts/
│   ├── analyze-issues.ts
│   └── bootstrap.ts
└── github/
    ├── git.ts
    ├── issues.ts
    ├── markdown.ts
    └── cache-plugin.ts
```

### Step 2: Copy workflow templates
- `assets/fleet-dispatch.yml` -> `.github/workflows/fleet-dispatch.yml`
- `assets/fleet-merge.yml` -> `.github/workflows/fleet-merge.yml`

### Step 3: Create `scripts/fleet/package.json`
Use the bundled `package.json` template in this skill and keep dependency versions pinned unless the user asks to change them.

### Step 4: Create environment template
Copy `assets/.env.example` to the repository root as `.env` and fill required values.

### Step 5: Install dependencies
```bash
cd scripts/fleet && bun install
```

### Step 6: Share next steps with the user
1. Add `JULES_API_KEY` in GitHub repository secrets.
2. Confirm `GITHUB_TOKEN` permissions for PR creation/merge.
3. Adjust schedule in `.github/workflows/fleet-dispatch.yml`.
4. Commit generated files.

## Validation
- Fail fast: stop at the first failed validation gate, fix the issue, and rerun checks.
- Confirm files exist in `scripts/fleet/` and `.github/workflows/`.
- Run `bun install` and verify it exits cleanly.
- Run `bun fleet-analyze.ts` to confirm issue fetch path is wired.
- Ensure task validation rejects overlapping file ownership before dispatch.

## Constraints
- Never print or commit secrets.
- Do not overwrite user workflow files without explicit confirmation.
- Do not add backward-compatibility migration paths unless explicitly required.

## Anti-patterns
- Dispatching parallel tasks before ownership conflict checks.
- Merging generated PRs without CI/branch protection checks.
- Introducing legacy adapters for unreleased repos by default.

## Variation and adaptation
- Tune analysis depth in `scripts/fleet/prompts/analyze-issues.ts`.
- Adjust issue filtering in `scripts/fleet/github/issues.ts`.
- Modify dispatch cadence by editing workflow schedules.

## Examples
- "Set up automated issue triage + parallel Jules execution for this repo."
- "Install fleet scripts/workflows and validate the issue dispatch pipeline."
- "Wire this repo for daily issue analysis and controlled sequential merges."

## Manual usage
```bash
cd scripts/fleet

bun fleet-analyze.ts
JULES_API_KEY=<key> bun fleet-plan.ts
JULES_API_KEY=<key> bun fleet-dispatch.ts
GITHUB_TOKEN=<token> bun fleet-merge.ts
```

## Resource references
- [Architecture Overview](resources/architecture.md)
- [Contract](references/contract.yaml)
- [Evals](references/evals.yaml)

## Troubleshooting
- "Unable to parse git remote URL": ensure `origin` points to GitHub.
- Ownership conflict errors: merge or split overlapping tasks before dispatch.
- CI timeout during merge: increase `maxWaitMs` in `fleet-merge.ts`.
- Bun not found: install Bun using the official installer at https://bun.sh/docs/installation.

## Remember
Use judgment, adapt the setup to repo constraints, and keep the pipeline auditable.
