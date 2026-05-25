## Agent-Native Architecture Review

### Summary
This slice extends existing agent integration in `./bin/ask repo closeout` by adding shared-workspace runtime evidence discovery and explicit truth-boundary signaling. Overall parity is strong: agents can discover the same runtime-evidence status users see, and JSON output preserves actionable follow-up commands. One should-fix gap remains in human-output parity for key truth boundaries.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Run closeout with changed scope | Infrastructure/bin/ask:1052 | `./bin/ask repo closeout --changed --json --robot` | N/A (CLI native) | Must have | Pass |
| Discover runtime evidence artifacts in shared workspace | Infrastructure/scripts/lib/ask/commands/repo_impl.py:1281 | `repo_closeout(... changed=True)` + `runtime_evidence` payload | N/A (CLI native) | Must have | Pass |
| Get validator command for runtime cards | Infrastructure/scripts/lib/ask/commands/repo_impl.py:1241 | `runtime_evidence.schema_validation.command` | N/A (CLI native) | Must have | Pass |
| See truth boundaries in human output | Infrastructure/bin/ask:1089 | Human closeout print path | N/A (CLI native) | Should have | Partial |
| Detect invalid RuntimeCard payloads | Infrastructure/scripts/lib/ask/commands/repo_impl.py:1249, Infrastructure/tests/test_ask_repo_doctor.py:609 | `runtime_evidence.status=invalid` and error details | N/A (CLI native) | Must have | Pass |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. **Human/JSON boundary mismatch for command/schema proof** -- `Infrastructure/bin/ask:1092`, `Infrastructure/scripts/lib/ask/commands/repo_impl.py:1323` -- JSON includes `truth_boundaries.command_proof` and `truth_boundaries.schema_proof`, but human output only prints PR/tracker/docs boundaries. This leaves a human-only operator without the same key interpretation context that agents get from JSON. Recommendation: print `command_proof` and `schema_proof` in the human closeout summary alongside PR/tracker/docs.

#### Observations
1. **Shared workspace evidence is correctly agent-discoverable** -- `Infrastructure/scripts/lib/ask/commands/repo_impl.py:1305` scans repo-owned `.harness/evidence/runtime-proof/**/runtime-card.json` and returns structured card metadata plus explicit validator command.
2. **Truth-boundary language is appropriately conservative** -- `Infrastructure/scripts/lib/ask/commands/repo_impl.py:1296` and :1323 clearly avoid over-claiming PR/tracker/docs/schema proof.
3. **Governance note file should not be treated as executable truth** -- `.harness/implementation-notes/...html:656` records reviewer artifact-compliance gaps; this is useful context but correctly separate from command-driven closeout payloads and validators.

### What's Working Well
- Runtime evidence is placed in a shared repo path, not an agent-only sandbox.
- Closeout adds a deterministic validator command with workspace-root binding for replayability.
- Invalid-card path is covered by focused tests and returns actionable diagnostic text.
- Focused validation queue now includes `runtime_evidence_cards` when runtime-proof artifacts change.

### Score
- **4/5 high-priority capabilities are fully agent-accessible**
- **Verdict:** NEEDS WORK (minor parity gap only)

### HE Eval Report Fields
- **eval_report_status:** completed
- **agent_native_readiness:** mostly_ready_with_minor_gaps
- **capability_map_delta:** Added runtime evidence discovery + validator command discoverability + invalid-card path coverage; human-output truth-boundary coverage is partial.
- **runtime_visibility_evidence:** `repo_impl.py` emits `runtime_evidence` with card summaries, counts, validator command, and explicit boundaries; `bin/ask` prints runtime-evidence status + PR/tracker/docs boundaries.
- **blocking_agent_gaps:** None that block agent operation; one non-blocking human-output parity gap (`command_proof/schema_proof` not printed).
- **recommended_completion_state:** proceed_with_packaging_after_optional_human_output_parity_tweak
- **confidence:** 0.88
- **residual_risk:** Human-only closeout readers may under-interpret command/schema boundary context until parity print lines are added.

WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-007/agent-native-final-reviewer.md
