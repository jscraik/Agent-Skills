# Validation and Checks

## Table of Contents

- [Repository checks](#repository-checks)
- [Config-sensitive checks](#config-sensitive-checks)
- [AI workflow checks](#ai-workflow-checks)
- [Skill quality ladder](#skill-quality-ladder)
- [PR gate structure](#pr-gate-structure)
- [Authoring-family contract behavior](#authoring-family-contract-behavior)
- [Failure handling](#failure-handling)

## Repository checks

- Fresh-checkout command reachability:
  `bash scripts/bootstrap-ask.sh --json`, then
  `python3 bin/ask repo status --json`.
- Git hook readiness:
  `bash scripts/install-prek-hooks.sh` installs `prek` hooks and patches the
  generated shims to use a writable temporary `PREK_HOME` outside Git
  metadata.
  This avoids repeated Codex sandbox failures on `~/.cache/prek/prek.log` and
  prevents cache writes from being confused with linked-worktree metadata
  locks. Run `python3 Infrastructure/scripts/validation-and-linting/git_metadata_preflight.py --json`
  from the repository root before expensive hook gates;
  it fails closed on a current
  `index.lock`, denied metadata writes, or a locked current worktree.
  `bash scripts/check-environment.sh` fails if the adapter or hook wiring is
  missing.
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh` (project-local default scope)
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh --workspace-governance` (explicit workspace scope)
- `bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh` (blocks direct edits to runtime/projection surfaces including `.agents/skills/**`, `.agents/plugins-runtime/cache/**`, `Plugins/cache/**`, and `runtime/**`)
  - projection-refresh exception only: `PATH_OWNERSHIP_ALLOW_CACHE_WRITES=1 bash Infrastructure/scripts/validation-and-linting/check_path_ownership_boundaries.sh`
  - default scope is staged diff locally and base-ref diff in CI; override with `PATH_OWNERSHIP_GUARD_SCOPE`.
- `bash Infrastructure/scripts/lifecycle-and-sync/sync_skills.sh`
- `python3 Infrastructure/scripts/validation-and-linting/docs_lint.py --mode warn --config Infrastructure/docs-policy.json`
- `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`
  validates the steering uptake ledger when agent operating rules, review
  feedback uptake, or high-signal steering surfaces change. It also rejects
  unknown failure-category and improvement-type labels so uptake records use
  the documented taxonomy instead of vague local phrasing.
- `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest scripts/testing/test_validate_steering_uptake.py -q`
  proves steering uptake cannot pass as ceremony by rejecting records that lack
  operating failure, blocker, mechanism, or proof fields.
- Interface-design changes should have tests that read as policy checks for
  authority, ownership, invariants, and operation-context errors. See
  [Misuse-Resistant Interface Design](/Docs/agents/20-misuse-resistant-interface-design.md).
- `just validate` (or `bash Infrastructure/scripts/validate_all.sh`)
- `python3 Infrastructure/scripts/skill-graph/plan_graph_lint.py .agents/PLANS.md`
- Use the repo-local wrapper above instead of the global `~/.codex` `verify-work` helper for this repository.
- `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json` when Jamie gives repeated or high-signal steering about agent behavior.
- `python3 Infrastructure/scripts/validation-and-linting/validate_sdk_runtime_lane_contract.py --json`
  validates the [Skills SDK runtime lane contract](/Docs/agents/25-sdk-runtime-lane-contract.md).
  Use it when work touches or reports SDK mechanical validation,
  `codex exec --profile oss-local`,
  `codex exec --profile oss-cloud`, local Tessl staging, or
  `--tessl-live-private` external Tessl proof.
- Scope policy reference: [hook-governance-scope-defaults.md](/Docs/guides/hook-governance-scope-defaults.md).
- Path ownership policy: [14-path-ownership-boundaries.md](/Docs/agents/14-path-ownership-boundaries.md).

### Managed asset lifecycle baseline

- When work touches lifecycle metadata, packaged-skill inheritance, plugin manifests, or `docs/solutions/` governance:
  - Re-read [managed-asset-lifecycle.md](/Docs/reference/managed-asset-lifecycle.md) before editing.
  - Keep lifecycle truth in the authoritative in-file source, not a sidecar-first shadow registry.
  - Treat derived catalogs or indexes as stale until regenerated when they disagree with the authoritative source.
  - Use [skill-factory plugin manifest](/Plugins/skill-factory/.codex-plugin/plugin.json) as the phase-one plugin proof target and [skill-factory router](/Plugins/skill-factory/skills/skill-factory-router/SKILL.md) as the packaged-skill proof target. Skill hardening scripts live under `Plugins/skill-factory/scripts/skill-builder/`; runtime skills live under `Plugins/skill-factory/skills/` and `Plugins/plugin-factory/skills/`.

## Config-sensitive checks

- For edits to `package.json`, CI workflows, `settings.json`, or similar config files:
  - Run applicable lint/test/typecheck gates before commit.
  - Confirm pass status explicitly in handoff notes.
- For implementation work, run separate implementation and verification workflows.
- Require `codex review --uncommitted` before merge.

## AI workflow checks

- Ensure `README.md`, `AGENTS.md`, and linked docs agree on commands and scope.
- Prefer repository-root commands over guessed defaults.
- Keep Skills SDK runtime proof lanes separate:
  SDK mechanical validation proves package/scenario/scorer/static readiness,
  `codex exec --profile oss-local` proves the oss-local flow,
  the Configs-backed strict `oss-cloud` executor chain proves the oss-cloud flow,
  local Tessl staging proves only the Tessl local flow, and
  `--tessl-live-private` plus a scored `tessl eval view --json` artifact
  proves the Tessl external flow.
- Skills SDK package movement must include a basic-requirement analytic rubric
  before Tessl handoff. `references/contract.yaml` must state observable
  `quality_criteria`, `evidence_requirements`, and
  `automatic_failure_conditions`; every non-selector quality criterion must
  include `purpose`, `why_it_matters`, `observable_evidence` as a non-empty
  string or list, and scoring anchors for `5`, `4`, `3`, `2`, and `1`.
  Multi-capability skills must also
  score selector criteria, such as `writing_type_selection` or
  `task_type_selection`, and expose the selected capability in inputs and
  outputs. `./bin/ask skills package verify <skill-path> --json --robot`
  blocks the package when this rubric contract is missing.
- Use the
  [Skills SDK Gold Standard Rubric](/Docs/reference/skills-sdk-gold-standard-rubric.md)
  as the top-level release-readiness standard. A package is not ready for Tessl
  live evals or registry release merely because internal checks, Plugin Eval,
  or Tessl scores pass; it must also satisfy the rubric's automatic failures,
  weighted readiness floors, and lane-specific evidence requirements.

## Skill quality ladder

For skill hardening, do not rediscover local evals, Plugin Eval, or Tessl ad hoc.
Run and report the ladder in this order, stopping at the first failed gate unless
the user explicitly asks for a full matrix:

```bash
./bin/ask skills audit <skill-path> --level strict --json --robot
./bin/ask evals run <skill-path> --mode smoke --json --robot
./bin/plugin-eval analyze <skill-path> --format json
./bin/ask skills external-review <skill-path> --json --robot
```

For Codex smoke runs, the wrapper selects `[profiles.fast]` through
`--profile fast`; do not rely on the ambient Codex profile.

`ask evals run` owns the ordinary local eval and native Tessl staging behavior.
Use [Tessl Live Skill Eval Workflow](/Docs/agents/24-tessl-live-skill-eval-workflow.md)
for scenario preparation, private Tessl execution, staged evidence shape, and
project identity. Use
[Skills SDK Runtime Lane Contract](/Docs/agents/25-sdk-runtime-lane-contract.md)
for lane admission, runtime-profile ownership, and non-substitution rules. Do
not duplicate model identifiers, temporary directory layouts, or Tessl project
mutation procedures in this general validation guide.

`ask skills external-review` remains the durable second-check entrypoint for
the external-review ladder. It runs strict audit, local Plugin Eval, and native
Tessl package lint by default; model-backed Tessl content review requires the
explicit `--with-tessl-review` switch.

When any rung is blocked, record the exact command, status, blocker class, and
the next minimal diagnostic. Do not replace a blocked rung with a different tool
and call the ladder complete.

When `ask evals run` or `ask skills external-review` receives `--dashboard`,
its JSON result is the canonical receipt and its HTML dashboard is a derived
local projection. The receipt's `dashboard.status` is one of `not_requested`,
`not_run`, `rendered`, or `unavailable`. A staging or rendering failure must
return `unavailable` without changing an otherwise established eval or review
result, and `report_path` appears only after its JSON receipt was written. A
rendered dashboard must be reflected in the final persisted JSON receipt. Use
JSON for automation and HTML only for human inspection.

## PR gate structure

See [CI Required Checks](/Docs/agents/12-ci-required-checks.md) for the complete dependency policy and workflow orchestration.

Named PR validation jobs call `./bin/ask repo validate --scope=<name>` so the
job name matches the subset it enforces:

- `lint`: docs, OpenAI skill format, skill type, and progressive-disclosure linting.
- `typecheck`: ask CLI, lifecycle, router, and governance-contract shape checks.
- `test`: skill lifecycle, authoring-family, graph-profile, and gotcha-store checks.
- `audit`: catalog, policy, projection, ownership, budget, shadowing, and runtime-separation checks.
- `check`: the full validation suite.
- `consistency-advisory` and `consistency-health`: drift artifact lanes used by the PR workflow.

Unknown scopes are rejected by `./bin/ask repo validate` and
`bash Infrastructure/scripts/validate_all.sh` with a non-zero exit.

## Authoring-family contract behavior

`authoring-family-gate` invokes `bash Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`.

CI local-memory policy:

- In PR CI, `SKILL_FAMILY_LOCAL_MEMORY_MODE` is set to `optional`.
- Expected behavior: local-memory preflight runs in warn-and-continue mode in CI, while remaining contract/eval/security checks continue to enforce pass/fail outcomes.
- Use `required` only in lanes where `local-memory` is guaranteed available.

That script enforces equivalent governance for:

- `Plugins/skill-factory/skills/*/skill-creator`
- `Plugins/skill-factory/skills/*/skill-installer`
- `Plugins/skill-factory/skills/skill-factory-router`
- `Plugins/skill-factory/scripts/skill-builder`
- `Plugins/plugin-factory/skills/*/plugin-creator`

Validation behavior includes:

- Contract/eval/security benchmark checks via `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family_benchmarks.py`.
- Contract/eval/prompt-injection/security fail criteria from `skill_gate.py` (`CONTRACT_*`, `EVALS_*`, `SEC_EVALS_*`, `PI_*`, `SCRIPT_SECURITY_*`, fail-fast workflow checks).
- OpenClaw security checks through `openclaw_skill_guard.py --mode both`.
- Structural eval coverage verification (smoke/release listing), with trusted-lane live eval execution only when explicitly enabled.

## Failure handling

- Stop at the first failed gate, fix, then rerun the minimal required check.
