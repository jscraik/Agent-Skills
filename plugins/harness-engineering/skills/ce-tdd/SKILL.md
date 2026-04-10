---
name: ce-tdd
description: "Build behavior-safe code changes with TDD and RED/GREEN evidence. Use when ce-plan or ce-work requires TDD for a concrete behavior target."
metadata:
  skill-type: team_automation
  lifecycle_state: active
  maturity: validated
  owner: Agent Skills Team
  review_cadence: monthly
  last_reviewed: 2026-04-07
  metadata_source: frontmatter
---

# CE TDD

**Note: The current year is 2026.** Use this when dating execution artifacts and searching for recent documentation.

`ce-plan` defines **HOW** to build it. `ce-tdd` defines the **test-first execution posture**. `ce-work` is the execution container.

This workflow produces verified behavior through vertical tracer bullet slices. It does **not** produce plans, specs, or untested code.

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Acceptance criteria](#acceptance-criteria)
- [Interaction Method](#interaction-method)
- [Core Principles](#core-principles)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Encouraging variation](#encouraging-variation)
- [Examples](#examples)
- [References](#references)
- [See Also](#see-also)
- [Gotchas](#gotchas)

## Working agreement
- Treat `ce-tdd` as the test-first execution posture inside `ce-work`, not a standalone skill for generic testing advice.
- Every behavior change follows vertical tracer bullet slices: one test → one implementation → repeat. Never horizontal slices.
- Tests verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't break.
- The Red-Green-Refactor loop is non-negotiable. Never skip the RED verification gate.
- Keep each slice small enough that the feedback loop stays tight and evidence stays clear.
- Integrate with `ce-plan` acceptance IDs and `ce-work` execution tracking throughout.

## When to use
Use this skill when implementing behavior changes with a test-first posture inside `ce-work`, or when `ce-plan` specifies TDD as the execution posture.

Primary triggers:
- `ce-plan` handoff with `Execution note: test-first` or TDD posture
- `ce-work` Phase 3 with `test-first` execution posture signal
- "use TDD for this implementation"
- "red-green-refactor this feature"
- "write tests first, then implement"
- "vertical tracer bullets for this work"
- "implement this with test-first discipline"

Non-triggers:
- the user wants to write tests after implementation (post-hoc testing)
- the user wants pure documentation edits
- the user wants non-behavioral config changes that do not require tests
- the user wants generic testing advice without a behavior target; use `test-driven-development` instead
- the user wants a test strategy or test plan; that belongs in `ce-plan`

## Required inputs
- a concrete behavior target: acceptance criterion, bug reproduction, or plan unit with `Execution note: test-first`
- the relevant test command/framework for the repository
- the likely files or components involved in the change
- optional: linked `ce-plan` with `AC`/`UAC` IDs for traceability

If the behavior target is missing, ask one direct question:
- What behavior should the first test verify? Give me an acceptance criterion or describe what should be observable.

## Deliverables
- a clear Red-Green evidence trail per tracer bullet slice
- at least one meaningful failing test (RED) followed by a passing result (GREEN) per slice
- minimal implementation changes that make tests pass
- refactoring evidence when cleanup was applied after GREEN
- traceability back to `ce-plan` acceptance IDs when they exist
- a concise summary of what was tested, what behavior was proved, and what regression checks were run
- when a structured execution status is requested, include `schema_version: 1`

## Failure mode
If you cannot produce a meaningful failing test for the target behavior, stop and switch to specification or debugging work before editing more production code.

If the test framework is missing, misconfigured, or produces unreliable results, stop and fix the test infrastructure before entering the TDD loop.

## Constraints
- never write implementation before a failing test exists for the current slice
- never write all tests first and then all implementation (horizontal slicing is forbidden)
- tests must verify behavior through public interfaces only
- tests should survive internal refactors — if a test breaks when you rename an internal function but behavior hasn't changed, the test was wrong
- mock only at system boundaries (external APIs, databases, time/randomness), never mock your own classes or internal collaborators
- keep changes scoped to the intended behavior
- redact secrets, tokens, PII in test logs and snippets
- do not use TDD language to justify implementation-first work with missing evidence
- never refactor while RED — get to GREEN first

## Acceptance criteria
- every behavior change follows vertical tracer bullet slices, not horizontal batches
- each slice has documented RED → GREEN evidence
- tests describe WHAT (behavior), not HOW (implementation)
- tests use public interfaces only and would survive an internal refactor
- mocking is restricted to system boundaries
- refactoring happens only after GREEN, never while RED
- if linked to a `ce-plan`, each slice is traceable to an `AC` or `UAC` ID
- if any required gate fails, stop at the first failed gate and do not proceed until it is fixed

## Interaction Method

Use the platform's blocking question tool when available (`AskUserQuestion` in Claude Code, `request_user_input` in Codex, `ask_user` in Gemini). Otherwise, present numbered options in chat and wait for the user's reply before proceeding.

Ask one question at a time. Prefer concise single-select choices when natural options exist.

## Core Principles

1. **Vertical slices, not horizontal** — One test → one implementation → repeat. Never write all tests first, then all code.
2. **Tests define intent** — Implementation follows intent. Tests are the specification.
3. **Behavior, not implementation** — Tests should verify observable behavior through public interfaces.
4. **Small feedback loops** — Each tracer bullet proves one behavior. Small loops beat large speculative rewrites.
5. **Evidence before claims** — Never declare a behavior verified without RED → GREEN evidence.
6. **Deep modules** — Design interfaces with small surface area and deep implementation. Fewer methods = fewer tests needed = simpler system.

## Philosophy
- Tests should verify behavior through public interfaces, not implementation details. Code can change entirely; tests shouldn't.
- Good tests are integration-style: they exercise real code paths through public APIs. They describe _what_ the system does, not _how_.
- A good test reads like a specification — "user can checkout with valid cart" tells you exactly what capability exists.
- Bad tests are coupled to implementation. The warning sign: your test breaks when you refactor, but behavior hasn't changed.
- Small feedback loops beat large speculative rewrites.
- Evidence before claims.

Guiding questions:
- What observable behavior does this test verify?
- Would this test survive an internal refactor?
- Is this test using the public interface, or reaching into internals?
- Am I testing WHAT the system does, or HOW it does it?
- Which assumption is weakest and should be tested first?

## Workflow

When `[[ce-tdd]]` runs inside a `[[ce-work]]` execution lane:
- scope and approval come from the governing plan/spec/todo contract already established in `ce-work`
- this skill governs RED/GREEN tracer-bullet mechanics and evidence standards
- ask new user questions only when uncertainty would change scope, interface, architecture, or shipping risk

### Phase 1: Planning (before any code)

Before writing any code:
- Confirm with user what interface changes are needed
- Confirm which behaviors to test (prioritize — you can't test everything)
- Identify opportunities for deep modules (small interface, deep implementation)
- Design interfaces for testability (dependency injection, return results over side effects)
- If the user explicitly requests delegation, select reviewer lanes from `references/sub-agent-map.md` before fan-out.
- List the behaviors to test (not implementation steps)
- Confirm approval state per `../ce-work/references/approval-flow.md`

Ask: "What should the public interface look like? Which behaviors are most important to test?"

### Phase 2: Tracer Bullet (first vertical slice)

Write ONE test that confirms ONE thing about the system:

```
RED:   Write test for first behavior → run test → confirm it fails for the expected reason
GREEN: Write minimal code to pass → run test → confirm it passes
```

This is your tracer bullet — proves the path works end-to-end.

**Verification gates:**
1. Targeted RED run fails for the expected reason (not a syntax error or import failure)
2. Targeted GREEN run passes
3. Related regression checks pass

If any gate fails, stop and return to root-cause analysis.

### Phase 3: Incremental Loop (remaining slices)

For each remaining behavior:

```
RED:   Write next test → fails for expected reason
GREEN: Minimal code to pass → test passes
```

Rules:
- One test at a time
- Only enough code to pass current test
- Don't anticipate future tests
- Keep tests focused on observable behavior
- Update Linear issue or tracker at governing cadence (the governing artifact determines frequency; default per implementation unit/phase as defined in `../ce-work/references/execution-workflow.md`; per tracer bullet only when explicitly required)

### Phase 4: Refactor

After all tests pass for the current slice, look for refactor candidates:
- Extract duplication
- Deepen modules (move complexity behind simple interfaces)
- Apply SOLID principles where natural
- Consider what new code reveals about existing code
- Run tests after each refactor step

**Never refactor while RED.** Get to GREEN first.

### Phase 5: Record Evidence

Per cycle, verify:
- [ ] Test describes behavior, not implementation
- [ ] Test uses public interface only
- [ ] Test would survive internal refactor
- [ ] Code is minimal for this test
- [ ] No speculative features added
- [ ] RED and GREEN evidence captured
- [ ] RED and GREEN command outputs are captured with the expected failure/pass reasons

## Validation
Fail fast: **stop at the first failed gate** and do not proceed until fixed.

Required gates:
1. Targeted RED run fails for the expected reason
2. Targeted GREEN run passes
3. Related regression checks pass
4. If any gate fails, stop and return to root-cause analysis
5. Evidence exists for each RED → GREEN transition
6. No horizontal slicing occurred (all tests weren't written before implementation)

## Anti-patterns

### Horizontal Slicing (Critical)

**DO NOT write all tests first, then all implementation.** This is "horizontal slicing" — treating RED as "write all tests" and GREEN as "write all code."

This produces poor tests:
- Tests written in bulk test _imagined_ behavior, not _actual_ behavior
- You end up testing the _shape_ of things (data structures, function signatures) rather than user-facing behavior
- Tests become insensitive to real changes — they pass when behavior breaks, fail when behavior is fine
- You outrun your headlights, committing to test structure before understanding the implementation

```
WRONG (horizontal):
  RED:   test1, test2, test3, test4, test5
  GREEN: impl1, impl2, impl3, impl4, impl5

RIGHT (vertical):
  RED→GREEN: test1→impl1
  RED→GREEN: test2→impl2
  RED→GREEN: test3→impl3
```

### Other Anti-patterns
- Writing implementation before a failing test exists
- Declaring success without showing RED and GREEN evidence
- Bundling unrelated refactors during GREEN
- Using brittle timing assertions instead of behavior assertions
- Mocking internal collaborators instead of system boundaries
- Testing private methods or internal state
- Asserting on call counts/order of internal calls
- Test name describes HOW not WHAT
- Verifying through external means instead of public interface
- **NEVER** skip the RED verification gate
- **DO NOT** merge "just one quick change" outside the test-first loop
- **DON'T** call a fix complete without targeted regression evidence

## Encouraging variation
IMPORTANT: Outputs should vary based on the behavior under test, the risk level, and the repo context.
- Vary test granularity by risk: tiny unit tests for pure logic, integration tests for boundary behavior.
- Adapt assertion style to context-specific failure modes instead of repeating a generic template.
- Customize test data to reflect unique domain invariants; avoid repetitive cookie-cutter fixtures.
- Use different verification depth for small bugfixes versus larger refactors.
- Greenfield code gets strict TDD; legacy code may need characterization tests first.
- Do not converge on one pattern when a context-specific approach is safer.

## Examples
- User says: "Implement retry behavior for transient API failures using vertical tracer bullets and show RED→GREEN evidence each slice."
- User says: "Fix this cache invalidation bug with a failing regression test first, then the smallest possible fix."
- User says: "My plan unit `P2` has `Execution note: test-first`; run this in strict ce-tdd posture."
- User says: "Do red-green-refactor for auth session rotation and stop if a slice cannot produce a meaningful failing test."

## References
- Good and bad test examples: `references/tests.md`
- Mocking guidelines: `references/mocking.md`
- Deep module design: `references/deep-modules.md`
- Interface design for testability: `references/interface-design.md`
- Refactor candidates: `references/refactoring.md`
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Task profile: `references/task-profile.json`
- Source parity and likeness review: `references/source-parity.md`
- Sub-agent routing map: `references/sub-agent-map.md`
- Script extension guidance: `scripts/README.md`

## See Also

| Skill | When to use together |
|---|---|
| [[ce-work]] | ce-tdd is the test-first execution posture inside ce-work |
| [[ce-plan]] | ce-plan specifies TDD posture via `Execution note: test-first` |
| [[test-driven-development]] | Standalone TDD discipline for non-CE contexts |
| [[systematic-debugging]] | Run the TDD loop inside debugging workflow for each fix |
| [[verification-before-completion]] | Verify the full test suite is green before claiming done |

**Topic map:** [[agent-ops]]

## Gotchas
- Horizontal slicing is the most common failure mode. If you catch yourself writing more than one test before implementing, stop.
- A test that breaks when you refactor but behavior hasn't changed was testing implementation, not behavior. Delete it and write a better one.
- Mock at system boundaries only. If you're mocking your own code, redesign the interface instead.
- "Just one quick change" outside the loop is how TDD discipline erodes. Stay in the loop.