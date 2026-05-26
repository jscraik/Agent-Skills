## Agent-Native Architecture Review

### Summary
PR #215 adds a new ownership check in `ask skills doctor`, introduces a project-manifest schema, and adjusts runtime proof gating for rooted symlink layouts. Agent integration exists and is mature (`skills doctor` emits structured checks, blocker classes, and next-command guidance), but there are two high-impact parity gaps: one allows runtime ownership checks to silently miss generated projections when path casing differs, and one introduces a new manifest schema without an agent-discoverable CLI path to validate/create it. Overall verdict: needs work before claiming full agent-operable parity.

### Capability Map

| UI Action | Location | Agent Tool | In Prompt? | Priority | Status |
|-----------|----------|------------|------------|----------|--------|
| Run doctor on handle/path | Infrastructure/scripts/lib/ask/commands/skills_impl.py:2984 | `./bin/ask skills doctor` | Yes (validation_commands + next_command) | Must-have | Partial |
| Detect projection/runtime root misuse | Infrastructure/scripts/lib/ask/commands/skills_impl.py:3493 | `projection_ownership` check | Yes | Must-have | Failing edge case |
| Validate runtime command-handle reachability for rooted symlink installs | Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1240 | `build_command_handle_proof` via doctor runtime check | Yes | Must-have | Pass |
| Discover/validate owner-repo manifest contract | Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:1 | No direct CLI lane added in this patch | No | Should-have | Missing |

### Findings

#### Critical (Must Fix)
1. **Case-sensitive path classification lets projection paths evade the new ownership gate** -- `Infrastructure/scripts/lib/ask/commands/skills_impl.py:2506-2525`, `Infrastructure/scripts/lib/ask/commands/skills_impl.py:3467-3479`
   Description: `_skill_root_ownership_for_path` only matches `.agents/skills/` and `.codex/skills/` with exact case. If the doctor target is path-based (not handle-based) and the user/agent passes `.Agents/skills/.../SKILL.md` or other case variants on a case-insensitive filesystem, classification becomes `unknown`, so `projection_ownership` can remain `pass` instead of blocking generated/runtime roots. This creates a direct action-parity hole: users/agents can still target runtime projection files via variant casing and bypass the intended guardrail.
   Ownership class: introduced by current patch.
   Fix: normalize the path to a canonical case for root detection (for example, compare lowercased POSIX segments) before applying classification rules, and add tests for path-based doctor targets with mixed-case `.agents/.codex` prefixes.

#### Warnings (Should Fix)
1. **New owner-manifest schema is not paired with an agent-discoverable command path** -- `Infrastructure/config/schemas/skills-sdk.project.v1.schema.json:1-104`, `Infrastructure/config/skills-sdk.json:96-105`, `Infrastructure/scripts/lib/ask/commands/skills_impl.py:3476-3491`
   Description: doctor now tells operators to “declare the root in an owner-repo `skills-sdk.json` manifest” and includes schema metadata, but this PR does not add a concrete CLI command to generate/validate that manifest in `operation_context.validation_commands` or `next_command` decisioning. That leaves a manual step dependency where an agent can detect the problem but lacks an explicit in-band operation to complete remediation autonomously.
   Ownership class: introduced by current patch.
   Recommendation: add a first-class CLI route (for example, `./bin/ask skills manifest validate --json --robot` or equivalent) and include it in doctor’s blocker remediation path so the agent can complete the loop without undocumented manual schema handling.

### Observations
1. Runtime proof handling improves agent operability for rooted symlink installs by accepting valid user-runtime handles when the user runtime link points to workspace runtime, which reduces false `blocked_runtime` outcomes in common rooted projections -- `Infrastructure/scripts/lib/ask/skills_sdk/runtime_adapters.py:1240-1250`, `Infrastructure/tests/test_runtime_proof_validation.py:538-586`.
2. Structured schema/test updates are coherent: `projection_ownership` is wired through contracts and schema tests, reducing silent schema drift -- `Infrastructure/scripts/lib/ask/skills_sdk/contracts.py:64-71`, `Infrastructure/config/schemas/skill-doctor.v1.schema.json:228-266`, `Infrastructure/tests/test_jsc351_codex_abi_schema_contracts.py:292-300`.

### No-Finding Coverage Notes
- **Shared workspace parity:** No regression found. Runtime checks still reason over repo workspace roots and linked user runtimes rather than isolated agent-only stores.
- **Tool output richness:** No regression found. Doctor continues to emit machine-usable check payloads, blocker classes, lifecycle event, and follow-up commands.
- **Human-only gated workflow:** No intentional human-only gate identified in this slice; gaps are remediable via missing/weak command surfaces.

### Open Questions
1. Should `skills-sdk.project.v1` be validated in CI as a required contract artifact when present, similar to existing doctor/package schema contract tests?
2. Is path normalization policy intentionally case-sensitive across all repo-path validators, or should doctor-specific ownership checks harden independently for macOS default filesystems?

### Score
- **2/4 high-priority capabilities are fully agent-accessible**
- **Verdict:** NEEDS WORK

WROTE: artifacts/reviews/agent-native-reviewer-pr215.md
