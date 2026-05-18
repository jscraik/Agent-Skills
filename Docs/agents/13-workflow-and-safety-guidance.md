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

## Repeated Error Protocol

Do not fight repeated errors. If the same command, validator, tool call, or
implementation attempt hits the same error twice, stop the retry loop.

Required behavior:

1. Capture the exact repeated error text and the command or action that caused
   it.
2. Research 3-5 plausible fixes. Use web research when network access is
   available and appropriate; if network is blocked, use repo-local docs,
   official cached docs, code search, and existing solution notes, and state the
   blocker.
3. Compare the options for safety, scope, validation cost, and likelihood.
4. Choose the most efficient safe option.
5. Implement the chosen fix and validate it against the original failing path.

Do not keep making local edits against the same failure without this option
search. If the most efficient option requires user approval, credentials, or
external access, report that as the blocker instead of inventing a workaround.

## Shell Scripting

When modifying shell scripts or configuration files, always use non-interactive command patterns. Avoid commands that require user input (like `op read` from 1Password) - they hang in CI/CD and headless environments.

## Git Workflow

When working with git branches, prefer to merge over rebase for complex histories (>50 commits). Always run `ask repo status` and resolve conflicts systematically before proceeding with changes.
For git operations like cherry-picking or branch syncing, prefer branch-aware merge/rebase flows that keep full-context history visible, and avoid direct low-level file restore commands.

Before commit or push, make sure generated `prek` hooks use repo-local cache
state:

```bash
bash scripts/install-prek-hooks.sh
```

This patches the generated git hook shims to set
`PREK_HOME="$REPO_ROOT/.cache/prek"`. If a hook fails with
`failed to open file ... ~/.cache/prek/prek.log`, do not retry the same push
with broader home-directory write access. Run the installer, then rerun the
normal hook-enforced commit or push path.

## Configuration Files

For YAML schema changes and configuration files, validate against the schema immediately after editing. Do not assume syntax is correct without verification.

## Code Review Fixes

When fixing CodeRabbit or automated review comments, batch related fixes by file type and verify each category (types, security, validation, linting) before moving to the next.

Review feedback is evidence, not automatically scope. Before applying a review
comment, classify whether the comment is a local defect, repeated pattern, API
design rule, architecture boundary, naming-language rule, validation gap,
test-contract gap, or documentation drift. If it expresses a transferable
principle, run a bounded pattern sweep and report similar cases as fixed,
intentionally left, or deferred with reasons. Do not apply principle-shaped
feedback only to the named line unless the sweep proves the radius is local.

For example, feedback that a function should return a named sentinel error
instead of a success/failure bool is an API design rule unless the local code
proves otherwise. Search the same API layer for equivalent bool-return failure
patterns, exclude pure predicates or compatibility-bound exported APIs, update
tests for the fixed cases, and record the durable rule or the reason it was not
retained.

When feedback or implementation work touches API shape, helper boundaries,
filesystem access, environment discovery, parsing, generated artifacts, or
ownership declarations, apply [Misuse-Resistant Interface Design](/Docs/agents/20-misuse-resistant-interface-design.md).
Prefer interfaces that carry authority, ownership, and invariants in their
shape over process rules callers must remember.

## Refactoring

When refactoring interfaces that affect multiple files, first update the interface/type definitions, then systematically update all consumers before running tests. Verify no 'conflated' concerns exist (e.g., subcommand vs. mode flags).

## Documentation

Always format markdown plan files cleanly before writing - avoid stray backticks, inconsistent heading levels, or mixed quote styles. Use `prettier --write` or equivalent for markdown files.
