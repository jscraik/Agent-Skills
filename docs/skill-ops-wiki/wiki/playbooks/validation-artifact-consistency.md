---
title: Validation Artifact Consistency
type: playbook
status: active
last_reviewed: 2026-04-09
sources:
  - artifacts
  - scripts/verify_recursive_skill_graph_artifacts.py
---

# Validation Artifact Consistency

## Purpose

Keep emitted artifacts internally coherent so CI/review signals are trustworthy.

## Checks

- Manifest counts align with listed run statuses.
- Waivers align with verifier behavior and waiver schema fields.
- Gate/eval outputs do not contradict each other.
- JSON artifact path fields are deterministic and normalized.
- Missing JSONL/file warnings are singular and actionable.

## Workflow

1. Reproduce current output with repo validation commands.
2. Fix generator code first, then regenerate artifacts.
3. Keep historical artifacts only when explicitly marked as historical.
4. Re-run artifact validators and tests.

## Related

- [Code Scanning Remediation](/docs/skill-ops-wiki/wiki/playbooks/code-scanning-remediation.md)
- [Git Conflict Resolution for Validation Logs](/docs/skill-ops-wiki/wiki/playbooks/git-conflict-resolution-validation-logs.md)
