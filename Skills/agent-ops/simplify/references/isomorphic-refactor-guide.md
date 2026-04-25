# Isomorphic Refactor Guide

Read when:
- the simplify pass proposes deduplicating similar code;
- code removal looks obvious but could hide runtime/config usage;
- a refactor must prove "same behavior, simpler shape";
- multiple cleanup candidates need prioritizing.

Use this guide to keep refactors behavior-preserving without importing heavy artifact requirements into the main skill.

## Operating Rule

For any non-trivial simplify edit, prove behavior equivalence before changing structure:

1. Identify the behavior surface that must stay identical.
2. Classify the duplication or smell.
3. Choose the smallest operation that removes the smell.
4. Validate the behavior surface with tests, snapshots, CLI output checks, or explicit reasoning.
5. Report residual uncertainty instead of pretending it is gone.

## Equivalence Axes

Check only the axes that matter for the changed code.

| Axis | Preserve |
|---|---|
| API shape | names, exports, signatures, accepted inputs, return shape |
| Error behavior | exception type, message contract, status code, fallback path |
| Ordering | stable sort, event order, lifecycle order, hook order |
| Side effects | writes, network calls, telemetry, cache mutation, cleanup |
| Data shape | schema fields, defaults, nullable values, serialization |
| Concurrency | cancellation, idempotency, locking, retries, promise handling |
| Observability | logs, metrics, trace propagation, redaction |
| Performance envelope | hot-path call count, repeated expensive work, startup cost |
| Security boundary | auth, authorization, validation, escaping, secret handling |

If an axis changes intentionally, stop treating the edit as simplify-only and call out the semantic change.

## Duplication Taxonomy

Use this before extracting helpers.

| Type | Meaning | Simplify action |
|---|---|---|
| I exact clone | copied code with only whitespace/comment changes | merge when tests or search prove all call sites align |
| II renamed clone | same structure with renamed variables/literals | extract only when parameter names do not carry different domain meaning |
| III near-miss clone | same algorithm with small statement differences | extract the common core; keep variant behavior explicit |
| IV semantic duplicate | different code that appears to do the same job | require domain proof and behavioral checks before merging |
| V accidental rhyme | code looks similar but has different ownership, timing, or failure behavior | do not merge in simplify mode |

Prefer existing project helpers before creating a new helper. If a new helper is needed, keep it narrow and colocated unless the project already has a shared utility home.

## Candidate Scoring

When there are several possible refactors, score quickly instead of chasing every smell:

`priority = (impact x confidence) / risk`

Use 1-5 for each value:
- impact: reduces duplication, complexity, bug surface, or hot-path waste;
- confidence: behavior is understood and covered by tests or clear evidence;
- risk: blast radius, missing tests, runtime/config coupling, public API surface.

Do high-priority candidates first. Skip low-confidence cleverness even when it would reduce LOC.

## Dead-Code Deletion Guard

Before deleting code, files, tests, exports, config, migrations, scripts, or runtime paths:

1. Search direct usages with `rg`, including quoted and unquoted names where relevant.
2. Check dynamic entrypoints: config files, package scripts, workflows, hooks, reflection, plugins, generated manifests, docs, and runtime loaders.
3. Check tests and examples for behavioral contracts.
4. Use git history when the code looks intentionally retained or recently added.
5. If evidence is incomplete, skip deletion or ask for explicit approval.

Safe deletion examples:
- unused import or local variable with compiler/linter support;
- commented-out code with no live behavior;
- private helper with no direct or dynamic references and adjacent tests still pass.

Unsafe deletion examples:
- exported symbol with no local references;
- test fixture, migration, hook, workflow, or script referenced by convention;
- code that only appears unused because it is loaded dynamically.

## Metrics and Tension Signals

Use metrics as evidence, not as goals.

Useful before/after signals:
- LOC or diffstat for the touched scope;
- complexity hotspot count;
- lint/type warning count;
- test/golden/snapshot result;
- repeated operation count in a hot path;
- bundle size or startup timing when already measured by the repo.

Tension signals that mean "stop or narrow the refactor":
- LOC drops because validation, error handling, or types were weakened;
- abstraction requires more parameters than the duplicated code;
- helper name becomes vague because variants do not share one concept;
- tests must be deleted or relaxed to make the refactor pass;
- public API, telemetry, or error text changes without user approval.

## AI-Generated Code Smells

These are good simplify targets when the current diff contains them:

- generic helpers with names like `processData`, `handleThing`, or `doStuff`;
- repeated defensive branches that hide the real invariant;
- multiple functions that differ only by superficial naming;
- broad try/catch blocks that swallow important failures;
- fake configurability with options that are never used;
- duplicate schema/type definitions that can drift.

Do not assume AI-looking code is wrong. Treat it as a prompt to gather evidence.

## Reporting Template

For a risky refactor, include a compact card in the final handoff:

- `operation`: extract-method, deduplicate-helper, delete-dead-code, rename, guard-clause, or other small operation
- `equivalence_axes`: axes checked and result
- `evidence`: tests, search, snapshots, output comparison, or reasoning used
- `metrics_delta`: LOC, complexity, warnings, or not applicable
- `residual_risk`: what could still be missed

Keep the card short. The main simplify output should still lead with what changed and how it was validated.
