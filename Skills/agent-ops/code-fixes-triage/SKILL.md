---
name: code-fixes-triage
description: "Turn Slack #code-fixes, CodeRabbit, Codex Review, CI, and check-status noise into a repo-and-PR action queue. Use when Jamie asks for a daily code-fixes digest, recent review-noise triage, or what needs fixing across active engineering repos."
metadata:
  version: "0.1.0"
  skill-type: team_automation
---

# Code Fixes Triage

Convert noisy review and CI signals into a small action queue before starting any fix lane.

## Philosophy

The useful unit is not a digest. The useful unit is a short queue that says what can move now, what only needs watching, what is informational, and what is blocked until a source of truth is refreshed.

## When To Use

- Jamie points to Slack '#code-fixes', CodeRabbit notifications, Codex Review output, CI status drift, or review-noise digests.
- The request is to decide what needs attention across repos or PRs.
- A signal may lead to 'pr-green-sweep', 'autofix', 'testing', 'release-notes', or a repo-specific fix, but the first job is classification.

## Inputs

- Signal source and time window, defaulting to the last 24 hours for '#code-fixes'.
- Target repos or PRs when provided.
- Available live source-of-truth tools: GitHub, CI, CodeRabbit, Linear, local repo checkout, and repo validation commands.

See 'references/contract.yaml' for the compact machine-readable contract and 'references/evals.yaml' for routing checks.

## Workflow

1. Gather only the relevant signal text and group it by repository and PR.
2. Treat Slack and bot messages as signal surfaces, not delivery truth.
3. For each item, refresh the live state that matters: GitHub PR, latest head SHA, required checks, review threads, tracker state, local branch or worktree, and relevant validation output.
4. Classify each item as 'fix_now', 'monitor', 'informational', or 'blocked'.
5. Name the owner lane: 'pr-green-sweep', 'autofix', 'testing', 'release-notes', 'docs-expert', repo-specific implementation, or no action.
6. Promote repeated noise into the durable destination it implies: guardrail, test, docs contract, skill behavior, eval fixture, or tracker issue.
7. Stop before implementing fixes unless the user asked for follow-through or the routing skill owns execution.

## Outputs

~~~yaml
schema_version: 1
mode: code_fixes_triage
window: <time window inspected>
sources: [<slack|github|coderabbit|ci|linear|local>]
action_queue:
  fix_now:
    - repo: <owner/repo or local path>
      pr: <number-or-null>
      signal: <short signal>
      live_truth: <what was refreshed>
      next_lane: <skill-or-agent>
      blocker: null
  monitor: []
  informational: []
  blocked: []
source_of_truth_gaps: []
durable_followups: []
validation: []
~~~

## Execution Boundaries

- Do not claim merge readiness from Slack, CodeRabbit summaries, old CI snapshots, or memory alone.
- Do not resolve review threads, merge PRs, mutate trackers, or post comments from this triage step unless the user explicitly asks for that action.
- Use explicit network permission for live GitHub, CodeRabbit, CI, package-registry, and tracker calls in sandboxed sessions.
- Redact secrets, private URLs, credentials, customer data, and sensitive operational details.

## Constraints

- Keep the first pass read-mostly and classification-only.
- Refresh live truth before placing any item in 'fix_now'.
- Preserve separate facts for local tests, remote checks, review threads, tracker state, artifacts, and merge readiness.
- Redact secrets, tokens, API keys, credentials, PII, and sensitive operational details by default.

## Gotchas

- Returning a generic Slack summary when Jamie asked what needs fixing.
- Blending local tests, remote checks, review threads, tracker state, and merge readiness into one optimistic status.
- Creating a PR sweep heartbeat before the queue proves there is useful follow-through work.
- Treating every bot message as actionable without stale-thread or latest-head checks.

## Anti-Pattern

- Treating a CodeRabbit summary, Slack message, or old CI notification as the current PR state.
- Spawning a broad fixer before grouping signals by repo and PR.
- Marking a stale review or check as resolved without latest-head proof.
- Routing a release-note, docs-only, or local-test request into this triage skill when a narrower owner already exists.

## Failure Mode

If live truth cannot be refreshed, keep the item in 'blocked' or 'source_of_truth_gaps' and state the exact missing surface. Do not upgrade the item to 'fix_now' from stale notification text.

## Examples

- Jamie asks: "Turn the last day of #code-fixes into a fix queue for coding-harness and agent-skills." Group each Slack or bot signal by repo and PR, refresh live GitHub/CI/review truth, then return fix_now, monitor, informational, and blocked buckets.
- Jamie asks: "Slack says PR 214 is green now; can we close it?" Refuse to treat Slack as readiness proof, refresh latest head checks and unresolved review threads, then report the remaining source-of-truth gaps.
- Jamie asks: "CodeRabbit says this can be simplified." Verify the thread is current and unresolved, then route to 'autofix' or mark informational if the branch moved on.

## Validation

For changes to this skill, run:

~~~bash
./bin/ask skills audit Skills/agent-ops/code-fixes-triage --level strict --json --robot
~~~

Fail fast at the first failed gate and classify the blocker before sync, commit, publish, or install.

## See Also

| Skill or Agent | Use After Triage |
| --- | --- |
| 'pr-green-sweep' | Open PRs need until-green fix, merge, and cleanup follow-through. |
| 'autofix' | Actionable CodeRabbit or Codex Review findings need implementation. |
| 'testing' | Test or validation failure ownership needs proof or repair. |
| 'release-notes' | The useful action is a changelog, release note, or publish handoff. |
| 'delivery-state-auditor' | A read-only readiness audit is needed before claiming closeout. |
