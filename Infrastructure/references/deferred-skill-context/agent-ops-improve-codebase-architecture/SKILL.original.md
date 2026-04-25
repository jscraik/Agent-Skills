---
name: improve-codebase-architecture
description: Review codebase architecture to find deeper module boundaries, sharper context language, and Linear-backed decision notes. Use when users ask to improve architecture, consolidate shallow modules, design better interfaces, improve testability, or make a repo easier for humans and agents to navigate.
metadata:
  skill-type: code_quality_review
---

# Improve Codebase Architecture

## When to use

Use this skill when a user asks for architecture improvement, module deepening, boundary cleanup, testability through better interfaces, codebase structure review, or a durable vocabulary for a specific domain context.

Use it before large refactors when the useful work is to find the right architectural move, not to immediately rewrite code.

Do not use it for ordinary cleanup of an existing diff, narrow bug fixes, generic documentation edits, or one-off naming questions. Use `[[simplify]]`, `[[docs-expert]]`, or `[[ubiquitous-language]]` for those.

## Goal

Surface numbered architecture opportunities that reduce cognitive load and increase leverage. A good result makes the code easier to understand, test, and change through deeper modules and sharper context language.

## Philosophy

- Deepen only where a module can hide meaningful complexity.
- Prefer local clarity over decorative architecture.
- Treat language as architecture: unclear domain terms create unclear boundaries.
- Use Linear as the durable memory surface for Jamie's architecture decisions.
- Preserve safety by redacting secrets, tokens, customer data, and sensitive logs from notes, examples, and Linear updates.

## Core Ideas

- **Deep module**: a module with a small interface and substantial hidden implementation complexity.
- **Shallow module**: a wrapper, helper, or abstraction that makes callers learn more code without hiding much complexity.
- **Interface**: the entry point callers and tests should rely on.
- **Seam**: a boundary worth naming only when it has at least two real implementations or a real dependency category.
- **Context language**: the project-specific terms that belong in `CONTEXT.md`, not generic programming vocabulary.

Read [references/architecture-language.md](./references/architecture-language.md) when term precision matters.

## Inputs

- Repository path and optional focus area.
- Existing `CONTEXT.md` or `CONTEXT-MAP.md` if present.
- Existing Linear issue, project, workpad, or branch name when the work is already tracked.
- Relevant docs, tests, recent diffs, and module entry points.
- Existing ADRs only as historical evidence when the repo already has them; do not create new ADRs by default.

## Outputs

- Numbered architecture opportunities with files, problems, proposed directions, risks, and validation paths.
- `CONTEXT.md` or `CONTEXT-MAP.md` updates when project-specific language is resolved.
- Linear decision notes for durable decisions or rejected options that meet the capture criteria.
- Interface alternatives after the user chooses a direction.
- Exact validation outcomes after any implementation.

## Deliverables

For a review-only pass, deliver a ranked opportunity list and a recommendation about which item to explore first.

For an implementation pass, deliver the scoped code change, context-language updates when needed, Linear persistence status, and exact validation command results.

## Workflow

1. Scope the request and read active repo instructions.
2. Discover context language:
   - If `CONTEXT-MAP.md` exists, read it and select the matching context.
   - If root `CONTEXT.md` exists, treat the repo as a single context.
   - If neither exists, proceed silently and create root `CONTEXT.md` only when a project-specific term is actually resolved.
3. Inspect Linear evidence when available:
   - Read the current issue or workpad if the user names one or the branch clearly maps to one.
   - Treat Linear as the durable decision surface for this user's projects.
   - Do not create `docs/adr/**` unless the user explicitly asks or a repo instruction requires ADRs.
4. Explore the code and docs with repo-native tools:
   - Map module boundaries, public entry points, tests, and callers.
   - Use `rg`, `git diff`, test files, README/docs, package manifests, route maps, and schema files.
   - Use a bounded subagent only when the repo surface is too broad for one pass.
5. Look for deepening opportunities:
   - Understanding one concept requires bouncing between many small modules.
   - Helpers or wrappers fail the deletion test: deleting them makes the code clearer.
   - Tests target extracted pure functions while real bugs live in call orchestration.
   - Boundaries leak internal details, lifecycle states, persistence shapes, or remote API concerns.
   - A seam exists for a hypothetical second implementation rather than a current need.
   - A module is hard to test through the interface users actually depend on.
6. Present opportunities before implementation:
   - Number each opportunity.
   - Include `Files`, `Problem`, `Proposed direction`, `Benefits`, `Risk`, and `Validation`.
   - Explain benefits with locality, leverage, and testability.
   - Use `CONTEXT.md` terms when they exist, and flag missing or overloaded terms.
   - Do not design detailed interfaces yet. Ask which opportunity to explore.
7. Grill the chosen opportunity:
   - Test constraints, callers, dependency categories, reversibility, and failure modes.
   - Update or propose `CONTEXT.md` language when a new domain term or boundary becomes clear.
   - Record load-bearing decisions in Linear using [references/linear-decision-capture.md](./references/linear-decision-capture.md).
8. Design interfaces only after the user chooses a direction:
   - Use [references/interface-design.md](./references/interface-design.md).
   - Compare at least three materially different interface shapes for broad or risky changes.
   - Recommend one option and explain the trade-off.
9. Implement only when asked:
   - Keep the change scoped to the chosen opportunity.
   - Prefer replacing shallow test surfaces with tests at the deeper module interface.
   - Validate with the repo's normal fast gate plus any focused tests.

## CONTEXT.md Rules

Use [references/context-format.md](./references/context-format.md) when creating or updating context language.

Minimum rules:

- Include only project-specific domain or operator concepts.
- Pick one canonical term and list aliases to avoid.
- Keep definitions to one sentence that says what the thing is.
- Show relationships and cardinality when obvious.
- Include example dialogue between a developer and domain expert.
- Flag ambiguities explicitly with a resolution or open question.

## Linear Decision Capture

For Jamie's projects, Linear replaces ADRs as the default durable decision memory.

Record a decision in Linear only when all three are true:

- The decision is hard to reverse.
- A future reader would find the code surprising without context.
- The choice involved a real trade-off.

Preferred order:

1. Update the current Linear issue or workpad.
2. If no issue exists and Linear access is available, create a small follow-up issue in the appropriate team/project.
3. If Linear is unavailable, include a `Linear decision note` in the final response and say it was not persisted.

Never create `docs/adr/` from this skill unless the user explicitly asks for ADRs or a binding repo instruction requires them.

## Output Format

For an opportunity review:

- `schema_version`: include this when output is structured or schema-bound.
- `Architecture Opportunities`: numbered list.
- `Files`: exact paths.
- `Problem`: one paragraph.
- `Proposed direction`: one paragraph.
- `Benefits`: locality, leverage, and testability.
- `Risk`: main risk or `low`.
- `Validation`: focused tests and repo gates.

For a chosen direction, add:

- `Chosen Direction`: one-sentence decision.
- `Context language`: `CONTEXT.md` updates or `none`.
- `Linear decision note`: updated issue/comment, created issue, not needed, or not persisted.
- `Validation`: exact commands and outcomes.

## Validation

When authoring or changing this skill, run:

- `./bin/ask skills audit Skills/agent-ops/improve-codebase-architecture --level strict --json`
- `bash Infrastructure/scripts/lint_progressive_disclosure.sh --mode strict`
- `git diff --check -- Skills/agent-ops/improve-codebase-architecture`

When using this skill on a project, validate according to the target repo's instructions and report exact pass, fail, or blocked outcomes.

Fail fast: stop at the first failed gate, fix the cause, and rerun the failed gate before proceeding to broader validation.

## Constraints

- Do not treat generic programming terms as context language.
- Do not create ADRs by default.
- Do not invent Linear issue IDs, project names, or persisted decisions.
- Do not begin a major refactor from a broad architecture review until the user chooses a specific opportunity.
- Do not add an adapter or interface for a hypothetical second implementation.
- Do not preserve shallow-module tests when a deeper interface test covers the same behavior more clearly.
- Do not hide uncertainty; flag ambiguous terminology and unresolved boundaries.
- Redact secrets, credentials, private customer data, and sensitive logs from outputs and Linear notes.

## Anti-patterns

- Starting a broad refactor from an architecture review without a chosen opportunity.
- Creating ADR files by habit when Linear is the requested decision surface.
- Adding a seam for a dependency that has only one real implementation and no dependency-category pressure.
- Filling `CONTEXT.md` with generic programming words.
- Keeping helper-level tests as the main confidence surface after behavior has moved behind a deeper interface.
- Copying raw logs, secrets, or private data into examples, notes, or Linear.

## References

Read only the references needed for the request:

| Reference | Read when |
| --- | --- |
| [references/architecture-language.md](./references/architecture-language.md) | You need precise terms for modules, seams, depth, locality, or leverage. |
| [references/context-format.md](./references/context-format.md) | You are creating or updating `CONTEXT.md` or `CONTEXT-MAP.md`. |
| [references/deepening-playbook.md](./references/deepening-playbook.md) | You are evaluating whether a module should be deepened, collapsed, or tested differently. |
| [references/interface-design.md](./references/interface-design.md) | The user picked a direction and wants interface alternatives. |
| [references/linear-decision-capture.md](./references/linear-decision-capture.md) | A decision or rejected alternative needs durable memory in Linear. |
| [references/contract.yaml](./references/contract.yaml) | Checking triggers, outputs, risks, and rollback behavior. |
| [references/evals.yaml](./references/evals.yaml) | Updating routing examples or expected skill-selection behavior. |
| [references/task-profile.json](./references/task-profile.json) | Inspecting machine-readable task-profile metadata. |

## Examples

- User says: "I'm in `apps/api/src/checkout` and the returns work is turning into five tiny helpers. Can you review the architecture and tell me which boundary should own returns?"
- User says: "In the `billing-stripe` branch, Fulfillment is reading Stripe payload fields directly. Please find the boundary leak and update `CONTEXT.md` if our Billing/Fulfillment terms are wrong."
- User says: "For LIN-482, we picked domain events instead of HTTP between Billing and Fulfillment. Can you record the reason on Linear and avoid adding an ADR?"
- User says: "`packages/orders/src/submitOrder.ts` is the path I want to fix. Please show three interface shapes before changing it."
- User says: "The `orders` tests cover `parseLineItem` and `buildTotals`, but production bugs happen in order submission. Can you find the deeper interface we should test?"

## Failure mode

- If the repo is too large to review safely in one pass, narrow to one bounded context or return a staged review plan.
- If Linear is unavailable, include the decision note in the final response and mark it as not persisted.
- If `CONTEXT.md` language is ambiguous, ask one focused question or mark the ambiguity instead of inventing a term.
- If validation fails, stop and report the exact failed command and blocker.

## See Also

| Skill | Why |
| --- | --- |
| [[ubiquitous-language]] | Use for broader shared vocabulary and prompt translation outside architecture work. |
| [[simplify]] | Use for maintainability cleanup of an existing diff after the architecture direction is known. |
| [[docs-expert]] | Use when the chosen architecture needs broader docs or runbook updates. |

**Topic map:** [[agent-ops]], [[architecture]], [[code-quality]]
