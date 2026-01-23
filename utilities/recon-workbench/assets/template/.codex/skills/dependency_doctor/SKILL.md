---
name: dependency_doctor
description: Run preflight checks and produce actionable install guidance for missing
  tools.
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
---

Run a preflight ("doctor") and classify missing tools by target kind:
- baseline required
- worst-case optional

Output:
- a checklist of missing tools
- recommended minimal installs for the active target kind
