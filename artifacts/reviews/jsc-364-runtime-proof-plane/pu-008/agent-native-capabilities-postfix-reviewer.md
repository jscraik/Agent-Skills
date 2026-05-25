## Agent-Native Architecture Review

### Summary
This slice now exposes agent capability discovery as a first-class public CLI surface (`ask skills capabilities`) with both JSON/robot and human-readable output paths, command metadata examples, and updated placement truth in implementation notes plus goal receipts. Overall parity for the targeted workflow is strong: agents can discover the workflow, run it, and see explicit truth boundaries. One test assertion is brittle and could regress when blocker state changes.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Discover capability workflow (machine-readable) | Infrastructure/bin/ask:536, Infrastructure/scripts/lib/ask/commands/skills_impl.py:2629 | `./bin/ask skills capabilities --runtime-target <target> --json --robot` | Yes (command metadata examples) | Must | Accessible |
| Discover capability workflow (human-readable) | Infrastructure/bin/ask:1138-1139, Infrastructure/scripts/lib/ask/commands/skills_impl.py:2716 | `./bin/ask skills capabilities --runtime-target <target>` | Yes (render path wired) | Should | Accessible |
| Discover aliases/samples for command surface | Infrastructure/scripts/lib/ask/command_metadata.py:152-154, :309-310 | `capability -> capabilities` and sample command | Yes | Should | Accessible |
| See source-of-truth placement for this slice | .harness/implementation-notes/2026-05-24-jsc-364-agent-skills-codex-runtime-proof-plane-governed-execution-notes.html:435-441, Docs/goals/jsc-364-agent-skills-codex-runtime-proof-plane/receipts.jsonl:23 | Goal + implementation receipts | Yes | Should | Accessible |

### Findings

#### Critical (Must Fix)
1. None.

#### Warnings (Should Fix)
1. **Brittle human-output status assertion** -- `Infrastructure/tests/test_ask_skills_codex_preview.py:222` -- The test hard-codes `status=partial` in plain-text output. If runtime blockers are resolved and status becomes `available`, this will fail despite correct behavior. Recommendation: assert invariant fields (prefix + runtime target + parity disclaimer + next command) and parse/regex the status token rather than pinning `partial`.

#### Observations
1. **Alias discoverability is implemented in both parser and metadata** -- `Infrastructure/bin/ask:122`, `Infrastructure/scripts/lib/ask/command_metadata.py:309-310`; this is good parity and reduces agent/user command-surface drift.
2. **Capability response explicitly distinguishes discovery vs parity proof** -- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2690-2711`; this prevents overclaiming and keeps truth boundaries explicit.

### What's Working Well
- The new command is wired end-to-end: parser route, command implementation, export surface, metadata examples, and human formatter.
- JSON shape includes actionable primitives for agents (`evidence_modes`, `supported_commands`, `required_artifacts`, `next_actions`) instead of opaque workflow prose.
- Placement/source-of-truth updates are reflected in both implementation notes and goal receipts, improving handoff clarity.

### Score
- **4/4 high-priority capabilities are agent-accessible**
- **Verdict:** PASS (with one test-hardening recommendation)
- **Residual risk:** Human output test may become flaky when environment/runtime blocker state changes.
WROTE: artifacts/reviews/jsc-364-runtime-proof-plane/pu-008/agent-native-capabilities-postfix-reviewer.md
