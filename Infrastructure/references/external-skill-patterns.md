# External Skill Pattern Extraction

Use this reference when creating, hardening, auditing, or refactoring a skill
from a high-quality external example set. It records reusable patterns observed
in `steipete/agent-scripts` at commit
`600c15eb2baa919f67930e1d83d791002b379820`.

Do not copy external skills as house style. Extract their operating contracts,
then adapt them to this repository's canonical source, validation, runtime
projection, and side-effect rules.

## Source Basis

The strongest reusable patterns came from these external skill types:

- review closeout skills with accepted/rejected finding loops and exact proof;
- GitHub triage skills with local-repo scope gates before broad queue scans;
- CLI design skills with stable I/O, exit-code, config, and non-interactive
  contracts;
- performance/debugging skills with decision trees, evidence capture, and
  before/after verification;
- credential and remote-control skills with explicit session, auth, and no
  silent-fallback rules;
- generated-artifact skills with draft-to-final workflows and precise output
  path behavior.

Use those examples as pressure tests for whether a local skill tells another
agent what to do, what not to do, how to verify it, and when to stop.

## Reusable Pattern Checklist

Apply this checklist before adding more prose to `SKILL.md`.

- **Trigger precision**: the description and opening lines should name the actual user phrases, context, and non-goals that route to the skill.
- **Fast first action**: the first operational section should say what to read, inspect, or run before any broad exploration.
- **Scope gate**: define when to stay in the current repo, issue, PR, file, or artifact and what wording authorizes broad scanning.
- **Evidence-first contract**: require the agent to read the real path, dependency contract, adjacent tests, or current state before accepting a finding or recommendation.
- **Accepted/rejected loop**: for review and hardening skills, require accepted findings to be fixed or consciously rejected with a short reason; rerun only the focused proof affected by accepted fixes.
- **Stop rule**: name the clean terminal state and prohibit extra reruns just to obtain nicer wording or another opinion.
- **Output shape**: define the final report fields, table, artifact path, machine-readable schema, or response template that proves the skill completed the intended task.
- **Command contract**: when a skill wraps a CLI, include stable stdout/stderr behavior, JSON/plain modes, exit-code semantics, config precedence, non-interactive mode, and dry-run or confirmation behavior.
- **Auth/session contract**: for credentials or interactive tools, require one persistent session, explicit account/target selection, redacted debugging, and a blocker instead of probing broadly.
- **Two-way validation**: for UI, remote, performance, or generated-artifact workflows, verify from the actor side and an independent observer side when feasible.
- **Before/after proof**: performance, remediation, and design-change skills should capture baseline, change, and delta rather than only listing advice.
- **Repair granularity**: fix the smallest failing artifact, row, command, trace, or package surface before restarting the whole workflow.
- **Current-state preference**: stale comments, cached data, and old CI are only hints until current source, live command output, or executable proof confirms them.

## Heading Guidance

Prefer domain-language headings over one rigid template. The useful pattern is the contract, not the exact heading name.

Use compact headings like these when they make the workflow easier to execute:

- `Start`, `Do This First`, or `Quick Start` for the first real action.
- `Scope Rule`, `Local Gate`, or `Pick Target` for narrowing the task.
- `Contract`, `Review Contract`, or `Command Contract` for invariants.
- `Workflow`, `Decision Tree`, or numbered phases for multi-step work.
- `Output`, `Output Shape`, or `Final Report` for completion evidence.
- `Safety`, `Guardrails`, or `Failure Handling` for hard stops.
- `Verify`, `Two-Way Validation`, or `Acceptance Criteria` for proof.

Remove headings that only restate generic skill anatomy. Add headings only when they help an agent choose the next action or preserve an invariant.

## Integration Rules

When applying an external pattern to this repository:

1. Resolve the canonical source first; never patch runtime projections, generated handles, or cache mirrors as the source of truth.
2. Classify the side effect before borrowing a workflow: read-only, artifact-write, repo-write, external-write, destructive, or completion-gating.
3. Keep `SKILL.md` compact. Move long examples, matrices, command libraries, issue-specific evidence, and prompt templates into references with a clear `Read when:` signpost.
4. Convert persona language into testable behavior: inputs, source order, validation, blockers, and output fields.
5. Preserve this repo's stricter validation reporting: every gate is `pass`, `fail`, `blocked`, or `not applicable`, with exact command or evidence.
6. Do not introduce personal machine paths, account names, hostnames, or service assumptions from an external skill unless the target user's workflow actually owns them.
7. Prefer one focused contract or eval over a broad style rewrite when the external example exposes a narrow missing invariant.

## Anti-Patterns

- Copying an external skill wholesale because it feels polished.
- Adding many headings without changing the agent's executable behavior.
- Hiding side effects inside a review, planning, or triage flow.
- Treating a helper script's existence as proof that the workflow is safe.
- Broadening from current repo or artifact scope without explicit user wording.
- Replacing validation evidence with confidence language.
- Keeping stale external account, host, or path details in a reusable skill.
