# PU-007 Testing Review

## Status

PASS: focused behavior proof exists for the changed command paths.

## Findings

### Informational: Focused test coverage exercises both direct function and CLI paths

- Evidence: Infrastructure/tests/test_ask_skills_conformance.py:58 verifies archive package success without mutation.
- Evidence: Infrastructure/tests/test_ask_skills_conformance.py:87, :107, :126, :147, and :171 verify untrusted provenance, digest mismatch, unsafe archive member, symlink escape, and missing rollback-journal evidence.
- Evidence: Infrastructure/tests/test_ask_skills_conformance.py:188 verifies conformance evidence files and per-case snapshots.
- Evidence: Infrastructure/tests/test_ask_skills_conformance.py:208 and :236 verify CLI JSON surfaces for package verify and conformance run.

## Validation Evidence

- Command: XDG_CACHE_HOME=/private/tmp/jsc351-uv-cache UV_CACHE_DIR=/private/tmp/jsc351-uv-cache/uv python3 -m pytest Infrastructure/tests/test_ask_skills_conformance.py -q -> pass, 9 tests.
- Command: ./bin/ask skills conformance run --suite codex-parity --json --robot --evidence-dir /private/tmp/jsc351-pu007-evidence-pass-2 -> pass.
- Command: ./bin/ask skills package verify skill-builder --json --robot -> pass.

WROTE: artifacts/reviews/jsc-351-pu007-conformance/review-testing.md
