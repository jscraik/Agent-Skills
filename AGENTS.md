---
schema_version: 1
---

# agent-skills Agent Guide

Agent Skills Kit is the canonical control plane for authoring, validating,
discovering, and syncing Codex skills, operator docs, and agent workflows.

## Root Essentials

- On a fresh checkout, run `bash scripts/bootstrap-ask.sh --json` before
  requiring `./bin/ask`; if the wrapper is unavailable, verify the fallback with
  `python3 bin/ask repo status --json`.
- Use `./bin/ask` for repo operations; it forwards to
  `Infrastructure/bin/ask`.
- The repository root has no package manager install step. Use repo wrappers at
  the root, and use package commands only inside verified package roots.
- Before changing skills, sync policy, runtime projections, or agent-facing
  docs, read [UBIQUITOUS_LANGUAGE.md](./UBIQUITOUS_LANGUAGE.md).
- Edit canonical sources, not runtime projections. See
  [Path Ownership Boundaries](./Docs/agents/14-path-ownership-boundaries.md).
- Treat every repeated user steering item or review correction from Jamie as a
  high-signal operating defect until classified. If the same command failure,
  tool-permission issue, approval blocker, or user correction appears twice in a
  lane, stop the active task, name the pattern, refine the repo/environment
  contract that allowed it, validate that refinement, and report the proof
  before resuming the original lane.
- For live GitHub, CodeRabbit, CircleCI, Snyk, package registry, or other
  networked repo operations in Codex sandboxed runs, request explicit network
  permission before diagnosing an outage or credential problem. When a command
  may invoke `gh`, `mise`, or `uv`, keep tool caches and state inside
  approved temp paths before treating cache warnings as the blocker. Set
  `XDG_CACHE_HOME`, `XDG_STATE_HOME`, `MISE_CACHE_DIR`, and
  `UV_CACHE_DIR` as applicable for the command family.
- Prefer fixing the mechanism that caused repeated feedback over fixing only
  the immediate symptom. Durable mechanism fixes belong in the relevant skill,
  agent guide, solution doc, validation command, or wrapper script.

## Common Commands

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

## Further Guidance

- Repo command behavior and `--robot` mode:
  [Agent Operating Contract](./Docs/agents/16-agent-operating-contract.md)
- Tooling and package command policy:
  [Tooling and Command Policy](./Docs/agents/02-tooling-policy.md)
- Validation order and evidence rules:
  [Validation and Checks](./Docs/agents/04-validation.md)
- Workflow, git, refactoring, docs, and safety:
  [Workflow and Safety Guidance](./Docs/agents/13-workflow-and-safety-guidance.md)
- Skill install, audit, fold, and line-budget rules:
  [Skill Management](./Docs/agents/17-skill-management.md)
- Browser and local preview fallback:
  [Browser and Local Preview](./Docs/agents/18-browser-and-local-preview.md)
- Instruction cleanup notes and stale guidance to remove:
  [Contradictions and Cleanup](./Docs/agents/05-contradictions-and-cleanup.md)

Start at [Docs/agents/README.md](./Docs/agents/README.md) when you need the
full instruction map.
