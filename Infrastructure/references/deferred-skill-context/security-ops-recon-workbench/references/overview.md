# Inspector overview

## Goal
Build or operate a controlled interrogation package that produces evidence-backed findings for web/React and OSS targets.

## Default loop
1) Baseline capture (minimal interaction)
2) Stimulus capture (single, controlled action)
3) Diff (baseline vs stimulus)
4) Summarize findings with evidence paths

## Escalation ladder
1) Static inventory
2) Baseline run
3) Stimulus run
4) Diff
5) Advanced observation (approved tools only)

Stop when goals are met, signals flatten, or authorization limits are reached.

## Required outputs
- Artifacts (raw outputs, logs, traces, HAR)
- Findings JSON (schema-valid)
- Report Markdown with evidence citations

## Guardrails
- Evidence-only claims
- No circumvention or bypass of protections
- Least privilege and observation-first
