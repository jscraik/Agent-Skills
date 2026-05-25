## Agent-Native Architecture Review

### Summary
Post-fix review of the runtime-proof evidence lane confirms the core parity objective is now met for this slice: runtime artifacts preserve canonical source provenance, explicit runtime-target proofs emit typed status (`implemented_enforced`, `blocked_runtime`, `stale_or_drifted`), and generated evidence remains user-observable and validator-consumable. I found no blocking agent-native regressions in discover/invoke/observe/validate/handoff for the reviewed paths.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Discover canonical skill source provenance from proof artifacts | .harness/evidence/runtime-proof/*/runtime-card.json | `./bin/ask skills proof <handle> --runtime-target <codex|agents>` | Yes (artifact + receipt metadata) | Must have | PASS |
| Invoke runtime reachability proof for Codex or Agents runtime | Infrastructure/scripts/lib/ask/commands/skills_impl.py:1303 | `skills_proof` command surface | Yes (validation command embedded in evidence) | Must have | PASS |
| Observe runtime-state outcome with typed blocker classification | Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:64 | RuntimeCard/receipt emission from `emit_command_handle_runtime_evidence` | Yes (runtime_status + blocker_class in artifacts) | Must have | PASS |
| Validate produced runtime artifacts against shared-workspace contract | Infrastructure/tests/test_command_surface_handles.py:675 | `validate_runtime_cards.py --require-shared-workspace` | Yes (consumer_contract + verifier path) | Must have | PASS |
| Handoff remediation path when runtime unavailable | Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:185 | Recovery plan in RuntimeCard | Yes (next_commands + preconditions) | Should have | PASS |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. None.

#### Observations
1. **Residual validation envelope risk** -- `Infrastructure/tests/test_command_surface_handles.py:675` validates RuntimeCard schema in targeted tests, but full suite execution remains externally blocked by pre-existing `ModuleNotFoundError: yaml` in separate tests. Recommendation: keep classifying this as an environment/pre-existing blocker (not a parity defect) until dependency baseline is restored, then rerun full Infrastructure tests for broader regression confidence.

### What's Working Well
- Canonical provenance is preserved end-to-end in runtime evidence via `resolution.source_path` fallback logic and appears correctly in live RuntimeCard `source_identity.source_paths` entries.
- Runtime status semantics now cleanly separate runtime reachability failures from non-reachability drift outcomes.
- Runtime evidence artifacts and receipts are discoverable, self-describing, and explicitly tied to verifier and rerun commands, which improves agent handoff reliability.

### Score
- **5/5 high-priority capabilities are agent-accessible**
- **Verdict:** PASS
