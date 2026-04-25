---
name: he-compound
description: Run a bounded Harness Engineering lifecycle across multiple stages. Use when the user wants coordinated brainstorm, spec, plan, work, review, and fix flow rather than one isolated stage.
metadata:
  skill-type: team_automation
---

# Harness Engineering Compound

Progressive-disclosure entrypoint for stage orchestration and durable learning capture in Harness Engineering.

## Philosophy

- Route to the correct stage before acting.
- Capture verified outcomes as reusable team knowledge.
- Keep orchestration, evidence gathering, and durable learning capture explicit instead of collapsing them into generic advice.

## When to use

- Route/resume work from the correct Harness Engineering stage.
- Capture a verified fix in `docs/solutions/` and avoid duplicate docs by refreshing existing artifacts when overlap is high.
- Decide whether a request needs lifecycle orchestration, solved-problem capture, or a resume-from-stage handoff before downstream work starts.

## Inputs

- Request, artifacts, repo context, and linked Linear issues.

## Outputs

- `schema_version: 1` when structured; result, validation, blockers, and next Harness Engineering action.

## Procedure

1. Select lifecycle mode using artifact-first evidence.
2. For lifecycle routing, continue from the earliest incomplete or untrusted stage.
3. If the user intent is ambiguous between stage orchestration and solved-problem capture, ask one direct question before continuing.
4. For learning capture, preserve `full` as the default and treat `compact-safe` as explicit opt-in.
5. For learning capture, validate solved evidence, gather supporting inputs, and write exactly one durable solution artifact.
6. If helpers are used during learning capture, they return text only; the orchestrator writes the final artifact.
7. If overlap with an existing solution is high, refresh the existing doc instead of creating a duplicate.
8. Recommend `he-compound-refresh` only when adjacent stale or overlapping docs need selective follow-up beyond the current artifact.

## Validation

- Confirm mode selection matches available evidence.
- Confirm stage recommendation names the exact next Harness Engineering command or stage.
- For learning capture, verify solved status before writing docs, keep the one-file-write contract explicit, and ensure duplicate-avoidance logic is explicit.
- Any refresh recommendation must be narrow and evidence-backed rather than a blanket cleanup suggestion.
- Fail fast: stop at first failed gate and do not continue.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not document unverified fixes as durable solutions.
- Do not treat `he-compound` as a substitute for implementation, debugging, review, or refresh stages that still need to happen.
- Do not let helper agents write intermediate files during learning capture.
- Do not recommend deleting or ignoring protected process artifacts just to simplify the handoff.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Guessing stage progression without checking existing artifacts.
- Recording unresolved incidents as solved knowledge.
- Creating a duplicate solution doc when a high-overlap artifact should be refreshed.
- Returning broad "use Harness Engineering" guidance without naming the exact mode and next stage.
## Examples

Read when: examples or role-routing details are needed, open the archived references for this skill.
