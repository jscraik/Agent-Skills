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
- Inspect YAML through the managed wrapper lane, not ad hoc system Python:
  `./bin/ask repo yaml-inspect <repo-relative-yaml> --json --robot` or
  `mise run yaml-inspect -- <repo-relative-yaml>`. Plain `python3` is not a
  PyYAML contract for this repo.
- Run Infrastructure Python tests through the locked Infrastructure environment,
  not the system Python from the repo root. Use
  `bash Infrastructure/scripts/run-infrastructure-python.sh -m unittest tests.<module>` or
  `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest <path>` so dependencies
  from `Infrastructure/uv.lock` are available.
- Before changing skills, sync policy, runtime projections, or agent-facing
  docs, read [UBIQUITOUS_LANGUAGE.md](./UBIQUITOUS_LANGUAGE.md).
- Before changing Skills SDK plans, specs, atlas visuals, capability claims, or
  product-direction docs, use the product-boundary terms in
  [UBIQUITOUS_LANGUAGE.md](./UBIQUITOUS_LANGUAGE.md): `agent-skills` is the
  foundry/dogfood/source repo, Skills SDK is the professional lifecycle
  contract, Tessl is distribution and external proof, and local runtime truth is
  a separate installed-behavior lane.
- Edit canonical sources, not runtime projections. See
  [Path Ownership Boundaries](./Docs/agents/14-path-ownership-boundaries.md).
- Finish the named outcome through the smallest local change and focused proof.
  Feedback is diagnostic evidence, not automatic authority to stop delivery or
  add process. Prefer no system change, a local implementation repair, or an
  existing test or instruction improvement. Select the
  [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md)
  route only when Jamie asks for system improvement, a consequential boundary
  is involved, the failure recurs across three independent tasks, or two named
  consumers need a contract the repository does not already provide. That
  selected route may use the existing ledger and validator; routine work does
  not require a papercut log, ledger row, or new artifact. Selected work
  requires opening and reading it in the current turn, an appropriate
  `.harness/quality/steering-uptake.md` entry, and
  `validate_steering_uptake.py --json` evidence.
- Runtime-handle safety is independent of steering selection: wait, poll, or
  resume only an active handle returned by the immediately preceding tool
  result. Re-discover state with direct repository commands when no such handle
  exists; never probe a guessed or stale identifier.
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
- For selected system improvement, identify the mechanism and improve the
  smallest existing surface that serves a named consumer. State its carrying
  cost, proof, and the overlapping surface it consolidates or replaces.
- Jamie Brain, SSM, and CO provide outcomes and cross-project constraints. The
  Agent Skills OC and this repository own project-specific discovery, technical
  design, specifications, implementation plans, and delivery. Backbriefs to
  Jamie Brain are compact evidence pointers, not duplicated technical plans.
- Skills SDK PM thread coordination: when Jamie designates one thread as the
  Skills SDK PM decision surface, delegated execution threads must report back
  through a validated `thread-report/v1` artifact and a PM delivery receipt
  before their work can influence the next SDK gate decision. Use
  [PM Thread Coordination](./Docs/agents/26-pm-thread-coordination.md) and
  validate with
  `python3 Infrastructure/scripts/validation-and-linting/validate_thread_pm_delivery.py <report> --require-delivery --json`.
- Tessl eval contract: when running skill/plugin evals, run the installed local
  `tessl` CLI automatically through the repo wrapper, stage only controlled
  input under `/tmp`, synthesize Tessl
  `scenarios/<case-id>/{task.md,criteria.json}` files from canonical
  `references/evals.yaml`, include a `tessl.json` project marker in the
  staged payload, and never point Tessl at the live repo source. A controlled
  copy of that staged payload may be uploaded to Jamie's private Tessl workspace
  for assessment; this is a workspace/project eval lane, not a public registry
  or publish lane. Do not use `npx tessl`, `publish`, registry upload, or
  package upload commands. If Tessl reports no workspace/project link, classify
  that setup blocker directly instead of re-litigating auth, sandboxing, or temp
  staging. Tessl project identity is
  deterministic: plugin-owned skills under `Plugins/<plugin-id>/skills/**`
  belong to the plugin project, for example `jscraik/skill-factory`, and
  standalone skills belong to their own skill project, for example
  `jscraik/technical-writer`. The workspace is `jscraik`; the project is the
  per-skill or per-plugin identity under that workspace. Wrappers must check or
  establish that project link before running the Tessl eval/install lane,
  relinking an existing project before creating a new one. The operator-provided
  workspace name is binding evidence; do not substitute a personal workspace or
  stale alias when the requested or visible Tessl workspace is `jscraik`. In
  Codex sessions,
  source the operator-approved
  `/Users/jamiecraik/.codex/.env` environment stream directly when the Tessl
  workspace token is needed; never print token values or shell-expanded
  environment contents. Treat stable `/tmp/ask-tessl-*` paths as evidence:
  reruns must archive prior temp contents to a sibling evidence archive rather
  than deleting generated payloads or keeping stale scenarios under the current
  upload root.

## Common Commands

## Project-specific correction boundary

Routine local skill corrections use existing local checks and do not invoke
cloud, Tessl, runtime, review, or release machinery unless promotion is
explicitly selected.

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
