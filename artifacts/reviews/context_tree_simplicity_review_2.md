## Simplification Analysis

### Core Purpose
The context-budgeted skill-tree changes should add one clear projection contract (flat vs rooted), generate rooted artifacts deterministically, and enforce budget/provenance gates with minimal branching and minimal duplicated policy logic.

### Unnecessary Complexity Found

- **[HIGH] Split-brain projection behavior across entrypoints**
  - Evidence: `Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh:99` hard-fails any non-`flat` mode, while rooted writes are explicitly supported in Python sync (`Infrastructure/scripts/lib/ask/commands/skills.py:1508`, `Infrastructure/tests/test_ask_skills_sync_security.py:77`) and shell tests assert that rejection (`Infrastructure/tests/test_sync_skills_shell_projection.py:23`).
  - Why unnecessary: We now maintain two projection truths (shell says rooted is deferred; Python says rooted mutates). That increases mental load, test surface, and operator confusion.
  - Suggested simplification: choose one canonical mutation path. Either:
    1. make shell delegate to `ask skills sync --projection ...` and remove shell-only projection rejection, or
    2. keep shell as flat-only but move projection handling fully out of shell and document it as a thin flat wrapper.

- **[MEDIUM] Unreachable mutation-availability error path and extra error-code plumbing**
  - Evidence: `ProjectionModeDecision.mutation_available` is set with `canonical in {"flat", "rooted"}` (`Infrastructure/scripts/lifecycle-and-sync/projection_engine.py:113`) after deferred/invalid modes already raise (`.../projection_engine.py:93`, `.../projection_engine.py:99`). `ensure_mutation_supported` (`.../projection_engine.py:118`) therefore cannot currently raise `ERR_PROJECTION_MUTATION_UNAVAILABLE` in normal flow, yet its code is wired into envelope/CLI maps (`Infrastructure/scripts/lib/ask/envelope.py:38`, `Infrastructure/bin/ask:69`).
  - Why unnecessary: dead-state handling adds concepts/tests/error codes without current runtime value.
  - Suggested simplification: remove `mutation_available` + `ensure_mutation_supported` + `ERR_PROJECTION_MUTATION_UNAVAILABLE` until a real parsed-but-non-mutable mode exists.

- **[MEDIUM] Overstuffed sync plan schema with currently unused fields**
  - Evidence: plan includes `ambiguous_entries` and `report_path` (`Infrastructure/scripts/lib/ask/commands/skills.py:1486`, `...:1494`) but no producer/consumer updates those fields elsewhere in the changed surface.
  - Why unnecessary: this is YAGNI metadata that expands contract complexity and downstream parsing burden.
  - Suggested simplification: remove unused keys now; reintroduce only when there is a concrete consumer and test asserting semantics.

- **[LOW] Budget config contains non-enforced knobs**
  - Evidence: config defaults define `max_visible_flat_skills_in_hybrid`, `forbid_full_manifest_output`, `forbid_unrelated_skillset_load`, plus full `modules` and `workouts` sections (`Infrastructure/scripts/validation-and-linting/check_context_budget.py:28`, `...:32`, `...:33`, `...:35`, `...:39`) but validation logic never reads these keys in this file.
  - Why unnecessary: config surface suggests governance guarantees that are not enforced yet.
  - Suggested simplification: either enforce these keys immediately or remove/defer them from active config until enforcement exists.

### Code to Remove

- `Infrastructure/scripts/lifecycle-and-sync/projection_engine.py:118` and related dead mutation-availability plumbing
  - Reason: unreachable branch in current supported/deferred mode model.
- `Infrastructure/scripts/lib/ask/envelope.py:38` and `Infrastructure/bin/ask:69` (only if dead error path is removed)
  - Reason: dead error code plumbing.
- `Infrastructure/scripts/lib/ask/commands/skills.py:1486` and `...:1494`
  - Reason: unused plan contract fields.
- `Infrastructure/scripts/validation-and-linting/check_context_budget.py:28,32,33,35,39` (if enforcement is deferred)
  - Reason: non-enforced policy knobs.

Estimated LOC reduction: ~45-90 LOC (depending on whether projection duplication cleanup includes shell/Python path consolidation).

### Simplification Recommendations

1. Unify projection control-plane behavior first
   - Current: shell path rejects rooted while Python path writes rooted.
   - Proposed: single canonical projection executor with one policy surface.
   - Impact: highest clarity gain, fewer contradictory tests/docs.

2. Remove dead mutation-availability abstraction
   - Current: latent state machine for modes that do not exist yet.
   - Proposed: keep only invalid/deferred checks actually used today.
   - Impact: smaller error taxonomy and easier reasoning.

3. Trim sync plan payload to active fields
   - Current: plan contract advertises placeholders.
   - Proposed: keep writes/deletes/symlinks/violations/warnings + counts only.
   - Impact: lower output noise and less parser fragility.

4. Tighten budget config to enforced rules
   - Current: declared governance keys exceed enforcement.
   - Proposed: either enforce or drop dormant keys.
   - Impact: policy docs and runtime behavior stay aligned.

### YAGNI Violations

- Mutation-availability state in projection engine for modes not in current supported set.
- Sync plan placeholders (`ambiguous_entries`, `report_path`) without behavior.
- Context-budget policy keys declared before enforcement.

### Final Assessment
Total potential LOC reduction: 8-15% across the newly introduced projection/budget helper surface.
Complexity score: Medium
Recommended action: Proceed with simplifications

WROTE: artifacts/reviews/context_tree_simplicity_review_2.md
