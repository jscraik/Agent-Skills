## Agent-Native Architecture Review

### Summary
The PU-006 slice adds explicit runtime-proof evidence emission for `--runtime-target codex|agents` and wires it into `skills proof`, producing shared-workspace RuntimeCard/receipt/probe artifacts that another agent can discover and validate without private session context. Overall parity is strong for discover, invoke, observe, validate, and handoff, with one provenance-path mismatch that should be corrected to keep source-of-truth discovery crisp.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Run runtime proof for a specific target | Infrastructure/scripts/lib/ask/commands/skills_impl.py:1303 | `./bin/ask skills proof <handle> --runtime-target codex|agents` | Yes (command output embeds rerun command + validation command) | Must-have | Implemented |
| Observe runtime proof outcome | .harness/evidence/runtime-proof/context7/codex/runtime-card.json:43 | RuntimeCard + receipt + probe artifacts | Yes (paths and verifier metadata embedded) | Must-have | Implemented |
| Validate artifact integrity | Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:330 | `validate_runtime_cards.py` command emitted in `runtime_evidence.validation_command` | Yes | Must-have | Implemented |
| Handoff blocked state with typed reason | .harness/evidence/runtime-proof/context7/codex/runtime-card.json:124 | `failed_check_id` + `recovery_plan` + blocker class | Yes | Must-have | Implemented |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. **Provenance path points at projection instead of canonical source** -- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:113` -- `source_paths` is hardcoded to `.agents/skills/<handle>/SKILL.md`, while the probe's resolution shows canonical ownership at `Skills/agent-ops/context7/SKILL.md` (`.harness/evidence/runtime-proof/context7/codex/probe.json:65`). This can cause an agent following provenance to inspect a generated projection first and miss canonical edit ownership. Recommendation: source canonical path from `proof["resolution"]["source_path"]` (fallback to command-handle path only when missing).

#### Observations
1. Explicit-target evidence flow is correctly scoped: `any` skips evidence emission by design (`Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:282`), while explicit targets always get typed output suitable for governed closeout.

### What's Working Well
- Runtime status classification is deterministic and agent-meaningful (`implemented_enforced`, `blocked_runtime`, `stale_or_drifted`) in `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:64`.
- Artifact payloads include concrete rerun/validation commands and shared workspace root, enabling independent replay by another agent.
- Blocked codex proof still emits schema-valid evidence with gate-level diagnostics (`failed_check_id: codex_user_runtime_ready`) and recovery steps.

### Score
- **4/4 high-priority capabilities are agent-accessible**
- **Verdict:** PASS (with one should-fix provenance accuracy gap)
WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-006/agent-native-final-reviewer.md
