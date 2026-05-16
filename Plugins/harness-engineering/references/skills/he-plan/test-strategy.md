# Test Strategy And Anti-Patterns

Read when defining verification and test scenarios.

- Test real behavior, not mock existence.
- Do not add test-only methods to production code as part of the plan.
- Mock only after understanding side effects and preserve behavior the test depends on.
- Mock complete documented structures, not only fields needed by the immediate assertion.
- Include integration scenarios when a unit crosses callbacks, middleware, persistence, process boundaries, or UI/API seams.
- Use `Test expectation: none -- <reason>` only for non-feature-bearing units.

Full retained notes: `Plugins/harness-engineering/references/he-plan-doctrine.md`.
