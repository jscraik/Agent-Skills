---
name: test-driven-development
description: "Create test-first Red-Green-Refactor delivery for behavior changes. Use when implementing a feature or bugfix before writing production code."
knowledge_graph_profile: references/task-profile.json
---

# Test-Driven Development

## Table of Contents
- [Usage triggers](#usage-triggers)
- [Required context and assumptions](#required-context-and-assumptions)
- [Deliverables and results](#deliverables-and-results)
- [Workflow](#workflow)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Constraints and safety](#constraints-and-safety)
- [Philosophy](#philosophy)
- [Variation and adaptation](#variation-and-adaptation)
- [Empowering execution style](#empowering-execution-style)
- [Examples](#examples)
- [References](#references)

## Usage triggers
Use this skill when:
- Implementing new behavior.
- Fixing regressions or bugs.
- Refactoring behavior-sensitive logic.

Do not use this skill for:
- Pure documentation edits.
- Non-behavioral config changes that do not require tests.

## Required context and assumptions
- Clear behavior target (acceptance criteria or bug reproduction).
- Test framework command for the repository.
- File paths likely involved.

## Deliverables and results
- One or more failing tests that prove the target behavior.
- Minimal implementation changes that make tests pass.
- Evidence of Red -> Green transitions.
- Concise summary of what was tested and why.

## Workflow
1. **Define the behavior**
   - State the observable outcome before editing code.
2. **RED: write failing test first**
   - Add the smallest focused test for one behavior.
3. **Verify RED**
   - Run the targeted test and confirm expected failure reason.
4. **GREEN: write minimal implementation**
   - Add only the code needed for the failing test.
5. **Verify GREEN**
   - Re-run targeted tests, then nearby suite for regressions.
6. **REFACTOR**
   - Improve clarity without changing behavior.
   - Re-run tests after each refactor change.
7. **Record evidence**
   - Capture commands and pass/fail outcomes.

## Validation
Fail fast: **stop at the first failed gate** and do not proceed until fixed.

Required gates:
1. Targeted RED run fails for the expected reason.
2. Targeted GREEN run passes.
3. Related regression checks pass.
4. If any gate fails, stop and return to root-cause analysis.

## Anti-patterns
- Writing implementation before a failing test exists.
- Declaring success without showing RED and GREEN evidence.
- Bundling unrelated refactors during GREEN.
- Using brittle timing assertions instead of behavior assertions.
- **NEVER** skip the RED verification gate.
- **DO NOT** merge “just one quick change” outside the test-first loop.
- **DON'T** call a fix complete without targeted regression evidence.

## Constraints and safety
- Redact secrets/tokens/PII in test logs and snippets.
- Avoid destructive repo operations unless explicitly requested.
- Keep changes scoped to the intended behavior.

## Philosophy
- Tests define intent; implementation follows intent.
- Small feedback loops beat large speculative rewrites.
- Evidence before claims.
- Why this approach? It lowers rework cost by validating behavior continuously.
- What tradeoff matters most: speed now or correctness later?
- Which assumption is weakest and should be tested first?

## Variation and adaptation
- Vary test granularity by risk: tiny unit tests for pure logic, different integration tests for boundary behavior.
- Adapt assertion style to context-specific failure modes instead of repeating a generic template.
- Customize test data to reflect unique domain invariants; avoid repetitive cookie-cutter fixtures.
- Use different verification depth for small bugfixes versus larger refactors.
- Do not converge on one pattern when a context-specific approach is safer.

## Empowering execution style
- You are capable of driving high-confidence delivery with small, evidence-backed loops.
- Use this workflow to unlock faster iteration without sacrificing quality.
- Explore creative but testable implementations once RED and GREEN gates are stable.
- Enable better team decisions by showing clear evidence and tradeoffs.

## Examples
- "Add a retry behavior for transient API failure using TDD."
- "Fix this cache invalidation bug with a failing regression test first."

## References
- `references/contract.yaml`
- `references/evals.yaml`
