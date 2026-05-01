---
name: he-brainstorm
description: Define problem scope, requirements, and decision options before spec or plan stages. Use when the user has ambiguity in what to build, why it matters, or which direction to choose.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps the full operational workflow in archived references. Use it to decide whether a structured Harness Engineering brainstorm is needed, run a right-sized clarification loop, and hand off with durable requirements when the idea is clear enough.

## Use

- Use this skill as normal for the Harness Engineering brainstorm stage.
- Use it before `he-spec` or `he-plan` when the work is still ambiguous.
- Use it when QA feedback reports confusing or "broken" behavior but the expected behavior is not yet clear enough for a Linear issue.
- If the request is already concrete enough for specification, planning, or direct execution, keep the interaction brief and recommend the next stage instead of forcing a brainstorm.
- Default a completed non-trivial brainstorm to `he-spec`; use `he-plan` only when the brainstorm output is already contract-grade, and use direct execution only for tiny, low-risk work.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Discover the right problem before proposing implementation.
- Keep options explicit, assumptions testable, and next-stage handoff safe.
- Resolve WHAT and WHY here; leave detailed HOW for later stages unless the brainstorm itself is architectural.

## When to use

- Use when scope is unclear, goals conflict, or candidate approaches need comparison.
- Use folded `he-ideate` mode when the request is mainly opportunity scanning, idea generation, or comparing possible directions; load the preserved context before producing options.
- Use before `he-spec` or `he-plan` when requirements are not yet stable.
- Use when the user asks to brainstorm, compare directions, sharpen requirements, or decide whether the idea needs a spec.
- Use when QA intake exposes product ambiguity that must be resolved before filing or implementing a bug.

## Inputs

- User intent, constraints, and current context artifacts.
- Relevant system boundaries, risks, and non-goals.
- If the core idea is missing, ask one direct question and do not proceed until the user supplies a feature, problem, or improvement to explore.

## Outputs

- Clarified requirements with ranked options and tradeoffs.
- A task-domain classification: software/system, UI/product, operations/process, content/docs, or mixed.
- A pressure-test result that names whether the problem should be solved now, simplified, deferred, or rejected.
- Domain-language notes when project-specific terms, aliases, relationships, or ambiguities affect the decision.
- Expected-behavior clarification for ambiguous QA reports, with a route to `he-fix-bugs`, `he-spec`, or `he-plan`.
- A recommendation on whether the next stage should be `he-spec`, `he-plan`, or direct execution; default to `he-spec` for non-trivial clarified work that still needs a WHAT/contract artifact.
- A right-sized requirements artifact when durable decisions exist, defaulting to `docs/brainstorms/YYYY-MM-DD-<topic>-requirements.md` for new substantial work.
- Requirements with stable `R1`, `R2`, ... identifiers, success criteria, scope boundaries, key decisions, dependencies or assumptions, and outstanding questions split into `Resolve Before Planning` and `Deferred to Planning`.
- Explicit `spec_required`, `risk_level`, and `complexity` values for non-trivial work.
- Recommended next Harness Engineering stage.
- Include `schema_version: 1`, `spec_required`, `risk_level`, and `complexity` in requirements artifact frontmatter.

## Procedure

1. Assess whether brainstorming is actually needed or whether the request is already clear enough for the next stage.
2. Classify the task domain and choose a lightweight, standard, or deep brainstorm scope before gathering detail.
3. Clarify objective, constraints, users, non-goals, and unknowns one question at a time.
4. Run a light repo/context scan before making claims about existing behavior or missing capabilities.
5. If domain language is fuzzy, read `CONTEXT-MAP.md` or `CONTEXT.md` when present, then resolve terms one focused question at a time before options harden.
6. Pressure-test whether the work should be solved now, simplified, deferred, or rejected; include the rationale when the answer changes scope.
7. For QA ambiguity, clarify expected behavior first, then route clear defects to `he-fix-bugs` for Linear intake or route missing contracts to `he-spec`.
8. Generate 2-3 concrete approaches when multiple plausible directions remain, then evaluate tradeoffs and recommend one. If only one path is credible, say why.
9. Derive `spec_required: none|lite|full`, `risk_level: low|medium|high`, and `complexity: small|medium|large` before handoff.
10. Capture durable requirements and `CONTEXT.md` updates only when the discussion produced decisions worth preserving.
11. When writing a requirements artifact, use stable requirement IDs, success criteria, scope boundaries, key decisions, dependencies or assumptions, and outstanding questions split into `Resolve Before Planning` and `Deferred to Planning`.
12. If any `Resolve Before Planning` item remains, ask the blocking question or stop with that blocker instead of handing off to `he-spec`, `he-plan`, or `he-work`.
13. Recommend the next Harness Engineering stage and stop instead of drifting into implementation planning. Use `he-spec` as the default next stage once requirements are clarified, unless the output is already contract-grade enough for `he-plan` or tiny enough for direct execution.

## Interaction Rules

- Ask one focused question at a time.
- Ask what the user is already thinking before steering the conversation.
- Start broad, then narrow: problem, users, value, constraints, exclusions, edge cases.
- Present options before the recommendation when alternatives are meaningful.
- Keep outputs concise and use repo-relative paths for any generated artifact references.

## Validation

- Ensure task-domain classification, pressure test, `spec_required`, `risk_level`, and `complexity` are present for non-trivial work.
- Ensure requirements and non-goals are explicit and testable.
- Ensure durable requirements use stable `R` IDs and identify success criteria, scope boundaries, key decisions, and material assumptions.
- Ensure `Resolve Before Planning` blockers are either resolved or explicitly block next-stage handoff.
- Ensure recommendation has rationale tied to constraints.
- Ensure any concrete claim about existing code, routes, tables, configs, or dependencies was verified against the repo or clearly labeled as an assumption.
- Ensure the brainstorm output is strong enough that the next stage does not need to invent user-facing behavior.
- Ensure canonical domain terms, avoided aliases, and unresolved ambiguities are captured or explicitly deferred before handoff.
- Ensure next-stage labels use current Harness Engineering names such as `he-spec`, `he-plan`, and `he-work`, not legacy `ce-*` labels.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not proceed to implementation planning when requirement ambiguity remains blocking.
- Do not force a brainstorm when the request is already well specified.
- Keep implementation details such as libraries, schemas, endpoints, and file layouts out of the requirements artifact unless the brainstorm is inherently technical.
- Use Linear issues or comments for durable decision capture; do not create ADRs.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Jumping to solution design before clarifying the actual problem.
- Asking a batch of unrelated questions in one turn.
- Returning unranked options without decision criteria.
- Skipping the pressure test and turning every idea into implementation work.
- Creating a new `*-brainstorm.md` artifact for substantial work instead of the default `*-requirements.md` artifact.
- Writing a requirements artifact that still leaves core behavior or scope boundaries undefined.
- Recommending `he-plan` while `spec_required` is `lite` or `full`, or while `Resolve Before Planning` contains blockers.
- Emitting stale `ce-spec`, `ce-plan`, or `ce-work` next-stage labels.
- Treating multiple names for the same project concept as harmless instead of choosing a canonical term.

## Examples

- "When the user asks for help thinking through a new approval flow before deciding whether it needs a spec."
- "User says, `Inspect the current admin onboarding and compare a few grounded directions before we commit.`"
- "Help me brainstorm this reporting feature and validate the best next Harness Engineering stage."
- "Can you help clarify what this QA feedback should mean before we file Linear bugs?"

## Full Context

- Full brainstorm guide: [./SKILL.full.md](./SKILL.full.md)
- Requirements artifact contract: [./references/requirements-artifact-guide.md](./references/requirements-artifact-guide.md)
- Brainstorm workflow details: [./references/brainstorm-workflow-details.md](./references/brainstorm-workflow-details.md)
- Discovery interview: [./references/discovery-interview.md](./references/discovery-interview.md)
- Document review pass: [./references/document-review-pass.md](./references/document-review-pass.md)
- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Domain model routing: [../../../references/domain-model-routing.md](../../../references/domain-model-routing.md)
- QA intake routing: [../../../references/qa-intake-routing.md](../../../references/qa-intake-routing.md)
- Folded `he-ideate` context: [../../../references/folded-skill-context.md](../../../references/folded-skill-context.md)
Read when: the user names `he-ideate`, asks to explore options, or needs opportunity comparison before requirements harden.
Read when: project terminology, `CONTEXT.md`, or Linear issue wording affects the brainstorm.
Read when: QA feedback is real but expected behavior is ambiguous enough that filing a bug would encode guesswork.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
