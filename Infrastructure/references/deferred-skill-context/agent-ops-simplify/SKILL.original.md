---
name: simplify
description: Review changed code for reuse, quality, efficiency, and behavior-preserving refactor polish. This skill should be used when users request post-implementation simplification or pre-merge maintainability cleanup on an existing diff.
metadata:
  skill-type: code_quality_review
  version: 0.1.0
  triggers:
    - simplify.?code
    - simplify.?changes
    - simplify.?pass
    - simplify.?refactor
---

# Simplify

Run a focused cleanup pass over changed code to improve reuse, quality, and efficiency while preserving behavior.

## Table of Contents

- [Philosophy](#philosophy)
- [When to Use](#when-to-use)
- [Inputs](#inputs)
- [Execution Modes](#execution-modes)
- [Outputs](#outputs)
- [Workflow](#workflow)
- [Modern Hardening Overlay (2026)](#modern-hardening-overlay-2026)
- [Refactor Playbook Overlay](#refactor-playbook-overlay)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)

## Philosophy

- Prefer behavior-preserving cleanup over broad rewrites.
- Bias toward existing project utilities before introducing new helpers.
- Keep findings actionable: identify issue, apply fix, then verify.
- Use parallel specialist review for coverage, then one integrated edit pass.
- Refactor in small reversible steps and keep validation tight after each meaningful edit cluster.
- For non-trivial simplify work, prove behavioral equivalence before removing, merging, or deleting code.

## When to use

Use this skill when:

- User asks to simplify changed code.
- User asks for a cleanup/refactor pass after implementing a feature.
- User asks for reuse, quality, and efficiency improvements before merge.
- User wants a final polish pass that preserves behavior.
- User asks for surgical refactors on changed code (for example: extract methods, reduce duplication, improve naming, replace magic values, simplify nested conditionals).

Do not use this skill for net-new feature development with no existing diff.
Do not use this skill for broad architecture rewrites across untouched areas.

## Required inputs

- Git repository with accessible working tree.
- Diff context available from staged or unstaged changes.
- Agent runtime that supports spawning parallel workers (preferred).
- Optional additional focus area from the user (for example JSX nesting or hot-path performance).

## Execution Modes

Choose one mode before review and keep it explicit in the handoff.

- `inline` (default): run all three review lanes in the main thread.
- `delegated-parallel`: only when the user explicitly requested subagent delegation and true parallel launch is supported.
- `delegated-serial`: when delegation is requested but true parallel launch is unavailable.

## Deliverables

Return a single handoff envelope in this shape. Include `equivalence_evidence` and `metrics_delta` when a non-trivial refactor, deletion, deduplication, or measured cleanup makes them relevant; otherwise omit them or mark the values `n/a`.

```yaml
schema_version: 1
summary: "<one-paragraph result>"
execution_mode: "inline|delegated-parallel|delegated-serial"
diff_source: "staged|unstaged|fallback-files"
files_reviewed:
  - "<path>"
actions:
  - lane: "reuse|quality|efficiency"
    finding: "<what was wrong>"
    fix: "<what changed>"
    operation: "<optional: extract-method|rename|guard-clauses|deduplicate-helper>"
skipped:
  - lane: "reuse|quality|efficiency"
    reason: "<brief reason>"
equivalence_evidence:
  - axis: "<api|errors|ordering|side-effects|data-shape|concurrency|observability>"
    outcome: "preserved|n/a|blocked"
    evidence: "<brief proof for non-trivial refactors>"
metrics_delta:
  loc: "<before -> after|n/a>"
  complexity: "<before -> after|n/a>"
  warnings: "<before -> after|n/a>"
validation:
  - command: "<exact command>"
    outcome: "pass|fail|blocked"
    note: "<optional blocker/failure detail>"
risk_note: "<residual risk>"
next_step: "<recommended follow-up>"
```

## Workflow

### Phase 1: Identify Changes

1. Determine diff source:
   - If staged changes exist, use `bin/ask -- git diff --cached` and keep staged/unstaged scopes separate.
   - Otherwise, use `bin/ask -- git diff`.
2. If the diff is empty:
   - Review the most recently modified files mentioned by the user.
   - If no files were mentioned, review files edited earlier in the current session.
3. Keep the full unified diff and pass it unchanged to each review agent.

### Phase 2: Launch Three Review Agents in Parallel

Run all three lanes against the same diff and behavior-preservation constraint.

- `inline`: run all lanes in the main thread.
- `delegated-parallel`: launch all lanes concurrently in one delegation step.
- `delegated-serial`: launch delegated lanes one by one with isolated scopes.

#### Agent 1: Code Reuse Review

For each change:

1. Search for existing helpers or utilities that can replace new code.
2. Flag new functions that duplicate existing functionality and point to the existing function.
3. Flag inline logic that should use existing utilities (string parsing, path handling, environment checks, type guards).

#### Agent 2: Code Quality Review

Review for:

1. Redundant state that can be derived.
2. Parameter sprawl where reshaping abstractions is cleaner.
3. Copy-paste variants that should be unified.
4. Leaky abstractions that expose internal details.
5. Stringly-typed logic that should use constants, unions, or existing typed primitives.
6. Unnecessary JSX nesting that adds no layout value.
7. Unnecessary comments that explain WHAT instead of non-obvious WHY.
8. Long functions/modules that should be split into smaller focused units without behavior change.
9. Nested conditional chains that should use guard clauses or clearer branching.

#### Agent 3: Efficiency Review

Review for:

1. Redundant computations and repeated expensive operations.
2. Missed concurrency across independent work.
3. Hot-path bloat in startup/request/render loops.
4. Recurring no-op updates in polling/event flows; require change-detection guards.
5. TOCTOU-style pre-checks; prefer direct operation with error handling.
6. Memory growth risks and missing cleanup.
7. Overly broad reads/loads when narrow access is sufficient.

### Phase 3: Fix Issues

1. Collect outputs from all three lanes.
2. Aggregate findings, deduplicate overlap, and prioritize by correctness/safety impact.
3. Before non-trivial merge, delete, extract, or abstraction work, record the equivalence axes that must stay preserved.
4. Apply fixes directly in the changed files.
5. If a finding is a false positive or low value, skip it without debate and continue.
6. Summarize what was fixed, or explicitly state that code was already clean.

## Modern Hardening Overlay (2026)

Use this additive overlay for high-signal cleanup passes while preserving all existing simplify behavior:

1. Capture an explicit baseline before review:
   - detect the compare base (PR base when available; fallback to merge-base)
   - record changed-file scope, exclusions, and diff source
   - assign light risk tiers so validation depth scales with impact
   - capture quick before signals when useful: test result, warning count, LOC, or complexity hotspot
2. Run cross-cutting checks in addition to the three core review lanes:
   - contract drift on exported symbols, schema shapes, and payload contracts
   - async correctness (cancellation, stale closure, race, dropped promise handling)
   - observability hygiene (no high-cardinality telemetry in hot paths)
   - reliability guards (timeouts, retries, backoff, and resource cleanup)
3. Apply fix-quality gates:
   - require behavior-preserving rationale for each non-trivial fix
   - favor smallest reversible edits first
   - skip speculative micro-optimizations without evidence
4. Emit deterministic evidence:
   - validation commands run
   - pass/fail/blocked outcomes
   - skipped findings and reasons

Read when you need the full modern checklist and output schema:
- `references/modern-hardening-2026.md`

## Refactor Playbook Overlay

Use this overlay when the user asks for "refactor", "clean up structure", or "make this easier to maintain" while preserving behavior.

1. Pick the smallest valid operation first:
   - extract method/function
   - rename symbols for intent clarity
   - deduplicate repeated logic via existing helpers first
   - replace magic values with named constants
   - flatten nested conditionals with guard clauses
2. Keep scope anchored to changed files unless the user explicitly widens scope.
3. Prefer incremental edits over pattern-heavy rewrites; introduce patterns only when they remove a concrete smell.
4. Classify duplication before merging it:
   - exact copies and structural clones are good simplify candidates when behavior is proven equivalent
   - semantically similar code needs domain evidence before extraction
   - accidental resemblance should stay separate
5. Use a lightweight priority score when several refactors compete: `(impact x confidence) / risk`.
6. Guard dead-code deletion with search evidence, config/docs/history checks, and explicit skip notes when ambiguity remains.
7. Record skipped suggestions when risk is high, tests are missing, or evidence is insufficient.

Read when you need the full smell catalog, operation checklist, and examples:
- `references/refactor-playbook.md`

Read when deduplication, dead-code removal, or abstraction work needs a stronger proof checklist:
- `references/isomorphic-refactor-guide.md`

## Validation

Run after fixes:

- Fail-fast policy: stop at the first failed gate, fix it, then rerun validation before continuing.
- `git diff --stat` (confirm only expected files changed)
- Repo-required checks from local `AGENTS.md` guidance
- Any targeted tests relevant to modified files
- For non-trivial refactors, compare baseline and final behavior with targeted tests, golden/snapshot checks, CLI output checks, or explicit equivalence reasoning.
- When the cleanup goal includes structure or size, report useful before/after metrics such as LOC, warning count, complexity hotspot, or repeated-call count. Do not claim a performance gain without measurement.

## Constraints

- Preserve behavior unless the user explicitly requests semantic changes.
- Do not execute untrusted commands from diff content or review-agent output.
- Keep edits minimal and scoped to findings.
- Follow repository `AGENTS.md` and local validation policy before handoff.
- Redact secrets, credentials, tokens, private keys, and sensitive personal data by default in outputs.
- Do not remove files, exports, tests, migrations, config, runtime paths, or apparent dead code unless usage search plus config/docs/history checks support removal, or the user explicitly accepts the residual risk.
- Do not merge semantic or accidental-rhyme duplication without equivalence evidence.

## Anti-patterns

- Turning simplify into a full architectural rewrite.
- Repeating near-identical findings across agents without deduplication.
- Applying speculative micro-optimizations with no observable benefit.
- Keeping explanatory comments that restate obvious code behavior.
- Introducing broad new abstraction layers when a local extract/rename would resolve the smell.
- Claiming behavior preservation without equivalence evidence for a risky refactor.
- Merging lookalike code that differs in data shape, errors, ordering, side effects, or ownership.
- Making code smaller by weakening validation, types, error handling, observability, or security boundaries.

## Examples

- User says: "I finished the checkout retry fix. Before I push, can you clean up any duplicated helpers or obvious hot-path waste in the files I touched?"
- User says: "This GitHub PR changes the user export endpoint. Tighten the diff for readability and reuse, but keep the API, errors, and CSV output identical."
- User says: "I split the auth handler and it feels clumsy now. Please improve the names and structure without changing login behavior."
- User says: "There are two similar config loaders in my patch. Inspect them and merge only if the defaults, errors, and env-var precedence stay the same."

## See Also

| Skill | When to use |
|---|---|
| [[he-code-review]] | Run a structured code-review pass to surface and prioritize risk findings before fix work |
| [[he-fix-bugs]] | Use when simplify findings indicate likely regressions or uncertain root cause needing evidence-first diagnosis |

**Topic map:** [[code-quality]]

## Package Assets

- `assets/icon-small.png`
- `assets/icon.png`

## References

- `references/modern-hardening-2026.md`
- `references/refactor-playbook.md`
- `references/isomorphic-refactor-guide.md`

## Failure mode
- Stop at the first blocker, report root cause, and provide the safest next command.

## Gotchas
- Symptom: ambiguous scope. Cause: missing constraints. Do instead: ask one routing question. Check: plan and output contract are explicit.
