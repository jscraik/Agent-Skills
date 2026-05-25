# Unslopify Maintainability Review - PU-006

## Findings (severity-ranked)

No blocking maintainability findings in the reviewed delta.

## Residual Risks

1. **Low - Stringly-typed shared context creates fragile cross-helper coupling**
   - Evidence: `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:67`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:104`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:127`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:140`
   - Why it matters: runtime evidence flows through many helpers using a generic `dict[str, Any]` context with repeated string-key lookups. This is workable now, but it increases change risk because key renames/additions can fail late and non-locally.
   - Remediation: introduce a small typed carrier (e.g., `@dataclass` or `TypedDict`) for evidence context and pass that object through helpers.

2. **Low - Duplicated runtime-card validator subprocess blocks in tests**
   - Evidence: `Infrastructure/tests/test_command_surface_handles.py:771`, `Infrastructure/tests/test_command_surface_handles.py:833`
   - Why it matters: the two tests duplicate the same subprocess invocation structure. Repeated command assembly tends to drift over time when validator args evolve.
   - Remediation: extract a local test helper (e.g., `_validate_runtime_card(card_path, repo_root)`) to centralize command shape and assertion behavior.

## Validation Ownership Classification

- None required; no reviewer-reported gate failures in this pass.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-006/unslopify-reviewer.md
