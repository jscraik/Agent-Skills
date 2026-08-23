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
  [UBIQUITOUS_LANGUAGE.md](./UBIQUITOUS_LANGUAGE.md):
  `/Users/jamiecraik/dev/skills-foundry` is the source-only Foundry for
  retained packages; `agent-skills` implements and dogfoods the Skills SDK and
  owns active SDK candidates; Tessl is distribution and external proof; and
  local runtime truth is a separate installed-behavior lane. A package's
  explicit owner decision—not a runtime path—decides its canonical source.
- For a package selecting `skills-sdk.gold-standard.v1`, read
  [Skills SDK Authoring Contract](./Docs/reference/skills-sdk-authoring-contract.md),
  update `references/contract.yaml: authoring_contract` with the skill, and run
  `./bin/ask skills package verify <skill-path> --json --robot`. That is a
  structural admission gate only: run the declared behavioral proof and the
  selected runtime or external lane before claiming the skill is ready.
- Edit canonical sources, not runtime projections. See
  [Path Ownership Boundaries](./Docs/agents/14-path-ownership-boundaries.md).
- Finish the named outcome through the smallest local change and focused proof.
  Feedback is diagnostic evidence, not automatic authority to stop delivery or
  add process. Select the
  [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md)
  only for its named conditions. Routine delivery does not require a steering
  ledger entry or new process artifact. When that route is selected, opening and reading it in the current turn is required; record the result in
  `.harness/quality/steering-uptake.md` and run
  `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`.
- Keep runtime handles candidate-bound: wait, poll, or resume only the active
  handle returned by the immediately preceding tool result, and perform those
  operations serially for that handle. See
  [High-Signal Steering Feedback](./Docs/agents/19-high-signal-steering-feedback.md#runtime-handle-safety)
  for recovery rules.
- Skills SDK PM thread coordination: when Jamie designates one thread as the
  Skills SDK PM decision surface, use
  [PM Thread Coordination](./Docs/agents/26-pm-thread-coordination.md).
- Keep local, runtime, cloud, Tessl, and release proof separate. Use
  [Tessl Live Skill Eval Workflow](./Docs/agents/24-tessl-live-skill-eval-workflow.md)
  and [Skills SDK Runtime Lane Contract](./Docs/agents/25-sdk-runtime-lane-contract.md)
  only when those lanes are selected.

## Project-specific correction boundary

Routine local skill corrections use existing local checks and do not invoke
cloud execution, external Tessl distribution, live runtime mutation,
publication, or release machinery unless promotion is explicitly selected.
Pre-merge local review remains required for PR-bound changes. This source-only
path does not waive the skill-management contract: runtime projection proof is
required before claiming a skill is usable or using it as a runtime skill; that
proof belongs to the separately selected runtime or promotion lane.

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
