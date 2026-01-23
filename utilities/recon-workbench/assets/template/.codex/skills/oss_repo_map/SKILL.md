---
name: oss_repo_map
description: 'Open-source repo mapping: hotspots, dependency tree, SAST, tests/coverage
  pointers.'
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
---

Inputs:
- REPO path
- GOAL

Use probes:
- oss.git_hotspots
- oss.deps_tree
- oss.sast_semgrep (if installed)

Output:
- Architecture sketch (modules, boundaries, key flows)
- Suggested reading order ("where to start")
- Risk hotspots (complexity, low test coverage if known)
