# JSC-351 PU-004 Architecture Re-review

## Scope Checked
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/config/schemas/skill-package.v1.schema.json
- Infrastructure/config/schemas/skill-package-readiness.v1.schema.json
- Infrastructure/tests/test_ask_skills_package_contract.py
- Infrastructure/tests/fixtures/skill_package_snapshots/skill-package-readiness-public-output.v1.json

## Re-review Findings
no actionable findings

## Verification Notes
- The prior boundary-coupling issue is resolved:
  - `codex_abi_source.path` now uses repo-neutral provenance (`codex-rs/core-skills/src/model.rs`) via centralized ABI helpers.
  - Evidence: `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2798-2827`, `2955`, `2976`.
- Snapshot drift-proofing now covers ABI evidence and expanded metadata surface:
  - `codex_abi_source`, `dependencies`, `policy`, `scope`, and `plugin_id` are included in snapshot projection and fixture.
  - Evidence: `Infrastructure/tests/test_ask_skills_package_contract.py:143-192`; fixture entries under `skill_package_contract`.
- Contract boundary hardening is in place:
  - `skill-package.v1` and `skill-package-readiness.v1` both reject unknown top-level keys.
  - Evidence: schema roots have `additionalProperties: false`; tests assert rejection of injected unknown keys.
  - Files: `Infrastructure/config/schemas/skill-package.v1.schema.json:6`, `Infrastructure/config/schemas/skill-package-readiness.v1.schema.json:6`, `Infrastructure/tests/test_ask_skills_package_contract.py:248-327`.

## Architecture Disposition
- eval_report_status: pass
- architecture_drift: none detected in reviewed scope
- boundary_changes: acceptable and aligned with approved intent
- unresolved_type1_decisions: none
- recommended_completion_state: ready_for_closeout
- confidence: high
- residual_risk: low (normal schema evolution risk only)

WROTE: artifacts/reviews/jsc-351-pu004/architecture-rereview.md

