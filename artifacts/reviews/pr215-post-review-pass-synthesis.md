# PR 215 Post-Review Pass Synthesis

Scope: branch `codex/skills-sdk-project-manifest-doctor`, PR #215.

## Reviewer Finding Disposition

- `api-contract-reviewer`: fixed. `skill-doctor.v1` no longer requires newly added `checks.projection_ownership`; schema tests now prove legacy v1 payloads without that check remain valid.
- `adversarial-reviewer`: fixed. Runtime handle proof now validates the resolved handle target itself, rejecting poisoned handle symlinks under a workspace-root symlink while preserving canonical source symlink support.
- `agent-native-reviewer`: fixed. Doctor root ownership classification is now case-insensitive for generated runtime roots and supports owner manifests that explicitly declare project-local canonical skill sources.

## Simplify Pass

- Kept the schema fix additive instead of introducing a version churn or compatibility adapter.
- Centralized project manifest constants in `skills_impl.py` instead of repeating schema and manifest path strings.
- Preserved the existing doctor payload shape while only adding the owner-manifest branch where it changes behavior.

## Unslopify Pass

- Removed the root-symlink shortcut that allowed a broad ambient runtime condition to stand in for handle-level proof.
- Added regression tests for the actual failure classes: poisoned runtime handle, case-insensitive generated roots, manifest-declared project source, and legacy schema compatibility.
- Guarded invalid manifest root classifications by falling back to `unknown` instead of trusting arbitrary strings.

## Architecture Pass

- Source-of-truth boundary is now explicit: generated roots stay non-editable unless an owner repo manifest declares them `canonical_project_source`.
- Runtime proof now checks the command handle target, not just the runtime root, matching the SDK contract that artifacts decide readiness.
- API compatibility is protected by tests that separate optional extension payloads from required v1 contract fields.

## Validation Evidence

- `python3 -m py_compile Infrastructure/scripts/lib/ask/commands/skills_impl.py Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py` -> pass
- `python3 -m pytest Infrastructure/tests/test_runtime_proof_validation.py Infrastructure/tests/test_jsc351_codex_abi_schema_contracts.py -q` -> pass
- `python3 -m pytest Infrastructure/tests/test_ask_cli_impl.py::TestAskCLI::test_skill_root_ownership_classifies_generated_roots_case_insensitively Infrastructure/tests/test_ask_cli_impl.py::TestAskCLI::test_skills_doctor_allows_manifest_declared_project_skill_source -q` -> pass
- `python3 -m pytest Infrastructure/tests/test_ask_cli_impl.py -q --maxfail=1` -> pass
- `bash scripts/validate-codestyle.sh --fast` -> pass
- `./bin/ask skills resolve unslopify --json --robot` -> pass
- `./bin/ask skills handles --check --json --robot` -> pass
- `git diff --check` -> pass
