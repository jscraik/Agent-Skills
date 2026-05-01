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
6. If past agent sessions are needed as evidence, route broad session inventory/extraction to `skill-refactor`; if the result is a reusable workflow, route skill creation to `skillify`.
7. If helpers are used during learning capture, they return text only; the orchestrator writes the final artifact.
8. If overlap with an existing solution is high, refresh the existing doc instead of creating a duplicate.
9. Treat `he-compound-refresh` as folded `he-compound` refresh mode. Load preserved refresh context when adjacent stale or overlapping docs need selective follow-up beyond the current artifact.

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
- Do not turn generic session-history search into a Harness Engineering stage; consume `skill-refactor` or `skillify` outputs when session evidence is relevant.
- Do not let helper agents write intermediate files during learning capture.
- Do not recommend deleting or ignoring protected process artifacts just to simplify the handoff.
- Do not remove important context for budget trimming; move it to references and index it in `../../../references/deferred-context-index.md`.

## Anti-patterns

- Guessing stage progression without checking existing artifacts.
- Recording unresolved incidents as solved knowledge.
- Creating a duplicate solution doc when a high-overlap artifact should be refreshed.
- Returning broad "use Harness Engineering" guidance without naming the exact mode and next stage.

## Full Context

- Assets: [icon-small.png](./assets/icon-small.png), [icon-large.png](./assets/icon-large.png)
- Folded refresh context: [../../../references/folded-skill-context.md](../../../references/folded-skill-context.md)

## Examples

- "Can you inspect this feature's artifacts, resume from the right Harness Engineering stage, and tell me the next exact action?"
- "We fixed the same CI failure twice. Capture the solved workflow once and refresh the existing solution if it overlaps."
- "Help me coordinate brainstorm, spec, plan, work, and review for this Linear issue without skipping the earliest weak stage."
