# PR #192 Governor Remediation At Head 5f20d84

## Status

STATUS: blocked_pending_push

## Runtime Truth

- PR: https://github.com/jscraik/Agent-Skills/pull/192
- Live head before local remediation: 5f20d846e7837eb05bf123f6e87ee9a9bb406ff8
- Local worktree: /private/tmp/agent-skills-jsc351-head-4d76
- PR state before local remediation: open, mergeable, converted back to draft while valid P1 review threads are being remediated.
- Subagent input artifact: artifacts/reviews/jsc-351-pr192-triage-lane/post-push-5f20d84.md

## Findings

### P1: Rooted symlink command handles could skip missing SKILL.md checks

Classification: valid.

Runtime evidence:

- Review thread: PRRT_kwDOQ6nR9s6EVjbv
- File: Infrastructure/scripts/lifecycle-and-sync/command_surface.py
- The rooted runtime-handle fast path returned the source path without verifying that the source file and runtime handle SKILL.md both existed.

Remediation:

- _runtime_handle_symlink_target now verifies the source file is present and the runtime handle directory contains SKILL.md before returning the rooted target.
- Added test_command_handle_check_rejects_rooted_symlink_with_missing_skill_file.
- Tightened test_command_handle_check_detects_missing_runtime_handle so it uses a concrete mocked handle instead of depending on ambient catalog state.

### P1: Default system bridge visibility was broader than the policy-approved bridge set

Classification: valid.

Runtime evidence:

- Review thread: PRRT_kwDOQ6nR9s6EVjbx
- File: Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py
- Default discovery treated every first-level system bridge as visible by default when hidden-path filtering allowed the bridge root.

Remediation:

- Added an explicit default-visible system bridge allowlist: imagegen and openai-docs.
- Mirrored the allowlist in verify_runtime_budget.py so budget validation and discovery agree.
- Added test_default_discovery_hides_non_default_system_bridges.
- Added test_render_index_does_not_emit_blank_line_at_eof after generator refresh exposed a trailing blank-line proof failure in SKILL.md.

### Catalog sync drift after filtering non-default bridges

Classification: valid secondary runtime discovery.

Runtime evidence:

- ./bin/ask repo doctor-catalog --json --robot initially reported default catalog count drift because README and root SKILL.md still described 27 default skills after non-default bridge filtering reduced the catalog to 25.
- sync_skills_impl.sh failed to update the README count reliably because its replacement flags were reused across independent replacement families.

Remediation:

- sync_skills_impl.sh now tracks sentence and count replacements separately.
- The script handles the current wrapped Agent Skills Kit intro, updates the visible default-skill count, and removes duplicate intro text.
- README.md and root SKILL.md were refreshed through repo-owned sync commands and now report 25 default catalog skills.

## Validation Evidence

| Command | Outcome |
| --- | --- |
| uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests/test_command_surface_handles.py Infrastructure/tests/test_skill_scope_precedence.py -q | pass: 51 tests and 11 subtests passed. |
| uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests/test_command_surface_handles.py Infrastructure/tests/test_skill_scope_precedence.py Infrastructure/tests/test_ask_skills_sync_security.py -q -k 'rooted_symlink or system_bridge or runtime_budget or command_handle or render_index' | pass: 29 tests, 62 deselected, and 6 subtests passed. |
| python3 -m py_compile Infrastructure/scripts/lifecycle-and-sync/command_surface.py Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py Infrastructure/tests/test_command_surface_handles.py Infrastructure/tests/test_skill_scope_precedence.py | pass. |
| bash -n Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh | pass. |
| ./bin/ask repo doctor-catalog --json --robot | pass after sync script repair and repo-owned catalog refresh. |
| ./bin/ask skills handles --check --check-command-handles --no-handles --json --robot | pass after repo-owned command-handle refresh. |
| ./bin/ask runtime budget --json --robot | pass. |
| ./bin/ask repo doctor --json --robot | pass. |
| python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py Docs/goals/jsc-351-agent-skills-codex-abi-conformance | pass before this receipt update. |
| git diff --check HEAD | pass after generated SKILL.md trailing blank-line repair. |

## Governor Disposition

Fix immediately. These are valid review blockers against the current PR head, and both affect deterministic conformance proof rather than optional polish.

Continuation remains blocked until:

- this remediation is committed and pushed to codex/jsc-351-abi-conformance;
- the two fixed review threads are resolved or proven stale against the new head;
- PR checks are current and green or any non-green state is classified;
- a fresh post-push subagent triage artifact is written;
- Linear state is updated to match runtime truth.

WROTE: artifacts/reviews/jsc-351-pr192-triage-lane/governor-remediation-5f20d84.md
