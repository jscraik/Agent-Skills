---
name: local-action-verification
description: Use when the user asks to validate GitHub Actions locally with act; output setup guidance, AGENTS.md instructions, and fail-fast checks before push or PR.
---

# Local Action Verification with act

## Philosophy
- Shift CI feedback left: run workflows locally before remote pushes.
- Keep setup explicit and reproducible across developer and agent environments.
- Favor canonical setup for unreleased/greenfield repos; only add compatibility layers when explicitly requested.

## Triggers and usage
- The user wants to run GitHub Actions locally with `act` before opening a PR.
- The repo needs agent-readable instructions for consistent CI verification behavior.

## Required inputs
- Target repository path.
- Confirmation Docker is available where checks run.
- CI workflow/job identifiers to execute with `act`.

## Expected deliverables
- Output contract schema_version: 1.0
- `scripts/act/install-act.sh` and `scripts/act/run-act.sh` in the target repo.
- `AGENTS.md` section that instructs agents to run local verification before push.
- `.gitignore` entries for `act_output.log` and `.secrets`.

## Setup steps

### Step 1: Copy scripts
Copy `scripts/` from this skill into `scripts/act/`:

```text
scripts/act/
├── install-act.sh
└── run-act.sh
```

Make scripts executable:

```bash
chmod +x scripts/act/install-act.sh scripts/act/run-act.sh
```

### Step 2: Add AGENTS.md guidance
Append a Local CI Verification section so agents know to run `scripts/act/run-act.sh` before pushing.

### Step 3: Update `.gitignore`
Add if missing:

```text
act_output.log
.secrets
```

### Step 4: Share user next steps
1. Start Docker before running verification.
2. Run `bash scripts/act/install-act.sh` once if `act` is missing.
3. Keep `.secrets` local and uncommitted.
4. Commit script + AGENTS.md updates.

## Validation
- Fail fast: stop at the first failed validation gate, fix the issue, and rerun checks.
- Confirm both scripts exist and are executable.
- Run a known workflow job with `bash scripts/act/run-act.sh "push -j <JOB_ID>"`.
- Verify logs are captured and cleaned up after successful runs.

## Constraints
- Do not commit `.secrets` or other sensitive CI material.
- Do not modify remote CI config without explicit user approval.
- Do not add backward-compatibility wrappers unless explicitly requested.

## Anti-patterns
- Skipping local verification and relying only on remote CI.
- Running `act` without Docker health checks.
- Preserving legacy behavior by default in new/unreleased repos.

## Variation and adaptation
- Increase timeout with `ACT_TIMEOUT` for slow pipelines.
- Use lightweight runner images for faster local iteration.
- Add matrix flags when reproducing job-specific CI failures.

## Examples
- "Set up local GitHub Actions verification for this repository."
- "Add act scripts and AGENTS.md instructions so Jules can run CI locally."
- "Install local verification tooling and document how to run workflow job test." 

## Troubleshooting
- Docker not running: start the Docker daemon and re-run.
- Image pull slow: use a smaller runner image where compatible.
- ARM64 issues: pass `--container-architecture linux/amd64` when needed.
- Secrets required: provide `--secret-file .secrets` and keep file uncommitted.
- Timeout/hanging: increase `ACT_TIMEOUT` and inspect `act_output.log`.

## Resource references
- [Troubleshooting Guide](resources/troubleshooting.md)
- [Contract](references/contract.yaml)
- [Evals](references/evals.yaml)

## Remember
Use this skill to reduce CI churn and tighten pre-push quality gates.
