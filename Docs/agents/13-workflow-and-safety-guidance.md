# Workflow and Safety Guidance

## Table of Contents

- [Testing](#testing)
- [Shell Scripting](#shell-scripting)
- [Git Workflow](#git-workflow)
- [Configuration Files](#configuration-files)
- [Code Review Fixes](#code-review-fixes)
- [Refactoring](#refactoring)
- [Documentation](#documentation)

## Testing

After fixing any code, always run the relevant test suite to verify the fix works before committing. If tests fail, debug and iterate rather than committing broken code.

When changing executable behavior, run the smallest real code path that exercises the exact production code touched before claiming the work is complete. Prefer invoking the production function, class, CLI command, shell script, validator, or route directly so the observed behavior comes from the same code users and CI will run.

If no existing test or command covers the changed path, create a temporary reproduction script under `/codex-scripts/`. Temporary reproductions are local evidence only and must remain gitignored. Use them to import or invoke the production modules/functions directly; copy only the minimum fixture data or input setup needed to trigger the behavior. Avoid copying production logic into the temporary script, because that can test the copy instead of the real implementation.

If the exact production path cannot be run because it requires unavailable credentials, external services, unsafe side effects, or generated runtime state, state the blocker clearly and run the nearest meaningful validation instead. Do not describe behavior as verified unless the touched production path actually ran.

## Shell Scripting

When modifying shell scripts or configuration files, always use non-interactive command patterns. Avoid commands that require user input (like `op read` from 1Password) - they hang in CI/CD and headless environments.

## Repeated Steering and Environment Refinement

Treat repeated user steering as operating evidence, not conversation history.
When a user has to point out the same failure class twice, stop the current
task lane and repair the mechanism that allowed the repeat before proceeding.

Use this loop:

1. Name the exact failure pattern and the command or behavior that exposed it.
2. Separate symptom from mechanism. For example, `error connecting to
api.github.com` may be a Codex sandbox network-permission issue even when it
   looks like a GitHub outage.
3. Apply the smallest durable refinement to the environment contract, docs,
   skill instructions, scripts, or validation surface.
4. Run the smallest proof that exercises the refined path.
5. Report the proof before resuming the original implementation, PR, or
   automation lane.

For Codex sandboxed network operations, retry API commands with explicit
network permission before classifying GitHub, CircleCI, Snyk, package registry,
or other external services as down. For commands that invoke `mise`, either set
`MISE_CACHE_DIR` to a writable temporary path such as
`/private/tmp/agent-skills-mise-cache` or request narrow write permission for
the cache directory. Cache write warnings are not API connectivity evidence.

Do not keep retrying the same failing command. After two equivalent failures,
change the environment, permission profile, command shape, or diagnostic path,
then record what changed.

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
