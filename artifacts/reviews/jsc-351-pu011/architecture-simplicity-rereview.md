# Architecture and Simplicity Re-review (T011)

## Findings (severity-ranked)

### High - Folded compatibility aliases are now globally disabled, breaking rooted sync compatibility contract
- Evidence:
  - [Infrastructure/scripts/lifecycle-and-sync/command_surface.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py):50 defines `HIDDEN_COMPATIBILITY_COMMAND_HANDLES = set(FOLDED_SKILL_HANDLE_ALIASES) | {"he-goal-governor-archive"}`.
  - [Infrastructure/scripts/lifecycle-and-sync/command_surface.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py):179-180 skips alias generation whenever alias is in `HIDDEN_COMPATIBILITY_COMMAND_HANDLES`.
  - [Infrastructure/scripts/lifecycle-and-sync/command_surface.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/lifecycle-and-sync/command_surface.py):334 routes command-handle writes through `_with_folded_alias_handles`, so skipping there removes folded alias files from rooted projection output.
  - Existing contract test still expects generated folded handles in rooted workspace sync: [Infrastructure/tests/test_ask_skills_sync_security.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/tests/test_ask_skills_sync_security.py):437-447.
  - Repro: `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py::TestAskSkillsSyncSecurity::test_sync_skills_rooted_user_scope_allows_generated_folded_handles -q` fails with missing `he-ideate/SKILL.md`.
- Architectural impact:
  - This conflates two distinct surfaces: picker visibility vs runtime compatibility handles.
  - It introduces boundary drift by using one hidden set to govern both UI visibility and runtime file generation.
  - Result: backward-compatibility aliases disappear from runtime projection, which can break user/runtime relink flows that still rely on those handles.
- Recommendation:
  - Split concerns into two explicit sets/policies:
    - `hidden_from_picker_aliases` (surface suppression only)
    - `generate_runtime_compat_aliases` (backward compatibility files)
  - Keep folded aliases hidden from picker while still generating runtime compatibility handles where contract requires them.
  - Update/align tests to the chosen policy explicitly (if policy is intentionally changing, retire or replace the rooted compatibility test with a migration decision artifact).

## Notes
- The newly added first-level system bridge pruning tests appear well-scoped and architecture-aligned for lane ownership (bridge aliases under hidden `.system` lane).
- No additional medium/low findings beyond the high-severity compatibility regression above.

WROTE: artifacts/reviews/jsc-351-pu011/architecture-simplicity-rereview.md

