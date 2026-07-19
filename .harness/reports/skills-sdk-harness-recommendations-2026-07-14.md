---
schema_version: 1
artifact_id: skills-sdk-harness-recommendations-2026-07-14
artifact_type: harness-recommendations
canonical_slug: skills-sdk-harness-recommendations
status: draft
created: 2026-07-14
scope: read-only Skills SDK harness inspection
ci_owner: CircleCI
---

# Skills SDK Harness Improvement Recommendations

## Executive Summary

The Skills SDK already has a strong local harness surface through `./bin/ask sdk`, focused SDK tests, runtime-lane documentation, PM thread coordination contracts, and validation wrappers. The main improvement opportunity is to turn existing preview, inventory, and advisory surfaces into replayed, CircleCI-gated, and learning-loop-backed proof.

The first implementation should be a CircleCI Skills SDK harness gate, not a GitHub Actions workflow.

## Inspection Evidence

Read-only inspection used these surfaces:

- `UBIQUITOUS_LANGUAGE.md`
- `Docs/agents/25-sdk-runtime-lane-contract.md`
- `Docs/agents/26-pm-thread-coordination.md`
- `Infrastructure/config/skills-sdk.json`
- `docs/goals/skills-sdk-v1-0-product-implementation/goal.md`
- `.harness/plan/2026-07-11-skills-sdk-stabilization-baseline-plan.md`
- `.circleci/config.yml`
- `.github/workflows/**` for workflow inventory only
- `./bin/ask sdk status --json --robot`
- `./bin/ask sdk evidence verify --scope capability-matrix --json --robot`
- `./bin/ask sdk evidence command-plan --scope capability-matrix --preview --json --robot`
- `./bin/ask sdk determinism audit --scope skills --limit 20 --json --robot`
- `./bin/ask repo validate --scope skills-sdk --json --robot`

Observed SDK status:

- Total capabilities: 52
- Implemented: 29
- Preview-only: 18
- Deferred: 2
- Out of scope: 3
- Feature-executed or preview-backed: 47
- Bounded mutation capabilities: 9

Observed capability evidence state:

- Evidence refs: 176
- Pass count: 133
- Not-run command refs: 43
- Proof mode: `inventory_only`
- Replay command: `./bin/ask sdk evidence command-plan --scope capability-matrix --preview --json --robot`

Observed determinism audit state:

- Skills scanned: 90
- High-priority candidates reported: 20
- Candidate areas:
  - `output_schema_contract`: 9
  - `validation_command_contract`: 7
  - `description_trigger_contract`: 4

## Current Harness Strengths

- `./bin/ask sdk` has a broad command surface for status, check, IR, evidence, route-map, eval, package, sandbox, intake, trust, observability, emitters, CI policy, explorer, security, plugin lifecycle, project lifecycle, lenses, determinism, and review.
- Runtime-lane separation is explicitly documented across SDK mechanical validation, oss-local, oss-cloud, Tessl local, and Tessl external lanes.
- PM-thread coordination requires validated `thread-report/v1` artifacts plus PM delivery receipts before execution-thread output can influence SDK gate decisions.
- Focused SDK tests already exist under `Infrastructure/tests/test_skills_sdk_*.py`.
- `./bin/ask repo validate --scope skills-sdk --json --robot` works locally and passed during inspection.
- `./bin/ask sdk evidence command-plan` already exposes the planned safe replay surface for capability command refs.

## Key Gaps

1. **Inventory evidence is not replay evidence.** Capability evidence verification passes while leaving 43 command refs as `not_run`.
2. **CircleCI lacks a dedicated Skills SDK gate.** `.circleci/config.yml` currently runs Snyk and `diagnose_skill.py --all`, but no SDK-specific validation step was found.
3. **Preview-only surfaces can be overclaimed.** The SDK status correctly distinguishes `implemented`, `preview_only`, `deferred`, and `out_of_scope`, but agents can still summarize preview/inventory evidence as readiness if not gated.
4. **Determinism findings are advisory.** `sdk determinism audit` finds high-priority prompt-only contracts, but there is no recurring triage loop that turns accepted candidates into validators, schemas, evals, or skill fixes.
5. **The stabilization baseline is planned but not executable as an automated harness lane.** The July 11 stabilization baseline plan is well scoped, but it still needs implementation authorization and a repeatable Worker/QA execution shape.

## Recommendations

### 1. Add a CircleCI Skills SDK Harness Gate

**Priority:** highest

Add a path-scoped CircleCI step or job that runs existing SDK validators when Skills SDK paths change.

Recommended commands:

```bash
./bin/ask repo validate --scope skills-sdk --ephemeral --json --robot
python3 Infrastructure/scripts/validation-and-linting/validate_sdk_runtime_lane_contract.py --json
python3 Infrastructure/scripts/validation-and-linting/validate_skills_sdk_typed_artifacts.py --json
```

Recommended path trigger set:

- `Infrastructure/scripts/lib/ask/skills_sdk/**`
- `Infrastructure/config/skills-sdk/**`
- `Infrastructure/config/schemas/skills-sdk/**`
- `Infrastructure/tests/test_skills_sdk_*.py`
- `Docs/agents/25-sdk-runtime-lane-contract.md`
- `Docs/agents/26-pm-thread-coordination.md`
- `docs/reference/skills-sdk/**`
- `.harness/specs/*skills-sdk*`
- `.harness/plan/*skills-sdk*`

Rollout:

1. Add as advisory or ordinary CircleCI job first.
2. Observe noise and runtime over several PRs.
3. Promote to required branch-protection check once stable.

### 2. Add a Safe Capability Command-Evidence Replay Lane

**Priority:** high

Current `sdk evidence verify` is inventory-only and reports 43 not-run command refs. Add a bounded replay lane that consumes the command plan and executes only safe local commands.

Recommended shape:

- Keep command planning preview-only.
- Add a replay script or SDK subcommand that:
  - reads the command-plan receipt;
  - executes only commands classified as safe `local_command`;
  - applies timeouts;
  - stores stdout/stderr summaries and exit codes;
  - emits a revision-bound replay receipt;
  - leaves external, Tessl, networked, and credentialed lanes classified instead of substituting proof.

Initial cadence:

- Manual CircleCI workflow or explicit local command.
- Do not run on every PR until runtime and flake profile are known.

### 3. Enforce Runtime-Lane Non-Substitution in CI

**Priority:** high

Wire `validate_sdk_runtime_lane_contract.py` into the CircleCI SDK gate for any changes touching eval, Tessl, OSS, runtime, or proof docs.

The gate should prevent agents from collapsing these lanes:

- SDK mechanical validation
- oss-local proof
- oss-cloud proof
- Tessl local proof
- Tessl external proof
- local runtime truth
- hosted CI truth
- PR review and merge-readiness truth

This directly protects against overclaiming readiness from adjacent proof lanes.

### 4. Add a Preview-Only / Readiness Language Verifier

**Priority:** medium-high

Create a deterministic verifier that fails or warns when SDK PRs use readiness language without matching proof.

Block or flag claims like `ready`, `proven`, `passing`, `release-ready`, `handoff-ready`, or `validated` when the cited evidence includes any of:

- `status: preview_only`
- `status: deferred`
- `status: out_of_scope`
- `proof_mode: inventory_only`
- `not_run` command refs
- Tessl local evidence used as Tessl external proof
- oss-local evidence used as oss-cloud proof
- CI, PR review, tracker, merge, and pulled-main truth collapsed into one status

Possible implementation destinations:

- deterministic repo validator under `Infrastructure/scripts/validation-and-linting/`;
- a CircleCI SDK-docs step;
- later, a `tessl change verify` verifier for SDK PR diffs.

### 5. Turn `sdk determinism audit` into a Recurring Triage Loop

**Priority:** medium

Use `./bin/ask sdk determinism audit --scope skills --limit <n> --json --robot` as a recurring improvement loop.

Recommended workflow:

1. Run weekly or manually.
2. Save a report artifact with candidate list and classifications.
3. Triage each candidate into:
   - schema/fixture validator;
   - exact command contract;
   - skill-frontmatter fix;
   - eval scenario;
   - no action with reason.
4. Feed accepted work into bounded PRs.

Do not block PRs on the full backlog until triage quality is proven.

### 6. Make the Stabilization Baseline Executable

**Priority:** medium

The plan at `.harness/plan/2026-07-11-skills-sdk-stabilization-baseline-plan.md` is the right next product-stabilization slice, but it should become an executable harness lane after implementation authorization.

Recommended shape:

- Worker packet for implementation.
- Independent QA disproof packet.
- Revision-bound baseline receipt.
- Read-only command/service rationalization inventory.
- CircleCI/manual workflow for dry-run validation after the slice lands.

Keep out of scope until explicitly authorized:

- public CLI behavior drift;
- extraction or service refactor;
- Tessl mutation;
- CircleCI mutation beyond the agreed harness gate;
- plugin install/update/uninstall mutation;
- home-root or runtime projection mutation.

## Recommended First Implementation Slice

Implement a CircleCI Skills SDK harness gate.

Suggested minimal patch:

1. Add a changed-file detection step in `.circleci/config.yml`.
2. If SDK-relevant files changed, run:

```bash
./bin/ask repo validate --scope skills-sdk --ephemeral --json --robot
python3 Infrastructure/scripts/validation-and-linting/validate_sdk_runtime_lane_contract.py --json
python3 Infrastructure/scripts/validation-and-linting/validate_skills_sdk_typed_artifacts.py --json
```

3. Upload or print concise JSON summaries.
4. Keep the command-evidence replay lane manual until the basic gate is stable.

## Later Tessl Integration

After the CircleCI gate and local replay lane are stable, use Tessl surfaces selectively:

- `tessl change verify` for proof-lane and readiness-language PR invariants.
- `tessl change review` for advisory SDK PR review using focused review skills.
- `tessl change risk` only after backtesting risk classifications against real SDK PR history.

Do not use Tessl external proof as a substitute for SDK mechanical, oss-local, oss-cloud, or local runtime proof.

## Proposed Monitoring Signals

Track these over time:

- SDK CircleCI gate pass/fail/noise rate.
- Number of capability evidence refs still `not_run`.
- Number of replayed command refs with fresh receipts.
- Number of determinism candidates promoted to validators, schemas, evals, or skill fixes.
- Number of preview-only/readiness overclaims caught before review.
- Number of PM thread reports rejected for missing delivery receipt or contradiction.
- Number of SDK PRs where validation, review, CI, tracker, merge, and pulled-main truth remained separate in closeout.

## Bottom Line

The Skills SDK does not need a new conceptual harness first. It needs the existing harness made executable in CircleCI, then expanded into command replay and recurring determinism triage.

Start with the CircleCI SDK gate, then add command-evidence replay as a manual workflow, then promote determinism audit and proof-lane verifiers once their signal is stable.
