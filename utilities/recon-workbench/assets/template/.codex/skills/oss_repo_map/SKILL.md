---
name: oss_repo_map
description: Analyze and map open-source repos (hotspots, dependency tree, SAST, tests/coverage
  pointers). Use when scoping an OSS codebase quickly.
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

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

