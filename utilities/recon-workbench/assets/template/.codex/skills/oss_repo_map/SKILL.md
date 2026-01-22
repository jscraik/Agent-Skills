---
name: oss_repo_map
description: "Open-source repo mapping: hotspots, dependency tree, SAST, tests/coverage pointers."
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
