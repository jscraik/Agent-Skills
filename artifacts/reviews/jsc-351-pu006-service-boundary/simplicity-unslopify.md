## Simplification Analysis

### Core Purpose
The PU-006 change extracts Skills doctor/proof/package contract logic out of `skills_impl.py` into a dedicated `ask.skills_sdk` service boundary while preserving behavior and test coverage.

### Unnecessary Complexity Found
- `low` [Infrastructure/scripts/lib/ask/commands/skills_impl.py:1088] + [Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:44]
- Runtime target normalization now happens twice (`normalize_runtime_target` in the command facade and again in the SDK service).
- Suggested simplification: normalize once in the command layer and treat service input as already normalized (or remove command-side normalization and keep only service-side).

- `low` [Infrastructure/scripts/lib/ask/skills_sdk/contracts.py:230-235]
- `doctor_sdk_layer_for` rebuilds a small `layer_maps` dict on every call.
- Suggested simplification: promote that map to a module-level constant and return a direct lookup.

- `low` [Infrastructure/tests/test_ask_skills_doctor.py:214-216] + [Infrastructure/tests/test_ask_skills_package_contract.py:248-252]
- Boundary tests rely on string-source negatives (`assertNotIn(...)`) that are fragile to harmless renames and formatting changes.
- Suggested simplification: keep one structural boundary assertion in `test_skills_sdk_boundaries.py` (AST import boundary) and reduce duplicated source-string checks in per-command tests.

### Code to Remove
- [Infrastructure/scripts/lib/ask/commands/skills_impl.py:1088] or [Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:44] - duplicate runtime-target normalization (remove one side).
- [Infrastructure/scripts/lib/ask/skills_sdk/contracts.py:230-234] - per-call temporary map literal in `doctor_sdk_layer_for`.
- [Infrastructure/tests/test_ask_skills_doctor.py:214-216] and [Infrastructure/tests/test_ask_skills_package_contract.py:248-252] - redundant brittle source-string checks already covered by dedicated boundary tests.
- Estimated LOC reduction: ~15-30 lines.

### Simplification Recommendations
1. Remove duplicated runtime-target normalization.
   - Current: both facade and service normalize `runtime_target`.
   - Proposed: single normalization boundary.
   - Impact: small LOC drop, less cognitive duplication.

2. Hoist doctor SDK layer map to module scope.
   - Current: temporary dict allocated inside `doctor_sdk_layer_for`.
   - Proposed: `DOCTOR_SDK_LAYER_MAPS` constant + one lookup.
   - Impact: simpler function body, less runtime churn, clearer intent.

3. Consolidate boundary assertions into one test surface.
   - Current: AST boundary tests + per-file source-string guards.
   - Proposed: keep AST boundary test as canonical and trim repeated string negatives.
   - Impact: less brittle test suite with same safety intent.

### YAGNI Violations
- `informational` [Infrastructure/tests/test_ask_skills_doctor.py:214-216]
- Source-level string prohibitions for specific call spellings are stronger than required by the boundary goal; they may constrain harmless refactors without increasing runtime safety.
- What to do instead: rely on import-layer boundary checks and one behavior-level assertion that command facade delegates to SDK functions.

### Final Assessment
No blocker findings.
Total potential LOC reduction: ~1-2% of touched files.
Complexity score: Low-Medium.
Recommended action: Minor tweaks only (safe simplification cleanup before commit).

WROTE: artifacts/reviews/jsc-351-pu006-service-boundary/simplicity-unslopify.md
