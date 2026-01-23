---
name: report_compiler
description: Compile multiple run findings into a single report with cross-run diffs
  and stable conclusions.
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
---

Inputs:
- A list of run folders containing derived/findings.json.

Output:
- consolidated report.md:
  - what changed between baseline and stimulus
  - stable behaviors (observed repeatedly)
  - open questions and recommended next probes
