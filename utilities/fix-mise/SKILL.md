---
name: fix-mise
description: Diagnose and resolve mise trust/setup failures for local toolchains. Use when the user reports mise trust errors, missing runtimes, or broken mise-managed commands.
knowledge_graph_profile: references/task-profile.json
---

# Fix Mise Trust Errors

Systematically resolve mise trust and runtime availability issues.

## When to Use

Use this skill when commands fail due to untrusted mise config, missing mise-managed tools, or environment activation problems.

## Philosophy

- Identify root cause before applying broad fixes.
- Prefer smallest safe remediation that restores expected tooling.
- Leave the environment easier to verify after repair.

## Inputs

- Error output that references mise trust/runtime issues.
- Repository or directory containing mise configuration (`mise.toml`, `.tool-versions`, etc.).
- Optional expected tool/runtime versions.

## Procedure

1. Locate the active mise config scope causing the failure.
2. Run targeted trust commands (`mise trust <path>`) for untrusted configs.
3. Verify mise health (`mise doctor`) and inspect active tool state.
4. Install/sync missing tools as needed.
5. Re-run the originally failing command to confirm recovery.
6. For update-safe maintenance, run `mise upgrade --dry-run` first and only apply upgrades if review passes.

## Outputs

- Root-cause summary of the mise failure.
- Remediation actions taken (trust/install/sync steps).
- Verification result showing whether the original command now succeeds.

## Constraints

- Redact secrets and sensitive data by default in diagnostics and command output.
- Avoid destructive global cleanup unless explicitly requested by the user.
- Keep fixes scoped to the relevant project/environment first.

## Validation

- `mise doctor` reports no blocking trust/runtime errors.
- `mise list` (or equivalent) reflects required tool availability.
- Original failing command is retried and outcome is recorded.
- Fail fast on unresolved blockers with explicit next steps.

## Anti-patterns

- Blindly trusting broad paths without identifying the triggering config.
- Marking issue resolved without re-running the failing command.
- Mixing unrelated shell/tooling changes into the fix workflow.

## Quick Runbook

1. Identify untrusted config path.
2. Run `mise trust <path>`.
3. Run `mise upgrade --dry-run` (optional, pre-change).
4. Run `mise doctor`.
5. Confirm runtime/tool presence via `mise list`.
6. Run `mise upgrade` only if dry-run looks good.
7. Retry the failing command.
