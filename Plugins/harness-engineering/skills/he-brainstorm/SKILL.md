---
name: he-brainstorm
description: "Analyze Harness Engineering ambiguity into evidence-labeled survivor options, risks, and stage routing. Use when a user asks to brainstorm, compare approaches, choose a direction, recover constraints, or decide whether work belongs in spec, plan, Linear, or implementation."
metadata:
  version: 1.0.0
  skill-type: team_automation
---

# Harness Engineering Brainstorm

## Philosophy
Make ambiguity useful without ceremony. Context preservation means keeping
Stated facts, Inferred bets, guesses, Out of scope work, rejected ideas, and
blockers visible so the routed HE stage can continue from evidence.

## When To Use
Use before commitment when intent, terminology, expected behavior, tradeoffs,
scope, idea quality, or the next HE stage is unsettled. Use folded `he-ideate`
mode when the user asks what to improve, wants options, wants weak ideas
filtered, or wants dropped leverage recovered before selecting a route.

## When Not To Use
Do not use for selected execution slices, direct implementation, concrete bug
fixes, approved specs, or approved plans. Route those to the matching HE stage.

## Inputs
User goal, identifiable subject, repo/Linear/session/`.harness` evidence,
constraints, rejected ideas, and success criteria.

## Procedure
1. Identify the subject. If it is missing, return a blocked brainstorm frame
   with the smallest safe recovery step.
2. Inspect cited repo, Linear, session, or `.harness` evidence before treating
   it as fact.
3. Separate stated facts, interpretations, guesses, and out-of-scope work.
4. Start with 2-3 focused surfaces; widen only when evidence shows the decision
   spans more than those surfaces.
5. Produce 2-5 survivor routes with warrants, risks, scope tier, and the next
   HE stage.
6. Before durable handoff for tracked work, resolve or block the Linear/tracker
   gate.
7. If an artifact is written, place brainstorms under `.harness/brainstorm/**`
   and folded ideation under `.harness/ideate/**`, then validate the artifact.

## Output Format
Return `schema_version`, `mode`, `scope_tier`, `stated`, `inferred`,
`guesses`, `out_of_scope`, `options_or_survivors`, `warrants`, `risks`,
`validation`, `blackboard_delta`, `artifact_path`, `next_stage`, and
`blocked_reason` when blocked.

Example output: `schema_version: he.brainstorm.v1`, `mode: brainstorm`,
`scope_tier: standard`, `stated: [JSC-246 needs a closure decision]`,
`inferred: [tracker mutation is unsafe until authority is explicit]`,
`options_or_survivors: [{route: he-reconcile, warrant: evidence is scattered}]`,
`validation: blocked`, `blocked_reason: Linear authority not verified`,
`next_stage: he-reconcile`.

## Validation
Fail fast on missing scope, traceability, evidence labels, tracker gate,
artifact route, handoff clarity, or unverified command/web/repo/Linear claims.
Report `pass`, `fail`, or `blocked`.

For non-trivial generated artifacts, run or block
`python3 Plugins/harness-engineering/scripts/check_bluf_structure.py <path> --json`.

## Guardrails
Non-mutating except for approved `.harness/brainstorm/**` or
`.harness/ideate/**` artifacts. Do not convert survivors into specs, plans,
Linear work, repo edits, external writes, or implementation without handoff
authority. Redact secrets and private transcripts. Keep guesses labeled as
guesses.

## Execution Boundaries
Classify side effects before acting: read-only, `.harness` artifact write,
external write, repo write, or destructive. Local `AGENTS.md`, rules, hooks,
command boundaries, and approval gates outrank this skill.

## Failure Handling
If required evidence, Linear linkage, next-stage routing, artifact destination,
tool availability, or authority is missing, stop with the blocker and smallest
recovery step. When one answer would unblock survivor selection, ask once;
otherwise set `validation: blocked` with a concrete recovery action.

## Handoff Rules
Hand off to `he-spec` for acceptance criteria, `he-plan` for an approved spec or
execution strategy, `he-work` for implementation, `he-review` for review, or
done when ambiguity is resolved. Do not hand off to planning while behavior or
domain terms remain ambiguous.

## Examples
- When the user asks, "Inspect `.harness/session-evidence/latest.md` and decide whether JSC-246 belongs in spec, Linear plan, or implementation", return stated facts, inferred bets, 2-3 survivor routes, blocked assumptions, and `next_stage`.
- When the user asks, "Inspect `.harness/review-log.md`; can we close JSC-246 from this evidence?", keep tracker mutation blocked unless proof and authority are explicit; return the evidence gap, recovery step, and route to `he-reconcile` or `he-linear-plan`.

## Gotchas
- Guesses must stay labeled as guesses.
- Survivor selection can require a user choice when it shapes downstream scope.
- Use `assets/` only for local skill packaging and browseability.

## Constraints
Do not turn brainstorming into execution. Do not drop useful context to save
tokens; move it to references and link the route.
Apply the context-disposition policy: move important still-valid context to
references, and intentionally discard stale, duplicated, unsafe, superseded, or
low-signal text.

## References
- [Brainstorm workflow details](references/brainstorm-workflow-details.md): intake, discovery, divergence, synthesis, handoff.
- [Ideation mode](references/ideation-mode.md): folded `he-ideate` candidate generation and survivor filtering.
- [Requirements artifact guide](references/requirements-artifact-guide.md): durable requirement boundaries before spec handoff.
- [Discovery interview](references/discovery-interview.md): focused user questions when interaction is available.
- [Document review pass](references/document-review-pass.md): final handoff review before durable artifacts.
- [Visual communication](references/visual-communication.md): diagrams or visual output guidance.
- [Folded context](references/hot-path-folded-context.md): expanded procedure, failure handling, examples, and reference routing.
- [Contract](references/contract.yaml), [evals](references/evals.yaml), and [task profile](references/task-profile.json): local validation, evaluation, and routing metadata.
- Shared HE policies, when their topic is active:
  `../../references/visual-reference-contract.md`,
  `../../references/subagent-call-contract.md`, and
  `../../references/deferred-context-index.md`.
