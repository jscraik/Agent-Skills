---
name: workflow-guardrail-candidates
description: Binary calibration pack for recurring workflow guardrail recommendations.
---

# Workflow Guardrail Candidates

This directory is the runnable source root for the workflow-guardrail-candidates eval pack.

## Layout

- `references/evals.yaml` holds the claim-to-case routing and calibration expectations.
- `evals/` contains per-case task and criteria files.
- `tessl.json` marks the staged project root for the eval runner.
- `workflow-guardrail-candidates.json` preserves the canonical pack content used to generate the staged source.
