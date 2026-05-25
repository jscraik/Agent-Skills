## Agent-Native Architecture Review

### Summary
The PU-005 postfix changes keep the Codex preview workflow agent-operable and machine-readable. The command family is now publicly discoverable through parser/help metadata, and the `skills codex-preview` surface explicitly inherits modeled status/source signals from `build_codex_load_preview(...)` while declaring `not_a_validation_result: true`. Overall parity for the preview slice is strong: agents can discover commands, invoke each command, and read explicit blocker semantics instead of inferring validation success.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Discover preview command family (`skills codex-preview`) | Infrastructure/bin/ask:124-139, Infrastructure/scripts/lib/ask/command_metadata.py:151-170 | `skills_codex_preview` | Yes (`agent_summary` + command list) | Must | Pass |
| Inspect modeled load behavior | Infrastructure/scripts/lib/ask/commands/skills_impl.py:2570-2574 | `skills_load_preview` | Yes (`commands[].validation_command`) | Must | Pass |
| Inspect render/truncation behavior | Infrastructure/scripts/lib/ask/services/codex_preview.py:672-706 | `skills_render_preview` | Yes | Must | Pass |
| Inspect config rule semantics | Infrastructure/scripts/lib/ask/services/codex_preview.py:710-737 | `skills_config_explain` | Yes | Should | Pass |
| Inspect explicit mention matching | Infrastructure/scripts/lib/ask/services/codex_preview.py:792-825 | `skills_inject_preview` | Yes | Should | Pass |
| Inspect implicit invocation attribution | Infrastructure/scripts/lib/ask/services/codex_preview.py:881-921 | `skills_implicit_preview` | Yes | Should | Pass |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. None.

#### Observations
1. **Human-output discoverability omits explicit caution line for codex-preview** -- `Infrastructure/bin/ask:1144-1152` -- Structured JSON includes `not_a_validation_result: true`, but the non-JSON summary line does not repeat this caution text. Suggestion: append one plain-text line in human output such as "Note: preview is modeled evidence, not runtime validation" to reduce operator ambiguity outside JSON consumers.

### What's Working Well
- `skills_codex_preview` now derives `status`, `source_identity`, `source_basis`, and `blocked_checks` from `build_codex_load_preview(...)`, preventing false success signaling drift (`Infrastructure/scripts/lib/ask/commands/skills_impl.py:2577-2589`).
- The explicit machine-readable disambiguator is present: `not_a_validation_result: true` (`Infrastructure/scripts/lib/ask/commands/skills_impl.py:2585`).
- `source_basis.live_runtime_parity` is explicitly modeled as `not_claimed`, and blocked check IDs are propagated (`Infrastructure/scripts/lib/ask/services/codex_preview.py:290-303`).
- Render preview now publishes truncation status/strategy/counts/warning in a stable object (`Infrastructure/scripts/lib/ask/services/codex_preview.py:672-706`).
- Public discoverability is wired across parser, dispatcher, and metadata examples (`Infrastructure/bin/ask:124-139`, `Infrastructure/bin/ask:541-555`, `Infrastructure/scripts/lib/ask/command_metadata.py:151-170`).
- Tests directly enforce the post-fix behavior and command discoverability claims (`Infrastructure/tests/test_ask_skills_codex_preview.py:165-216`).

### Validation Evidence
- `python3 -m pytest -q Infrastructure/tests/test_ask_skills_codex_preview.py` -> `23 passed`.

### Score
- **6/6 high-priority capabilities are agent-accessible**
- **Verdict:** PASS

Residual risk: parity remains source-modeled by design (not live-runtime execution parity), and this contract still depends on downstream consumers honoring `blocked_checks` and `not_a_validation_result` fields.
WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/agent-native-postfix-reviewer.md
