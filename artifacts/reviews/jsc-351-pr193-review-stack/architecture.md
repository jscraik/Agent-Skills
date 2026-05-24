# Architecture Review — JSC-351 PR193

## Findings (severity-ranked)

### medium — Duplicated policy constant introduces cross-surface drift risk
- Evidence:
  - `Infrastructure/scripts/lifecycle-and-sync/skill_discovery.py:39` defines `DEFAULT_VISIBLE_SYSTEM_BRIDGE_SKILL_NAMES = {"imagegen", "openai-docs"}`.
  - `Infrastructure/scripts/validation-and-linting/verify_runtime_budget.py:44` defines `DEFAULT_VISIBLE_BRIDGE_SKILLS = {"imagegen", "openai-docs"}`.
  - Both modules separately gate default visibility (`skill_discovery.py:264-268`, `verify_runtime_budget.py:259, 355`).
- Architectural impact:
  - This creates a second policy axis outside the canonical discovery-policy constants (`POLICY_* / SYSTEM_BRIDGE_SKILL_NAMES`), which weakens control-plane coherence.
  - Future changes to bridge defaults can silently diverge between runtime discovery and budget validation, producing false pass/fail outcomes and avoidable governance drift.
- Recommendation:
  - Promote default-visible bridge names to a single policy source (for example in `skill_discovery_policy.py`) and import it in both modules.
  - Keep tests but assert they consume the shared constant rather than duplicated literals.

## Additional assessment (no issue found)
- Rooted handle integrity hardening in `Infrastructure/scripts/lifecycle-and-sync/command_surface.py:431-439` is architecture-positive: it strengthens generated/runtime separation by requiring both canonical source file and runtime `SKILL.md` presence before treating rooted symlink handles as valid.
- Added tests in `Infrastructure/tests/test_command_surface_handles.py` and `Infrastructure/tests/test_skill_scope_precedence.py` improve contract safety around symlink legitimacy and default visibility behavior.
- Documentation/runtime projection updates (`README.md`, `SKILL.md`, runtime-separation receipts) appear aligned with the implementation intent.

## Residual risk
- If bridge-default membership changes again without centralization, the duplicated-literal pattern may reintroduce mismatched catalog surfaces despite test coverage.

WROTE: artifacts/reviews/jsc-351-pr193-review-stack/architecture.md
