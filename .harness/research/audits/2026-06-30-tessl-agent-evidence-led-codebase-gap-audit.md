# Tessl-Agent Evidence-Led Codebase Gap Audit

Date: 2026-06-30

Target codebase: /Users/jamiecraik/dev/agent-skills

Named audit lane: tessl-agent

Source research:
- /Users/jamiecraik/dev/coding-harness/.harness/research/deep/2026-06-30-tessl-agent-evidence.md

Audit skills used:
- /Users/jamiecraik/dev/agent-skills/Skills/agent-ops/improve-agent-native/SKILL.md
- /Users/jamiecraik/dev/agent-skills/Skills/agent-ops/improve-codebase-architecture/SKILL.md

Audit mode:
- Evidence-led codebase gap audit.
- Read-only inspection plus this report artifact.
- Existing dirty worktree changes were treated as unrelated/user-owned and not modified.

## 1. Executive Summary

Overall grade: B

The repository is already much closer to a Tessl-agent style harness than a conventional skills/docs repo. It has an explicit foundry-vs-distribution boundary, a governed `./bin/ask` control plane, schema-backed receipt families, runtime-card validators, PM thread-report validators, lane separation for SDK mechanical, oss-local, oss-cloud, Tessl local, and Tessl external proof, and durable steering uptake rules. Those are real architecture surfaces, not just aspirations.

The main gap is not "build an agent harness from scratch." The main gap is turning existing evidence surfaces into a smaller loop-first runtime product. The codebase has many strong validators and receipts, but it still lacks a first-class Tessl-agent loop specification that ties one recurring workflow to triggers, evidence intake, background execution, verifier extraction, human risk gates, cost policy, recovery, and decommissioning. Several pieces exist, but the loop is assembled by operator discipline rather than a single enforced contract.

The research document's strongest recommendations map well to this repo:

1. Start with recurring operational loops, not platform sprawl.
2. Promote interactive workflows into background checks only after evidence stabilizes.
3. Create skills from observed repository evidence and human correction.
4. Treat verifiers, evals, and review loops as LLM lint, not final truth.
5. Capture local session failures into durable, redacted, team-visible artifacts.
6. Keep human gates around high-risk changes.
7. Prevent "local maximum shipping" by converting repeated failures into validators, tests, schemas, skills, or explicit exceptions.

The repo already does some of this well. It is weaker where the research expects one loop-level product surface: loop specs, recurring automation maturity, session-to-eval promotion, cost-aware delegation policy, and enforceable architecture boundaries beyond path ownership and selected SDK module tests.

## 2. Overall Gradecard

| Category | Grade | Status | Evidence | Main Gap | Recommended Fix |
|---|---:|---|---|---|---|
| Repo as agent control plane | A- | implemented_enforced | `AGENTS.md` defines `./bin/ask`, canonical source boundaries, Tessl lane policy, PM thread report policy, and learned-fix uptake. | The public product surface is still broad and expert-shaped. | Add a one-command loop health facade for recurring agent workflows. |
| Runtime truth and decision packets | B+ | implemented_partial | Runtime cards, evidence receipts, capability matrix, schema spine, and PM thread reports exist. | Runtime truth is split across several receipt families and external usage/session paths. | Add a unified `agent-loop-run-receipt.v1` that references existing receipts. |
| Claim-vs-evidence discipline | A- | implemented_enforced | Runtime lane contract forbids substituting oss-local, oss-cloud, Tessl local, and Tessl external proof. Thread report validation requires outcomes and evidence. | Enforcement is strongest in SDK/PM lanes, weaker for ordinary PR closeout and ad hoc automation claims. | Add a generic claim-boundary validator for PR/update artifacts. |
| Mechanical architecture enforcement | B- | partial | Path ownership, runtime lane validator, schema tests, SDK module boundary tests, CI gates. | No general layer/import graph enforcement for the whole control plane; several rules are doc-enforced. | Add an architecture boundary manifest plus import/dependency checks for SDK, CLI, validators, and skills. |
| Harness runtime loop | C+ | scaffolded | Research describes loop-first harness; repo has steering uptake, PM reports, eval ladders, runtime proof. | No first-class loop-spec schema, maturity rubric, or recurring automation lifecycle. | Create loop-spec schema, validator, and `.harness/loops/<loop-id>/` receipt convention. |
| Trace/session evidence | B- | partial | Runtime cards include session observability fields; observability feedback receipts and tests exist. | Session evidence promotion is not a standard redacted intake path for new skills/evals. | Add redacted session-evidence intake and promotion receipts. |
| Context engineering | B | implemented_partial | Skills, references, capability matrix, runtime projection, package verification, KnowledgeOS capsule references. | Context provenance is strong for packages but not yet loop-scoped or cost-aware. | Require each loop spec to name hot/cold context, retrieval limits, and update triggers. |
| Skills/workflow density | B+ | implemented_partial | Large skill catalog, skill package verification, eval metadata, external review lane, Tessl staging. | Skill overlap and loop ownership can still sprawl. | Add skill overlap/route-collision checks to the loop adoption gate. |
| Recovery/failure handling | B+ | implemented_partial | Runtime cards include recovery plans; steering uptake requires deterministic guardrail; lane contract names blockers. | Repeated automation failure does not universally auto-open a repair owner class. | Add repeated-failure classifier for loop receipts. |
| Governance/safety | A- | implemented_enforced | Private Tessl workspace policy, no npx/publish lane, secrets boundary, thread PM delivery, network permission guidance. | Human-risk gate exists in docs and lane policy, but not as a generic risk score in every loop. | Add `human_risk_gate` to loop specs and closeout claims. |

Status legend:
- `implemented_enforced`: executable and mechanically checked.
- `implemented_partial`: executable pieces exist, but the full product contract is split or optional.
- `scaffolded`: schema, artifact, or doc direction exists but the operator must assemble the loop.
- `documented_only`: stated in docs but not enforced by code.
- `missing`: no live code/tree evidence found.
- `non_enforced`: present but not a gate.

## 3. Evidence-To-Code Mapping

| Research pattern | Research evidence | Codebase evidence | Runtime status | Confidence |
|---|---|---|---|---|
| Loop-first harness building | The research recommends loop specs with trigger, inputs, outputs, failure signals, eval extraction, rollback, and ownership. | `AGENTS.md:38-63` requires repeated steering/failures to become durable guardrails; PM report and Tessl runtime lanes create loop-like evidence paths. | scaffolded | High |
| Interactive-to-background migration | Research recommends promoting stable interactive patterns into CI/scheduled checks. | `.github/workflows/*`, `docs/agents/04-validation.md`, and skill quality ladders define CI and wrapper gates. | implemented_partial | Medium |
| Evidence-backed skill creation | Research requires skill rules to cite PRs, issues, CI, session logs, or docs. | Skill package contracts and source-context references exist; `validate_thread_report.py` requires lessons with durable recorded locations. | implemented_partial | High |
| Team-owned review skill | Research expects review loops with human correction before skill creation. | `external_review_skill` uses local audit, plugin-eval, Tessl lint/review policy, Snyk opt-in policy, and non-publish boundaries. | implemented_partial | High |
| Human-risk gate | Research names owner approval and high-risk change gating. | Tessl policy forbids public publish/upload, lane contract forbids proof substitution, PM delivery blocks gate decisions without delivery evidence. | implemented_enforced in SDK lanes | High |
| Verifiers as LLM lint | Research treats verifiers as cheap systematic checks. | `validate_runtime_cards.py`, `validate_sdk_runtime_lane_contract.py`, `validate_thread_report.py`, schema spine tests, and CI workflows provide verifier surfaces. | implemented_enforced | High |
| Observation-derived evals | Research recommends extracting evals from observed failures. | `observability-feedback-receipt`, `observability-promotion-receipt`, eval metadata, and scenario-quality receipts exist. | implemented_partial | Medium |
| Delegation as cost optimization | Research recommends selecting model/tool depth by risk and cost. | Eval profiles define local and cloud profiles with model roles, secret boundaries, and sanitized-output rules. | implemented_partial | Medium |
| Open modular factory ownership | Research warns against vendor lock-in at the factory layer. | `AGENTS.md` separates agent-skills foundry, Skills SDK lifecycle, Tessl distribution, and local runtime truth. | implemented_enforced | High |
| Factory from either end | Research says loops can start from repo observation or desired skill workflows. | `./bin/ask skills improve`, `skills explain`, `skills prove`, and capability matrix allow goal-to-skill routing. | implemented_partial | High |

## 4. Gap Register

### GAP-001: No First-Class Loop Spec

Category: harness runtime loop

Current state:
The repo has repeated-failure policies, steering uptake, PM reports, runtime cards, and eval/Tessl lanes. These are strong ingredients, but they are not bound by a single recurring-loop artifact.

Expected state:
A recurring workflow should have one machine-readable loop spec with trigger, source inputs, owner, safe mutation surface, expected outputs, validation commands, human-risk gate, session evidence policy, retry budget, cost profile, eval extraction rule, decommission path, and closeout receipt.

Evidence:
- Research recommends a loop-spec template for recurring agent workflows.
- `AGENTS.md:38-63` requires repeated failures to become durable guardrails.
- `docs/agents/25-sdk-runtime-lane-contract.md:83-96` defines lane report shape, not a generic loop spec.

Status: scaffolded

Risk:
Operators can keep repairing individual symptoms and never get a durable recurring-loop product surface.

Fix:
Add `Infrastructure/config/schemas/agent-loop-spec.v1.schema.json`, `Infrastructure/scripts/validation-and-linting/validate_agent_loop_spec.py`, and a `.harness/loops/<loop-id>/loop.json` convention. Start with one loop: PR review/evidence closeout or SDK oss-local runtime health.

Priority: P0

### GAP-002: External Evidence Intake Is Not Mechanically Promoted

Category: evidence-backed skill creation

Current state:
The Tessl-agent research lives outside this repo under `/Users/jamiecraik/dev/coding-harness/.harness/research/deep/`. This audit consumes it manually. The repo does not appear to have an enforced intake artifact that records source repo, source digest, accepted rules, rejected rules, owner correction, and promoted guardrail.

Expected state:
External research should enter agent-skills through a signed or digest-recorded intake receipt before it changes skill rules, evals, validators, or roadmap claims.

Evidence:
- Research lines 108-129 recommend evidence-backed skill creation and a skill-intake artifact.
- The live repo has many receipt schemas, but this audit did not find a dedicated cross-repo research-intake receipt.

Status: partial

Risk:
A transcript-derived recommendation can become doctrine without an owner decision or evidence digest.

Fix:
Add `research-intake-receipt.v1` with fields for source path, digest, evidence class, accepted findings, rejected findings, owner, target surfaces, and validation command. Make audits reference it when external research becomes an implementation input.

Priority: P1

### GAP-003: Session-To-Eval Promotion Is Partial

Category: trace/session evidence

Current state:
Runtime cards include session observability and limitation fields. Observability feedback/promotion receipts and tests exist. However, there is no single required path from local Codex/session logs to a sanitized eval, skill update, or validator.

Expected state:
Local agent failures should be redacted, summarized, classified, and routed into one of: eval case, validator, skill change, architecture rule, or explicit no-action reason.

Evidence:
- Research lines 623-649 identify unobserved local agent failure as high severity.
- Runtime proof sample `.harness/evidence/runtime-proof/improve-agent-native/codex/runtime-card.json` records session observability and limitations.
- `Infrastructure/tests/test_skills_sdk_observability_feedback.py` covers feedback/promotion receipts.

Status: implemented_partial

Risk:
The repo can prove a runtime card exists while still losing the repeated failure pattern that should become an eval.

Fix:
Create `session-evidence-intake.v1` and a validator that requires redaction status, source class, failure taxonomy, promotion target, and no-secret proof before a session-derived rule enters a skill or eval.

Priority: P1

### GAP-004: Architecture Boundaries Are Strong In Places But Not System-Wide

Category: mechanical architecture enforcement

Current state:
The repo has path ownership, runtime lane contract validation, schema spine tests, SDK module boundary tests, and CI governance. It does not appear to have one architecture boundary manifest that describes allowed imports/dependencies among CLI dispatch, SDK domain modules, validators, schemas, skill sources, runtime projections, and evidence artifacts.

Expected state:
A machine-readable architecture contract should define layer ownership and dependency direction. CI should fail on direct imports or writes that cross boundaries without an explicit adapter.

Evidence:
- `docs/agents/04-validation.md` names path ownership checks.
- Search found focused SDK boundary and path/projection enforcement, but no general repo architecture graph contract.
- `improve-codebase-architecture` asks for caller/public/verifier proof and owner boundaries.

Status: partial

Risk:
New receipts and validators can accrete into the CLI layer without a domain boundary, making the control plane harder to simplify.

Fix:
Add `Infrastructure/config/architecture-boundaries.v1.json` and a validator covering `Infrastructure/scripts/lib/ask/commands/**`, `Infrastructure/scripts/lib/ask/skills_sdk/**`, `Infrastructure/scripts/validation-and-linting/**`, `Infrastructure/config/schemas/**`, `Skills/**`, and `.harness/**`.

Priority: P1

### GAP-005: Claim-Boundary Enforcement Is Not Universal

Category: claim-vs-evidence

Current state:
SDK runtime lane docs and thread report validators strongly prevent proof-lane substitution. The hook prompt and AGENTS.md reinforce exact command evidence. But ordinary comments, PR bodies, and ad hoc reports do not all pass through the same claim-boundary validator.

Expected state:
Any artifact that says done, fixed, green, ready, mergeable, passed, or released should either reference exact command evidence or a workflow-closeout/v1 receipt.

Evidence:
- `docs/agents/25-sdk-runtime-lane-contract.md:56-81` forbids lane substitution and merged status lines.
- `validate_thread_report.py:183-190` validates commands and artifact assertions for thread reports.
- The user's hook prompt repeats the readiness-claim rule, indicating this remains a recurring operational failure.

Status: implemented_partial

Risk:
A strong SDK lane can still be undermined by a human-facing report that overclaims hosted CI, review, PR, or merge state.

Fix:
Add `validate_claim_boundaries.py` for PR descriptions, closeout reports, thread reports, and Codex final-response draft artifacts when available. Start with regex terms plus required command/receipt references.

Priority: P0

### GAP-006: Human Risk Gate Is SDK-Lane-Specific

Category: governance/safety

Current state:
Tessl and SDK lanes have explicit no-publish, private workspace, no npx, secret boundary, and PM delivery policies. There is not a generic risk gate schema that every recurring loop must evaluate.

Expected state:
Every loop spec should classify risk: source mutation, external service, credentials, public output, user runtime links, destructive commands, and model-provider authority. High risk should require an explicit human approval field or blocked status.

Evidence:
- Research lines 169-192 call out human-risk gates.
- `AGENTS.md:71-99` describes strict Tessl eval and private workspace constraints.
- `eval_profiles.py` separates secret-bearing cloud profiles from local profiles.

Status: partial

Risk:
A non-Tessl loop could gain background authority without the same gate clarity.

Fix:
Add a reusable `human_risk_gate` object to loop specs and workflow closeout receipts. Validate that high-risk loops cannot be marked active without owner approval evidence.

Priority: P1

### GAP-007: Cost-Aware Delegation Policy Is Under-Specified

Category: runtime economics

Current state:
The eval profile system names local and cloud profiles, model roles, network requirements, and secret boundaries. It does not yet encode budget, expected token/runtime envelope, or escalation policy at the loop level.

Expected state:
Recurring loops should state when they use local OSS, cloud OSS, fast Codex, Tessl local, Tessl external, or human review, including cost/risk tradeoffs and fallback order.

Evidence:
- Research lines 262-285 identify delegation as cost optimization.
- `eval_profiles.py` declares local and cloud profile boundaries.
- Runtime lane contract separates proof lanes but not loop-level cost policy.

Status: non_enforced

Risk:
The platform can be correct but expensive, or cheap but insufficiently verified, without a clear loop owner decision.

Fix:
Add `execution_budget` and `model_escalation_policy` to loop specs. For SDK loops, require profiles to be selected from `eval_profiles.py`.

Priority: P2

### GAP-008: Skill Sprawl And Route Collision Need Stronger Guardrails

Category: skills/workflow density

Current state:
The repo has a large skill catalog and package/eval machinery. Install intake includes overlap candidates and promotion rules, but recurring loops can still create new skills or eval cases without a centralized ownership/routing collision check.

Expected state:
New skills, recurring loops, and generated eval suites should be checked against existing skill handles, descriptions, routing language, and owner package identity.

Evidence:
- Research lines 809-832 warn about skill sprawl.
- `skills_impl.py` install intake has local overlap logic and post-install gates.
- `.skillsets/agent-ops/manifest.jsonl` exists but is currently dirty from unrelated work, indicating this surface is active and potentially sensitive.

Status: implemented_partial

Risk:
The loop-first approach could produce overlapping automation and skills faster than governance can absorb them.

Fix:
Add a `loop_owner` and `skill_route_impact` section to loop specs. Validate new loop specs against skill manifests and existing loop ids.

Priority: P2

## 5. Contradictions And Tensions

### CT-001: The repo says "loop-first", but the executable surface is receipt-first.

The repo's strongest mechanics are receipts, validators, and lane contracts. The research argues that the recurring loop should be the product unit. This is not a fatal contradiction; it means the next abstraction should wrap existing receipts rather than replace them.

Resolution:
Create loop specs and loop-run receipts that reference existing receipt families.

### CT-002: The repo has strong lane separation, but the current worktree shows many simultaneous lanes.

The live worktree contains many unrelated modified and untracked files. That is not a source defect by itself, but it raises operational risk for any closeout or implementation lane.

Resolution:
This audit did not modify existing dirty files. Any implementation follow-up should start with dirty-state classification and a bounded branch/PR plan.

### CT-003: Tessl evidence is external proof direction, but agent-skills is the foundry.

The source research is in coding-harness, while agent-skills owns SDK foundry/source truth. The repo's language already separates foundry, Skills SDK lifecycle, Tessl distribution, and local runtime truth. The missing piece is a mechanical research-intake record.

Resolution:
Do not copy the external evidence into product doctrine directly. Promote only digest-recorded, owner-accepted findings.

### CT-004: Runtime cards can be valid while runtime observability remains partial.

The sample `improve-agent-native` runtime card records `claim_status: partial` and says skill invocation is not asserted. That is healthy honesty, but it also shows why runtime-card existence alone should not be reported as live skill invocation proof.

Resolution:
Keep partial runtime status visible and add session-to-eval promotion for recurring partial/runtime gaps.

## 6. Missing Features

1. `agent-loop-spec.v1` schema and validator.
2. `agent-loop-run-receipt.v1` receipt that binds trigger, commands, evidence, claim boundary, risk gate, and next action.
3. Cross-repo `research-intake-receipt.v1` for transcript/research imports.
4. Session evidence redaction and promotion path into evals/skills/validators.
5. Generic claim-boundary validator for human-facing closeout/PR/report artifacts.
6. Architecture boundary manifest and dependency direction validator.
7. Loop maturity rubric: manual, assisted, repeatable, scheduled, CI-gated, self-improving, decommissioned.
8. Cost-aware execution policy for recurring loops.
9. Skill/loop route-collision detector.
10. Human-risk gate object reusable outside Tessl/SDK lanes.

## 7. Fix Roadmap

### Phase 1: Make Loop Ownership Mechanical

Goal:
Convert the Tessl-agent "loop-first" research into one minimal executable repo contract.

Scope:
- Add `agent-loop-spec.v1.schema.json`.
- Add `validate_agent_loop_spec.py`.
- Add one fixture loop for SDK runtime health or PR evidence closeout.
- Add docs entry under `docs/agents/`.

Acceptance:
- A sample loop spec validates.
- The schema requires trigger, owner, evidence inputs, validation command, human-risk gate, retry budget, and decommission policy.
- The loop spec references existing receipts rather than duplicating them.

Suggested validation:
- `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest Infrastructure/scripts/testing/test_validate_agent_loop_spec.py -q`
- `python3 Infrastructure/scripts/validation-and-linting/validate_agent_loop_spec.py .harness/loops/sdk-runtime-health/loop.json --json`

### Phase 2: Add Claim-Boundary Validation

Goal:
Prevent recurring overclaims across reports and PR/update artifacts.

Scope:
- Add `validate_claim_boundaries.py`.
- Start with thread reports, closeout artifacts, and PR templates if locally available.
- Require exact command evidence or workflow-closeout/v1 receipt for readiness terms.

Acceptance:
- Fixtures fail when "ready", "mergeable", "green", or "done" appears without evidence.
- Fixtures pass when evidence is exact and lane-scoped.

Suggested validation:
- `bash Infrastructure/scripts/run-infrastructure-python.sh -m pytest Infrastructure/scripts/testing/test_validate_claim_boundaries.py -q`

### Phase 3: Add Research Intake And Session Promotion

Goal:
Turn external research and local session failures into governed improvement inputs.

Scope:
- Add `research-intake-receipt.v1`.
- Add `session-evidence-intake.v1`.
- Add validators for source digest, redaction, accepted/rejected findings, owner decision, and target surface.
- Connect observability promotion receipts to eval/skill/validator targets.

Acceptance:
- This Tessl-agent research could be represented as an intake receipt without copying raw transcript content.
- A redacted session failure can generate a candidate eval or explicit no-action reason.

### Phase 4: Add Architecture Boundary Manifest

Goal:
Make the control-plane architecture enforceable beyond individual validators.

Scope:
- Add `Infrastructure/config/architecture-boundaries.v1.json`.
- Encode allowed dependencies among CLI dispatch, SDK domain modules, schemas, validators, skills, runtime projections, and evidence artifacts.
- Add validator and tests.

Acceptance:
- Command layer can call domain modules.
- Domain modules cannot import command dispatch.
- Validators can load schemas but do not mutate evidence.
- Runtime projections remain generated surfaces.

### Phase 5: Make Loop Health Operator-Friendly

Goal:
Expose a single loop health command that summarizes the recurring workflow state.

Scope:
- Add or extend `./bin/ask` with a loop health/status facade.
- Output active loops, last run status, claim boundary, blocker, next command, and decommission state.

Acceptance:
- An agent can ask one command for the next safe action for a recurring loop.
- Output is robot-friendly and evidence-linked.

## 8. Highest-Leverage Fixes

1. P0: `agent-loop-spec.v1` plus validator.
2. P0: claim-boundary validator for readiness/merge/green/done claims.
3. P1: research intake receipt for external evidence.
4. P1: session evidence redaction and promotion receipt.
5. P1: architecture boundary manifest.
6. P2: loop cost/escalation policy.
7. P2: route-collision checks for loops and generated skills.

The smallest useful first move is not another broad SDK surface. It is one loop spec and one validator, using an existing high-friction loop such as SDK runtime health or PR evidence closeout as the fixture. That would make the Tessl-agent research concrete without expanding the platform aimlessly.

## 9. Implementation Advice

Use the current repo strengths:
- Reuse existing schema patterns under `Infrastructure/config/schemas/skills-sdk/`.
- Reuse validator style from `validate_thread_report.py`, `validate_thread_pm_delivery.py`, and `validate_runtime_cards.py`.
- Reuse runtime lane terms from `docs/agents/25-sdk-runtime-lane-contract.md`.
- Reuse steering taxonomy from `validate_steering_uptake.py`.
- Reuse existing receipt language: `status`, `command`, `evidence`, `does_not_prove`, `blocker`, `next_action`.

Avoid:
- Creating a new broad orchestrator before one loop is validated.
- Copying external research into skill rules without source digest and owner decision.
- Treating Tessl local staging as Tessl external scoring.
- Treating runtime-card existence as live invocation proof.
- Merging PR/CI/review/merge state into one status line.
- Editing runtime projections directly.

Suggested first loop fixture:
- Loop id: `sdk-runtime-health`
- Trigger: stale/blocked oss-local, Codex/Ollama tool-call failure, or profile-sandbox mismatch.
- Inputs: runtime lane receipt, Codex profile config, local model runtime evidence, latest thread report.
- Outputs: runtime-health triage report, owner class, next safe command.
- Human gate: required before user-runtime link mutation or Tessl external run.
- Eval extraction: repeated blocker becomes validator/test/learning.
- Decommission: loop closes when runtime health is proven by current receipt and no blocked_next_gates remain.

## 10. Final Recommendation

Do not build a separate Tessl-agent clone inside this repo. The repo already has the right kind of primitives: schemas, receipts, validators, proof lanes, runtime cards, skill packages, and PM delivery contracts.

Instead, add the missing loop abstraction that makes those primitives behave like a Tessl-agent system:

1. Define one recurring loop spec.
2. Validate it mechanically.
3. Run it on one real workflow.
4. Convert every repeated failure into a guardrail or explicit deferred owner.
5. Only then broaden to additional recurring loops.

This preserves the repo's canonical-only, evidence-led operating model while adopting the research's strongest point: the loop, not the platform, is the unit of agent-harness improvement.

## 11. Command Evidence

Commands run during this audit:

- Command: `git status --short --branch` -> pass (reported live dirty worktree; existing unrelated/user-owned changes preserved)
- Command: `rg -n "^(##|### Pattern|### Gap|### Recommendation|### Risk)" /Users/jamiecraik/dev/coding-harness/.harness/research/deep/2026-06-30-tessl-agent-evidence.md` -> pass (listed research structure)
- Command: `fd -a 'evidence-led|tessl|gap-audit' .harness/research/audits` -> pass (found prior audit artifacts)
- Command: `rg -n "thread-report|workflow-closeout|runtime|Tessl|claim|evidence|readiness|steering|Local Memory|Project Brain" AGENTS.md Docs/agents Infrastructure/scripts Infrastructure/config Skills/agent-ops -g '!**/__pycache__/**' -g '!**/.venv/**'` -> pass (output truncated because the repo has many matching evidence surfaces)
- Command: `fd -a 'ask|validate|thread|schema|contract|runtime|profile|tessl|eval' Infrastructure/bin Infrastructure/scripts Infrastructure/config Docs/agents .github .harness 2>/dev/null` -> pass (output truncated after showing validator/schema/evidence surfaces)
- Command: `sed -n '1,220p' docs/agents/16-agent-operating-contract.md` -> pass (read ask CLI contract)
- Command: `sed -n '1,220p' docs/agents/25-sdk-runtime-lane-contract.md` -> pass (read runtime/Tessl lane separation contract)
- Command: `sed -n '1,220p' docs/agents/26-pm-thread-coordination.md` -> pass (read thread-report and delivery contract)
- Command: `sed -n '1,220p' docs/agents/04-validation.md` -> pass (read validation guidance)
- Command: `sed -n '1,260p' Infrastructure/scripts/validation-and-linting/validate_runtime_cards.py` -> pass (read runtime-card validator structure)
- Command: `sed -n '1,260p' Infrastructure/scripts/validation-and-linting/validate_sdk_runtime_lane_contract.py` -> pass (read lane-contract validator structure)
- Command: `sed -n '1,260p' Infrastructure/scripts/lib/ask/skills_sdk/eval_ab_judge_codex.py` -> pass (read Codex profile execution wrapper)
- Command: `fd -a '.schema.json' Infrastructure/config/schemas/skills-sdk` -> pass (listed Skills SDK schema spine)
- Command: `fd -a . .github/workflows` -> pass (listed hosted workflow surfaces)
- Command: `rg -n "import graph|dependency|layer|boundary|architecture|path ownership|directed|cycle|depcruise|madge|ruff|mypy" Infrastructure/scripts Infrastructure/tests Docs/agents .github -g '!**/__pycache__/**'` -> pass (output truncated; found path/gate/boundary evidence but no single architecture manifest)
- Command: `rg -n "observability|runtime-card|session|trace|usage-data|artifact-record|evidence-receipt|feedback" Infrastructure/scripts Infrastructure/tests Docs/agents .harness/evidence/runtime-proof -g '!**/__pycache__/**'` -> pass (output truncated; found runtime/observability evidence)
- Command: `sed -n '1,220p' .harness/evidence/runtime-proof/improve-agent-native/codex/runtime-card.json` -> pass (read sample runtime-card evidence)
- Command: `sed -n '1,180p' Infrastructure/config/skills-sdk/capability-matrix.v1.json` -> pass (read capability truth surface sample)

No Tessl, oss-cloud, or runtime mutation commands were run.

