---
name: he-refine
description: "[BETA] Improve user-facing quality of an existing feature through guided refinement and validation loops. Use when behavior works but UX, accessibility, or polish quality must be raised before review."
metadata:
  skill-type: team_automation
---

# Progressive Disclosure Entry

This entrypoint stays concise and keeps full operational context in archived references.

## Use

- Use this skill as normal for this Harness Engineering stage.
- For full stage policy, workflow details, and examples, load the archived full guide.

## Philosophy

- Refine through tight feedback loops, not speculative redesign.
- Keep polish work measurable and bounded to user-visible outcomes.
- Keep the dev-server and browser loop stable so each refinement maps to live behavior the user can verify quickly.

## When to use

- Use when implementation is functional but needs quality polish before final review.
- Use for browser-first refinement loops with explicit iteration gates.
- Use when the fastest path is to run the feature, inspect it in the browser, and iterate directly on what the user says feels off.

## Inputs

- Current implementation state, target UX outcomes, and constraints.
- Existing QA findings, visual diffs, or usability observations.
- Optional PR number or branch name to refine.
- Dev-server startup constraints, launch config, or framework hints when known.

## Outputs

- Prioritized refinement actions with acceptance criteria.
- Iteration summary and readiness recommendation.
- Verified branch and dev-server URL when the refinement loop is running.
- Explicit next-stage recommendation: `continue`, `he-work`, `he-code-review`, or `stop`.
- Include `schema_version: 1` when structured output is requested.

## Procedure

1. Start from the correct branch or PR context and block if the current branch is a protected default branch.
2. Resolve dev-server startup from launch config first, then fall back to project-type and port detection when needed.
3. Start and probe the dev server before claiming readiness.
4. Open the feature in the browser and iterate in small loops: one user-noted issue, one focused fix, one quick re-check.
5. Report resolved gaps, remaining blockers, and the safest next stage.

## Validation

- Ensure each refinement maps to a measurable user-facing improvement.
- Ensure regression risk is checked before stage exit.
- Ensure branch, server, and browser readiness are verified before edits depend on live feedback.
- Ensure each iteration stays focused on explicit user feedback rather than bundled polish churn.
- Fail fast: stop at first failed gate and do not proceed.

## Constraints

- Redact secrets, credentials, tokens, and sensitive data by default.
- Do not broaden refinements into unrelated feature work.
- Do not polish directly on `main` or `master`.
- Do not skip server-health probing before asking the user to browse and react.
- Do not remove important context for budget trimming; move it to references and index it in [../../../references/deferred-context-index.md](../../../references/deferred-context-index.md).

## Anti-patterns

- Cosmetic churn without acceptance criteria.
- Iterating without verifying whether user-facing quality improved.
- Making multiple unrelated fixes in one loop without user confirmation.
- Treating refinement as a replacement for broader implementation or planning stages.

## Examples

- "When the user asks, `Can you run the feature locally with me and polish the rough edges before review?`"
- "Please start from the existing `launch.json`, inspect the dev-server startup, and then guide the browser refinement loop."
- "Help me keep the refinement tight: one issue, one fix, one quick re-check."

## Full Context

- Canonical contract: [./Infrastructure/references/contract.yaml](./Infrastructure/references/contract.yaml)
- Canonical eval cases: [./Infrastructure/references/evals.yaml](./Infrastructure/references/evals.yaml)
- Canonical task profile: [./Infrastructure/references/task-profile.json](./Infrastructure/references/task-profile.json)
- Compatibility mirror (non-canonical): [./references](./references)
- Assets: [./assets](./assets)
- Assets directory marker: `assets/`
- Subagent routing: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
Read when: deeper behavior or routing policy is needed.

## Subagent Routing

- Canonical stage map: [../../../references/subagent-routing.md](../../../references/subagent-routing.md)
- Machine-readable policy: [../../../references/routing-map.json](../../../references/routing-map.json)
- Resolve available roles from `~/.codex/agents/manifest.json` before spawning helpers.
- Apply the mapped stage policy (`always`, `conditional`, or `manual-only`) before delegation.
- If auto-spawn is unavailable, continue inline and explicitly list the roles the user can launch manually.
- If required roles are missing from the manifest, create or install them with [../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md](../../../../../Skills/agent-ops/codex-agent-creator/SKILL.md) before rerunning delegated coverage.
