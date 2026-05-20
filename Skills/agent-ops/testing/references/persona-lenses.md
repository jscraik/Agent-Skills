# Testing Persona Lenses

Use these lenses for review-style testing work: test strategy critique, coverage
design, validation plan review, exploratory charters, or deciding whether a
green result proves the thing Jamie actually asked to prove.

Lenses are advisory. They sharpen the questions before command selection; they
do not replace repo-native validators, deterministic checks, schemas, or
artifact proof.

## Lens Selection

- Use one named lens when the user asks for a specific testing perspective.
- Combine two or three lenses when the risk surface spans decision quality,
  maintainable automated tests, and exploratory discovery.
- Report the active lens names in the answer when they materially shape the
  validation route.
- Convert each lens into exact proof: commands, artifacts, charters, assertions,
  or blocked evidence.

## Weinberg Information Lens

Inspired by _Perfect Software... and other illusions about testing_.

Use when the risk is false certainty, vague completion claims, bug-count theater,
or pressure to treat testing as proof of perfection.

Ask:

- What decision will this test information support?
- What risk is being sampled, and what risks remain intentionally unsampled?
- Is the team using the test result, or merely performing testing rituals?
- Is a green check being over-claimed as correctness, quality, or release safety?
- Are reports, bug counts, coverage numbers, demos, or stale artifacts being
  treated as stronger evidence than they really are?
- Did a repair get retested on the failing path, or only patched and assumed?

Signals:

- Phrases like "prove it is correct", "test everything", "the suite is green",
  "QA will find it", or "coverage proves it was tested".
- Blame, fear, or schedule pressure distorting what failures are recorded.
- Test data, fixtures, or environments that are too weak to support the claim.

Output shape:

- Name the decision.
- Name the information still missing.
- Separate tested behavior, inferred confidence, and unverified risk.
- Prefer small exact probes over broad symbolic reassurance.

## xUnit Pattern Lens

Inspired by Meszaros-style xUnit patterns and the Four Phase Test.

Use when reviewing or designing automated tests for clarity, maintainability,
and real behavior proof.

Ask:

- Can a reader quickly see the setup, exercise, verify, and teardown phases?
- Is the test verifying one behavior or hiding multiple conditions in one blob?
- Is the fixture explicit enough to explain the before-picture?
- Does result verification assert observable behavior instead of implementation
  trivia or duplicated production logic?
- Are test doubles clarifying a boundary, or masking the integration behavior
  the change actually needs to prove?
- Would this test fail for the defect it claims to catch?

Signals:

- Mixed setup and exercise calls.
- Obscure tests that require deep implementation reading to understand intent.
- Assertions that restate mocks rather than proving behavior.
- Shared fixtures that make state leakage plausible.

Output shape:

- Recommend the smallest test rewrite that makes intent visible.
- Keep production-path checks separate from fixture convenience.
- Add targeted tests before broad suite expansion when behavior is uncovered.

## Classic Test Design Lens

Inspired by _The Art of Software Testing_.

Use when a validation plan needs sharper test-case design rather than more
undirected command volume.

Ask:

- Does every test define the expected output or result before execution?
- Are invalid, unexpected, malformed, empty, boundary, and adversarial inputs
  represented alongside valid happy paths?
- Does the test check unwanted side effects, not only the intended output?
- Are one-off exploratory cases worth preserving as regression tests?
- Are test results inspected carefully, or merely counted as green/red output?
- Are newly found failures clustered in one component, suggesting higher yield
  from deeper tests around that component?
- Would independent review, inspection, or walkthrough catch faults that runtime
  execution is unlikely to reveal?

Signals:

- Tests assert only that "nothing crashed" or compare output loosely.
- The test suite misses invalid input and side-effect behavior.
- A repair is made without retaining the reproducing case.
- Repeated failures concentrate in one module, command, or integration boundary.

Output shape:

- Spell out input, expected output, and forbidden side effects.
- Add negative and boundary cases before widening to broad suites.
- Preserve valuable cases for regression rather than treating them as disposable.
- Use failure clustering to prioritize the next exact probe.

## Key Examples Lens

Inspired by _Fifty Quick Ideas to Improve Your Tests_.

Use when acceptance criteria, BDD examples, or executable specifications are too
large, too UI-mechanical, or too weak to create shared understanding.

Ask:

- Are examples explaining the business concept, or drowning it in combinations?
- Which missing concept would simplify the scenarios if named explicitly?
- Can validation be split from processing or action from decision?
- Can similar examples be grouped by commonality so only meaningful variation
  remains visible?
- Are important boundary conditions represented by a few key examples?
- Are coverage area and test purpose being confused?

Signals:

- Pages of scenarios give a false sense of completeness but hide the rule.
- Business users cannot tell what confidence the automated examples provide.
- One acceptance test mixes UI mechanics, workflow, and business decision logic.
- A team assumes examples replace every other useful kind of testing.

Output shape:

- Replace long scenario lists with smaller focused groups of key examples.
- Name hidden domain concepts and propose test slices around those concepts.
- Separate purpose from coverage: business-oriented unit tests are allowed when
  they prove the business decision more directly than UI tests.
- Keep examples as shared-understanding tools, then add other tests for risks
  that examples do not cover.

## Property-Based Lens

Inspired by Hypothesis and the HypothesisWorks project.

Use when hand-picked examples undersample the input space, invariants are clear,
or generated counterexamples would make failures easier to debug.

Ask:

- What property should hold for all generated inputs in the chosen range?
- What generator or strategy describes valid, invalid, boundary, and structured
  data without over-filtering away useful cases?
- What oracle makes a generated failure meaningful: invariant, round trip,
  reference implementation, metamorphic relation, or state-machine invariant?
- How will the simplest failing example be captured as a regression?
- Does stateful behavior need rules, preconditions, bundles, or invariants?
- Is there a natural target metric, such as queue length, load factor, or error
  magnitude, that could guide targeted search?

Signals:

- Example tests cover a few values but the input domain is broad or combinatory.
- Bugs depend on duplicate values, empty collections, NaN, Unicode, dates,
  serialization, parser/formatter pairs, or operation sequences.
- A flaky or generated failure was not saved in a reproducible form.
- Tests rely heavily on filters or assumptions that make generation inefficient
  and shrink results hard to interpret.

Output shape:

- State the property in plain language before choosing the tool.
- Pair generated checks with explicit regression examples for known failures.
- Prefer local, composable generators that shrink to readable counterexamples.
- Use stateful or targeted property testing only when the model or metric is
  clear enough to improve bug discovery.

## Issue Reproduction Lens

Inspired by SWE-Tester and issue-reproduction research.

Use when the task is to prove a reported bug, generate a reproduction test, or
judge whether a proposed test actually exercises the fix.

Ask:

- Does at least one test fail on the pre-fix code and pass on the fixed code?
- Do all tests pass after the fix, avoiding false F -> F or P -> F failures?
- Which existing test file best teaches conventions, fixtures, utilities, and
  naming for the new reproduction test?
- Which source files are likely defective, and which test file should be edited
  first before scattering multi-file changes?
- Is the patch merely applicable, or does it reproduce the issue and cover the
  changed lines or behavior?

Signals:

- The issue has a natural-language report but no reproduction test.
- A generated or hand-written test applies cleanly but never fails before the fix.
- The test uses alien conventions instead of nearby fixtures and helpers.
- Validation claims rely on patch applicability, not fail-to-pass behavior.

Output shape:

- Report reproduction status as pre-fix fail, post-fix pass, post-fix fail, or
  not run.
- Prefer editing the most relevant existing test file before adding new harness
  surfaces.
- Track applicability separately from reproduction success and change coverage.
- Keep regression tests that prove the issue, plus any P -> P guard tests that
  protect adjacent behavior.

## Explore It Charter Lens

Inspired by Elisabeth Hendrickson's _Explore It!_ workshop material.

Use when automation is not enough, the system behavior is poorly understood, or
the work needs discovery before stable assertions exist.

Charter template:

    Explore <thing or feature>
    with <resources, constraints>
    to discover <information>

Ask:

- What are we exploring, with what constraints, and to discover what information?
- Which variables can change the behavior: data, permissions, timing, sequence,
  environment, feature flags, integration state, user role, or load?
- What surprising result would change the next automated test we write?
- What notes, screenshots, logs, or repro steps must become durable artifacts?

Signals:

- The user asks "what should I test here?" for a new or ambiguous workflow.
- Requirements are incomplete, informal, or still being discovered.
- Failures depend on order, timing, prior state, or combinations not covered by
  deterministic tests.

Output shape:

- Produce one to three focused charters, each small enough for a bounded session.
- End each charter with the artifact expected from the session.
- Convert stable discoveries into automated tests or explicit blocked evidence.

## Persona And User-Breakdown Lens

Inspired by the Explore It persona technique.

Use when behavior may fail different users, roles, accessibility needs,
permissions, or operational contexts.

Ask:

- Which user role, permission level, workflow frequency, or domain expectation
  changes the risk?
- How would an impatient, novice, expert, malicious, interrupted, offline, or
  assistive-technology user expose a different failure?
- What does the system do when a user succeeds partially, repeats an action, or
  returns after stale state?

Signals:

- UI, CLI, API, auth, onboarding, migration, or workflow changes.
- Requirements mention "user", "admin", "agent", "operator", "reviewer", or
  "customer" but tests only cover a happy-path default role.

Output shape:

- Name the persona as a lens, not as a fictional story.
- Turn the persona into concrete paths, inputs, permissions, and assertions.
- Keep empathy useful by tying it to observable behavior and failure evidence.

## Entity, State, And Sequence Lens

Inspired by Explore It topics on variables, sequences, entities, relationships,
states, and transitions.

Use when correctness depends on data relationships, lifecycle transitions, or
the order in which actions occur.

Ask:

- Which entities, attributes, and relationships can drift out of sync?
- Which states exist before, during, and after the workflow?
- Which transitions are allowed, repeated, forbidden, interrupted, or retried?
- Which sequence variations reveal stale cache, race, idempotency, rollback, or
  cleanup bugs?

Signals:

- Data migrations, queues, background jobs, state machines, retries, caches,
  branch/PR lifecycle, generated artifacts, or multi-step workflows.

Output shape:

- Draw a compact state/transition or entity relationship inventory in prose.
- Select tests that cross the riskiest transition, not only the easiest state.
- Include repeat, retry, and repair paths where the system claims idempotency.

## Ecosystem And Intermittent Lens

Inspired by Explore It ecosystem, no-UI, and intermittent bug material.

Use when bugs cross service boundaries, have no GUI, or reproduce only sometimes.

Ask:

- Which trust boundaries, API contracts, file-system paths, clocks, caches,
  queues, external services, credentials, or sandbox permissions participate?
- Which variables can be controlled to make an intermittent issue repeatable?
- Is the no-UI surface still testable through APIs, CLIs, logs, schemas,
  generated files, or telemetry?
- What would distinguish code failure from environment/tooling failure?

Signals:

- Flaky CI, networked validation, live credentials, sandbox denials, race
  conditions, delayed jobs, generated artifacts, or API-only behavior.

Output shape:

- List controlled variables and uncontrolled variables separately.
- Classify blocked proof truthfully instead of weakening the claim.
- Add instrumentation or artifact capture only when it makes the next run more
  diagnostic.

## Source Notes

- _Perfect Software... and other illusions about testing_ contributed the
  information, fallacy, meta-testing, and evidence-quality lens.
- _xUnit Patterns_ contributed the Four Phase Test, fixture/result verification,
  test organization, doubles, and design-for-testability lens.
- _The Art of Software Testing_ contributed expected-result discipline,
  destructive test design, invalid input, side-effect, regression-retention,
  inspection, and error-clustering guidance.
- _Fifty Quick Ideas to Improve Your Tests_ contributed key-example selection,
  hidden concept discovery, validation/processing split, boundary examples, and
  coverage-purpose separation.
- _SWE-Tester: Training Open-Source LLMs for Issue Reproduction in Real-World
  Repositories_ contributed fail-to-pass reproduction, existing-test
  localization, applicability versus success, and change-coverage framing.
- HypothesisWorks/hypothesis contributed property-based testing, generated input
  strategies, shrinking, explicit regression examples, stateful testing, and
  targeted property-based testing guidance.
- testobsessed/exploreit contributed charter syntax and exploratory lenses for
  variables, sequences, personas, entities, states, ecosystem boundaries, no-UI
  surfaces, intermittent bugs, requirements, and integrating exploration.
