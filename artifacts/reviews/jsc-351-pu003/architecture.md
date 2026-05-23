# Architecture Review — JSC-351 PU-003

## Findings (Severity-ranked)

### Informational
- No actionable architectural violations found in PU-003 scope.

## Architecture Overview
PU-003 is scoped to deterministic doctor contract shape and machine-readable runtime failure payloads for skills proof / skills doctor, without introducing new services, ownership shifts, or runtime projection mutations. The touched surfaces remain inside the existing CLI-to-command implementation boundary:
- Infrastructure/bin/ask keeps argument plumbing and dispatch.
- Infrastructure/scripts/lib/ask/commands/skills_impl.py owns validation semantics and structured payload formation.
- Infrastructure/config/schemas/skill-doctor.v1.schema.json remains the canonical doctor payload contract.
- Infrastructure/tests/test_ask_skills_doctor.py verifies both schema and behavior at command-contract level.

## Change Assessment
- Parser ownership was intentionally shifted from argparse choices to handler validation for --runtime-target, enabling a stable runtime failure payload on invalid values (Infrastructure/bin/ask:137, Infrastructure/scripts/lib/ask/commands/skills_impl.py:1114-1137).
- skills_proof now emits runtime_failure consistently for both invalid runtime-target and gate-failure paths, preserving deterministic machine-readable fields (Infrastructure/scripts/lib/ask/commands/skills_impl.py:1118-1128, 1270-1292, 2577-2596).
- Doctor runtime-reachability check now preserves proof-level runtime failure metadata (runtime_failure, error_code, failed_check_id, path, recovery_guidance) and threads codex-targeted proof when parity is requested (Infrastructure/scripts/lib/ask/commands/skills_impl.py:3353-3376).
- next_command remains preserved while new next_command_decision adds explicit precedence rationale (Infrastructure/scripts/lib/ask/commands/skills_impl.py:2599-2714, 3497-3507, 3558-3559).
- Schema was updated to require next_command_decision, with tests asserting deterministic compatibility against repo-owned schema (Infrastructure/config/schemas/skill-doctor.v1.schema.json:7-27, 299-327; Infrastructure/tests/test_ask_skills_doctor.py:182-191, 649-672).

## Compliance Check
- Boundary integrity: upheld. No new cross-module layering violations; CLI remains thin and command module remains policy owner.
- Coupling/cohesion: improved. Runtime-failure construction centralized in _runtime_failure_payload instead of ad hoc envelope-only branching.
- Contract stability: additive at payload-content level, explicit at schema level. next_command remains available, with next_command_decision required for deterministic downstream consumption.
- Circular dependency risk: none introduced in touched imports/functions.
- Scope compliance (PU-003): upheld. No package-schema expansion, preview-command surface, or service extraction observed.

## Risk Analysis
- Residual risk (low): consumers that validate against older snapshots of skill-doctor.v1 but do not tolerate newly required next_command_decision may need synchronized schema adoption. Within this repo, deterministic tests indicate alignment.
- Residual risk (low): next_command_decision allows additionalProperties: true, which preserves extensibility but permits non-canonical extra keys; current tests cover required core fields.

## Recommendations
1. Keep next_command and next_command_decision dual-output until downstream consumers prove complete migration to decision-first parsing.
2. If external consumers exist beyond this repo, publish a brief contract note indicating next_command_decision is now required in skill-doctor.v1.
3. Retain handler-owned runtime-target validation pattern for future proof-related arguments to avoid parser-only failures that bypass machine-readable payloads.

## Eval-report obligations
- eval_report_status: pass
- architecture_drift: none observed
- boundary_changes: CLI parser hands runtime-target validity to command handler by design; no ownership-plane drift
- unresolved_type1_decisions: none
- recommended_completion_state: proceed
- confidence: high
- residual_risk: low (consumer schema synchronization outside this repo, if any)

Validation evidence:
- python3 -m pytest Infrastructure/tests/test_ask_skills_doctor.py -q -> 14 passed, 15 subtests passed

WROTE: artifacts/reviews/jsc-351-pu003/architecture.md
