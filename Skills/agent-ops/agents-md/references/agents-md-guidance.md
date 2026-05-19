# Agents Md Guidance

Read when an AGENTS refactor needs Codex discovery rules, Context Pointer design, or Harness Engineering plan-routing context that would bloat the entrypoint.

## Codex Instruction Discovery

- Codex loads discovered `AGENTS.md` files before work and merges applicable global, root, and nested guidance by scope.
- A closer instruction file overrides broader guidance inside its subtree.
- Codex discovers at most one instruction file per directory by default. Linked docs are references, not automatically loaded instructions, unless repo configuration or a discovered instruction explicitly makes them part of the route.
- Keep root AGENTS content focused on rules relevant to every task in that scope: project purpose, non-default toolchain, non-standard commands, command boundaries, and critical validation expectations.

## Context Pointer Use

Use Context Pointers for task-specific detail that does not need to be always loaded: linked docs, nested AGENTS files, skill handles, command names, headings, scripts, schemas, hooks, and code anchors.

Context ledger routing categories:

- root: relevant to every task in the active scope;
- nested AGENTS scope: narrower rule that should auto-load only below a directory;
- linked reference: durable detail, examples, or procedures needed only on demand;
- Context Pointer: a stable link, heading, command, function, module, or skill handle that helps future agents find relocated context;
- supplemental: useful context that is not binding instruction; and
- deletion candidate: redundant, vague, obsolete, or already replaced by a verified canonical source.

A pointer is acceptable only when:

- the target path, heading, handle, command, or code anchor exists;
- the owning instruction surface tells future agents when to follow it;
- the moved rule remains binding where it must be binding; and
- the context ledger records why the move did not lose required behavior.

## Harness Engineering Plan Pointer

For Harness Engineering work, AGENTS should point to the `@harness-engineering` or `he-plan` contract instead of defining a competing plan format. The durable plan artifact should carry source traceability, stable acceptance IDs, repo-relative paths, risks, validation, and tracker or PR traceability.

Keep plan instructions concise in AGENTS. Use unresolved questions only when planning is the requested output or evidence is insufficient to choose safely.

## Required Subagent And Review Swarm Contract

When creating or updating AGENTS guidance for a repository that uses subagents,
reviewers, review swarms, delegated agents, or artifact review lanes, preserve
an explicit coordinator-owned contract.

Minimum behavior:

- Use subagents only for independent lanes, specialist review, or bounded
  parallel investigation.
- The coordinator keeps responsibility for scope, evidence, synthesis,
  validation, and closeout.
- Before delegation, verify path-dependent inputs, prefer absolute paths, create
  coordinator-owned artifact parent directories, and keep prompts narrow.
- For broad swarms or uncertain runtime health, run one probe subagent first and
  verify that its artifact exists and is non-empty before launching the larger
  swarm.
- Artifact-producing subagents must end with
  `WROTE: /absolute/path/to/artifact.md`.
- Mailbox or status text is not completion evidence when artifacts were
  requested.
- Missing artifacts get one narrow retry. Remaining misses are recorded as
  failed coverage with an explicit coverage-gap note.
- Blocked work must use the blocked schema with `STATUS: complete`,
  `blocked_runtime`, `blocked_missing_artifact`, or `blocked_validation`.
- Validation failures reported by subagents must be classified before
  remediation as introduced by current patch, pre-existing, unrelated dirty
  worktree, environment/tooling failure, or user-owned config drift requiring
  explicit approval.
- Coordinator closeout records agents requested, agents completed, agents
  blocked, agents failed artifact verification, agents closed, and validation
  run with exact pass/fail/blocked outcomes.
- Close consumed agents when they are no longer needed.

Use the full contract for higher-risk or control-plane repositories, including
configs, coding-harness, agent-skills, CI/security surfaces, and repos that
regularly run review swarms. Use the compact version in ordinary application
repositories where the behavior guardrails matter but a long governance section
would dominate the AGENTS file.

Portable snippet:

````md
## Subagent Contract

Before spawning subagents, verify path-dependent inputs, use narrow prompts, and create expected artifact parent directories when the coordinator owns the output path. For broad swarms or uncertain runtime health, run one probe subagent first and verify its artifact exists before continuing.

Subagents must produce durable evidence. Artifact-producing tasks must end with `WROTE: /absolute/path/to/artifact.md`; the coordinator must verify every expected artifact exists and is non-empty before synthesis. Missing artifacts get one narrow retry; remaining misses are recorded as failed coverage, not replaced with mailbox/status text.

Blocked subagents must use:

```text
STATUS: complete | blocked_runtime | blocked_missing_artifact | blocked_validation
blocker_class:
attempted_command_or_tool:
exact_failure:
fallback_attempted:
coordinator_next_step:
```

Classify validation failures before remediation as one of: introduced by current patch, pre-existing, unrelated dirty worktree, environment/tooling failure, or user-owned config drift requiring explicit approval.

The coordinator remains responsible for synthesis, validation evidence, coverage-gap notes, and closing consumed agents.
````

## CODESTYLE Fallback

AGENTS files for technical repositories must give agents a CODESTYLE route.
Verify the local instruction scope or discovery path first:

- If a local `CODESTYLE.md` exists, point agents to that file.
- If no local `CODESTYLE.md` exists, AGENTS must say to use the global Codex
  CODESTYLE at `~/dev/configs/codex/instructions/CODESTYLE` instead and to
  report the verified absolute path before relying on it.
- If `~/dev/configs/codex/instructions/CODESTYLE` cannot be found or read,
  mark style guidance as blocked rather than inventing local style rules.

Portable fallback snippet:

```md
## Codestyle

For technical work, read this repo's `CODESTYLE.md` before editing. If this repo does not have a local `CODESTYLE.md`, use the global Codex CODESTYLE at `~/dev/configs/codex/instructions/CODESTYLE` instead and report the verified absolute path. If neither local CODESTYLE nor `~/dev/configs/codex/instructions/CODESTYLE` can be read, mark codestyle guidance as blocked and continue only with the repo's discovered AGENTS instructions and explicit user directions.
```

## Validation Checklist

- Active instruction scope and discovery order identified.
- All moved pointers resolve.
- Contradictions are resolved or explicitly blocked for user choice.
- Binding memory, handoff, validation, approval, and security contracts are preserved.
- Subagent/review-swarm contract is present or deliberately preserved through a verified local equivalent.
- CODESTYLE route is present: local CODESTYLE, global fallback, or blocked note.
- Exact validation commands are reported with `pass`, `fail`, or `blocked`.
