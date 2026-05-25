## Agent-Native Architecture Review

### Summary
Re-reviewed against the correct PR base (`origin/main` `82e201598`) and head (`7ddc456cca799756a55b35b888dae58f6b502c3f`). This branch does include the full JSC-364 integration stack (90 files changed), including command-surface/runtime-proof implementation, tests, governance artifacts, and review evidence. Agent-operable command paths are present and discoverable, and runtime proof artifacts are written to shared workspace evidence paths. Remaining risk is concentrated in unresolved runtime-separation parity blockers that still report degraded status.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Discover capability command for Codex runtime | `Infrastructure/scripts/lib/ask/command_metadata.py:152` | `ask skills capabilities --runtime-target codex --json --robot` | N/A (CLI) | Must-have | Pass |
| Resolve skill handle to runnable command surface | `Infrastructure/tests/test_command_surface_handles.py:38` | `ask skills resolve <handle> --json` (validated in tests and command-handle rendering) | N/A (CLI) | Must-have | Pass |
| Emit runtime-proof artifacts to shared workspace | `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:295` | `ask skills proof <handle> --runtime-target codex|agents --json --robot` | N/A (CLI) | Must-have | Pass (with blocker typing when failed) |
| Read runtime readiness/doctor signals | `Infrastructure/scripts/lib/ask/commands/repo_impl.py:17` | `ask repo doctor --json --robot` signal stack | N/A (CLI) | Should-have | Pass |
| Assert runtime separation is healthy | `Infrastructure/GOVERNANCE/runtime-separation/current.json:26` | Governance artifact consumed by doctor workflows | N/A | Must-have | Degraded |

### Findings

#### Critical (Must Fix)
None in this corrected-base review.

#### Warnings (Should Fix)
1. **Runtime-separation remains degraded in integrated state** -- `Infrastructure/GOVERNANCE/runtime-separation/current.json:26`, `Infrastructure/GOVERNANCE/runtime-separation/current.json:245`, `Infrastructure/GOVERNANCE/runtime-separation/current.json:255`, `Infrastructure/GOVERNANCE/runtime-separation/current.json:265` -- Even with the full stack integrated, the governance snapshot still reports `status: degraded` and `plugin_package_root_parity` failures for `harness-engineering`, `plugin-factory`, and `skill-factory`. Recommendation: either clear parity failures before merge readiness claims, or explicitly classify them as accepted pre-existing blockers with owner + follow-up issue.
2. **Runtime-proof limitation is explicitly encoded but still a handoff risk if misread** -- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:285` -- Runtime proof verifies command-handle wiring but does not execute an interactive Codex session (`manual_session_gate`). Recommendation: keep this limitation surfaced in closeout messaging to avoid over-claiming end-to-end runtime execution proof.

### Observations
1. The previous scope mismatch finding is no longer valid once compared to the correct base (`82e201598`); the integration content is present in this PR.
2. Command-surface discoverability improved materially: capabilities and examples include explicit codex runtime targeting (`Infrastructure/scripts/lib/ask/command_metadata.py:152`).
3. Runtime-proof evidence is agent-readable and user-observable, with explicit mutation scope and recovery plans (`Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:141`, `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:203`).

### What's Working Well
- The PR includes both implementation and tests for command-surface/runtime-proof behavior, improving agent-native closure confidence.
- Runtime evidence artifacts are written into shared workspace paths under `.harness/evidence/runtime-proof/**`, preserving shared visibility.
- Doctor/repo command surfaces provide actionable next commands and typed signal priorities for agent remediation workflows.

### Score
- **4/5 high-priority capabilities are agent-accessible**
- **Verdict:** PASS (with follow-up warnings)

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/integration/pr208-agent-native-review.md
