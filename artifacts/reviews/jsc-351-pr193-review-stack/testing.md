# Testing Review — JSC-351 PR #193

## Findings (severity-ranked)

### medium — Behavioral README rewrite logic changed without targeted regression tests
- Evidence:
  - [Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh:1192) adds new fallback/normalization branches for README sentence replacement, duplicate-collapse, and default-catalog count rewrite through multiple new regex paths.
  - [Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/scripts/lifecycle-and-sync/sync_skills_impl.sh:1253) introduces duplicate sentence collapse logic that can mutate README text shape.
  - Existing shell projection tests only assert high-level shell delegation and selected static script strings (no execution/assertions for these README transformation branches): [Infrastructure/tests/test_sync_skills_shell_projection.py](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/tests/test_sync_skills_shell_projection.py:29).
- Risk:
  - A future README format drift can silently bypass or over-apply one of these regex branches, causing duplicated text or stale catalog sentences without a failing test.
- Suggested remediation:
  - Add focused tests that execute the embedded README rewrite logic against fixture variants (single-line sentence, wrapped multiline sentence, duplicate sentence case, legacy sentence case) and assert exact normalized output.

## Coverage strengths observed
- New rooted-symlink guard in command-handle validation is exercised for happy path and missing-runtime-SKILL failure path: [Infrastructure/tests/test_command_surface_handles.py](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/tests/test_command_surface_handles.py:361), [Infrastructure/tests/test_command_surface_handles.py](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/tests/test_command_surface_handles.py:407).
- New default system-bridge visibility policy is covered in discovery and runtime-budget paths: [Infrastructure/tests/test_skill_scope_precedence.py](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/tests/test_skill_scope_precedence.py:134), [Infrastructure/tests/test_skill_scope_precedence.py](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/tests/test_skill_scope_precedence.py:145).
- Rendered catalog EOF formatting change is explicitly asserted: [Infrastructure/tests/test_skill_scope_precedence.py](/private/tmp/agent-skills-jsc351-pr193-rebuild/Infrastructure/tests/test_skill_scope_precedence.py:113).

## Validation evidence
- `python3 -m pytest Infrastructure/tests/test_command_surface_handles.py Infrastructure/tests/test_skill_scope_precedence.py Infrastructure/tests/test_sync_skills_shell_projection.py -q`
- Result: `60 passed, 11 subtests passed`.

## Residual risks
- README rewrite remains regex- and formatting-sensitive with no fixture-backed output tests for the newly added rewrite branches.

WROTE: artifacts/reviews/jsc-351-pr193-review-stack/testing.md
