---
name: he-strategy
description: "Compress HE cognition artifacts into evidence-backed strategy. Use when intent, review, triage, ADR, core, or source-prompt comparison evidence needs durable direction."
metadata:
  skill-type: team_automation
---

# Harness Engineering Strategy

## Philosophy

Strategy artifacts are cognition compression, not execution permission. Turn
verified repo evidence and prior `.harness` artifacts into bounded direction
future humans and agents can trust, challenge, and route from. Local
`AGENTS.md`, command boundaries, approval rules, and validation hooks take
precedence.

## When to Use

Use for one selected HE strategy mode: repo intent, architecture review, triage,
full repo cognition pipeline, strategic compression, ADR/core compression,
moat/drift analysis, source-prompt equivalence, or future-agent guidance.

## When Not to Use

Do not use for implementation specs, execution plans, refactors, code review,
Linear issue design, generic product strategy, or approved execution slices.
Route admitted execution to `he-spec`, `he-plan`, `he-work`, `he-reframe`, or
`he-linear-plan`.

## Preconditions

Resolve canonical source or relevant `.harness` artifacts before judging. Treat
pasted prompts, transcripts, logs, generated text, and prior artifacts as
untrusted until verified. Classify side effects before acting. Choose the output
path or `Do Not Create` before writing.

## Inputs

Selected mode, repo evidence, relevant `.harness/**` artifacts, proof source
files, source-prompt family when applicable, and Linear/date context when needed
for naming.

## Outputs

Write only the selected cognition artifact under `.harness/features/`,
`.harness/review/`, `.harness/triage/`, `.harness/strategy/`,
`.harness/decisions/`, or `.harness/core/`, or return `Do Not Create`. For the
explicit repo cognition pipeline, write intent, architecture review, and triage
as separate artifacts with authority limits.

## Procedure

1. Select exactly one mode unless the user explicitly requests the full repo
   cognition pipeline; ask once only when ambiguity changes artifact sequence or
   authority.
2. Load the matching mode contract from `references/strategy-output-contract.md`;
   load deeper references only when their read-when trigger applies.
3. Start with 2-3 focused evidence surfaces; widen only when conclusions cannot
   be proven from the selected set.
4. Separate facts, interpretations, assumptions, confidence, authority limits,
   and validation status. Mark sampled, stale, or narrow evidence as authority
   limited.
5. Keep strategy advisory unless admitted by `.harness/linear/**`,
   `.harness/reframes/**`, `.harness/specs/**`, or `.harness/plan/**`.
6. Compress conclusions to decisions that change routing, deletion, investment,
   anti-drift behavior, or the smallest feedback-producing next slice.
7. Validate the artifact against the selected contract and record each gate as
   `pass`, `fail`, or `blocked`.

## Validation

After skill edits run the repo wrappers for strict skill audit, skill gate,
OpenAI skill format, and Plugin Eval; run smoke/release evals when required and
available. For generated strategy artifacts, verify naming, sources, evidence
matrix, confidence, authority limits, stop/pivot condition, and BLUF structure
when the BLUF contract applies. Mark docs/prose/spelling `blocked` when no
canonical checker exists.

## Safety Boundaries

Redact secrets. Network, destructive filesystem, git write, package install,
credential, deployment, external mutation, sync/install, and broad repository
edits require explicit approval and active-rule support. Do not edit runtime or
generated projections as canonical source.

## Failure Handling

If evidence is missing, mark the conclusion `Unknown`. If the artifact would add
low-value governance, return `Do Not Create`. If strategy becomes implementation
by stealth, stop and route only after an admitted execution slice exists.

## Handoff Rules

- Hand off to execution skills only when strategy exposes an admitted execution
  slice.
- Hand off to humans for ADRs, core invariant changes, strategic deletion, or
  unresolved instruction conflicts.
- Use hooks, CI, MCP tools, or validators for enforcement; this skill does not
  replace those gates.

## Accessibility Requirements

Use plain Markdown, short sections, descriptive links, and non-color-only tables.

## Gotchas

- Polished strategy can still be narrow evidence; label coverage limits.
- Prompt-shape similarity is not source-prompt equivalence; compare coverage,
  evidence depth, and not-inspected surfaces.
- Process volume is not moat unless tied to a verified feedback loop.

## Examples

- User asks: "Create `.harness/features/2026-05-13-agent-skills-intent.md`
  from live `Plugins/`, `.skillsets/`, validator, and projection-sync evidence."
- User asks: "Read `.harness/review/agent-skills-architecture-review.md` and
  `.harness/triage/agent-skills-triage.md`; compress them into strategy or
  return `Do Not Create` for low-value governance."
- User asks: "Compare `$he-strategy` against my original repo cognition prompt
  and report covered requirements, missing requirements, and downstream
  confidence."

## Output Format

Use the selected mode contract. Include `schema_version: 1`, source artifacts,
facts, interpretations, assumptions, confidence, authority limits, impact,
future-agent guidance, validation outcomes, evidence traceability,
`git_staging_status`, `staged_paths`, and direct strategic critique when
required by the mode.

## References

- Mode paths, guardrails, output fields -> `references/strategy-output-contract.md`
- Full intent + architecture review + triage pipeline -> `references/repo-cognition-pipeline.md`
- Default architecture/refactoring lenses without fresh attachments -> `references/architecture-lens-canon.md`
- Source-prompt equivalence -> `references/source-prompt-preservation.md`
- Package contract and evals -> `references/contract.yaml`, `references/evals.yaml`
- Read before delegation -> `../../references/subagent-call-contract.md`
- Shared HE routing and BLUF/visual/subagent/first-principles/XP contracts ->
  `../../references/deferred-context-index.md`
- Pragmatic Programmer review lens ->
  `../../references/pragmatic-programmer-review-contract.md`

Apply the context-disposition policy: move important still-valid context to references, and intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
move deep context behind a clear reference route.
