# Build Plan — <feature>

## 1) Epics (sequenced)
Epic 1: ...
Epic 2: ...

## 2) Stories per epic (each w/ AC)
- Story: ...
  - Acceptance criteria:
  - Telemetry/events:
  - Tests:

## 2.1) TDD Guidance (non-negotiable for non-trivial work)
- Write tests BEFORE implementation for any story with:
  - More than 2 branches
  - Complex logic (state machines, algorithms, data transformations)
  - Error handling or edge cases
- Test structure: Given/When/Then format for clarity
- Failing tests are blocked work—DO NOT merge PRs with failing tests
- Manual verification is NOT evidence—automated tests are the truth

## 2.2) Component Registry Guidance
- Before building UI, check the component registry/design system
- If a component exists, USE IT—custom implementations create divergence
- If a component is missing, ADD IT to the registry before building
- Custom implementations must be justified (unique domain requirements)
- Component registry location: `references/component-registry.md` or design system docs
- Story: ...
  - Acceptance criteria:
  - Telemetry/events:
  - Tests:

## 3) Data + contracts (lightweight)
- Entities:
- Key fields:
- API/routes (if any):
- Permissions/auth:

## 4) Test strategy
- Unit: Test individual functions and classes in isolation. Aim for >80% coverage for critical paths.
- Integration: Test component interactions and API contracts. Mock external dependencies.
- E2E: Test critical user journeys end-to-end. Limit to 5-10 scenarios per epic.
- Failure-mode tests: Test error handling, edge cases, and system degradation. MUST include authentication failures, data corruption, and network timeouts.

## TDD Workflow (for non-trivial stories)
1) Write failing test (Given/When/Then)
2) Run test → confirm it fails
3) Write minimal code to make test pass
4) Run test → confirm it passes
5) Refactor while keeping tests green
6) Repeat for next test case

**Non-negotiable:** DO NOT write code without a corresponding test. Tests are the definition of "done."

## 5) Release plan
- Feature flags:
- Rollout:
- Monitoring:
