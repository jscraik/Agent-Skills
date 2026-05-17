# Software Literature Expert Lens Pack

Use this pack as optional expert-review lenses for skills, evals, architecture
reviews, and code-quality passes. It converts software books into small
operator cards: when to load the lens, what evidence to inspect, what good and
bad look like, what output shape to return, and when to stop.

Do not quote, summarize chapters, reproduce examples, or cite books as proof of
local behavior. Source titles are provenance only. Repo files, command output,
runtime traces, user intent, and missing-evidence notes are the proof.

## House Bias

- Repo evidence beats literature pattern.
- Canonical source beats generated projection.
- Exact blocker beats optimistic fallback.
- Smallest verifier beats broad confidence.
- Skill invocation quality beats documentation polish.

## Consumption Contract

When a skill uses this pack:

1. Select the smallest matching lens set, normally one to three lenses.
2. Gather concrete evidence before applying the lens.
3. Use the lens to generate checks, not conclusions.
4. Return findings in the invoking skill's output contract.
5. Classify missing evidence instead of guessing.
6. Prefer the invoking skill's SKILL.md when guidance conflicts.

Valid lens findings include lens, finding, evidence, risk, move, and validation
or blocked_reason.

Invalid lens findings rely on source literature as authority, recommend broad
rewrites without a failing behavior, conflict with the invoked skill contract,
or lack file, command, artifact, trace, or user-request evidence.

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

## Shared Mermaid Model

~~~mermaid
flowchart TD
  A["Task Evidence"] --> B["Select 1-3 Lenses"]
  B --> C["Inspect Required Evidence"]
  C --> D["Generate Checks"]
  D --> E["Return Skill Output Contract"]
  C --> F{"Evidence Missing?"}
  F -->|"yes"| G["Blocked Or Missing Evidence"]
  F -->|"no"| D
~~~

## Clean Code Craftsperson

Use when reviewing implementation clarity, names, function shape, test
readability, error handling, and cleanup discipline.

Required evidence: changed files, one caller or test, validation command, and
any public API surface.

Good signals: names reveal intent, functions operate at one abstraction level,
errors are contextualized at boundaries, tests read as behavior examples.

Bad signals: names encode accidents, one function mixes parsing/policy/IO,
comments apologize for unclear code, tests assert incidental structure.

Example: replace a repeated anonymous data transform with a named helper only
when callers/tests prove the helper hides a real concept.

Stop when behavior preservation or validation cannot be shown.

## Refactoring Catalog Operator

Use when behavior should stay the same but structure should improve.

Required evidence: baseline behavior, target smell, smallest affected path,
rollback route, and verifier.

Good signals: one mechanical move, scoped diff, existing tests still prove
behavior, public contracts unchanged.

Bad signals: mixed semantic and structural changes, new abstraction from one
caller, no baseline, broad rename without verifier.

Example: extract a duplicated guard into a private helper beside the owner, then
run the test that exercises the guard.

Stop when the refactor changes behavior or requires inventing broad fixtures.

## Micro-Refactoring Surgeon

Use for safe incremental cleanup and slop removal.

Required evidence: references/imports, dead-code proof, baseline validation,
and rollback note.

Good signals: tiny batches, each removal has reference evidence, validation is
rerun after the batch.

Bad signals: deleting dynamic entrypoints, cleaning by hunch, removing context
only to improve token count.

Example: remove an unused helper only after rg/import/test evidence shows no
runtime owner.

Stop when dynamic registration or reflection makes usage uncertain.

## Deep Module Examiner

Use for module boundaries, skill design, and API shape.

Required evidence: target module, caller, test/contract, hidden assumptions,
and language used by the repo.

Good signals: callers know less, defaults and special cases live with the owner,
interfaces hide coordination, deletion test shows the module earns its keep.

Bad signals: shallow wrappers, pass-through helpers, leaked config ordering,
mixed abstraction levels.

Example: prefer an owner-owned command builder when three callers construct the
same payload and tests can assert output shape.

Stop when only one implementation exists and variation is speculative.

## Domain Language Guardian

Use for glossary, DDD, source/projection terminology, and user-language drift.

Required evidence: user wording, canonical docs or glossary, code/CLI/runtime
terms, generated projections when relevant.

Good signals: one canonical term, useful aliases, explicit bounded context,
foreign terms isolated behind adapters.

Bad signals: generated projection treated as source, same concept under several
names, impressive terms that make prompts harder.

Example: map "make sure it works" to repo-specific validation wording while
preserving the user's phrase as an alias.

Stop when the authority for a terminology change is unclear.

## Data-Intensive Systems Critic

Use for backend data, consistency, reliability, queues, state, and production
tradeoffs.

Required evidence: data model, read/write path, consistency expectation,
failure mode, and operational verifier.

Good signals: explicit consistency tradeoff, idempotent writes, bounded
backfills, observable failure states.

Bad signals: hidden coupling between reads and writes, unbounded scans, eventual
without user-facing semantics, no rollback or monitoring.

Example: before adding a background sync, name replay behavior, duplicate
handling, and the check that proves state converges.

Stop when production data assumptions are unavailable.

## Integration Pattern Mechanic

Use for MCP, tools, queues, events, CLIs, plugins, and external integrations.

Required evidence: message/tool schema, route, correlation/idempotency story,
auth/sensitivity boundary, and sample verification call.

Good signals: stable schema, explicit error semantics, pagination/backpressure,
idempotent receiver, scoped auth.

Bad signals: tool does several unrelated actions, errors are strings only,
missing correlation IDs, auth hidden in prose.

Example: split a write tool from a read resource when consumers need different
permissions and validation paths.

Stop when tool ownership or auth scope cannot be verified.

## Architectural Pattern Cartographer

Use when naming structural alternatives helps choose the first move.

Required evidence: current structure, drivers, constraints, changed paths,
runtime path, and decision surface.

Good signals: pattern name clarifies tradeoff, first move is reversible, proof
path exists.

Bad signals: pattern applied as decoration, architecture chosen before drivers,
framework added without stable variation.

Example: compare patch design vs broker-like boundary only when multiple
callers already need independent routing.

Stop when no concrete complexity symptom is visible.

## Pattern Catalog Skeptic

Use alongside architecture patterns to prevent over-engineering.

Required evidence: number of implementations, expected variation, cost of
indirection, and deletion test.

Good signals: abstraction hides real complexity and removes caller knowledge.

Bad signals: one implementation, pass-through wrapper, abstract names without
behavior, "professional" used as the reason.

Example: keep a local helper private until a second caller proves public
variation.

Stop when the proposed abstraction only improves aesthetics.

## XP Feedback Coach

Use for evals, planning, validation loops, CI repair, and release readiness.

Required evidence: desired outcome, smallest feedback slice, current failing
signal, rerun command, and stop/pivot rule.

Good signals: thin slice, fast feedback, failing test before fix when possible,
clear blocked state.

Bad signals: broad plan without proof, slow gate as only signal, no learning
capture after repeated failure.

Example: add one realistic eval case for a reproduced skill miss before adding
ten synthetic cases.

Stop when the next slice cannot produce observable feedback.

## Pragmatic Delivery Partner

Use for repo hygiene, delivery discipline, durable evidence, automation, and
broken-window prevention.

Required evidence: owner, command contract, validation state, dirty worktree
classification, and decision or handoff surface.

Good signals: one owner per rule, reversible changes, exact validation, durable
learning capture, no hidden manual sync.

Bad signals: stale docs, duplicate command contracts, manual-only process,
success claims without receipts.

Example: after repeated review feedback, update the canonical instruction and
add a validator rather than fixing only one line.

Stop when ownership or validation authority is contradictory.

## Story Slicer

Use for eval prompts, acceptance criteria, product specs, and thin delivery
slices.

Required evidence: actor, goal, current state, success state, extension path,
and acceptance signal.

Good signals: actor-goal wording, negative path, observable artifact or state,
small enough to run repeatedly.

Bad signals: implementation-only prompt, no user-visible outcome, keyword-only
assertions.

Example: turn "test the skill" into "when a user asks to shrink AGENTS.md,
does the agent preserve validation and memory contracts?"

Stop when the actor or success state is unknown.

## Use-Case Flow Designer

Use for CLI/app flows, skill invocation quality, and negative-path behavior.

Required evidence: primary actor, preconditions, main success scenario,
extensions, postcondition, and blocked states.

Good signals: main path is short, extensions are explicit, failure states tell
the next actor what to do.

Bad signals: happy path only, hidden preconditions, ambiguous completion.

Example: for a skill installer, define compatible, duplicate, incompatible, and
blocked-auth paths before writing install steps.

Stop when scope level or actor is not agreed.
