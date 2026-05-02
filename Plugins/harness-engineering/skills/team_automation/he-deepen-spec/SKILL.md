---
name: he-deepen-spec
description: Deepen an existing system or UI spec so boundaries, lifecycle rules, failure handling, and validation are strong enough for planning. Use when the user wants Harness Engineering spec hardening or a requirements review pass before planning.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Specifications must be executable contracts, not narrative placeholders.
- Resolve ambiguity before downstream planning and delivery.
- Domain language is part of the contract; specs are not planning-ready while project terms or relationships conflict.
- The first interface shape is rarely the best; compare meaningfully different caller-facing designs before locking a boundary.

## When to use

- Use when an existing spec needs tighter boundaries, contracts, and failure behavior.
- Use before planning when specification trust is not high enough.

## Inputs

- Existing specification plus related requirements and constraints.
- Interfaces, lifecycle assumptions, and validation expectations.

## Outputs

- Deepened specification with explicit boundaries, invariants, and acceptance criteria.
- A domain-consistency pass for project terms, aliases, relationships, code/spec contradictions, and unresolved ambiguities.
- An interface-design pass for any new or weak module/API boundary, including alternatives, usage examples, hidden complexity, and the selected shape.
- Clear readiness recommendation for planning.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Inspect current spec for ambiguity, missing edge cases, and contract gaps.
2. Run a domain-consistency pass against `CONTEXT-MAP.md` or `CONTEXT.md` when present, plus code and linked artifacts when they can verify term usage.
3. If the spec introduces or changes a module, API, CLI, plugin, tool, service, data-access, or shared-helper boundary, run an interface-design pass before planning readiness.
4. Generate at least two meaningfully different interface shapes, each with signature/call shape, caller usage example, what it hides internally, and tradeoffs.
5. Compare the shapes in prose for simplicity, flexibility, implementation efficiency, depth, and ease of correct use versus misuse.
6. Select or synthesize the final caller-facing contract, then deepen lifecycle behavior and failure handling around that contract.
7. Return readiness outcome and next stage recommendation.

## Domain Consistency Pass

- Use when a spec introduces project terms, reuses overloaded language, or disagrees with code/user wording.
- Prefer canonical terms from the relevant `CONTEXT.md`; list avoided aliases when they matter.
- Test boundaries with concrete scenarios when two concepts overlap.
- Update or request an update to `CONTEXT.md` when a term or relationship is resolved.
- Record hard-to-reverse domain decisions in Linear issue comments, not ADRs.

## Interface Design Pass

- Use when a spec names a boundary but callers, operations, or hidden complexity are still unclear.
- Prefer radically different shapes over minor naming variations.
- Keep evaluation focused on interface quality, not implementation effort.
- Treat shallow wrappers as suspect unless they hide meaningful complexity or stabilize a real dependency boundary.
- Block planning when a required interface shape is still unresolved.

## Validation

- Ensure acceptance criteria are testable and non-goals explicit.
- Ensure domain terms and relationships match the relevant `CONTEXT.md`, or unresolved conflicts are blocked before planning.
- Ensure interface alternatives were compared when the spec depends on a new or weak caller-facing boundary.
- Ensure operational, security, and rollback concerns are covered.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not silently alter core scope without explicit rationale.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Treating speculative assumptions as settled requirements.
- Passing a spec downstream when terminology conflicts remain unresolved.
- Comparing cosmetic variants instead of genuinely different interface shapes.
- Choosing an interface because it is easiest to implement rather than easiest to use correctly.
- Passing specs downstream with unresolved contract gaps.

## Examples

- "Can you deepen the export spec before planning because retries, ownership terms, and rollback behavior are still unclear?"
- "Please inspect the code, Linear issue, and `CONTEXT.md`; the code says `member`, Linear says `user`, and `CONTEXT.md` says `Customer`."
- "This spec adds a parser module boundary; can you validate two caller-facing APIs and choose the one that is easiest to use correctly?"

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Domain model routing: [../../../references/domain-model-routing.md](../../../references/domain-model-routing.md)
Read when: project terminology, `CONTEXT.md`, or Linear issue wording affects spec readiness.
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Call contract: [../../../references/subagent-call-contract.md](../../../references/subagent-call-contract.md)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, create or install them with [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) before rerunning delegated coverage.
