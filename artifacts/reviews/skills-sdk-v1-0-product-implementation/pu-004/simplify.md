# PU-004 Simplify Review

Status: pass_after_cleanup

Scope reviewed: risk classifier, doctor emission, schema updates, fixtures, tests, goal receipts, and implementation notes for PU-004.

Finding fixed: The first implementation repeated manifest-source sensor metadata across each source-kind profile. That made every risk tier noisier than needed and increased the chance that future profile edits would drift. Remediation: introduced `_sensor(...)` and `MANIFEST_SOURCE_SENSOR` in `Infrastructure/scripts/lib/ask/skills_sdk/risk.py` so shared metadata is defined once and source-kind profiles only carry their tier-specific sensors.

Result: No remaining simplification finding. The classifier stays as a small deterministic module, and no new abstraction layer was added around command dispatch.

Validation: `uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_risk_classifier.py Infrastructure/tests/test_skills_sdk_schema_spine.py Infrastructure/tests/test_ask_skills_doctor.py -q` passed with 33 tests and 21 subtests.
