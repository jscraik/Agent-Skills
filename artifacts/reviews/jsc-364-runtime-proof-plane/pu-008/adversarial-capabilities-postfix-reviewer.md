# Adversarial Capabilities Postfix Review (PU-008)

## Scope
Reviewed current PU-008 diff only for:

1. `--runtime-target any` artifact claims.
2. `--runtime-target agents` false-green / false-available behavior under source blockers.
3. Human output parity-claim safety.
4. Governed-state verification freshness discipline.

## Result
PASS — no material findings for the scoped checks.

## Evidence

- `skills_capabilities` routes `runtime_target=any` to explicit proof targets `codex` and `agents`; required artifact paths are generated per explicit target and never under `/any/`.
  - Evidence: `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2646-2655`
  - Test coverage: `Infrastructure/tests/test_ask_skills_codex_preview.py:275-294`

- `skills_capabilities` sets readiness to `partial` when source blockers exist and preserves blocked checks for `agents` target instead of claiming availability parity.
  - Evidence: `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2648-2650,2701`
  - Test coverage: `Infrastructure/tests/test_ask_skills_codex_preview.py:295-305`

- Human output explicitly prints runtime truth boundaries and avoids live parity claims by surfacing `not_claimed` (or discovery-only boundary for `any`).
  - Evidence: `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2716-2732`
  - CLI wiring: `Infrastructure/bin/ask:1138-1140`
  - Test coverage: `Infrastructure/tests/test_ask_skills_codex_preview.py:215-223`

- Governed state keeps verification freshness metadata via explicit `checked_at` timestamp in `last_verification`, reducing stale-claim ambiguity.
  - Evidence: `docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/state.yaml:47-51`

## Residual Risks (non-blocking)
- Capability discovery remains command-availability evidence, not live runtime proof; this is correctly disclosed but still depends on operators following `next_actions`.
- `last_verification.detail` contains volatile PR check narrative; freshness depends on maintaining `checked_at` updates during future sweeps.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/adversarial-capabilities-postfix-reviewer.md
