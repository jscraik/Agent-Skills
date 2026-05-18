# Software Literature Expert Lens Pack

This pack distills the books staged in tmp/ into small expert lenses that skills can reuse. It intentionally avoids chapter summaries, long quotations, copied examples, diagrams, or proprietary phrasing. Each lens is a persona plus review checks, good and bad signals, a small original example, and a Mermaid model.

Use this from skill references, eval rubrics, and review prompts. Keep SKILL.md files compact: link to a lens or copy only two or three checks when the skill needs them inline. Treat each lens as an agent invocation adapter: it should tell the invoking skill when to load the lens, what evidence to inspect, what output shape to return, and when to stop.

## Source Boundary

This pack may use source titles only as provenance for the lens inspiration. Do not quote, summarize chapters, reproduce examples, or present the lens as a substitute for the source text.

All checks, examples, eval probes, and Mermaid models must be original operational guidance for local skills. Do not cite a source book as proof of repository behavior; cite repo files, command output, runtime observations, or clearly labeled missing evidence.

## House Bias

- Repo evidence beats literature pattern.
- Canonical source beats generated projection.
- Exact blocker beats optimistic fallback.
- Smallest verifier beats broad confidence.
- Skill invocation quality beats documentation polish.

## Reference Roles

- [agent-native-skill-contract.md](./agent-native-skill-contract.md): defines the minimum executable skill contract.
- [external-skill-patterns.md](./external-skill-patterns.md): captures reusable patterns from external skill examples.
- This file: provides optional expert review heuristics for skill design, review, and evals.

Do not duplicate policy across all three files. Link sparingly, then let the invoking skill's own contract decide what completion means.

## Priority And Conflict Rules

Priority order:

1. System, developer, and user instructions.
2. Active `AGENTS.md` instructions.
3. Invoked skill's `SKILL.md`.
4. Agent-native skill contract.
5. This lens pack.

If lens guidance conflicts with the invoking skill's command, artifact, safety, or validation contract, follow the invoking skill contract and record the conflict.

## Agent-Native Consumption Contract

When a skill uses this pack:

1. Select the smallest lens set that matches the task surface, normally one to three lenses.
2. Gather concrete evidence before applying a lens.
3. Use the lens to generate checks, not conclusions.
4. Return findings in the invoking skill's output contract.
5. Record validation as `pass`, `fail`, or `blocked` when validation is part of the invoking workflow.
6. Classify missing evidence instead of guessing.
7. Do not cite the source books as proof of repo behavior.

A lens finding is agent-native only when another Codex thread can reproduce the evidence path and understand the smallest next move without private thread context.

## Usage Modes

Use `quick` mode for ordinary skill invocation:

- Select zero or one lens.
- Return only the relevant checks inline.
- Skip lens output if no lens clearly applies.

Use `audit` mode for skill hardening, architecture review, eval design, or release-readiness work:

- Select up to three lenses.
- Return structured findings using the shared output contract.
- Include eval probes, validation mapping, or blocked evidence when useful.

Do not make simple tasks slower just because this pack exists.

## Lens Router

| Task surface | Primary lens | Secondary lens |
| --- | --- | --- |
| Skill authoring or refactor | Deep Module Examiner | Pragmatic Delivery Partner |
| Skill invocation quality | Use-Case Flow Designer | Story Slicer |
| Repo terminology or source/projection drift | Domain Language Guardian | Pragmatic Delivery Partner |
| MCP, tools, queues, events | Integration Pattern Mechanic | Data-Intensive Systems Critic |
| Architecture review | Architectural Pattern Cartographer | Pattern Catalog Skeptic |
| Code clarity review | Clean Code Craftsperson | Refactoring Catalog Operator |
| Safe incremental cleanup | Micro-Refactoring Surgeon | XP Feedback Coach |
| Eval prompt and acceptance design | Story Slicer | Use-Case Flow Designer |
| Delivery, validation, and durable evidence | Pragmatic Delivery Partner | XP Feedback Coach |

## Shared Output Contract

Unless the invoking skill has a stricter artifact schema, return lens findings with these fields:

- `lens`: lens name.
- `finding`: one-sentence issue, strength, or blocked condition.
- `evidence`: exact file, path, command, trace, or missing-evidence note.
- `risk`: why this matters for agent execution, maintainability, product behavior, or validation.
- `move`: smallest useful improvement or next evidence step.
- `validation`: `pass`, `fail`, `blocked`, or suggested verifier.

## Lens Finding Validity

A lens finding is valid only when it includes:

- selected lens
- local evidence
- agent/runtime, product, or maintainability risk
- smallest recommended move
- verifier or blocked reason

A lens finding is invalid when it:

- relies on source literature as authority
- recommends a broad rewrite without a failing behavior or named complexity symptom
- conflicts with the invoked skill contract
- lacks file, command, artifact, trace, or user-request evidence
- proposes abstraction for aesthetic polish rather than a task-linked problem

Every recommendation must name the user-visible or agent-runtime problem, the smallest useful change, and the verifier that would prove it helped.

## Lens Collision Tie-Breakers

When lenses disagree:

1. Prefer the invoking skill's current execution contract.
2. Prefer the smallest reversible change.
3. Prefer evidence-backed runtime failures over conceptual elegance.
4. Prefer stopped/blocked evidence over optimistic fallback.
5. Record unresolved tradeoffs instead of forcing consensus.

## Eval Probe Quality Bar

Do not evaluate lens usage by checking whether the answer mentions a lens name. Good probes use messy, realistic conditions: missing files, generated projection confusion, ambiguous user wording, partial validation failures, live-state claims, and conflicting docs.

Pass criteria should require evidence classification, stop behavior, and source/projection/runtime distinctions. For skill-invocation drift, a passing answer must distinguish canonical source, generated projection, runtime handle, and validation evidence.

## Lens Stack Recipes

### Skill Hardening

1. Use `Use-Case Flow Designer` to identify actor, goal, success state, and extensions.
2. Use `Deep Module Examiner` to simplify the visible skill contract.
3. Use `Pragmatic Delivery Partner` to map validation and durable evidence.
4. Use `XP Feedback Coach` to add one focused eval before widening.

### Architecture Review

1. Use `Deep Module Examiner` to name complexity symptoms.
2. Use `Architectural Pattern Cartographer` to compare structural options.
3. Use `Pattern Catalog Skeptic` to reject decorative abstraction.
4. Use `Pragmatic Delivery Partner` to record the reversible first move.

### Eval Design

1. Use `Story Slicer` to turn broad claims into user-visible scenarios.
2. Use `Use-Case Flow Designer` to add happy path, extensions, and stop states.
3. Use `XP Feedback Coach` to keep the first run small.
4. Use `Pragmatic Delivery Partner` to make results durable and repeatable.

## Eval Probes

### Probe: Skill Invocation Drift

Prompt: "This skill works locally but fails when invoked by handle. Review it."

Expected lens: Domain Language Guardian plus Pragmatic Delivery Partner.

Expected behavior:

- Checks canonical source and runtime projection when relevant.
- Distinguishes Canonical Skill Source, Runtime Projection, and Generated Command Handle.
- Does not hand-edit generated files.
- Returns smallest repair and verifier.

### Probe: Over-Abstracted Refactor

Prompt: "Make this skill architecture more professional."

Expected lens: Pattern Catalog Skeptic plus Deep Module Examiner.

Expected behavior:

- Resists adding abstraction without stable variation.
- Names concrete complexity symptoms.
- Suggests one small contract improvement.
- Provides a focused validation or blocked evidence note.

### Probe: Weak Skill Eval

Prompt: "This skill has evals but they only check wording. Improve them."

Expected lens: Story Slicer plus Use-Case Flow Designer plus XP Feedback Coach.

Expected behavior:

- Converts vague assertions into actor-goal scenarios.
- Adds at least one negative or extension path.
- Ties checks to artifacts, commands, traces, schemas, or user-visible outcomes.
- Keeps the first eval patch narrow enough to run.

## Clean Code Craftsperson

Source inspiration: Clean Code A Handbook of Agile Software Craftsmanship

When to use: Use when reviewing implementation clarity, naming, function shape, test readability, error handling, and cleanup discipline.

Good signals:
- Names reveal intent without side-channel comments.
- Functions do one coherent thing at one level of abstraction.
- Errors are handled explicitly at the boundary that can add context.
- Tests read as behavior examples, not implementation transcripts.

Bad signals:
- Names encode mechanics or historical accidents.
- One function mixes parsing, policy, mutation, IO, and presentation.
- Comments apologize for unclear code instead of clarifying why a constraint exists.
- Tests assert incidental structure while missing visible behavior.

Example:
Bad: `processData()` reads files, mutates state, posts results, and formats output. Good: split into `load_report_inputs`, `apply_report_policy`, and `write_report_output`, with the command layer owning IO.

Mermaid model:

~~~mermaid
flowchart TD
  A["Unclear code"] --> B{"Can a name reveal intent?"}
  B -->|Yes| C["Rename"]
  B -->|No| D{"Is the unit doing multiple jobs?"}
  D -->|Yes| E["Extract coherent steps"]
  D -->|No| F["Add a why comment only for hidden constraints"]
  E --> G["Add behavior-facing test"]
  C --> G
  F --> G
~~~

## Data-Intensive Systems Critic

Source inspiration: Designing Data-Intensive Applications

When to use: Use when a skill touches persistence, events, queues, caches, consistency, migrations, indexing, or production reliability.

Good signals:
- The design names the consistency model and failure mode it accepts.
- Data ownership, replication, retention, and replay semantics are explicit.
- Indexes and read models match real query paths.
- Backfills and migrations include rollback or stop conditions.

Bad signals:
- The design says 'eventually consistent' without user-visible consequences.
- A cache becomes a hidden source of truth.
- A queue is added without idempotency, ordering, or retry policy.
- A migration assumes perfect data shape and no partial deployment.

Example:
Bad: 'send a webhook after save'. Good: persist an outbox event with an idempotency key, process it asynchronously, and expose retry/dead-letter evidence.

Mermaid model:

~~~mermaid
flowchart LR
  W["Write path"] --> T["Transaction boundary"]
  T --> S["System of record"]
  T --> O["Outbox/event log"]
  O --> R["Retryable worker"]
  R --> V{"Idempotent receiver?"}
  V -->|Yes| D["Delivered"]
  V -->|No| B["Duplicate side effects risk"]
~~~

## Domain Language Guardian

Source inspiration: Domain Driven Design

Use when:
- A task involves repo terminology, source/projection drift, command handles, skill blending, domain ownership, intake decisions, or language cleanup.
- The user uses informal wording that must be translated into canonical repo terms.
- External tools, plugins, or runtime projections impose vocabulary that may conflict with canonical skill source language.

Do not use when:
- The task is only local code clarity with no domain or ownership ambiguity.
- The user asks for direct implementation and the vocabulary is already stable.
- The conclusion would be based on preferred terminology rather than observed repo usage.

Required evidence:
- User wording that triggered the task.
- Current canonical source path and relevant `SKILL.md` wording.
- Runtime projection, generated command handle, manifest entry, or sync output when the task mentions invocation/discovery.
- Existing glossary, UBIQUITOUS_LANGUAGE.md, validation contract, or command output when available.

Diagnostic questions:
- Which terms does the user use, and which terms does the repo treat as canonical?
- Are two concepts being merged because they share a word?
- Is generated/runtime language being mistaken for canonical source language?
- Does an external tool require an anti-corruption translation layer?

Review moves:
- Build a small term map: user phrase -> canonical term -> source owner -> runtime/projection surface.
- Preserve bounded contexts when a proposed merge would erase useful distinctions.
- Rename only after identifying the owner that can safely change the term.
- Add eval or validation wording when drift repeatedly causes agent mistakes.

Output contract:
- `lens`: `Domain Language Guardian`.
- `finding`: terminology strength, drift, or blocked ownership issue.
- `evidence`: exact source/projection/glossary/user wording evidence.
- `risk`: how language drift affects invocation, ownership, or future agent work.
- `move`: smallest rename, glossary entry, source edit, or sync/verifier.
- `validation`: pass/fail/blocked or the command/check that would prove the language is aligned.

Stop conditions:
- No canonical source file was found.
- Runtime projection exists but source ownership is unclear.
- The task asks for live runtime visibility without command evidence.
- The suggested fix would require hand-editing generated `.agents/**`, `.skillsets/**`, cache, or mirror files.

Eval probes:
- Prompt: "This skill works from source but the handle invokes different wording." Expected: distinguishes canonical source, runtime projection, and generated handle.
- Prompt: "Blend this external skill into our existing skill." Expected: identifies duplicate and separate bounded contexts before recommending merge.

Good signals:
- The skill preserves the user's and repo's canonical vocabulary.
- Bounded contexts are named before concepts are merged.
- External tool terms are isolated behind an anti-corruption boundary.
- Domain rules live with the owner that has authority to change them.

Bad signals:
- One word means different things in docs, CLI output, runtime projection, and source.
- A generic service owns rules from multiple domains.
- A plugin's terminology leaks into canonical repo language without translation.
- A skill blend erases a useful domain distinction.

Example:
Bad: use 'skill', 'runtime skill', 'projection', and 'handle' interchangeably. Good: map each to Canonical Skill Source, Runtime Projection, or Generated Command Handle before editing.

Mermaid model:

~~~mermaid
flowchart TD
  U["User wording"] --> E["Gather evidence"]
  S["Canonical source"] --> E
  P["Projection or handle"] --> E
  E --> M["Term map"]
  M --> C{"Same bounded context?"}
  C -->|Yes| A["Align wording through owner"]
  C -->|No| K["Keep concepts separate"]
  A --> V["Verify invocation or docs"]
  K --> V
~~~

## Integration Pattern Mechanic

Source inspiration: Enterprise Integration Patterns

When to use: Use when a skill designs MCP tools, plugin interfaces, events, webhooks, workflow routing, queues, or message transformations.

Good signals:
- Message channel, payload contract, routing rule, and consumer ownership are named.
- Correlation, idempotency, retries, and poison-message behavior are designed up front.
- Transformers are explicit and testable.
- The integration can be observed with traceable message IDs.

Bad signals:
- A tool call is treated as a local function when it is really a distributed boundary.
- Message transformation is hidden in an unrelated orchestrator.
- Retries can duplicate external writes.
- Routing rules live in prose only.

Example:
Bad: an MCP tool forwards arbitrary JSON to a backend. Good: validate an envelope, add a correlation ID, transform into a typed command, and return a classified failure.

Mermaid model:

~~~mermaid
flowchart LR
  P["Producer"] --> C["Channel"]
  C --> F["Filter/router"]
  F --> T["Transformer"]
  T --> H["Handler"]
  H --> I{"Idempotent?"}
  I -->|Yes| A["Acknowledge"]
  I -->|No| Q["Quarantine / manual review"]
~~~

## Pattern Catalog Skeptic

Source inspiration: Design Patterns

When to use: Use when architecture or refactoring skills need to name a recurring object collaboration, extension point, or composition boundary.

Good signals:
- A pattern name explains a real collaboration already visible in code.
- Composition hides variation without forcing callers to know internals.
- The chosen pattern reduces conditionals or ownership confusion.
- The skill explains the cost of the pattern, not only the benefit.

Bad signals:
- A pattern is introduced because it sounds professional.
- A factory or strategy wraps one implementation with no likely variation.
- The abstraction hides nothing and creates more files to inspect.
- The pattern vocabulary replaces repo-specific language.

Example:
Bad: add `StrategyFactoryManager` for one formatter. Good: keep a function until there are two stable variations, then introduce a strategy at the caller's variation point.

Mermaid model:

~~~mermaid
flowchart TD
  N["Need variation?"] --> V{"Two or more stable variants?"}
  V -->|No| S["Stay simple"]
  V -->|Yes| C{"Does abstraction hide decisions?"}
  C -->|No| S
  C -->|Yes| P["Introduce named pattern"]
  P --> R["Document tradeoff and rollback"]
~~~

## XP Feedback Coach

Source inspiration: Extreme Programming Explained

When to use: Use when planning evals, implementation slices, validation loops, team workflows, and stop/pivot criteria.

Good signals:
- Work is sliced into the smallest behavior that can be proven.
- Tests or evals are close to the user-visible behavior.
- The plan includes a feedback point before broad rollout.
- The skill captures learning from failure into a durable check.

Bad signals:
- A plan grows large before the first proof point.
- Validation is deferred until after many unrelated edits.
- The team optimizes local elegance while feedback stays slow.
- Failures are discussed but not converted into tests or eval prompts.

Example:
Bad: rewrite a skill family and then run audits. Good: update one skill, add one eval case, run the focused audit, then widen.

Mermaid model:

~~~mermaid
flowchart LR
  I["Intent: name behavior"] --> S["Small slice: change one surface"]
  S --> F["Feedback: run focused eval"]
  F --> L["Learning: record new check"]
  L --> I
~~~

## Micro-Refactoring Surgeon

Source inspiration: Five Lines of Code

When to use: Use when simplifying code or skill text through tiny mechanical moves that preserve behavior.

Good signals:
- Each move is small enough to review independently.
- Behavior is preserved before aesthetics are improved.
- Conditionals and duplication shrink through named concepts.
- The verifier is narrow and run after each meaningful move.

Bad signals:
- A refactor changes structure, naming, behavior, and tests in one sweep.
- The agent rewrites a working module to satisfy taste.
- A helper is extracted before the duplication is real.
- No one can tell which move caused a regression.

Example:
Bad: replace a command parser wholesale. Good: first extract one predicate, test it, then move one branch behind a clearer command object.

Mermaid model:

~~~mermaid
flowchart TD
  A["Messy surface"] --> B["Find smallest smell"]
  B --> C["Make one mechanical move"]
  C --> D["Run narrow verifier"]
  D --> E{"Behavior preserved?"}
  E -->|Yes| F["Continue"]
  E -->|No| G["Revert just that move"]
~~~

## Refactoring Catalog Operator

Source inspiration: Refactoring

When to use: Use when a skill must improve existing code without changing behavior, especially after review findings or architecture pressure.

Good signals:
- The current behavior is characterized before the refactor.
- Smells are named precisely: long method, feature envy, shotgun surgery, primitive obsession, duplicated code.
- Refactorings are sequenced from safe preparation to deeper moves.
- Tests prove behavior before and after.

Bad signals:
- The agent calls a redesign a refactor.
- The diff changes public behavior without migration notes.
- A smell is named but no local evidence is cited.
- The refactor improves internals while breaking callers.

Example:
Bad: 'clean up the service'. Good: characterize the current command output, extract `build_review_lanes`, rerun the command, then move ownership.

Mermaid model:

~~~mermaid
flowchart LR
  S["Smell"] --> E["Evidence"]
  E --> T["Characterization test"]
  T --> R["Refactoring move"]
  R --> V["Verifier"]
  V --> D{"Public behavior same?"}
  D -->|Yes| N["Next smell"]
  D -->|No| X["Stop and classify"]
~~~

## Architectural Pattern Cartographer

Source inspiration: Pattern-Oriented Software Architecture, Volume 1

When to use: Use when comparing system structures such as layers, pipes and filters, brokers, plugins, microkernels, or reflective systems.

Good signals:
- The architecture pattern matches real forces: change rate, deployment boundary, extensibility, coupling, and observability.
- The skill names both benefits and liabilities of the structure.
- Cross-layer dependencies are visible and justified.
- Extension points have ownership, compatibility, and validation rules.

Bad signals:
- A layered architecture is claimed while lower layers import upper-layer policy.
- A plugin architecture exists without contract tests or compatibility boundaries.
- A broker hides all errors behind generic runtime failure.
- Pattern language replaces concrete file and command evidence.

Example:
Bad: 'make it plugin-based'. Good: identify stable core, plugin contract, compatibility tests, discovery path, and failure classification.

Mermaid model:

~~~mermaid
flowchart TD
  F["Forces"] --> P{"Pattern fit"}
  P --> L["Layered"]
  P --> B["Broker"]
  P --> M["Microkernel"]
  P --> PF["Pipes and filters"]
  L --> C["Check dependency direction"]
  B --> C2["Check failure visibility"]
  M --> C3["Check extension contract"]
  PF --> C4["Check transform boundaries"]
~~~

## Deep Module Examiner

Source inspiration: A Philosophy of Software Design

Use when:
- A task asks for architecture improvement, skill hardening, simplification, or boundary cleanup.
- Callers, users, or future agents must know hidden ordering, setup, defaults, or implementation facts.
- A skill or module looks agent-native on paper but still requires private context to execute.

Do not use when:
- The task is a one-line copy edit or direct bug fix with no boundary concern.
- The proposed change would only rename wrappers without hiding complexity.
- Current evidence does not show a complexity symptom.

Required evidence:
- The public interface: `SKILL.md`, command help, function signature, CLI surface, or exported contract.
- At least one caller, workflow, eval, test, or command that consumes the interface.
- Evidence of coordination burden, such as repeated setup steps, hidden order, duplicated validation, or source/projection drift.
- Existing verifier or reason a verifier is blocked.

Diagnostic questions:
- What must a caller know before this interface works?
- Which implementation facts leak into docs, tests, configs, or users?
- Does the abstraction hide hard coordination or merely rename it?
- Would the next change touch fewer files after this move?

Review moves:
- Name the complexity symptom before recommending structure.
- Compare a small patch against a deeper boundary change.
- Prefer moving coordination behind the owner over adding another wrapper.
- Ask for a tracer proof: one caller, one path, one verifier.

Output contract:
- `lens`: `Deep Module Examiner`.
- `finding`: complexity symptom or boundary strength.
- `evidence`: exact interface/caller/workflow evidence.
- `risk`: how the boundary increases cognitive load, change amplification, or agent failure.
- `move`: smallest boundary or contract change that hides real complexity.
- `validation`: focused verifier or blocked reason.

Stop conditions:
- No caller or workflow evidence is available.
- The current behavior cannot be characterized before the proposed refactor.
- The recommended change would add indirection without hiding a named complexity symptom.
- The task requires broad rewrite before a tracer proof exists.

Eval probes:
- Prompt: "Make this skill architecture more professional." Expected: names a complexity symptom before suggesting structure.
- Prompt: "This wrapper feels useful; review it." Expected: classifies whether the wrapper hides coordination or only forwards.

Good signals:
- Interfaces are simpler than implementations.
- A module hides hard coordination, defaults, validation, or special cases.
- Callers need less hidden knowledge after the change.
- Complexity symptoms are named before solutions are proposed.

Bad signals:
- A wrapper forwards calls without hiding complexity.
- Implementation facts leak into config, docs, tests, or callers.
- One change requires edits across unrelated modules.
- The skill adds indirection to look architectural.

Example:
Bad: create `SkillValidationService` that forwards to three scripts. Good: create one command that owns setup, classification, and report shape so callers stop knowing the sequence.

Mermaid model:

~~~mermaid
flowchart TD
  I["Visible interface"] --> C{"What must caller know?"}
  C --> L["Leaked coordination"]
  C --> H["Hidden by owner"]
  L --> S{"Named symptom?"}
  S -->|Yes| R["Redesign boundary"]
  S -->|No| E["Gather more evidence"]
  H --> V["Verify caller got simpler"]
  R --> V
~~~

## Pragmatic Delivery Partner

Source inspiration: The Pragmatic Programmer

When to use: Use when skills govern repo hygiene, automation, reversibility, knowledge capture, broken-window cleanup, and delivery discipline.

Good signals:
- Every repeated manual step has an owner or automation path.
- Decisions are reversible or have an explicit lock-in note.
- Knowledge is captured where future agents will actually read it.
- Small defects are fixed or classified before becoming background noise.

Bad signals:
- A workflow depends on thread lore.
- Docs describe a command that no validator enforces.
- Temporary files become invisible dependencies.
- The agent optimizes for a green report while leaving drift behind.

Example:
Bad: tell future agents to remember Snyk policy. Good: encode the policy in the validation contract and dashboard classification.

Mermaid model:

~~~mermaid
flowchart LR
  O["Observation"] --> A{"Repeated?"}
  A -->|No| N["Note if useful"]
  A -->|Yes| W{"Can it be automated?"}
  W -->|Yes| S["Script/validator"]
  W -->|No| D["Durable decision note"]
  S --> V["Verify"]
  D --> V
~~~

## Story Slicer

Source inspiration: User Stories Applied

When to use: Use when skills create prompts, specs, eval cases, acceptance criteria, or planning slices around user value.

Good signals:
- Stories name user role, goal, and value without over-specifying implementation.
- Acceptance criteria are observable and testable.
- Large work is split by workflow, risk, data shape, or user outcome.
- Negative controls are included where false positives matter.

Bad signals:
- A story is a disguised technical task with no user outcome.
- Acceptance criteria say 'works correctly'.
- All slices are horizontal technical layers with no demonstrable value.
- Edge cases are hidden until implementation.

Example:
Bad: 'Add eval framework'. Good: 'As a skill maintainer, I can run three prompts and see which skill behavior regressed, so I know whether a rewrite improved reliability.'

Mermaid model:

~~~mermaid
flowchart TD
  R["Role"] --> G["Goal"]
  G --> V["Value"]
  V --> A["Acceptance checks"]
  A --> S{"Too large?"}
  S -->|Yes| P["Split by user-visible slice"]
  S -->|No| E["Add eval prompt"]
~~~

## Use-Case Flow Designer

Source inspiration: Writing Effective Use Cases

Use when:
- A skill defines CLI flows, app flows, agent workflows, install/review flows, exception handling, or completion criteria.
- A request needs actor-goal clarity before implementation, eval design, or validation.
- A skill has happy-path instructions but weak failure behavior.

Do not use when:
- The task is only low-level code cleanup with no user or agent workflow.
- The actor, goal, preconditions, and done state are already explicit and tested.
- The flow would duplicate an existing contract instead of clarifying a missing one.

Required evidence:
- Primary actor: user, agent, maintainer, CLI operator, reviewer, or external system.
- Goal and trigger wording from the request or skill description.
- Existing workflow steps, command contract, output contract, or acceptance criteria.
- Known extension paths: missing file, auth failure, validation failure, runtime projection drift, unsupported input, or no-op.

Diagnostic questions:
- Who is trying to accomplish what, and why?
- What must already be true before the flow starts?
- What is the shortest main success scenario?
- Which extension paths block completion rather than allow silent fallback?
- What postcondition proves the task is done?

Review moves:
- Rewrite vague workflow text into actor, preconditions, main success scenario, extensions, and postconditions.
- Convert extension paths into blocked/fail/pass evidence.
- Add negative or alternate eval prompts for the most likely false completion claim.
- Keep implementation details out of the use case unless they are part of the observable contract.

Output contract:
- `lens`: `Use-Case Flow Designer`.
- `finding`: flow gap, success-state strength, or blocked extension.
- `evidence`: skill wording, command output, eval prompt, artifact path, or missing evidence.
- `risk`: how the unclear flow could cause false completion or missed user intent.
- `move`: smallest workflow, output contract, extension path, or eval addition.
- `validation`: verifier or blocked reason.

Stop conditions:
- The primary actor or goal cannot be inferred from the request or source.
- No observable postcondition can be named.
- The flow would require live external state that has not been authorized or evidenced.
- The lens would invent acceptance criteria unrelated to the user's goal.

Eval probes:
- Prompt: "This skill says run external review; make the flow clearer." Expected: actor, preconditions, main success path, extensions, postconditions.
- Prompt: "Add evals for this skill's workflow." Expected: at least one main-path probe and one extension/negative probe.

Good signals:
- The primary actor and goal are explicit.
- Main success scenario is short, ordered, and technology-neutral enough to test intent.
- Extensions cover failures, alternate paths, and recovery.
- Preconditions and postconditions make completion unambiguous.

Bad signals:
- The flow starts with implementation steps before actor intent.
- Exceptions are treated as afterthoughts.
- The use case has no clear success state.
- A skill only documents happy-path commands.

Example:
Bad: 'Run external review'. Good: actor wants release readiness evidence; precondition is canonical skill path; main flow runs audit, Plugin Eval, Tessl review; extension classifies Snyk skipped vs required.

Mermaid model:

~~~mermaid
flowchart TD
  A["Actor goal"] --> P["Preconditions"]
  P --> M["Main success scenario"]
  M --> X{"Extension?"}
  X -->|No| O["Postconditions"]
  X -->|Yes| E["Recovery / blocked path"]
  E --> O
  O --> V["Verifier or evidence"]
~~~
