---
name: fix-mise
description: Diagnose and repair mise trust/runtime failures and reconcile `~/.config/mise/config.toml` with required versions; use when commands fail due to trust blockers or stale tool config.
---

# Fix Mise

Diagnose and repair `mise` trust, runtime, and version-drift failures with the smallest safe change set.

## Standards snapshot (March 2026)
- Diagnose the actual trust or runtime blocker before changing config.
- Prefer project-local fixes first and global config edits only when required.
- Treat `mise doctor`, `mise list`, and retrying the failing command as mandatory verification.
- Keep any global config change explicit, backed up, and easy to audit.

## When to use
- Commands fail because of untrusted `mise` config.
- Required runtimes are missing or stale.
- `~/.config/mise/config.toml` or project `mise` files are out of sync with expected tool versions.

## When not to use
- The failure is unrelated to `mise`.
- The user wants a broad toolchain upgrade with no actual `mise` blocker.
- The issue is generic shell configuration with no `mise` trust or runtime involvement.

## Required inputs
- The failing command or error output.
- The repo or directory containing `mise` configuration.
- Optional expected tool versions or target global config.

## Deliverables
- Root-cause summary of the `mise` failure.
- The exact remediation path taken or recommended.
- Verification evidence showing whether the original command now works.
- If global config changed, the path and backup details.

## Philosophy
- Small, proven `mise` fixes beat broad shell surgery.
- Trust only the config that is actually in scope.
- A repair is not complete until the original command is retried.

## Constraints
- Redact secrets and sensitive environment details by default.
- Avoid destructive global cleanup unless the user explicitly asks for it.
- Request confirmation before ambiguous edits to `~/.config/mise/config.toml`.

## Workflow
1. Capture the failing command and identify the active `mise` config scopes.
2. Trust the specific config files causing the blocker.
3. Reconcile missing tools or stale versions with the smallest scoped change.
4. Run `mise doctor`, `mise list`, and other relevant checks.
5. Retry the original failing command.
6. If global config changed, confirm only the intended entries were updated.

## Tooling and references
- Prefer:
  - `mise doctor`
  - `mise list`
  - `mise trust <path>`
  - `mise use -g <tool>@<version>`
  - `mise install`
  - `mise outdated`
  - `mise upgrade`
- Reference files:
  - `references/contract.yaml`
  - `references/evals.yaml`
  - `references/task-profile.json`

## Validation
- Verify `mise doctor` reports no blocking trust or runtime failures.
- Verify required tools appear in `mise list`.
- Verify the original failing command was retried and its outcome recorded.
- Fail fast at the first unresolved blocker.

## Anti-patterns
- Trusting broad paths without identifying the triggering config.
- Declaring success without retrying the failing command.
- Mixing unrelated shell or package-manager changes into the fix.

## Examples
- Fix this untrusted `mise.toml` so the command can run again.
- Reconcile my global `mise` config with the required tool version.
- Diagnose why `mise` says the runtime is missing even though the repo has config.

## See Also

| Skill | When to use together |
|---|---|
| [[bootstrap]] | Fix mise before retrying the bootstrap |
| [[codex-home-audit]] | Address mise issues found during a home directory audit |
| [[verification-before-completion]] | Confirm mise is healthy after the fix |
| [[systematic-debugging]] | Debug root cause of mis trust or shim failures |
| [[process-watch]] | Watch process health while diagnosing mise shim issues |

**Topic map:** [[backend-platform]]

## Remember
If the original command was not retried, the `mise` fix is still only a theory.
