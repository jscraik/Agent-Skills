# PU-007 Architecture Review

## Status

PASS: no blocker findings.

## Findings

### Informational: Conformance is a fixture-backed regression layer, not live Codex parity

- Evidence: Infrastructure/scripts/lib/ask/skills_sdk/conformance.py:311 defines run_skills_conformance, and Infrastructure/scripts/lib/ask/skills_sdk/conformance.py:386 writes the summary around deterministic fixture cases.
- Evidence: Infrastructure/scripts/lib/ask/skills_sdk/conformance.py:139 and Infrastructure/scripts/lib/ask/skills_sdk/conformance.py:204 record modeled preview limitations inside case evidence rather than promoting them to runtime proof.
- Disposition: accepted for PU-007 because the plan scopes this slice to conformance workouts and replayable evidence. Full live Codex runtime proof remains owned by the earlier parity/preview commands and later PR triage.

### Informational: Package verification is isolated into an SDK service module

- Evidence: Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py:194 owns archive package verification.
- Evidence: Infrastructure/scripts/lib/ask/commands/skills_impl.py:2996 delegates archive verification to _verify_archive_package instead of embedding archive inspection in the CLI command layer.
- Disposition: acceptable deep-module direction. The CLI layer still contains directory/handle verification orchestration, but the risky archive inspection logic is behind the SDK module boundary.

## Validation Evidence

- Command: python3 -m py_compile Infrastructure/bin/ask Infrastructure/scripts/lib/ask/commands/skills_impl.py Infrastructure/scripts/lib/ask/skills_sdk/conformance.py Infrastructure/scripts/lib/ask/skills_sdk/package_verify.py -> pass.
- Command: XDG_CACHE_HOME=/private/tmp/jsc351-uv-cache UV_CACHE_DIR=/private/tmp/jsc351-uv-cache/uv python3 -m pytest Infrastructure/tests/test_ask_skills_conformance.py -q -> pass, 9 tests.
- Command: ./bin/ask skills conformance run --suite codex-parity --json --robot --evidence-dir /private/tmp/jsc351-pu007-evidence-pass-2 -> pass, 12 fixture cases.

WROTE: artifacts/reviews/jsc-351-pu007-conformance/review-architecture.md
