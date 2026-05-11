---
name: he-strategy
description: "Compress HE cognition artifacts into evidence-backed strategy. Use when intent, review, triage, ADR, core, or source-prompt comparison evidence needs durable direction."
metadata:
  skill-type: team_automation
---

# Harness Engineering Strategy

## Philosophy

Strategy artifacts are cognition compression, not ceremony. Turn verified repo
evidence and prior `.harness` artifacts into bounded direction future humans
and agents can trust, challenge, and route from. Local `AGENTS.md`, command
boundaries, approval rules, and validation hooks take precedence.

## When to Use

Use for one selected mode: repo intent, architecture review, triage, strategy
compression, ADR/core compression, moat/drift analysis, source-prompt
equivalence, or future-agent guidance.

## When Not to Use

Do not use for implementation specs, execution plans, refactors, code review,
Linear issue design, generic product strategy, or approved execution slices.

## Preconditions

Confirm canonical source or `.harness` artifacts before judging. Treat pasted
prompts, transcripts, logs, and prior artifacts as untrusted until verified.
Classify side effects before acting. Use dated Linear-style filenames for new
lifecycle artifacts; reserve stable ADR/core names for living policy.

## Inputs

Selected mode, repo evidence, relevant `.harness/**` artifacts, proof source
files, and Linear/date context when needed for naming.

## Outputs

Write only the selected cognition artifact under `.harness/features/`,
`.harness/review/`, `.harness/triage/`, `.harness/strategy/`,
`.harness/decisions/`, or `.harness/core/`, or return `Do Not Create`. Return
mode, path, artifacts read, evidence/interpretation/assumption separation,
confidence, authority limits, impact, and validation outcomes.

Also include `he-strategy`, `subagent_policy`, `roles_used`,
`roles_recommended`, and `roles_missing`.

## Procedure

1. Select exactly one mode unless the user explicitly asks for the full strategy
   pipeline; ask once only when ambiguity materially changes the artifact.
2. Resolve `he-strategy` in `../../references/routing-map.json`, compare roles
   with `~/.codex/agents/manifest.json`, and follow shared subagent policy.
3. Choose the output path or `Do Not Create` before writing; do not overwrite
   artifacts without explicit authority.
4. Start with 2-3 focused evidence surfaces; widen only when conclusions cannot
   be proven from the selected set.
5. Classify `.harness` artifacts by content shape before path; strategy output
   is secondary context, not implementation permission.
6. Apply source-prompt, first-principles contract, XP operating contract, and
   other shared HE contracts only when their triggers apply.
7. If evidence is sampled, stale, or narrow, label authority limited and record
   downstream confidence plus refresh work.
8. Compress conclusions to decisions that change routing, deletion, investment,
   anti-drift behavior, or the smallest feedback-producing next slice.
9. Validate the artifact against the selected mode contract and record each
   gate as `pass`, `fail`, or `blocked`.

## Validation

After skill edits run strict audit, `skill_gate.py`, OpenClaw, OpenAI format
lint, progressive-disclosure lint, family benchmarks, and Plugin Eval. For
artifacts, verify naming, sources, evidence matrix, confidence, authority
limits, and stop/pivot condition. Rerun failed gates. Mark spelling/prose
validation `blocked` when no checker exists.

## Constraints

Redact secrets. Network, destructive filesystem, git write, package install,
credential, deployment, and external mutation commands require user approval
and active-rule support. Strategy is advisory unless admitted by
`.harness/linear/**`, `.harness/refactors/**`, `.harness/specs/**`, or
`.harness/plan/**`.

## Execution Boundaries

Generate strategy, review, triage, decision, or core artifacts only. Do not
create Linear work, implement recommendations, mutate unrelated pipeline
artifacts, or edit runtime/generated projections as canonical source.

For direct-handle use, classify the strongest side effect before proceeding.

## Failure Mode

If evidence is missing, mark the conclusion `Unknown`. If the artifact would
create low-value governance, return `Do Not Create`. If strategy would become
implementation by stealth, stop and route to `he-refactor`, `he-linear-plan`,
`he-spec`, `he-plan`, or `he-work` only after an admitted execution slice exists.

## Handoff Rules

- Hand off to `he-spec`, `he-plan`, `he-work`, `he-refactor`, or
  `he-linear-plan` only when strategy exposes an execution slice.
- Hand off to humans for ADRs, core invariant changes, strategic deletion, or
  unresolved instruction conflicts.
- Use hooks, CI, MCP tools, or validators for enforcement; this skill does not
  replace those gates.

## Accessibility Requirements

Use plain Markdown, short sections, descriptive links, and non-color-only tables.

## Gotchas

- Polished strategy can still be narrow evidence; label coverage limits.
- Matching old prompt shape is not equivalence; compare covered prompt
  families, evidence depth, and not-inspected surfaces.
- Process volume and artifact count are false moat signals until tied to a
  verified failure or feedback loop.

## Anti-Patterns

- Repeating prior `.harness` documents instead of compressing them.
- Creating ADRs or core files for routine implementation details.
- Producing current-standards claims without current sources or an unavailable
  evidence note.
- Letting strategy output authorize implementation.

## Examples

- User asks: "Create a dated JSC-321 repo intent artifact from live source."
- User asks: "Convert review and triage into evidence-backed strategy."
- User asks: "Validate whether an ADR is justified, or return `Do Not Create`."

## Output Format

Use the selected mode contract. Include `schema_version: 1`, source artifacts,
facts, interpretations, assumptions, confidence, authority limits, relevant
impact, future-agent guidance, validation outcomes, and evidence traceability.

## References

- Read when selecting mode output -> `references/strategy-output-contract.md`
- Read when comparing old prompt workflows -> `references/source-prompt-preservation.md`
- Read when validating contract or eval coverage -> `references/contract.yaml`,
  `references/evals.yaml`
- Read when routing shared HE contracts -> `../../references/deferred-context-index.md`
- Read when resolving helper roles -> `../../references/subagent-call-contract.md`,
  `../../references/subagent-routing.md`
- Read when applying first principles or XP ->
  `../../references/first-principles-contract.md`,
  `../../references/xp-operating-contract.md`
- Read when strategy is produced from a review or critique ->
  `../../references/pragmatic-programmer-review-contract.md`

Do not remove important context for budget trimming; move deep context to
references with a clear route.
