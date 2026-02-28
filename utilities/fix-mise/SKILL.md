---
name: fix-mise
description: Diagnose and repair mise trust/runtime failures and reconcile `~/.config/mise/config.toml` with required versions; use when commands fail due to trust blockers or stale tool config.
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
- Keep global tool configuration current by making any needed updates explicit and auditable.

## Inputs

- Error output that references mise trust/runtime issues.
- Repository or directory containing mise configuration (`mise.toml`, `.tool-versions`, etc.).
- Optional global configuration target (`$HOME/.config/mise/config.toml`).
- Optional expected tool/runtime versions.
- Evidence of scope ambiguity (e.g., conflicting project/global expectations or request scope not explicit).

## References

- `references/contract.yaml`
- `references/task-profile.json`
- `references/evals.yaml`
- Output schema version: `schema_version: "1.0"` in `references/contract.yaml`

## Examples

- Untrusted config file in a repo and trust check fails: run `mise trust <path>`, `mise doctor`, then retry.
- `~/.config/mise/config.toml` lacks a required tool/version: run `mise use -g` for that tool/version, `mise install`, then verify.
- Stale global tool entries are present (`mise outdated`): if the user requested dependency refresh, run `mise outdated` and `mise upgrade` explicitly, then re-check state.
- User asks “fix global tools” but does not specify versions: confirm required versions before running global update and log a pending-confirmation step if unknown.

## Variation

- Prefer minimal intervention first in project-local scope, then expand to global updates only when required.
- If `~/.config/mise/config.toml` is out of sync, choose the least-disruptive change path:
  - request confirmation for ambiguous edits,
  - otherwise apply scoped `mise use -g` / `mise install` updates with backups.
- If a tool is unavailable in the global backend, avoid forcing global rollback and route via a targeted install/fallback plan.

## Procedure (canonical-first)

1. Capture failure context and identify all active config scopes:
   - project/local configs (`mise.toml`, `.tool-versions`, nested configs),
   - workspace/global config (`$HOME/.config/mise/config.toml` or equivalent on this system).
2. Trust exactly the untrusted config files discovered in step 1 using `mise trust <path>`.
3. For any trust/runtime blocker tied to missing tools, reconcile versions:
   - update global config for required tools using scoped `mise use -g <tool>@<version>` (or your project-standard install flow),
   - run `mise sync` / `mise install` to install anything still missing.
4. Reconcile tool drift in scope if requested:
   - run `mise outdated` and record stale entries.
   - if stale entries are present and dependency refresh was requested/confirmed, run `mise upgrade` and re-run `mise outdated`.
5. Re-run trust/runtimes checks (`mise doctor`) and confirm all expected tools are installed (`mise list` plus `which <tool>` checks where relevant).
6. Retry the original failing command.
7. If global trust/config changes were required, verify they are persisted and safe:
   - keep a timestamped backup of `~/.config/mise/config.toml` before writing,
   - confirm file contents contain only intended tool entry updates.

## Outputs

- Root-cause summary of the mise failure.
- Remediation actions taken (trust/install/sync steps).
- Verification result showing whether the original command now succeeds.
- Global `mise.toml` update result (`path`, entries added/updated, backup location if changed).

## Constraints

- Redact secrets and sensitive data by default in diagnostics and command output.
- Avoid destructive global cleanup unless explicitly requested by the user.
- Keep fixes scoped to the relevant project/environment first.
- If global updates are needed and user intent is ambiguous, request explicit confirmation before editing `~/.config/mise/config.toml`.

## Validation

- `mise doctor` reports no blocking trust/runtime errors.
- `mise list` (or equivalent) reflects required tool availability.
- `mise outdated` is clean after any requested upgrade flow (or stale drift is logged and handled with user confirmation).
- Original failing command is retried and outcome is recorded.
- Fail fast on unresolved blockers with explicit next steps.

## Anti-patterns

- Blindly trusting broad paths without identifying the triggering config.
- Marking issue resolved without re-running the failing command.
- Mixing unrelated shell/tooling changes into the fix workflow.

## Quick Runbook

1. Identify untrusted config path.
2. Run `mise trust <path>`.
3. Run `mise doctor`.
4. Reconcile global tool entries as needed with `mise use -g` and `mise install`.
5. If dependency refresh is requested, run `mise outdated` then `mise upgrade`.
6. Confirm runtime/tool presence via `mise list` (and rerun `mise outdated` after upgrades).
7. Retry the failing command.
