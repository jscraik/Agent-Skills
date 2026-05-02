# Harness Engineering Plan Doctrine

This retained doctrine preserves the context used to harden `he-plan` without loading it into every invocation.

## Sources Synthesized

- `SKILL (14).md`: universal planning workflow, source handling, synthesis, depth, local/external research, plan template, confidence checks, and handoff.
- `universal-planning.md`: non-software planning classification, research need, domain-appropriate plan shape, and save/share handling.
- `synthesis-summary (1).md`: Stated/Inferred/Out-of-scope checkpoint, headless assumptions routing, and complete-replacement revision discipline.
- `plan-handoff.md`: mandatory document review after confidence checks, final options, tracker handoff, and stale-review handling.
- `deepening-workflow.md`: confidence-gap scoring, targeted reviewer dispatch, direct vs artifact-backed research, and accepted-finding integration.
- `visual-communication (1).md`: dependency graphs, interaction diagrams, comparison tables, and visual anti-patterns.
- `testing-anti-patterns.md`: real-behavior tests, mock discipline, complete mocks, and no test-only production methods.
- `SKILL (12).md` and `SKILL (13).md`: useful TDD and execution-handoff ideas, adapted away from micro-step code plans.
- `plan-document-reviewer-prompt.md`: implementation-readiness review rubric.
- Live `/Users/jamiecraik/dev/codex` and codex-repo MCP: Codex Plan Mode behavior, `update_plan` distinction, `request_user_input` semantics, proposed-plan rendering, and implementation confirmation flow.

## Transferable Codex Plan Mode Lessons

Plan Mode works because it separates exploration, intent, and implementation shape:

1. Ground in the environment first. Discover repo facts, patterns, configs, and schemas before asking.
2. Ask only when the answer changes scope, architecture, sequencing, risk, or an assumption.
3. Treat discoverable facts and preferences differently.
4. Avoid mutation while planning. Planning may inspect, search, and run non-mutating checks, but implementation belongs elsewhere.
5. Keep `update_plan` separate from plan mode. It is a live checklist/progress tool, not the durable plan artifact.
6. Final plans should be complete replacement artifacts. Partial deltas are easy for downstream agents to misapply.

Codex chat uses `<proposed_plan>` to render approved plan text and can offer "implement this plan" or "clear context and implement" actions. Harness Engineering should not require that wrapper inside saved plan files, but it should preserve the underlying behavior: clear handoff, complete artifact, and a fresh-context implementation option when context pressure is high.

## HE Plan Shape

A Harness Engineering plan is ready when another agent can implement it without making product or architecture decisions. It should include:

- problem frame and scope boundary
- source traceability to Linear/spec/requirements/brainstorm/UI criteria
- stable unit IDs and stable acceptance IDs
- dependencies and blocker order
- repo-relative file paths
- test file paths and concrete scenarios
- validation outcomes, rollout notes, rollback notes, and residual risks
- Linear/spec/plan/PR evidence matrix for tracked work

The plan should not include copy-paste implementation code, exact shell choreography, commit commands, or RED/GREEN/REFACTOR micro-steps. It may include directional sketches, diagrams, or pseudocode when they help reviewers validate shape, but those must be explicitly non-prescriptive.

## Source Resolution

Prefer the strongest source in this order:

1. Existing plan path or obvious current plan to resume.
2. Active Linear issue and related parent/child/blocking issue graph.
3. Requirements or brainstorm document with acceptance examples and scope boundaries.
4. Approved spec or UI spec.
5. Direct feature, bug, refactor, or improvement description.

If the source has unresolved product blockers, route back to `he-brainstorm` or `he-spec`. If the source has technical questions that planning can resolve through repo or docs research, resolve them during planning. If the answer depends on writing code, running changed behavior, or seeing test failures, record it as a deferred implementation note.

## Depth And Research

Use the smallest depth that protects delivery:

- Lightweight: compact plan, low ambiguity, straight-line dependencies.
- Standard: normal feature/refactor/bug with meaningful decisions and validation.
- Deep: cross-cutting, risky, ambiguous, migration/security/privacy/payment/external API work, or work touching external contract surfaces.

Local research always comes first. External research is warranted for high-risk domains, third-party APIs, missing local patterns, current framework behavior, or unfamiliar territory. Skip external research when local patterns are strong, recent, and directly applicable.

Reclassify lightweight work to standard when it touches environment variables, public APIs, CLI flags, CI, shared types, or externally consumed docs.

## Synthesis And Assumptions

Use Stated, Inferred, and Out-of-scope checkpoints when the agent has made consequential assumptions. In interactive work, revise and re-present after user changes until explicitly confirmed. In headless work, put unconfirmed Inferred bets in `## Assumptions` so reviewers and `he-work` can scrutinize them.

## Deepening

Deepen only where confidence gaps are real. Score sections by missing rationale, weak source grounding, vague units, bad sequencing, shallow tests, hidden blockers, weak rollout, and missing system impact. Dispatch targeted reviewers only for the section/risk being strengthened.

Deepening should make the plan stronger, not longer.

## Testing Guidance

Plans must require real behavior tests. Avoid test scenarios that only assert mocks, snapshots of mocked children, or implementation internals. Include happy path, edge case, error path, and integration scenarios only where they genuinely apply.

For non-feature units, use an explicit no-test rationale rather than leaving tests blank.

## Visual Guidance

Use visuals when they reduce reader work:

- dependency graph for non-linear unit dependencies
- interaction diagram for three or more affected surfaces
- comparison table for modes, variants, or alternatives
- state diagram for state-heavy lifecycle

Skip visuals that duplicate prose or smuggle implementation detail into the plan.

## Handoff

After the plan is complete, hand off to:

- `he-work` for implementation
- Linear workflow when creating or updating tracked work
- `he-deepen-plan` or document review when confidence gaps remain

Do not auto-implement from `he-plan`. The handoff can recommend the next workflow, but the planning skill itself remains plan-only.
