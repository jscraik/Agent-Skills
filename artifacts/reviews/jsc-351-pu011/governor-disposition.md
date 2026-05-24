# T011 Governor Disposition

## Slice

T011 remediates live repo-doctor blockers by:

- pruning stale first-level system bridge aliases during rooted sync;
- keeping system bridge handles out of first-level generated command handles;
- preserving folded compatibility command handles required by rooted sync;
- regenerating command-surface and runtime projection artifacts through repo-owned sync commands.

## Review Coverage

- `architecture.md`: no actionable findings.
- `simplicity-unslopify.md`: low finding on duplicated folded-alias hidden policy.
- `architecture-simplicity-rereview.md`: high finding after the first simplification attempt disabled folded compatibility aliases.
- `docs-language.md`: no actionable findings; low residual that Local Memory CLI evidence was blocked by sandbox pid-file write denial.
- `final-architecture.md`: no actionable findings after folded compatibility restoration.
- `final-testing.md`: no actionable findings after test remediation and artifact recovery.

## Findings And Decisions

| Severity | Finding | Decision | Evidence |
|---|---|---|---|
| medium | Testing review found rooted symlink skip assertions only checked count. | Fixed immediately. | `Infrastructure/tests/test_command_surface_handles.py` now asserts exact skipped rows for write and check paths. |
| low | Testing review found file-shaped bridge alias pruning was untested. | Fixed immediately. | `Infrastructure/tests/test_ask_skills_sync_security.py` now covers stale first-level bridge symlink, directory, and regular file cases. |
| low | Simplicity review suggested reducing folded-alias hidden policy duplication. | Attempted, then reverted to compatibility-preserving explicit policy after re-review. | `architecture-simplicity-rereview.md` found the derived hidden set broke `test_sync_skills_rooted_user_scope_allows_generated_folded_handles`; final code restores folded compatibility handles while keeping bridge handles suppressed. |
| high | Architecture re-review found folded compatibility aliases were globally disabled. | Fixed immediately. | `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py::TestAskSkillsSyncSecurity::test_sync_skills_rooted_user_scope_allows_generated_folded_handles -q` passes after the fix. |
| low | Testing re-review requested negative symlink target coverage. | Fixed immediately. | `Infrastructure/tests/test_command_surface_handles.py` now covers wrong in-repo symlink target and out-of-repo symlink target. |
| low | Docs/language review noted Local Memory CLI was blocked by sandbox pid-file write denial. | Accepted as environment-only residual for this slice. | Review used repo evidence, implementation notes, board state, and validation commands; this does not block T011 runtime proof. |

## Final Validation

| Command | Result |
|---|---|
| `python3 -m pytest Infrastructure/tests/test_command_surface_handles.py -q` | pass, 37 passed and 11 subtests passed |
| `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py::TestAskSkillsSyncSecurity::test_sync_skills_rooted_user_scope_allows_generated_folded_handles Infrastructure/tests/test_ask_skills_sync_security.py::TestAskSkillsSyncSecurity::test_sync_skills_rooted_prunes_first_level_system_bridge_aliases Infrastructure/tests/test_ask_skills_sync_security.py::TestAskSkillsSyncSecurity::test_sync_skills_rooted_prunes_first_level_system_bridge_directories Infrastructure/tests/test_ask_skills_sync_security.py::TestAskSkillsSyncSecurity::test_sync_skills_rooted_prunes_first_level_system_bridge_files -q` | pass, 4 passed |
| `./bin/ask runtime budget --json --robot` | pass, `budget_status=pass`, no violations, no first-level bridge skills |
| `./bin/ask skills handles --check --check-command-handles --no-handles --json --robot` | pass, command-surface projection pass, generated command handles pass, `command_handle_count=103`, `checked_count=206`, no violations |
| `./bin/ask repo doctor --json --robot` | pass, `blocking=false`, no blockers |
| `python3 Skills/agent-ops/goal-governor/scripts/check_goal_board.py docs/goals/jsc-351-agent-skills-codex-abi-conformance` | pass |

## Decision

T011 has no unresolved blocker, high, or medium findings. The slice is safe to close after receipt and tracker/triage updates.
