---
name: coderabbit
description: Use the local CodeRabbit crawl corpus to answer CodeRabbit setup, configuration, CLI, and workflow questions with source-grounded guidance. Use when the user needs CodeRabbit-specific help from repository-local docs, not generic CI or Git hosting setup.
metadata:
  skill-type: library_api_reference
---

# CodeRabbit Reference Assistant

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Discovery interview](#discovery-interview)
- [Deliverables](#deliverables)
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
- Prefer retrieval-first answers: locate evidence in `utilities/coderabbit/references/coderabbit-docs` before drafting recommendations.
- Return concrete, actionable steps with file-backed provenance whenever possible.
- Distinguish local-corpus answers from live/vendor-state assumptions.
- Escalate missing-doc or stale-doc risk explicitly instead of guessing.

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

## Discovery interview
- Use discovery only when scope is ambiguous.
- Ask one round at a time and keep it short.
- Confirm platform and desired outcome before proposing config changes.
- Use `references/evals.yaml` pressure and negative cases to guard against over-triggering.

## Deliverables
- Source-grounded answer with cited corpus files.
- Optional draft snippets for `.coderabbit.yaml` or PR command playbooks.
- Clear boundary notes when docs are stale, missing, or require live verification.
- If asked for structured output, return the JSON shape in this file's Output contract section.

## Failure mode
- If corpus evidence is missing for the requested topic, report the gap and propose the narrowest next retrieval step.
- If user asks for live account state validation, state that this skill is corpus-based and suggest the live verification path.
- If request is out of scope, route to the nearest skill and explain why.

## Output contract
Use this shape when structured output is requested:

```json
{
  "schema_version": 1,
  "topic": "configuration|commands|cli|integrations|tools|planner|reporting|troubleshooting",
  "question": "string",
  "evidence": [
    {
      "path": "string",
      "reason": "string"
    }
  ],
  "recommendation": "string",
  "snippet": "string|null",
  "risk": "none|low|medium|high",
  "blocker": "string|null",
  "next_step": "string"
}
```

Contract rules:
- Always include `schema_version`.
- Keep `snippet` and `blocker` as `null` when unavailable.
- Prefer 2 or more evidence entries for non-trivial recommendations.

## Corpus and evidence policy
- Primary corpus root: `utilities/coderabbit/references/coderabbit-docs`.
- First-pass retrieval should use targeted search against slug and body text, then open only relevant files.
- Treat metadata line `source: https://docs.coderabbit.ai/...` as provenance.
- Preserve exact command names and config keys from corpus evidence.
- If the corpus and existing local repo policy conflict, surface both and ask which policy should win.

## Workflow
1. Classify user request into one topic: config, commands, CLI, integrations, tools, planner, reporting, or troubleshooting.
2. Retrieve the smallest evidence set from `utilities/coderabbit/references/coderabbit-docs` using targeted search terms.
3. Extract exact command/config primitives and summarize with source paths.
4. Draft an answer tailored to the user's platform and requested depth.
5. If user requests implementation artifacts, provide file-ready snippets and clearly mark assumptions.
6. End with the safest next verification step.

## Verification
- Verify every recommendation maps to at least one local corpus file.
- Verify config key names and command strings match corpus text.
- Verify platform-specific guidance matches requested platform.
- Verify any generated snippet is internally consistent and minimally scoped.

## Validation
- Verify `references/contract.yaml` reflects triggers, inputs, and outputs in this file.
- Verify `references/evals.yaml` includes trigger, negative, and pressure cases.
- Verify this skill does not claim live account introspection by default.

## Constraints
- Do not fabricate unsupported CodeRabbit features.
- Do not expose secrets or token placeholders as real credentials.
- Do not claim local corpus is always current with vendor docs.
- Keep recommendations reversible and incremental when user intends rollout.

## Gotchas
- Missing corpus evidence for a recommendation means you should pause and retrieve specific files before answering.
- `source:` lines prove provenance but do not guarantee freshness against current vendor docs.
- Platform-specific commands can differ across GitHub, GitLab, Bitbucket, and Azure DevOps, so always scope recommendations to the requested platform.

## Anti-patterns
- Guessing config fields without corpus evidence.
- Treating this skill as a generic CI migration assistant.
- Returning broad policy claims without citing corpus paths.
- Ignoring platform differences when providing setup steps.

## Examples
- "Give me a minimal `.coderabbit.yaml` for TypeScript repos with explicit sequence diagrams enabled."
- "What are the PR comment commands like pause, review, and update summary?"
- "Summarize the difference between Autofix and Simplify with rollout caveats."
- "Which docs describe CircleCI integration and how failure analysis is surfaced?"

## References
- `references/contract.yaml`
- `references/evals.yaml`
- Corpus root: `/Users/jamiecraik/dev/agent-skills/utilities/coderabbit/references/coderabbit-docs`

## See Also

| Skill | When to use together |
|---|---|
| [[cf-crawl]] | Refresh or expand the local CodeRabbit docs corpus before analysis |
| [[gh-workflow]] | Apply CodeRabbit guidance while executing GitHub PR lifecycle changes |
| [[circleci]] | Pair CodeRabbit guidance with broader CircleCI migration and policy workflows |
| [[context7]] | Cross-check third-party library docs when CodeRabbit guidance references external tools |

**Topic map:** [[agent-ops]]
