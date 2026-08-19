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

## Repeated Steering and Environment Refinement

Treat repeated user steering as operating evidence, not conversation history.
Select this system-improvement route only when Jamie asks for it, a
consequential boundary is involved, a failure recurs across three independent
tasks, two named active consumers need a contract that no existing surface can
provide, or executable contracts contradict one another. Routine work does not
stop solely because a failure or correction repeats.

When the route is selected, stop before another unchanged retry and use this loop:

1. Name the exact failure pattern and the command or behavior that exposed it.
2. Separate symptom from mechanism. For example, `error connecting to
api.github.com` may be a Codex sandbox network-permission issue even when it
   looks like a GitHub outage.
3. Apply the smallest durable refinement to the environment contract, docs,
   skill instructions, scripts, or validation surface.
4. Run the smallest proof that exercises the refined path.
5. Record the selected route in `.harness/quality/steering-uptake.md` and run
   `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
   A failed validator keeps the selected route blocked.
6. Report the proof before resuming the original implementation, PR, or
   automation lane.

For Codex sandboxed network operations, retry API commands with explicit
network permission before classifying GitHub, CircleCI, Snyk, package registry,
or other external services as down. Before launching commands that invoke `gh`,
`mise`, `uv`, or npm, set `XDG_CACHE_HOME`, `XDG_STATE_HOME`,
`MISE_CACHE_DIR`, `MISE_STATE_DIR`, and `UV_CACHE_DIR` to sandbox-approved
writable paths. For a repository `mise` config, set
`MISE_TRUSTED_CONFIG_PATHS` to the root configuration file
`$(git rev-parse --show-toplevel)/.mise.toml`, not the current subdirectory or
the entire repository directory. Set `npm_config_cache` only when npm is
in scope. Retain the operator-authenticated `gh` configuration; set
`GH_CONFIG_DIR` only when an explicitly supplied configuration is already
authenticated. Cache or state write warnings are not API connectivity evidence.

Do not keep retrying the same failing command. After two equivalent failures,
change the environment, permission profile, command shape, or diagnostic path,
then record what changed.

## Git Workflow

When working with git branches, prefer to merge over rebase for complex histories (>50 commits). Always run `ask repo status` and resolve conflicts systematically before proceeding with changes.
For git operations like cherry-picking or branch syncing, prefer branch-aware merge/rebase flows that keep full-context history visible, and avoid direct low-level file restore commands.

Before committing or pushing, make sure generated `prek` hooks use a writable
temporary cache and that Git metadata is healthy:

```bash
bash Infrastructure/scripts/install-prek-hooks.sh
repo_root="$(git rev-parse --show-toplevel)"
preflight="$repo_root/Infrastructure/scripts/validation-and-linting/git_metadata_preflight.py"
python3 "$preflight" --repo-root "$repo_root" --json
```

The installer patches generated git hook shims to set `PREK_HOME` below
`CODEX_HOOK_CACHE_ROOT` (a writable temporary directory by default). If a hook
fails with `failed to open file ... ~/.cache/prek/prek.log`, do not retry the
same push with broader home-directory write access. Run the installer, run the
metadata preflight, and then rerun the normal hook-enforced commit or push
path. A stale lock is only a candidate: prove no owner and perform any
cleanup explicitly; the preflight never removes locks or worktrees.

### Worktree Removal And Runtime Links

Before removing or pruning a worktree, check whether any user-level runtime
links, plugin marketplaces, generated projections, active config paths, or
tooling state point into that worktree. A worktree can be obsolete as a git
branch while still serving a live runtime surface.

At minimum, inspect these links before deletion when working in this repository:

```bash
ls -ld ~/.agents/skills ~/.codex/skills ~/.agents/plugins ~/.codex/plugins 2>/dev/null || true
find -L ~/.agents/skills -maxdepth 3 -name SKILL.md | sed -n '1,20p'
find -L ~/.codex/skills -maxdepth 3 -name SKILL.md | sed -n '1,20p'
```

If a runtime link points at the worktree being removed, repoint it to the active
workspace projection or run the owning sync command before deleting the
worktree. After deletion, verify the visible runtime surface, not just git
state:

```bash
./bin/ask skills sync --scope workspace --json --robot
./bin/ask skills load-preview --json --robot
./bin/ask skills proof unslopify --runtime-target codex --json --robot
```

Do not report worktree cleanup as complete when it leaves dangling user runtime
links or makes skills disappear from the modeled Codex loader roots.

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

## Repeated Steering and Environment Refinement

The selected-route criteria and refinement loop above govern repeated steering.
Repeated feedback, review findings, approval failures, and live-state mismatches
do not stop routine work by themselves. After two equivalent failures of the
same command, change the command, environment, permission profile, or
diagnostic path before retrying, then record the changed evidence.

For sandboxed Codex runs, live PR and CI operations are networked operations.
Run GitHub, CodeRabbit, CircleCI, Snyk, package-registry, and external API
commands with explicit network permission before diagnosing an outage,
credential issue, or platform regression. If the command may invoke `gh`,
`mise`, `uv`, or npm, apply the sandbox-state environment contract above before
the shell starts. `GH_CONFIG_DIR` selects GitHub CLI configuration, not
`XDG_STATE_HOME`; do not point it at an empty scratch directory. Set it only
when the operation is given an explicitly supplied, authenticated configuration.
Before invoking a tool, verify each resolved cache or state path is inside the
approved scratch directory and writable. Treat `MISE_TRUSTED_CONFIG_PATHS` as
a separate trust control: set it to the explicitly approved root
`$(git rev-parse --show-toplevel)/.mise.toml` file, never to writable state,
a current subdirectory, or the entire repository directory.

After two equivalent failures, change the environment, permission request,
command shape, or repo contract before trying again. Do not keep rotating
through the same failing command and call that progress.
