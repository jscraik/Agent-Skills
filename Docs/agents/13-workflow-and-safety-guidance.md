# Workflow and Safety Guidance

## Table of Contents

- [Testing](#testing)
- [Shell Scripting](#shell-scripting)
- [Git Workflow](#git-workflow)
- [Configuration Files](#configuration-files)
- [Code Review Fixes](#code-review-fixes)
- [Refactoring](#refactoring)
- [Documentation](#documentation)
- [Repeated Steering and Environment Refinement](#repeated-steering-and-environment-refinement)

## Testing

After fixing any code, always run the relevant test suite to verify the fix works before committing. If tests fail, debug and iterate rather than committing broken code.

When changing executable behavior, run the smallest real code path that exercises the exact production code touched before claiming the work is complete. Prefer invoking the production function, class, CLI command, shell script, validator, or route directly so the observed behavior comes from the same code users and CI will run.

If no existing test or command covers the changed path, create a temporary reproduction script under `/codex-scripts/`. Temporary reproductions are local evidence only and must remain gitignored. Use them to import or invoke the production modules/functions directly; copy only the minimum fixture data or input setup needed to trigger the behavior. Avoid copying production logic into the temporary script, because that can test the copy instead of the real implementation.

If the exact production path cannot be run because it requires unavailable credentials, external services, unsafe side effects, or generated runtime state, state the blocker clearly and run the nearest meaningful validation instead. Do not describe behavior as verified unless the touched production path actually ran.

## Shell Scripting

When modifying shell scripts or configuration files, always use non-interactive command patterns. Avoid commands that require user input (like `op read` from 1Password) - they hang in CI/CD and headless environments.

## Git Workflow

When working with git branches, prefer to merge over rebase for complex histories (>50 commits). Always run `ask repo status` and resolve conflicts systematically before proceeding with changes.
For git operations like cherry-picking or branch syncing, prefer branch-aware merge/rebase flows that keep full-context history visible, and avoid direct low-level file restore commands.

## Configuration Files

For YAML schema changes and configuration files, validate against the schema immediately after editing. Do not assume syntax is correct without verification.

## Code Review Fixes

When fixing CodeRabbit or automated review comments, batch related fixes by file type and verify each category (types, security, validation, linting) before moving to the next.

## Refactoring

When refactoring interfaces that affect multiple files, first update the interface/type definitions, then systematically update all consumers before running tests. Verify no 'conflated' concerns exist (e.g., subcommand vs. mode flags).

## Documentation

Always format markdown plan files cleanly before writing - avoid stray backticks, inconsistent heading levels, or mixed quote styles. Use `prettier --write` or equivalent for markdown files.

## Repeated Steering and Environment Refinement

Jamie steering is operational evidence. When a user correction, review finding,
approval failure, command failure, or live-state mismatch repeats in the same
work lane, stop the lane before another retry and run this refinement loop:

1. Name the repeated failure pattern in concrete terms.
2. Separate the visible symptom from the mechanism that allowed it.
3. Apply a durable refinement in the closest canonical surface: skill guidance,
   AGENTS guidance, solution docs, wrappers, validation scripts, or repo memory.
4. Validate the refinement with the smallest command that proves the corrected
   behavior.
5. Report the proof, then resume the original work.

For sandboxed Codex runs, live PR and CI operations are networked operations.
Run GitHub, CodeRabbit, CircleCI, Snyk, package-registry, and external API
commands with explicit network permission before diagnosing an outage,
credential issue, or platform regression. If the command may invoke `gh`,
`mise`, or `uv`, set `XDG_CACHE_HOME`, `XDG_STATE_HOME`,
`MISE_CACHE_DIR`, and `UV_CACHE_DIR` to sandbox-approved writable directories
before treating cache or state warnings as failures.

After two equivalent failures, change the environment, permission request,
command shape, or repo contract before trying again. Do not keep rotating
through the same failing command and call that progress.
