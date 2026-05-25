## Agent-Native Architecture Review

### Summary
This slice adds and verifies a public Codex preview command family that clearly communicates source-modeled-only behavior across both machine-readable and human-readable surfaces. Agent-native parity for this feature is now consistent: the agent can discover the preview commands, consume structured safety-boundary metadata, and see equivalent boundary messaging in CLI output. Overall assessment: parity for discoverability and safety-boundary communication is in good shape for the reviewed scope.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Discover Codex preview workflow (`skills codex-preview`) | Infrastructure/bin/ask:1144 | `skills_codex_preview` | Yes (`commands[]`, `agent_summary`) | Must have | Pass |
| Read machine-safe boundary (not validation result, source basis, blockers) | Infrastructure/scripts/lib/ask/commands/skills_impl.py:2581 | `skills_codex_preview` JSON payload | Yes | Must have | Pass |
| Surface scan-root failure as explicit blocker | Infrastructure/scripts/lib/ask/services/codex_preview.py:543 | `build_codex_load_preview` | Yes (`blocked_checks`) | Must have | Pass |
| Read truncation status/strategy/counts | Infrastructure/scripts/lib/ask/services/codex_preview.py:680 | `build_codex_render_preview` | Yes (`truncation`) | Should have | Pass |
| Human-readable parity boundary for preview family | Infrastructure/bin/ask:1151 | CLI text output for `skills codex-preview` | Yes | Must have | Pass |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. None.

#### Observations
1. **Boundary messaging is centralized on `skills codex-preview`** -- `Infrastructure/bin/ask:1151` prints the explicit non-validation disclaimer and parity state, while sibling preview commands focus on command-specific summaries. This is acceptable for current scope; if users frequently invoke `load-preview` directly, consider mirroring a short boundary line there for consistency.

### What's Working Well
- Structured payload now explicitly encodes non-validation semantics via `not_a_validation_result`, `source_identity`, `source_basis`, and `blocked_checks` (`Infrastructure/scripts/lib/ask/commands/skills_impl.py:2585`).
- Source-basis metadata consistently advertises `live_runtime_parity: not_claimed` and blocker IDs, preventing false confidence (`Infrastructure/scripts/lib/ask/services/codex_preview.py:300`).
- Modeled scan failures now degrade status and attach `preview_scan_errors`, improving failure visibility for both agents and humans (`Infrastructure/scripts/lib/ask/services/codex_preview.py:543`).
- Render preview returns a stable truncation contract (status/strategy/counts/warning), which supports reliable downstream agent reasoning (`Infrastructure/scripts/lib/ask/services/codex_preview.py:680`).
- Regression coverage is strong and directly tests the repaired claims, including human-output disclaimer and scan-error degradation (`Infrastructure/tests/test_ask_skills_codex_preview.py:191`, `Infrastructure/tests/test_ask_skills_codex_preview.py:92`).

### Score
- **5/5 high-priority capabilities are agent-accessible**
- **Verdict:** PASS

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/agent-native-final-reviewer.md
