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
  locks. Run `git_metadata_preflight.py --json` from
  `Infrastructure/scripts/validation-and-linting/` before expensive hook gates;
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
- `python3 ~/.codex/Infrastructure/scripts/plan-graph-lint.py .agents/PLANS.md`
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
  `codex exec --profile oss-cloud` proves the oss-cloud flow,
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

For Codex smoke runs, the wrapper must select `[profiles.fast]` by passing
`--profile fast` to the eval runner. Do not leave smoke evals on the ambient
Codex profile when validating skill-factory output.

`ask evals run` must include the installed local Tessl CLI lane every time after
the repo eval runner. Stage only the controlled Tessl input files into the
stable evidence directory `/tmp/ask-tessl-evals/<skill-path>-<sha12>`, then run
`tessl eval run --json <staged-temp-source>`; do not point Tessl at the live
skill or plugin source tree. The hard boundary is registry upload: use native
`tessl`, no `npx tessl`, no publish, no registry upload, and no package upload
path. A controlled copy of the staged payload may be uploaded to Jamie's private
Tessl workspace for assessment; do not describe that private workspace eval as a
public publish, registry upload, or leak.

The staging layer must adapt repo-native eval metadata into Tessl's expected
project shape: copy the skill entrypoint and eval reference files, synthesize
`evals/<case-id>/task.md` plus `evals/<case-id>/criteria.json` from
`references/evals.yaml`, and include a minimal `tessl.json` project marker.
Project identity is deterministic:
plugin-owned skills under `Plugins/<plugin-id>/skills/**` use the plugin
project, while standalone skills use the skill project. When a Tessl workspace
is provided, the wrapper must check the staged project link before evals run,
relink an existing project first, and create a project only when relink proves
one does not already exist. The requested workspace is part of the evidence
contract: every SDK Tessl run uses the `jscraik` workspace and must create,
link, list, and report the exact per-skill or per-plugin project identity,
such as `jscraik/technical-writer` or `jscraik/skill-factory`, not a personal
workspace or stale alias with the same project name. Leave the staged directory in place so the copied
inputs, synthesized Tessl tasks, and Tessl project marker remain inspectable
evidence. Reruns must archive prior staged contents to a sibling archive such
as `/tmp/ask-tessl-evals/<skill-path>-<sha12>-evidence-archive/` before
refreshing current inputs; do not delete temp evidence to get a clean
workspace. Do not keep historical `scenarios/`, `evals/`, or
`criteria.json` evidence under the staged upload root, because Tessl may ingest
stale evidence as current scenarios. Do not duplicate eval cases by hand unless
the canonical eval format changes.

The live Tessl workflow is a separate explicit lane. Use
`./bin/ask evals run <skill-path> --tessl-live-private --tessl-workspace jscraik`
only when the operator asks for live private Tessl evidence. This lane must
stage a plugin-shaped package under
`/tmp/ask-tessl-evals/<skill-path>-<sha12>`, write
`.tessl-plugin/plugin.json` with `"name": "jscraik/<plugin-name>"`,
`"private": true`, and `"skills": "./skills/"`, copy the skill package to
`skills/<skill-name>/SKILL.md`, omit `tile.json`, and convert eval cases into
`evals/<case-id>/task.md` plus `evals/<case-id>/criteria.json` using Tessl's
`weighted_checklist` criteria shape. Include local `references/**` support
files beside the staged skill so Tessl plugin discovery and skill-relative links
resolve from the plugin root. Run
`tessl eval run --json --workspace jscraik <staged-plugin-dir>`.
Stage `tessl.json` for the same
`jscraik/<plugin-name>` identity because Tessl saves eval runs to a project.
Before invoking Tessl evals, the wrapper must check that project link, relink an
existing project first, and create the project only when needed. Start with
`--tessl-live-dry-run` when proving package shape or policy before any live
service call.

For plugin-owned skills under `Plugins/<plugin-id>/skills/**`, `<tile-name>`
is the plugin id, not the leaf skill directory. For example, live private
validation of `Plugins/skill-factory/skills/skill-factory-router`
must stage and save to `jscraik/skill-factory` while keeping the
`skills` manifest entries aligned to the surviving Skill Factory skills.

The live-private lane is still not a publish lane. Do not run `tessl install`,
`tessl skill publish`, `tessl tile publish`, `tessl tile pack`, registry upload,
or package upload from `ask evals run`. If live evals require Tessl project
setup, classify the exact setup need: `tessl init`, `tessl project create`,
`tessl project link`, or `tessl project repair`. For Codex sessions, load
credentials from the operator-approved environment stream directly when needed;
do not gate on regular-file checks, and never print API tokens.

Tessl scenario generation is a separate prep lane, not part of ordinary
`ask evals run`. When the operator asks to use Tessl's scenario-generation
skill, run:

```bash
./bin/ask evals prepare-tessl-scenarios <skill-path> --tessl-workspace jscraik --json --robot
```

Start with `--dry-run` to prove package shape. The command stages the target
skill under `/tmp/ask-tessl-scenario-generation/<skill-path>-<sha12>/target-tile`
and installs only `tessl-labs/tessl-skill-eval-scenarios@0.1.0` under the
paired `tool-project`. Do not run this install in the repo root. This command
prepares the workspace and points to the installed Tessl scenario skill; it does
not by itself write the scenario files. Reruns archive the previous
`target-tile`, `tool-project`, and generated scenario evidence under
`evidence-archive/`; do not remove those temp artifacts manually during
closeout. After it succeeds, follow the generated
`scenario-generation-brief.md` and create `target-tile/evals/instructions.json`,
`summary.json`, `summary_infeasible.json`, and sequential
`scenario-*/{task.md,criteria.json,capability.txt}` files before claiming the
external scenario-generation pass completed. Generated Tessl scenarios remain
draft evidence until reviewed for instruction leakage,
feasibility, criteria totals, and duplication. Import only selected cases back
into canonical `references/evals.yaml`. See
[Tessl Live Skill Eval Workflow](/Docs/agents/24-tessl-live-skill-eval-workflow.md) for
the full agent checklist.

In Codex sandboxed sessions, do not request network permission for the Tessl
eval lane up front. The repo wrapper already limits Tessl input to the staged
stable staged project, and asking the sandbox for network turns the command into an
external-export approval path instead of exercising the local Tessl CLI
contract. `--allow-tessl-project-save` is accepted for compatibility but is not
required. Run the wrapper normally, then report any Tessl CLI credential,
workspace/project-link, sandbox, or policy blocker from the command output with
the exact staged command and blocker. `--skip-tessl` is only for an explicitly
documented Tessl outage, policy block, or intentionally scoped debug run. If
Tessl reports that no existing project safely matches the staged directory,
classify it as a Tessl workspace/project-link setup blocker; do not loop back
to auth, sandbox, temp-staging, or registry-upload explanations.

If the native Tessl subprocess exits with a negative return code such as `-9`
and produces no stdout or stderr, classify it as `blocked_runtime` with the
terminating signal name, for example `SIGKILL`. Do not continue into fallback
project relink/create attempts, and do not call the skill failed or reviewed.
Treat the preserved `/tmp/ask-tessl-*` directory as the evidence packet for
the staged inputs and diagnose the local Tessl CLI, sandbox, or OS runtime
separately before rerunning the same wrapper lane.

`ask skills external-review` is the durable second-check entrypoint for the
external-review ladder. It runs strict audit, local Plugin Eval, and native
Tessl review by default. Treat `tessl skill review` path shape as the skill
directory containing `SKILL.md`; Tessl plugin lint expects a staged package with
`.tessl-plugin/plugin.json` and is not interchangeable. Plugin Eval is acceptable at `B+` or
better when it has zero failures and the local/Tessl gates pass. Tessl review
must meet the `95` threshold and must run through the wrapper, which preserves
`/tmp/ask-tessl-reviews/<skill-path>-<sha12>/current` with
`.tessl-plugin/plugin.json`, `tessl.json`, the copied skill, and included
references for evidence. Reruns move the previous `current` directory under
`evidence-archive/` before refreshing staged inputs.

When any rung is blocked, record the exact command, status, blocker class, and
the next minimal diagnostic. Do not replace a blocked rung with a different tool
and call the ladder complete.

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
