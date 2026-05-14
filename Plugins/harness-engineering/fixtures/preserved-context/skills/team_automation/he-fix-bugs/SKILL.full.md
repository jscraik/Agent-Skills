---
name: he-fix-bugs
description: Systematically reproduce, diagnose, and fix bugs with root-cause-first evidence and safe validation gates. Use when the user asks to debug failures, investigate regressions, or fix broken behavior from tracker issues or direct symptoms.
metadata:
  skill-type: team_automation
---

# Harness Engineering Fix Bugs

**Note: The current year is 2026.** Use this when dating incident artifacts and validating recency-sensitive references.

`he-plan` defines execution strategy. `he-work` executes scoped implementation. `he-fix-bugs` is the canonical Harness Engineering bug workflow for root-cause diagnosis and targeted remediation.

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Interaction Method](#interaction-method)
- [Workflow](#workflow)
- [Subagent policy](#subagent-policy)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Output contract](#output-contract)
- [References](#references)

## Working agreement
- Investigate before fixing.
- Explain the full causal chain from trigger to symptom before proposing changes.
- Use one hypothesis and one meaningful change at a time.
- Keep evidence explicit: command, artifact, path, and observed result.
- Keep tracker context intact when the request comes from Linear or GitHub.
- If diagnosis confidence is insufficient, return partial or blocked status rather than forcing a speculative fix.

## When to use
Use this stage when:
- the user asks to debug or fix a bug,
- there is a failing test, runtime error, or regression to investigate,
- the request references issue context from Linear/GitHub that must be reproduced first,
- prior fix attempts failed and the user needs a disciplined root-cause loop.

Typical triggers:
- "debug this"
- "fix this bug"
- "why is this failing?"
- "trace this error"
- "investigate issue ENG-123"
- "reproduce GitHub issue #482 then fix it"

## When not to use
Route elsewhere when:
- the user wants greenfield implementation (`he-work`),
- the user wants lifecycle/stage routing (`he-compound` or `he-router`),
- the user needs design-level reframing rather than bug-level diagnosis (`he-brainstorm`),
- the request is pure issue management with no reproduction/investigation work.

## Required inputs
- bug context:
  - tracker issue reference (`linear | github`) or
  - manual symptom report (`manual-context`)
- observed symptom(s) or failure artifact(s),
- expected behavior,
- environment clues and constraints,
- execution permission (`diagnosis-only` or `diagnose-and-fix`).

If critical context is missing, ask one blocking question before execution.

## Deliverables
- explicit intake source (`linear`, `github`, or `manual-context`),
- reproduction status (`confirmed`, `not_reproduced`, `partial`, or `blocked`),
- root-cause summary with file:line evidence where available,
- proposed fix scope and regression test recommendations,
- implemented fix evidence when the user opted into remediation,
- concise next-step recommendation (`fix now`, `investigate further`, `route to he-brainstorm`, `route to he-compound`),
- `schema_version: 1` when structured output is requested.

## Failure mode
- If tracker content cannot be fetched, ask for the smallest missing identifier or pasted issue context.
- If reproduction is not possible in this environment, return `blocked` with exact missing condition(s).
- If repeated hypotheses fail, escalate with diagnosis rationale and next safest route.

## Interaction Method

Use the platform's blocking question tool when available (`AskUserQuestion` in Codex, `request_user_input` in Codex, `ask_user` in OpenAI). Otherwise, present numbered options in chat and wait for the user's reply before proceeding.

Ask one question at a time. Prefer concise single-select choices when natural options exist.

## Workflow

### Phase 0: Intake and triage
1. Parse bug context and issue reference.
2. If tracker-based:
   - fetch and summarize issue context (symptom, expectation, reproduction hints, environment clues),
   - keep tracker source (`linear` or `github`) attached to all downstream findings.
3. If prior failed attempts are mentioned, capture what was already tried.

### Phase 1: Reproduce first
1. Attempt deterministic reproduction using the narrowest route:
   - test route for logic/backend failures,
   - browser route for UI behavior,
   - manual route for environment-constrained failures.
2. Capture evidence for each attempt (logs, command output, screenshots, failing test output).
3. If reproduction fails after multiple attempts, switch to intermittent/instrumented tactics from `references/investigation-techniques.md`.

### Phase 2: Trace and identify root cause
1. Trace backward from symptom to origin:
   - where invalid state first appears,
   - why that state is allowed through,
   - which boundary failed to block it.
2. Form ranked hypotheses.
3. For uncertain links, define one prediction that should hold in a separate code path or scenario.
4. Confirm the full causal chain before suggesting remediation.

### Phase 3: Present diagnosis and options
Present:
- root cause summary with file:line references,
- minimal fix plan,
- tests to add or update,
- why current tests did not catch this earlier.

Then offer next action:
1. fix now in this stage,
2. continue diagnosis if confidence is still low,
3. route to `he-brainstorm` when the issue is structural design debt,
4. route to `he-compound` for solved-problem capture after fix validation.

### Phase 4: Implement fix (when chosen)
1. Confirm workspace safety (`git status` and overlap check).
2. Prefer test-first or failing-test-first validation.
3. Apply minimal root-cause fix.
4. Re-run targeted tests and relevant broader gates.
5. Verify no new regressions in touched behavior.

### Phase 5: Close and handoff
Return:
- problem statement,
- root cause chain,
- evidence summary,
- fix summary (or diagnosis-only status),
- prevention guidance,
- confidence level.

For tracker-driven requests, provide ready-to-post issue update text but do not post automatically unless explicitly requested.

## Subagent policy
- Stage policy source: `../../../../../references/routing-map.json` under `he-fix-bugs`.
- Resolve role availability from `~/.codex/agents/manifest.json`.
- If auto-spawn is unavailable, continue inline and provide manual role guidance.
- If required roles are missing, route creation/install to `[[codex-agent-creator]]`.

## Validation
- Verify reproduction status is explicit.
- Verify diagnosis evidence supports the causal chain.
- Verify remediation scope matches the diagnosed cause.
- Verify fix validation includes at least one failure-proof check.
- Verify any blocked state includes concrete missing inputs or environment gaps.

## Anti-patterns
- proposing fixes before root cause confirmation,
- shotgun edits across unrelated files,
- declaring success from symptom suppression,
- skipping reproduction evidence,
- merging tracker intake and issue management into one speculative step.

## Output contract
Use this schema when structured output is requested:

```json
{
  "schema_version": 1,
  "issue_source": "linear|github|manual-context",
  "issue_ref": "string|null",
  "reproduction_status": "confirmed|not_reproduced|partial|blocked",
  "root_cause_summary": "string|null",
  "fix_status": "not_started|in_progress|completed|skipped",
  "evidence": ["string"],
  "next_step": "string"
}
```

## References
- [Anti-Patterns](./references/anti-patterns.md)
- [Investigation Techniques](./references/investigation-techniques.md)
- [Tracker Intake And Reporting](./references/tracker-intake-and-reporting.md)
- [Contract](./references/contract.yaml)
- [Evals](./references/evals.yaml)
- [Source Parity](./references/source-parity.md)
- [Task Profile](./references/task-profile.json)

## See Also

| Skill | When to use |
|---|---|
| [[he-work]] | Execute broader implementation once bug scope is resolved |
| [[he-plan]] | Re-sequence work when repeated bugs reveal plan gaps |
| [[he-brainstorm]] | Redesign boundaries when root cause is architectural |
| [[he-compound]] | Capture validated fix learnings in durable docs/solutions |

**Topic map:** [[agent-ops]]
**Topic map:** [[agent-ops]]

## Deferred Context Preservation

Apply the context-disposition policy: move important still-valid context to references and index it when meaningful; intentionally discard stale, duplicated, unsafe, superseded, or low-signal text.
