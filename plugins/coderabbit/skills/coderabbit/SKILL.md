---
name: coderabbit
description: Answer CodeRabbit setup, configuration, knowledge-base, review-command, tool, and rollout questions by retrieving evidence from the local crawl corpus. Use when a user needs repository-local CodeRabbit documentation to decide how to configure, operate, or troubleshoot CodeRabbit, not when they need generic CI authoring or live SaaS state changes.
metadata:
  skill-type: library_api_reference
---

# CodeRabbit Reference Assistant

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [Philosophy](#philosophy)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Deliverables](#deliverables)
- [Fix CodeRabbit Review Comments](#fix-coderabbit-review-comments)
- [Failure mode](#failure-mode)
- [Output contract](#output-contract)
- [Corpus and evidence policy](#corpus-and-evidence-policy)
- [Workflow](#workflow)
- [Verification](#verification)
- [Validation](#validation)
- [Constraints](#constraints)
- [Gotchas](#gotchas)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [See Also](#see-also)

## Standards snapshot
- Treat local crawl artifacts as the primary source of truth for CodeRabbit guidance.
- Prefer retrieval-first answers: locate evidence in `plugins/coderabbit/skills/coderabbit/references/coderabbit-docs` before drafting recommendations.
- Return concrete, actionable steps with file-backed provenance whenever possible.
- Distinguish local-corpus answers from live/vendor-state assumptions.
- Escalate missing-doc or stale-doc risk explicitly instead of guessing.

## Philosophy
- Use a setup-first framework: baseline configuration, safety checks, then optional advanced features.
- Explain why each recommendation exists and what tradeoff it introduces.
- Adapt depth to user context: quickstart for first-time setup, cross-family evidence for mature teams and multi-surface rollout guidance.
- Keep scope tight: start with the smallest package boundary that answers the question before widening to different or more customized surfaces.
- Help the user choose the smallest safe rollout step that still moves their CodeRabbit setup forward.
- Unlock a capable next step so the user can explore, customize, and extend the rollout without guessing.

## When to use
- User asks how to configure CodeRabbit reviews, tools, checks, CLI, or pull request commands.
- User wants CodeRabbit YAML examples adapted from official docs captured in local crawl output.
- User needs CodeRabbit feature guidance (Autofix, Simplify, Walkthroughs, metrics, integrations).
- User asks for a CodeRabbit migration or rollout plan and wants evidence-backed references.

## When not to use
- The request is primarily CircleCI pipeline authoring with no CodeRabbit decision point.
- The request is generic PR review triage unrelated to CodeRabbit behavior.
- The user needs fresh live data from CodeRabbit SaaS state not present in local artifacts.
- The user asks for Cloudflare crawl orchestration itself (use `cf-crawl`).

## Required inputs
- The target outcome, for example config draft, command reference, migration plan, or troubleshooting path.
- The CodeRabbit surface area in scope: config, CLI, PR commands, tools, integrations, planner, or reporting.
- Any platform constraints: GitHub, GitLab, Bitbucket, Azure DevOps, self-hosted.
- Optional path constraints if output must target specific repo files such as `.coderabbit.yaml`.
- Guiding questions:
  - Which repository surface should this update target first?
  - What review behavior should be enabled now versus later rollout phases?
  - Which constraints (compliance, CI policy, branch protections) must the setup respect?

## Discovery interview
- Use discovery only when scope is ambiguous.
- Ask one round at a time and keep it short.
- Start each round with one plain-language question.
- Include a short `Why this matters:` line after the question.
- Avoid dumping the whole interview plan at once.
- Confirm platform and desired outcome before proposing config changes.
- Use `references/evals.yaml` pressure and negative cases to guard against over-triggering.
- Use `references/discovery-interview.md` when discovery is needed.

## Deliverables
- Source-grounded answer with cited corpus files.
- Optional draft snippets for `.coderabbit.yaml` or PR command playbooks.
- Clear boundary notes when docs are stale, missing, or require live verification.
- If asked for structured output, return the JSON shape in this file's Output contract section.

## Fix CodeRabbit Review Comments

This flow is for an external CodeRabbit CLI workflow (not a local corpus command). If a PR number is provided, check out the PR branch first, then run the supported CLI review command.

### Prerequisites

- Install the CodeRabbit CLI from the official installer:

  ```bash
  curl -fsSL https://cli.coderabbit.ai/install.sh | sh
  ```

- Authenticate the CLI and confirm it is available in the active environment.

1. Fetch all open CodeRabbit comments via API or local dump.
2. Categorize each comment by type: `types`, `security`, `validation`, `linting`, `tests`.
3. Fix each category in batch, by file type, running tests after each batch.
4. Commit with message: `fix: address CodeRabbit review comments`.
5. Verify all comments are resolved before finishing.

Example command entry (explicit, CLI-driven flow):

```bash
# Review changes in the checked-out PR branch (local CLI)
gh pr checkout <pr-number>
cr --plain

# If the short `cr` wrapper is unavailable in your environment:
coderabbit review --plain
```

## Setup quickstart
1. Confirm the target platform and repository constraints before drafting config.
2. Start with a minimal `.coderabbit.yaml` and explicitly set `reviews.sequence_diagrams`.
3. Validate that review comments and PR command flows operate on a test PR.
4. Expand to integrations (for example CI/CD failure analysis) only after baseline stability.
5. Capture the chosen defaults and rollout caveats in repo docs for repeatable onboarding.

## Failure mode
- If corpus evidence is missing for the requested topic, report the gap and propose the narrowest next retrieval step.
- If user asks for live account state validation, state that this skill is corpus-based and suggest the live verification path.
- If request is out of scope, route to the nearest skill and explain why.

## Output contract
Use this shape when structured output is requested:

```json
{
  "schema_version": 1,
  "recommendation": "string",
  "evidence": [
    {
      "path": "string",
      "reason": "string"
    }
  ],
  "snippet": "string|null",
  "risk_note": "string"
}
```

Contract rules:
- Always include `schema_version`.
- Keep `snippet` as `null` when unavailable.
- Prefer 2 or more evidence entries for non-trivial recommendations.

## Corpus and evidence policy
- Primary corpus root: `plugins/coderabbit/skills/coderabbit/references/coderabbit-docs`.
- First-pass retrieval should use targeted search against slug and body text, then open only relevant files.
- Treat metadata line `source: https://docs.coderabbit.ai/...` as provenance.
- Preserve exact command names and config keys from corpus evidence.
- If the corpus and existing local repo policy conflict, surface both and ask which policy should win.

## Workflow
1. Classify user request into one topic: config, commands, CLI, integrations, tools, planner, reporting, or troubleshooting.
2. Retrieve the smallest evidence set from `plugins/coderabbit/skills/coderabbit/references/coderabbit-docs` using targeted search terms.
3. Extract exact command/config primitives and summarize with source paths.
4. Draft an answer tailored to the user's platform and requested depth.
5. If user requests implementation artifacts, provide file-ready snippets and clearly mark assumptions.
6. End with the safest next verification step.

Fast path for low-latency responses:
- If the user asks a conceptual or command-reference question and no repo edits are requested, answer directly without tool calls.
- Include an `Evidence` line that cites the corpus root or specific corpus paths used.
- State when guidance is corpus-based and may require live verification for current SaaS state.

## Verification
- Verify every recommendation maps to at least one local corpus file.
- Verify config key names and command strings match corpus text.
- Verify platform-specific guidance matches requested platform.
- Verify any generated snippet is internally consistent and minimally scoped.

## Validation
- Verify `references/contract.yaml` reflects triggers, inputs, and outputs in this file.
- Verify `references/evals.yaml` includes trigger, negative, and pressure cases.
- Verify this skill does not claim live account introspection by default.
- Validation is fail-fast: stop at the first blocking gate, fix that issue, then rerun the smallest relevant check before broader validation.

## Constraints
- DO NOT fabricate unsupported CodeRabbit features.
- NEVER expose secrets or token placeholders as real credentials.
- DO NOT claim local corpus is always current with vendor docs.
- Keep recommendations reversible and incremental when user intends rollout.

## Gotchas
- Missing corpus evidence for a recommendation means you should pause and retrieve specific files before answering.
- `source:` lines prove provenance but do not guarantee freshness against current vendor docs.
- Platform-specific commands can differ across GitHub, GitLab, Bitbucket, and Azure DevOps, so always scope recommendations to the requested platform.
- A common pitfall is overloading first-time setup with advanced tooling before baseline review behavior is stable.

## Anti-patterns
- Guessing config fields without corpus evidence.
- Treating this skill as a generic CI migration assistant.
- Returning broad policy claims without citing corpus paths.
- Ignoring platform differences when providing setup steps.
- Mistake: presenting one cookie-cutter template as universally correct.
- Warning: forcing a generic rollout when a context-specific or phased approach is safer.

## Examples
- User says: "I just installed the review bot. What should I configure first before I touch the YAML?"
- User says: "Give me a minimal `.coderabbit.yaml` for a TypeScript repo with explicit sequence diagrams enabled, then validate what I actually need."
- User says: "What are the PR comment commands like pause, review, update summary, and configuration?"
- User says: "Walk me through GitHub setup, YAML config, CircleCI failure analysis, and linked issue planning without skipping the relevant docs."
- User says: "Inspect the docs and explain why path instructions might beat learnings in one repository folder."
- User says: "Summarize the difference between Autofix and Simplify with rollout caveats."

## References
- `references/contract.yaml`
- `references/evals.yaml`
- Corpus root: `plugins/coderabbit/skills/coderabbit/references/coderabbit-docs`

## See Also

| Skill | When to use together |
|---|---|
| [[gh-workflow]] | Apply CodeRabbit guidance while executing GitHub PR lifecycle changes |
| [[circleci]] | Pair CodeRabbit guidance with broader CircleCI migration and policy workflows |
| [[context7]] | Cross-check third-party library docs when CodeRabbit guidance references external tools |

**Topic map:** [[agent-ops]]
