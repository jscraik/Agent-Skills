---
name: skill-refactor
description: "WHAT: Analyze skill reliability from Codex session evidence. WHEN: Use when skill failures, routing gaps, quality regressions, or keep-improve-merge-retire decisions need evidence."
metadata:
  skill-type: data_fetch_analysis
---

# Skill Refactor

Analyze skill reliability from session evidence and return prioritized recommendations.

## Philosophy

Evidence first. Every recommendation should trace to a concrete session, artifact, or validator result.

## When To Use

- User asks for evidence-backed skill reliability analysis.
- User wants daily skill-health monitoring.
- User is deciding whether to install, improve, merge, fold, or retire skills.

## Required inputs

- Analysis scope: single skill, category, or full inventory.
- Session evidence sources, preferably a `~/.agents/session-collector` bundle for broad scope.
- Ranking criteria for severity, confidence, and implementation cost.

## Workflow

1. Define scope and evidence boundaries.
2. Use session-collector bundles or bounded session extracts before deep dives.
3. Include PR review artifacts, CodeRabbit/Codex findings, validation logs, and plugin-eval reports when they are part of the requested evidence.
4. Group failures by root cause: coverage gap, instruction drift, routing mismatch, quality regression, context-package conflict, or missing observation path.
5. Flag repeated review feedback as context feedback when the same issue recurs across PRs, sessions, or validations.
6. Recommend the destination lane: update an existing skill with `skill-builder`, capture a repeatable workflow with `skillify`, or keep observing if evidence is weak.
7. Rank findings by impact, confidence, and implementation cost.
8. Return keep, improve, merge, and retire actions with evidence anchors.

Read when: choosing whether the requested factory work should build a new artifact, improve an existing one, stay docs-only, or stop: [First-principles factory gate](../../../../../Infrastructure/references/first-principles-factory-gate.md).

For non-trivial factory work, include `first_principles_gate` or an explicit `first_principles_gate_status: not_applicable` with the reason in the output or handoff before claiming readiness.

Reference scripts are preserved in deferred context:

- `Infrastructure/references/deferred-skill-context/skill-factory-skill-refactor/scripts/scan_codex_sessions.py`
- `Infrastructure/references/deferred-skill-context/skill-factory-skill-refactor/scripts/correlate_multi_source_skill_failures.py`

Assets: `assets/skill-refactor.png`.

## Deliverables

Return `schema_version: 1` when automation consumes the result, prioritized findings, concrete artifact evidence, recommended action, risk note for removals, and validation status.

For context lifecycle work, also return the observed failure source, affected skill/context package, recommended lifecycle stage, and the smallest evidence-backed adaptation.

## Safety

- Do not invent evidence or confidence ratings.
- Do not paste raw large transcripts into context.
- Do not recommend destructive removals without impact and rollback notes.
- Redact secrets, credentials, tokens, and sensitive user content.

## Anti-Patterns

- Calling a skill low quality without citing evidence.
- Proposing merges from naming similarity alone.
- Reading raw multi-megabyte transcripts before bounded inventory.

## Examples

- "Inspect last week's sessions and rank which skills to keep, improve, merge, or retire."
- "Find the top recurring skill routing failures and recommend minimal fixes."

## Failure mode

If evidence sources are missing, unreadable, or too broad to inspect safely, stop and report the exact missing artifact or scope decision.

## Gotchas

- Do not recommend merges solely on naming similarity.
- Prefer bounded session-collector evidence before raw transcript inspection.

## Progressive Disclosure

Never drop required context for brevity; move it into references or deferred context and link it here.

- Local contract, evals, and task profile: `references/`
- Session-evidence workflow and wrapper scripts: `Infrastructure/references/deferred-skill-context/skill-factory-skill-refactor/`
- Archived full package: `Infrastructure/references/deferred-skill-context/skill-factory-skill-refactor/`

## Validation

Verify every recommendation cites concrete evidence, severity ordering is reproducible, and no recommendation conflicts with repository instruction hierarchy. Fail fast: stop at the first failed gate and do not proceed until the blocker is fixed.
