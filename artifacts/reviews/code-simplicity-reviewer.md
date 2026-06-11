## Simplification Analysis

### Core Purpose
Keep rooted skill sync and command-surface projection based on canonical skill sources, while only preserving generated `$` handle files if legacy compatibility is explicitly enabled.

### Unnecessary Complexity Found
- [High] `Infrastructure/scripts/lifecycle-and-sync/command_surface.py:208-346` hardcodes the generated-handle path to inert behavior by returning `False` from `requires_generated_command_handle()`, empty rows from `_command_handle_write_rows()`, and an empty set from `generated_command_handle_names()`.
- Why it's unnecessary: the code still carries a compatibility surface and documentation for generated handle files, but the implementation can never produce them.
- Suggested simplification: either restore a tiny env-gated predicate for the legacy path or remove the compatibility wording and helper surface entirely.
- [Medium] `Infrastructure/scripts/lifecycle-and-sync/projection_integrity_impl.py:37-46,670-688,1018-1087` adds `plugin_cache_package` as a special-case flag and then forks both sync and verify behavior through package-specific transforms.
- Why it's unnecessary: only three mirrors need this packaging rule, so embedding it in the generic projection model broadens the abstraction for a narrow case.
- Suggested simplification: keep the generic mirror model and move the cache-package normalization into a dedicated helper or the three cache call sites.

### Code to Remove
- `Infrastructure/scripts/lifecycle-and-sync/command_surface.py:208-346` - legacy generated-handle plumbing is now dead under the current always-false predicate. Estimated LOC reduction: 40-60.
- `Infrastructure/bin/ask:127-133,569-586` - the CLI already dropped the write/check flags for generated handles, which is consistent only if the legacy path is truly retired.
- Estimated LOC reduction: 2-4% if the compatibility layer is fully removed instead of half-retained.

### Simplification Recommendations
1. Make the legacy handle mode explicit or delete it.
   - Current: the code still advertises generated-handle compatibility, but the implementation path cannot emit those files.
   - Proposed: restore a single env-gated predicate if the opt-in mode matters, or remove the helper surface and compatibility wording.
   - Impact: removes the dead branch and makes the contract honest.
2. Keep plugin-cache normalization out of the generic mirror model.
   - Current: `MirrorProjection` now carries a `plugin_cache_package` boolean that splits sync and verify behavior.
   - Proposed: factor the package-copy transform into a helper and call it only for the three plugin-cache mirrors.
   - Impact: smaller abstraction surface, easier to read and test.

### YAGNI Violations
- The generated-handle helpers remain in the command-surface module even though the implementation can no longer produce those files.
- The `plugin_cache_package` flag adds a narrow special case to a general projection type.
- The CLI and projection code no longer expose generated-handle write/check switches, so any surviving compatibility prose now needs to match that reduced surface exactly.

### Final Assessment
Total potential LOC reduction: ~5-8% of the touched command-surface/projection plumbing if the legacy handle path is removed completely.
Complexity score: Medium
Recommended action: Minor tweaks only if legacy wrappers must survive; otherwise delete the compatibility path and update the contract to match.

### Accountability Receipt
- status: review_complete
- artifact_paths:
  - /Users/jamiecraik/dev/agent-skills/artifacts/reviews/code-simplicity-reviewer.md
  - /Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/code-simplicity-reviewer-20260607T220000Z/manifest.json
- manifest_path: /Users/jamiecraik/dev/agent-skills/artifacts/agent-runs/code-simplicity-reviewer-20260607T220000Z/manifest.json
- findings:
  - severity: high
    file: Infrastructure/scripts/lifecycle-and-sync/command_surface.py:208-346
    impacted_behavior: The legacy generated-handle compatibility mode can no longer emit any files, even when explicitly enabled, so the contract is misleading and the opt-in path is inert.
    remediation: Reintroduce a single env-gated predicate or delete the compatibility surface entirely.
    confidence: high
    validation_ownership: introduced_by_current_patch
  - severity: medium
    file: Infrastructure/scripts/lifecycle-and-sync/projection_integrity_impl.py:37-46,670-688,1018-1087
    impacted_behavior: Plugin-cache package sync/verify now forks the generic mirror model for a narrow special case.
    remediation: Move the package-copy normalization into a dedicated helper or three explicit call sites.
    confidence: medium
    validation_ownership: introduced_by_current_patch
- failures_or_blockers:
  - `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -vv -x` failed at `test_sync_skills_rooted_non_dry_run_writes_generated_surface`; the assertion expected `.agents/skills/he-heartbeat/SKILL.md` to exist under `ASK_ENABLE_COMMAND_HANDLE_FILES=1`, but it did not.
- improvement_opportunities:
  - Make the legacy handle mode explicit or delete it.
  - Keep plugin-cache normalization out of the generic projection model.
- strengths:
  - The patch successfully removed the generated-handle CLI switches from `Infrastructure/bin/ask`.
  - The plugin-cache regression tests added for the new package transform are focused and readable.
- validation_evidence:
  - `python3 -m pytest Infrastructure/tests/test_local_plugin_picker_surface.py -q` -> pass
  - `ASK_ENABLE_COMMAND_HANDLE_FILES=1 python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py::TestAskSkillsSyncSecurity::test_sync_skills_rooted_non_dry_run_writes_generated_surface -q` -> fail
  - `python3 -m pytest Infrastructure/tests/test_ask_skills_sync_security.py -vv -x` -> failed at `test_sync_skills_rooted_non_dry_run_writes_generated_surface`
- next_action: Decide whether the repo should keep a real legacy generated-handle compatibility mode; if yes, restore the minimal env-gated write predicate, otherwise remove the remaining compatibility wording and helper surface.

WROTE: /Users/jamiecraik/dev/agent-skills/artifacts/reviews/code-simplicity-reviewer.md
