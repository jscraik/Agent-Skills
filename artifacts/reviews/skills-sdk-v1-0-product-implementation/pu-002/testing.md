schema_version: 1
execution_mode: focused_testing_review
diff_source: git diff main..HEAD
coverage_assessment:
  - "Positive fixtures cover manifest source, check receipt, risk classification, install preview with embedded lockfile preview, and placeholder lifecycle."
  - "Negative fixtures cover dishonest pass placeholder receipt, install preview write claim, and placeholder execution claim."
  - "Existing scaffold tests are rerun with the new schema-spine tests to guard the JSC-391 baseline."
gaps:
  - "No production CLI command emits these schemas yet; PU-003 and later slices should add command-output tests when runtime facade behavior exists."
  - "The schema subset validator is intentionally limited; full JSON Schema engine coverage remains out of scope for PU-002."
validation:
  - "UV_CACHE_DIR=/private/tmp/agent-skills-uv-cache uv run --python 3.12 pytest Infrastructure/tests/test_skills_sdk_schema_spine.py Infrastructure/tests/test_skills_sdk_scaffold.py -q -> pass, 16 tests and 6 subtests"
status: pass_with_deferred_runtime_coverage
