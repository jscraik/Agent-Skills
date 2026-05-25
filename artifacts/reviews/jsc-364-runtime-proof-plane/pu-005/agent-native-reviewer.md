## Agent-Native Architecture Review

### Summary
PU-005 improves agent-native parity for Codex preview proofs by exposing a public command-family entrypoint, adding command metadata discoverability, and returning explicit source-modeled basis plus truncation state in preview payloads. The reviewed diff shows that agents can discover the command family via `ask skills` surfaces, run each workflow from published validation commands, and receive explicit non-parity signaling (`live_runtime_parity: not_claimed`) to prevent false runtime-equivalence claims.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Discover preview command family from public CLI help | Infrastructure/bin/ask:123 | `./bin/ask skills codex-preview --help` | Yes (command metadata examples + CLI help text) | Must | Pass |
| Enumerate runnable preview workflows with exact validation commands | Infrastructure/scripts/lib/ask/commands/skills_impl.py:2587 | `skills_codex_preview` | Yes (`agent_summary` + validation commands in payload) | Must | Pass |
| Retrieve source identity + source basis for load preview | Infrastructure/scripts/lib/ask/services/codex_preview.py:290 | `./bin/ask skills load-preview --json --robot` | Yes (`source_basis` object in output) | Must | Pass |
| Retrieve truncation status for render preview | Infrastructure/scripts/lib/ask/services/codex_preview.py:672 | `./bin/ask skills render-preview --json --robot` | Yes (`truncation` object in output) | Must | Pass |
| Discover preview commands via metadata-driven guidance | Infrastructure/scripts/lib/ask/command_metadata.py:10 | command metadata examples (`ask skills codex-preview`, `render-preview`, `config explain`) | Yes | Should | Pass |
| Human-readable non-JSON summary of command family | Infrastructure/bin/ask:1144 | non-JSON `skills codex-preview` output | N/A | Should | Pass |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. None.

#### Observations
1. **Command-family index is metadata-only by design** -- Infrastructure/scripts/lib/ask/commands/skills_impl.py:2584 returns `status: "pass"` for `skills codex-preview` even when individual downstream preview commands may later return partial/blocked fidelity. This is acceptable for a discoverability endpoint; keep this distinction explicit in docs and reviews to avoid over-reading this command as runtime proof.
2. **Implementation-notes placement map improved artifact discoverability** -- .harness/implementation-notes/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-governed-execution-notes.html:291 adds “Work lands in” path blocks that help agents navigate relevant files/artifacts without private context.

### What's Working Well
- Public command routing is complete end-to-end: parser registration, dispatcher branch, and stdout summary path are all wired.
- Output schema now includes machine-readable `source_basis` and `truncation` surfaces, improving context parity for agent consumers.
- Command metadata includes explicit topic/action examples for preview commands, strengthening capability discoverability through assistant guidance surfaces.
- Tests cover both behavior and discoverability lanes, including help reachability and command-family listing.

### Score
- **5/5 high-priority capabilities are agent-accessible**
- **Verdict:** PASS

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-005/agent-native-reviewer.md
