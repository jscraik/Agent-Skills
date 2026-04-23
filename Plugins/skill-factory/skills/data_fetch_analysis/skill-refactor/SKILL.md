---
name: skill-refactor
description: Scan Codex session history for skill failures, usage patterns, and coverage gaps. Use when the user wants daily skill-health monitoring or evidence-backed recommendations about installing, improving, merging, or pruning skills.
metadata:
  skill-type: data_fetch_analysis
---

# Skill Refactor

Analyze skill reliability from session evidence and return prioritized recommendations.

Read when: evidence schema or audit criteria are needed: [contract](./references/contract.yaml)

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

## Failure mode

- If evidence sources are missing or unreadable, stop and report the exact gap.
- If scope is ambiguous, request clarification before producing recommendations.

## Gotchas

- Do not infer outcomes without evidence; mark uncertainty explicitly.
- Avoid duplicate recommendations when one root cause explains multiple symptoms.
