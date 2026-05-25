## Agent-Native Architecture Review

### Summary
The updated Codex preview command family in `ask skills` preserves agent-native parity for this PU-005 scope: human-facing CLI output now explicitly disclaims runtime-validation parity, modeled preview scan failures are surfaced as blocked fidelity checks, and `source_basis.blocked_check_ids` is kept synchronized with `blocked_checks` after late-appended blockers (including shell parse-error paths). Across this slice, core preview actions users can invoke are represented in agent-discoverable metadata and maintain consistent blocked-state semantics.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Run `ask skills codex-preview` and interpret runtime confidence | Infrastructure/bin/ask:1144 | `skills_codex_preview` | Yes (explicit disclaimer + parity line) | Must have | Pass |
| Run modeled load preview and detect degraded scan fidelity | Infrastructure/scripts/lib/ask/services/codex_preview.py:544 | `build_codex_load_preview` | Yes (`blocked_checks` + `source_basis`) | Must have | Pass |
| Explain config semantics with live-layer fidelity limits | Infrastructure/scripts/lib/ask/services/codex_preview.py:723 | `build_codex_config_explain` | Yes | Should have | Pass |
| Preview explicit skill mention injection | Infrastructure/scripts/lib/ask/services/codex_preview.py:811 | `build_codex_inject_preview` | Yes | Should have | Pass |
| Preview implicit invocation, including parse-error blockers | Infrastructure/scripts/lib/ask/services/codex_preview.py:894 | `build_codex_implicit_preview` | Yes | Should have | Pass |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. None.

#### Observations
1. **Residual parity boundary is explicitly modeled, not eliminated** -- `Infrastructure/scripts/lib/ask/services/codex_preview.py:900` documents shell-parser non-exact parity (`shell_parser_exact_parity`) and intentionally keeps status partial where fidelity cannot be claimed. This is expected and correctly surfaced.
2. **Human-mode disclosure now matches modeled data contract** -- `Infrastructure/bin/ask:1152-1156` prints non-validation disclaimer, `Live runtime parity: not_claimed`, and blocked-check count, reducing risk of operators inferring false runtime proof from source-modeled previews.

### What's Working Well
- `_refresh_preview_status_and_source_basis` is the single synchronization point for status plus blocker IDs, preventing drift after blockers are appended in command-specific branches (`Infrastructure/scripts/lib/ask/services/codex_preview.py:353-356`).
- Load-preview scan failures now degrade status and emit a dedicated blocker (`preview_scan_errors`) that is propagated into `source_basis.blocked_check_ids` (`Infrastructure/scripts/lib/ask/services/codex_preview.py:549-557`).
- Regression coverage is direct and behavior-specific, including blocker-ID synchronization and human-output disclaimer checks (`Infrastructure/tests/test_ask_skills_codex_preview.py:46-48`, `:96-108`, `:195-207`).

### Score
- **5/5 high-priority capabilities are agent-accessible**
- **Verdict:** PASS

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/agent-native-final2-reviewer.md
