## Agent-Native Architecture Review

### Summary
This plan now provides strong agent-native parity for command handles, fallback behavior, proof artifacts, and live invocation gating. The previous executable fallback gap is fixed, and proof sequencing is mostly aligned with the intended gate model. No blocking findings remain, but one contract-level risk still exists: the live invocation gate is required by the plan, yet the canonical cutover command set does not include an explicit live invocation proof step.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Resolve skill handle | Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:622 | `./bin/ask skills resolve <handle> --json` | Yes | Must | Covered |
| Resolve reviewer handle | Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:624 | `./bin/ask reviewers resolve <handle> --json` | Yes | Must | Covered |
| Router low-confidence fallback | Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:738 | `./bin/ask skills route --skill-set <name> --fallback flat --task-stdin --json` | Yes | Must | Covered |
| Handle proof artifact | Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:659 | `./bin/ask skills handles proof <handle> --with-reviewer <handle> --json` | Yes | Must | Covered |
| Live `$<handle>` invocation proof after sync | Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:660 | command/artifact required by plan | Partial | Must | Partial |

### Findings

#### Critical (Must Fix)
1. **None.** No blocking parity defects were found in this revision.

#### Warnings (Should Fix)
1. **Canonical cutover validation does not explicitly execute the live invocation gate** -- `Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:660`, `Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:703`, `Docs/plans/2026-04-24-feat-context-budgeted-skill-trees-plan.md:1155` -- The plan requires separate live invocation proof after sync, but the canonical command set lists resolver/proof/sync commands without an explicit live-invocation proof command invocation. Recommendation: add a concrete public `./bin/ask ... --json` live-invocation verifier step to the canonical cutover set (or explicitly state `skills handles proof` is the authoritative live gate and enforce its schema fields for synced hash, handle token, stub path, source path, module count, and pass/fail).

#### Observations
1. **Fallback contract is now executable for agents** -- The default fallback now includes `--skill-set <name>`, matching the public router contract and removing prior agent dead-end risk.
2. **Gate separation quality is significantly improved** -- D6/B2a now clearly separate resolver, command-surface, stub, sync, proof artifact, and live invocation concepts, reducing false-positive parity claims.

### What is Working Well
- Public `./bin/ask` wrappers are treated as the stable agent/operator contract surface.
- Skill and reviewer namespaces are explicitly separated with distinct resolver surfaces.
- Command-visible stubs are constrained to thin pointers with anti-leak budget rules.
- Proof artifacts include a concrete schema shape and deterministic-path expectations.

### Score
- **5/5 high-priority capabilities are specified for agent access** (with 1 validation-contract residual risk)
- **Verdict:** PASS

WROTE: artifacts/reviews/agent-native-reviewer.md
