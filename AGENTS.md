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
- Treat every Jamie steering or review feedback item as high-signal operating
  evidence until classified otherwise. If the same command, tool failure,
  approval error, missing permission, or user correction happens twice, stop
  the active task lane before retrying. Classify the failure pattern, refine the
  environment or repo contract that allowed it, validate the refinement, and
  report the proof before resuming ordinary implementation or PR work.
  Record the failure category and durable improvement type; an acknowledgement
  without a repo artifact plus validation evidence is not uptake.
  Use [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md)
  and record uptake in `.harness/quality/steering-uptake.md`; validate with
  `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
- For networked repo operations in Codex sandboxed sessions, do not diagnose
  `gh`, CircleCI, Snyk, package registry, or other API failures as service
  outages until the same command has been retried with explicit network
  permission. When a command invokes `gh`, `mise`, or `uv`, keep tool caches
  and state inside approved temp paths before treating cache warnings as the
  blocker. Set `XDG_CACHE_HOME`, `XDG_STATE_HOME`, `MISE_CACHE_DIR`,
  `MISE_STATE_DIR`, `MISE_TRUSTED_CONFIG_PATHS`, and `UV_CACHE_DIR` as
  applicable for the command family. In temp worktrees with a repo `.mise.toml`,
  set `MISE_STATE_DIR` before launching the shell so mise tracked-config writes
  do not fall back to `~/.local/state/mise`.
- Systems-thinking posture: a fix is not complete when the named symptom is
  gone. Identify the mechanism that allowed the symptom, encode the smallest
  durable guardrail in docs, skills, scripts, or validation, and prove the
  guardrail prevents the same class of failure from reaching Jamie again.
- Tessl eval contract: when running skill/plugin evals, run the installed local
  `tessl` CLI automatically through the repo wrapper, stage only controlled
  input under `/tmp`, synthesize Tessl `scenarios/<case-id>/task.md` files from
  canonical `references/evals.yaml`, include a `tessl.json` project marker in
  the staged payload, and never point Tessl at the live repo source. This is a
  project-save eval lane, not a registry-publish lane: do not use `npx tessl`,
  `publish`, registry upload, or package upload commands. If Tessl reports no
  workspace/project link, classify that setup blocker directly instead of
  re-litigating auth, sandboxing, or temp staging. Tessl project identity is
  deterministic: plugin-owned skills under `Plugins/<plugin-id>/skills/**`
  belong to the plugin project, for example `skills-sdk/skill-factory`, and
  standalone skills belong to their own skill project. Wrappers must check or
  establish that project link before running the Tessl eval/install lane,
  relinking an existing project before creating a new one. In Codex sessions,
  source the operator-approved
  `/Users/jamiecraik/.codex/.env` environment stream directly when the Tessl
  workspace token is needed; never print token values or shell-expanded
  environment contents. Treat stable `/tmp/ask-tessl-*` paths as evidence:
  reruns must archive prior temp contents under `evidence-archive/` rather
  than deleting generated payloads to create a clean workspace.

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
