# Adversarial Final2 Review (PU-005)

## Findings
No actionable adversarial findings verified in the reviewed fix set.

## What I stress-tested
- False-success composition path for human-mode `skills codex-preview` output against source-modeled payload semantics.
- Scan-error cascade path where partial root scan errors must degrade status and propagate into blocker surfaces.
- Blocker synchronization path ensuring `source_basis.blocked_check_ids` tracks `blocked_checks` after late blocker appends (including shell parse errors).

## Evidence checks
- `Infrastructure/bin/ask:1141` prints explicit source-mode disclaimer and parity status for plain-text `skills codex-preview`.
- `Infrastructure/scripts/lib/ask/services/codex_preview.py:549` appends `preview_scan_errors` blocker and `codex_preview.py:557` re-synchronizes status/source basis.
- `Infrastructure/scripts/lib/ask/services/codex_preview.py:353` centralizes blocker/status/source-basis synchronization via `_refresh_preview_status_and_source_basis`.
- `Infrastructure/scripts/lib/ask/services/codex_preview.py:732`, `:821`, `:904`, and `:917` call synchronization after command-specific blocker additions.
- `Infrastructure/tests/test_ask_skills_codex_preview.py:46` adds blocker parity assertion helper and exercises key late-blocker branches.

## Residual Risks
- Duplicate blocker IDs remain possible if future call sites append semantically identical blockers multiple times; status and parity remain correct, but downstream tooling that treats blocker IDs as unique may require dedupe.
- Source-modeled previews still depend on modeled assumptions rather than live runtime execution by design; parity remains intentionally `not_claimed`.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/adversarial-final2-reviewer.md
