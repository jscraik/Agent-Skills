---
name: skill-refactor
description: Scan Codex session history for skill failures, usage patterns, and coverage gaps. Use when the user wants daily skill-health monitoring or evidence-backed recommendations about installing, improving, merging, or pruning skills.
metadata:
  skill-type: data_fetch_analysis
---

# Skill Refactor

Analyze skill reliability from session evidence and return prioritized recommendations.

Read when: evidence schema or audit criteria are needed: [contract](./references/contract.yaml)

## Philosophy

- Evidence first: recommendations must be traceable to concrete session artifacts.
- Favor high-leverage fixes that reduce repeated failures across multiple skills.
- Keep recommendations executable by mapping each finding to a clear next action.

## When to use

- Use when the user asks for evidence-backed skill reliability analysis from session history.
- Use when deciding whether to install, improve, merge, or retire skills.

## Required inputs

- A clear analysis scope (single skill, category, or full inventory).
- Session evidence sources or local artifacts available for review.
- Ranking criteria for severity and impact.

## Deliverables

- Prioritized findings with explicit evidence links or file references.
- Recommended actions grouped by keep, improve, merge, or retire.
- A short risk note for any recommendation that could remove capabilities.

## Procedure

1. Define scope: single skill, lane, or full inventory.
2. Gather evidence from session logs, skill metadata, and related references.
3. Group failures by root cause (coverage gap, instruction drift, routing mismatch, or quality regression).
4. Rank recommendations by impact, confidence, and implementation cost.
5. Return a concise keep/improve/merge/retire action table with evidence anchors.

Reference scripts for deterministic evidence extraction:
- [scan_codex_sessions.py](./scripts/scan_codex_sessions.py)
- [correlate_multi_source_skill_failures.py](./scripts/correlate_multi_source_skill_failures.py)

## Constraints

- Do not invent evidence or confidence ratings.
- Do not recommend destructive skill removals without explicit impact and rollback notes.
- Redact secrets, credentials, tokens, and sensitive user content in summaries and artifacts.
- Keep analysis scoped to the requested repository or dataset.

## Validation

- Verify each recommendation cites at least one concrete artifact.
- Verify severity ordering is explicit and reproducible.
- Verify no recommendation conflicts with repository instruction hierarchy.
- Fail fast: stop at first missing or unreadable evidence source and report the exact gap.

## Anti-patterns

- Concluding "low quality" without citing failure evidence.
- Proposing merges solely on naming similarity without overlap analysis.
- Mixing unrelated tooling advice into a skill-refactor recommendation set.

## Failure mode

- If evidence sources are missing or unreadable, stop and report the exact gap.
- If scope is ambiguous, request clarification before producing recommendations.

## Gotchas

- Do not infer outcomes without evidence; mark uncertainty explicitly.
- Avoid duplicate recommendations when one root cause explains multiple symptoms.

## Examples

- "Analyze the last week of Codex sessions and tell me which skills to keep, improve, merge, or retire."
- "Use skill-refactor to identify the top three recurring skill failures and suggest minimal fixes."
