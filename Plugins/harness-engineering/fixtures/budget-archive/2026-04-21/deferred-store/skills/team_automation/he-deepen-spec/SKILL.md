---
name: he-deepen-spec
description: Improve an existing Harness Engineering spec with missing behavior, boundaries, domain terms, and acceptance criteria. Use when a user asks to deepen or complete a spec before planning.
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Philosophy

- Specifications must be executable contracts, not narrative placeholders.
- Resolve ambiguity before downstream planning and delivery.
- Domain language is part of the contract; specs are not planning-ready while project terms or relationships conflict.
- The first interface shape is rarely the best; compare meaningfully different caller-facing designs before locking a boundary.

## When to use

- Use when an existing spec needs tighter boundaries, contracts, and failure behavior.
- Use before planning when specification trust is not high enough.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

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
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Treating speculative assumptions as settled requirements.
- Passing a spec downstream when terminology conflicts remain unresolved.
- Comparing cosmetic variants instead of genuinely different interface shapes.
- Choosing an interface because it is easiest to implement rather than easiest to use correctly.
- Passing specs downstream with unresolved contract gaps.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
