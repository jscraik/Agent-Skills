# JSC-351 PU-004 Governor Disposition

## Slice

- Task: T013
- Plan unit: PU-004 / JSC-353
- Objective: Add SkillPackage v1 schemas and package-readiness compatibility snapshots so package metadata has a Codex-native contract and public package output has drift-proof schema identity.

## Review Stack Summary

| Review Artifact | Findings | Governor Disposition |
|---|---|---|
| artifacts/reviews/jsc-351-pu004/architecture.md | High: machine-local Codex ABI source path; Medium: ABI evidence omitted from snapshot; Low: schema openness | Fixed immediately except low schema openness, then upgraded to enforcement after maintainability/testing re-review confirmed metadata drift risk. |
| artifacts/reviews/jsc-351-pu004/testing.md | No findings; low residual risk around custom schema subset validator | Accepted as residual informational; unsupported schema keywords fail fast in the test validator. |
| artifacts/reviews/jsc-351-pu004/maintainability-docs.md | High: machine-local ABI path; Medium: schema strictness; Medium: snapshot omission; residual implementation-note absolute path | Fixed immediately. |
| artifacts/reviews/jsc-351-pu004/architecture-rereview.md | No actionable findings | Accepted. |
| artifacts/reviews/jsc-351-pu004/testing-rereview.md | Medium: metadata envelope still allowed unknown keys | Fixed immediately. |
| artifacts/reviews/jsc-351-pu004/maintainability-docs-rereview.md | Medium: metadata envelope still allowed unknown keys | Fixed immediately. |
| artifacts/reviews/jsc-351-pu004/testing-final-rereview.md | No actionable findings | Accepted. |
| artifacts/reviews/jsc-351-pu004/maintainability-docs-final-rereview.md | No actionable findings | Accepted. |

## Remediation Applied

- Replaced machine-local `codex_abi_source.path` with repo-neutral `codex-rs/core-skills/src/model.rs`.
- Centralized Codex ABI evidence fields in `skills_impl.py`.
- Added `codex_abi_source` and the full Codex metadata field set to snapshot projection and fixture.
- Tightened `skill-package.v1` root and metadata envelopes with `additionalProperties=false`.
- Tightened `skill-package-readiness.v1` top-level envelope with `additionalProperties=false` and explicit existing public payload properties.
- Added negative tests for unknown SkillPackage root keys, unknown SkillPackage metadata keys, and unknown package-readiness top-level keys.
- Updated implementation notes to remove machine-local ABI provenance wording.

## Final Validation Evidence

- `python3 -m pytest Infrastructure/tests/test_ask_skills_package_contract.py -q` -> pass, 8 tests.
- `python3 -m pytest Infrastructure/tests/test_ask_skills_package_contract.py Infrastructure/tests/test_ask_skills_package.py Infrastructure/tests/test_ask_skills_doctor.py -q` -> pass, 34 tests and 15 subtests.
- `env UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache XDG_CACHE_HOME=/private/tmp/agent-skills-xdg-cache uv run --python 3.12 --with pytest --with pyyaml python -m pytest Infrastructure/tests -q -k 'skill_package or package or doctor'` -> pass, 114 tests, 1386 deselected, and 15 subtests.
- `./bin/ask skills package skill-builder --json --robot` -> pass, exit 0 with repo-neutral ABI source and compatibility snapshot identity.
- `./bin/ask repo doctor --json --robot` -> pass, exit 0 with no blockers.

## Decision

- Status: ready_for_goal_board_receipt
- Unresolved blockers: none
- Unresolved high findings: none
- Unresolved medium findings: none
- Residual risk: low, limited to normal schema evolution and the repo-owned custom schema subset validator's deliberate fail-fast keyword support.

