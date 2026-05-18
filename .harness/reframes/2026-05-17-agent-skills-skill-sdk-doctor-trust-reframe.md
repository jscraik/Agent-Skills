---
schema_version: 1
selected_stage: he-reframe
program_path: .harness/reframes/2026-05-17-agent-skills-skill-sdk-doctor-trust-reframe.md
source_strategy: .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md
source_strategy_status: missing_in_current_checkout
status: approved_for_he_plan
date: 2026-05-17
repo: agent-skills
handoff: he-plan
---

# Agent Skills Kit Skill SDK Doctor Trust Reframe

## Command Summary

BLUF: This reframe converts the approved Skill SDK north star into a phased migration program so Agent Skills Kit can prove skill readiness through `./bin/ask skills doctor <handle> --json --robot` before Codex or coding-harness rely on a skill. It matters because readiness truth is currently split across source ownership, runtime projection, package metadata, profiles, events, memory, outcome proof, and the agent's ability to generalize high-signal feedback instead of patching one named instance. The first phase should harden doctor contract fixtures for one representative skill because a broad SDK rewrite would add ceremony before proving runtime trust.

Decision Needed: Approve RF-1 as the first implementation slice for `he-plan`.

Top Risks: The SDK contract can become ceremony without behavior proof; harness can duplicate Agent Skills Kit logic; stale memory or runtime projections can look current; package readiness can be mistaken for outcome proof.

Next Action: Create an `he-plan` for RF-1 that adds doctor JSON contract fixtures and negative-path checks around `context7`, while preserving RF-0 steering uptake gates as a non-negotiable preflight for implementation work.

## Reframe Classification

- Type: architecture and process-repair reframe.
- High-leverage threshold: met.
- Primary improvement: determinism, routing trust, eval quality, governance simplicity, and future-agent cognition.
- Scope boundary: plan SDK trust through `skills doctor`; do not implement broad packaging, marketplace, or remote execution changes in this program.
- Authority: this artifact designs phased change only. It does not authorize code mutation, public API changes, tracker mutation, publication, or projection edits.

## Problem Statement

Agent Skills Kit is already more than a folder of prompts, but its readiness model is still distributed. A skill can be source-valid, runtime-blocked, package-incomplete, eval-missing, memory-stale, and still appear partially healthy depending on which command or surface a future agent reads first.

The north-star strategy names the right product direction: professional SDK of skills with thin surface, strong guardrails, durable memory, and professional output. The missing bridge is a migration program that makes that strategy executable without turning it into a broad refactor.

The clarified operating outcome adds one more requirement: every high-signal
steering event must become an environment refinement when it changes future
behavior. The SDK cannot be professional if agents can still absorb review or
strategy feedback as a single local patch, a polished explanation, or a stale
memory note. The migration must therefore prove both skill readiness and agent
uptake behavior.

## Root Cause Analysis

The current structure emerged because skill authoring, runtime projection, package readiness, and Harness Engineering evolved as useful layers at different times.

It survived because each layer solves a real local problem:

- `SKILL.md` gives Codex a compact runtime entrypoint.
- `.agents/skills/**` and command handles make skills discoverable.
- `./bin/ask skills doctor` diagnoses readiness.
- `./bin/ask skills package` reports promotion and share metadata.
- `./bin/ask skills profiles` exposes operation modes.
- `./bin/ask skills events` exposes lifecycle evidence.
- `coding-harness` needs a control pane over runs, evidence, and gates.
- Review feedback often arrives as a local comment even when it expresses a broader design rule.
- Agent steering often arrives in conversation, but the durable owner is the
  nearest repo contract, validator, eval, memory surface, or workflow gate that
  prevents the same correction from recurring.

The pressure is strategic and operational, not just historical. Jamie wants Codex to rely on skills in real workflows without re-explaining safety, ownership, and proof every time. The force keeping drift in place is that each surface can be locally reasonable while the combined readiness contract remains implicit.

## Evidence

- Agent Skills Kit north star: `.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md` is referenced by this reframe but is missing in the current checkout as of 2026-05-18. Restore it or replace the reference with an existing canonical source before using it as live evidence.
- [UBIQUITOUS_LANGUAGE.md](/Users/jamiecraik/dev/agent-skills/UBIQUITOUS_LANGUAGE.md:13) defines Agent Skills Kit as the governed repository and CLI system for authoring, validating, discovering, and syncing Codex skills.
- [UBIQUITOUS_LANGUAGE.md](/Users/jamiecraik/dev/agent-skills/UBIQUITOUS_LANGUAGE.md:15) separates Canonical Skill Source from [Runtime Projection](/Users/jamiecraik/dev/agent-skills/UBIQUITOUS_LANGUAGE.md:16).
- [Path Ownership Boundaries](/Users/jamiecraik/dev/agent-skills/Docs/agents/14-path-ownership-boundaries.md:10) uses a product, factory, and runtime plane model.
- [Agent Capability Control Plane](/Users/jamiecraik/dev/agent-skills/Docs/product/agent-capability-control-plane.md:36) already maps diagnosis to `ask skills doctor <handle-or-path> --json --robot`.
- `./bin/ask skills doctor context7 --json --robot` currently returns `blocked_runtime` while also preserving `outcome_proof_missing`, package metadata gaps, operation context, lifecycle event data, and a `next_command`.
- `./bin/ask skills package context7 --json --robot` is the baseline package-readiness probe for separating package metadata gaps from runtime blockers.
- [High-Signal Steering Feedback](/Users/jamiecraik/dev/agent-skills/Docs/agents/19-high-signal-steering-feedback.md:1) defines steering as operating evidence and requires classified uptake before ordinary work resumes.
- [Steering Uptake Ledger](/Users/jamiecraik/dev/agent-skills/.harness/quality/steering-uptake.md:1) records the repeated-steering environment refinement with operating failure, blocker, mechanism, proof, validation, and repeat prevention.
- [validate_steering_uptake.py](/Users/jamiecraik/dev/agent-skills/Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py:1) makes that uptake executable.
- [CTF Workflow Evals](/Users/jamiecraik/dev/agent-skills/Docs/agents/23-ctf-workflow-evals.md:1) makes flag capture the win condition for workflow skills whose truth lives in UI or app state.
- Final review artifacts approved the strategy after fixes:
  - [adversarial reviewer](/Users/jamiecraik/dev/agent-skills/artifacts/reviews/sdk_north_star_round4d_adversarial_reviewer.md:5)
  - [adversarial document reviewer](/Users/jamiecraik/dev/agent-skills/artifacts/reviews/sdk_north_star_round4_adversarial_document_reviewer.md:6)
  - [architecture strategist](/Users/jamiecraik/dev/agent-skills/artifacts/reviews/sdk_north_star_round4b_architecture_strategist.md:6)

## Architectural Impact

The reframe changes the center of gravity from "skills are authored and projected" to "skills expose a small SDK contract that can be diagnosed, packaged, evaluated, and consumed by harness without reading internals."

Expected impact:

- Doctor becomes the operator readiness aggregator, not a replacement for package, eval, audit, or events.
- Agent Skills Kit owns schema, check classes, profile semantics, package contracts, eval proof contracts, and canonical source.
- Coding-harness owns invoking, preserving, correlating, and presenting evidence without duplicating skill logic.
- Future agents get one deterministic entrypoint for readiness before relying on a skill.

## Desired End State

A representative skill such as `context7` can be checked through doctor and produce a stable JSON contract with:

- `schema_version`
- `status`
- `target_summary`
- `checks`
- `blockers`
- `warnings`
- `operation_context`
- `contract_schemas`
- `agent_summary`
- `next_command`

The same run clearly separates:

- source resolution;
- runtime reachability;
- structural audit;
- package readiness;
- profile requirements;
- freshness state;
- outcome proof;
- lifecycle event evidence.

No release-readiness claim is allowed unless the relevant profile says missing eval proof, stale memory, package gaps, and runtime blockers are resolved or explicitly non-promotional.

Review-handling skills should also prove they can turn feedback into transferable rules when the text warrants it. A local reviewer comment such as "return a named sentinel error instead of a success/failure bool" should not be applied only to the named line when the comment expresses an API design rule. The SDK contract should require:

- `feedback_intent`: `local_bug`, `repeated_pattern`, `api_design_rule`, `architecture_boundary`, `naming_language`, `validation_gap`, `test_contract_gap`, or `documentation_drift`;
- `intent_radius`: `line`, `function`, `file`, `package`, `repository`, `architecture_rule`, or `durable_memory`;
- bounded search scope and explicit exclusions;
- similar-case classification as `fixed_now`, `left_different_semantics`, `deferred_public_api`, `deferred_risk`, or `not_applicable`;
- durable guidance or eval update when the rule should guide future work.

Stable does not mean frozen forever. Schema evolution should follow these rules before any harness consumer depends on the contract:

- additive fields are allowed within the same schema version when existing required fields keep their meaning;
- removing or renaming a required field requires a schema version bump;
- changing status precedence, blocker class semantics, or `next_command` nullability requires a schema version bump;
- deprecated fields need a documented replacement and a compatibility window;
- cross-consumer fixtures must include the schema version and fail when `./bin/ask` and coding-harness interpret the same fixture differently.

## Migration Strategy

Use the smallest reversible sequence that proves the SDK direction without broad rewrites.

1. Harden doctor contract fixtures for one non-mutating skill.
2. Add negative-path coverage for contradictory readiness states.
3. Add package/profile/event cross-consumer checks.
4. Add review-feedback intent-radius handling for design-rule comments.
5. Teach harness to consume the stable contract only after Agent Skills Kit owns it.
6. Expand from `context7` to Harness Engineering skills after proof exists.

## Smallest Reversible Step

RF-1: Add doctor JSON fixture and contract assertions for `context7`.

This is reversible only if the phase records before/after command snapshots and names any tolerated output differences. If RF-1 changes doctor behavior, rollback must revert the implementation change as well as the fixtures/tests. It produces observable feedback immediately by showing whether `skills doctor` can act as the trusted operator view.

## Execution Phases

### RF-0: Steering Uptake Environment Gate

- Objective: Prove the agent operating environment absorbs high-signal steering
  as a durable mechanism before SDK implementation work proceeds.
- Affected systems: `AGENTS.md`, `UBIQUITOUS_LANGUAGE.md`,
  `Docs/agents/19-high-signal-steering-feedback.md`,
  `.harness/quality/steering-uptake.md`,
  `Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py`,
  and `Infrastructure/scripts/testing/test_validate_steering_uptake.py`.
- Expected risk: low, because this phase constrains agent closeout behavior
  without changing skill runtime behavior.
- Feedback expected from this phase: whether future agents can prove blocker,
  mechanism, proof, pattern sweep, and disposition before resuming ordinary
  implementation after high-signal steering.
- Stop or pivot condition: the validator cannot reject ceremonial uptake
  records without blocking legitimate local-only feedback.
- Can run in parallel: no.
- Validation requirements:
  - `python3 Infrastructure/scripts/validation-and-linting/validate_steering_uptake.py --json`
  - `python3 -m pytest Infrastructure/scripts/testing/test_validate_steering_uptake.py -q`
  - changed-file repo validation for the touched steering instruction, ledger,
    validator, and test files
- Rollback conditions: restore the previous steering uptake schema and remove
  the regression test if it proves too strict for legitimate local-only records.
- Linear mapping: no issue required; this is the preflight gate for the program.
- Agent-safe: yes.
- Human review required: no.

### RF-1: Doctor Contract Fixture For One Skill

- Objective: Prove the doctor JSON contract shape and status precedence using `context7`.
- Affected systems: `Infrastructure/scripts/lib/ask/commands/skills_impl.py`, relevant ask CLI tests, and fixture/report paths selected by `he-plan`.
- Expected risk: medium, because command contract tests can expose existing drift.
- Feedback expected from this phase: whether doctor already has enough structured output to serve as the SDK readiness spine.
- Stop or pivot condition: doctor cannot expose required fields without duplicating package/eval implementation logic.
- Can run in parallel: no.
- Validation requirements:
  - `./bin/ask skills doctor context7 --json --robot`
  - a focused ask CLI test covering required fields, status precedence, and `next_command` nullable semantics
  - before/after doctor JSON snapshots with explicit tolerated differences
  - a read-only representativeness check against one additional skill class, chosen by `he-plan`, to prove `context7` is not hiding a contract assumption that fails immediately elsewhere
  - advisory document-governance check only: `python3 Plugins/harness-engineering/scripts/check_bluf_structure.py .harness/strategy/2026-05-17-agent-skills-sdk-north-star.md --json`
- Rollback conditions: remove the new fixture/tests, revert any doctor implementation changes made by RF-1, and verify the post-rollback `skills doctor context7` snapshot matches the recorded pre-change snapshot except for explicitly tolerated environmental fields such as trace IDs or timestamps.
- Linear mapping: create or map one implementation issue only after RF-1 plan is accepted.
- Agent-safe: assisted.
- Human review required: yes.

### RF-2: Negative-Path Readiness Matrix

- Objective: Prove contradictory states are classified separately.
- Affected systems: ask CLI doctor tests, package readiness fixtures, runtime reachability fixtures, and proof/outcome fixtures.
- Expected risk: medium.
- Feedback expected from this phase: whether blocker and warning classes are expressive enough for professional reports.
- Stop or pivot condition: too many cases require special-casing instead of a general readiness taxonomy.
- Can run in parallel: no.
- Validation requirements:
  - tests for `blocked_missing_source`, `blocked_runtime`, `capability_contract_incomplete`, `outcome_proof_missing`, `blocked_validation`, `freshness_stale`, and `freshness_unknown`
  - fixture asserting `operation_context` and `next_command` are present in pass, warning, and blocked statuses
- Rollback conditions: remove negative-path fixtures while preserving RF-1 contract tests.
- Linear mapping: child issue after RF-1 closes with evidence.
- Agent-safe: assisted.
- Human review required: yes.

### RF-3: Profile And Freshness Determinism

- Objective: Make profile semantics decide whether missing proof or stale memory is promotable, warning-only, or blocked.
- Affected systems: `skills profiles`, memory/freshness reporting, doctor operation context, and tests.
- Expected risk: medium-high, because freshness rules can affect promotion gates.
- Feedback expected from this phase: whether deterministic UTC evaluation time and profile-owned thresholds are enough.
- Stop or pivot condition: freshness cannot be represented without a broader memory contract change.
- Can run in parallel: yes, after RF-1.
- Validation requirements:
  - fixed evaluation-time tests
  - UTC timestamp normalization tests
  - exploratory vs promotion profile tests
- Rollback conditions: keep doctor contract but remove freshness-based promotion decisions.
- Linear mapping: child issue after RF-1, can run alongside RF-2 only if fixture ownership is clear.
- Agent-safe: assisted.
- Human review required: yes.

### RF-4: Harness Consumer Boundary

- Objective: Make coding-harness consume doctor/package/profile/event schemas without parsing skill internals.
- Affected systems: coding-harness command bridge, report generation, trace correlation, and contract tests.
- Expected risk: high because it crosses repository/control-plane boundaries.
- Feedback expected from this phase: whether harness can act as control pane without duplicating Agent Skills Kit implementation.
- Stop or pivot condition: harness needs fields that Agent Skills Kit cannot expose as stable public contract.
- Can run in parallel: no.
- Validation requirements:
  - cross-consumer contract test using one doctor JSON fixture
  - proof that harness preserves raw JSON and reports pass/warning/blocked/skipped/not-run buckets
- Rollback conditions: revert harness consumer changes and keep Agent Skills Kit contract intact.
- Linear mapping: separate parent or cross-repo child after RF-2/RF-3 evidence.
- Agent-safe: assisted.
- Human review required: yes.

### RF-5: Review Feedback Intent Radius

- Objective: Prove review-handling skills distinguish patch compliance from principle uptake.
- Affected systems: review-resolution skills, code-review guidance, eval fixtures, durable guidance or memory admission, and harness report shape.
- Expected risk: medium-high because over-generalizing reviewer feedback can create unsafe broad edits.
- Feedback expected from this phase: whether the SDK can require a bounded pattern sweep only when feedback expresses a transferable rule.
- Stop or pivot condition: feedback classification creates broad churn, or agents cannot explain why similar cases were fixed, left, or deferred.
- Can run in parallel: yes, after RF-1 contract shape exists.
- Validation requirements:
  - fixture where a line-level API comment implies `feedback_intent=api_design_rule` and `intent_radius=package`;
  - fixture where a truly local typo remains `feedback_intent=local_bug` with no repo sweep;
  - pattern-sweep report listing matched symbols, exclusions, fixed cases, deferred public API cases, and durable-rule action;
  - test or review artifact proving pure predicates are not rewritten into error-return APIs.
- Rollback conditions: remove intent-radius enforcement while preserving ordinary local review-fix behavior.
- Linear mapping: child issue after RF-1, before broad review-skill promotion.
- Agent-safe: assisted.
- Human review required: yes.

### RF-6: Expand To High-Value Harness Engineering Skills

- Objective: Apply the proven SDK readiness contract to `he-strategy`, `he-linear-plan`, `he-code-review`, `skill-factory`, and `plugin-factory`.
- Affected systems: canonical skill sources, metadata contracts, eval fixtures, package readiness, and proof artifacts.
- Expected risk: high because it touches multiple skill families.
- Feedback expected from this phase: whether the SDK contract scales without ceremony.
- Stop or pivot condition: mature-skill requirements slow draft authoring or create false-green quality gates.
- Can run in parallel: yes, one skill at a time after RF-2/RF-3.
- Validation requirements:
  - `./bin/ask skills doctor <handle> --json --robot`
  - `./bin/ask skills package <handle> --json --robot`
  - one proof/eval artifact per promoted skill
- Rollback conditions: revert individual skill metadata/eval additions; keep core doctor contract.
- Linear mapping: one child per skill family.
- Agent-safe: assisted.
- Human review required: yes.

## Linear Mapping

No Linear issue is assumed in this artifact.

Recommended mapping if Jamie promotes this program:

- Parent: Agent Skills Kit professional skill SDK readiness program.
- RF-1 child: Harden `skills doctor` contract fixtures for `context7`.
- RF-2 child: Add negative-path readiness matrix.
- RF-3 child: Add profile and freshness determinism.
- RF-4 child: Wire coding-harness as schema consumer.
- RF-5 child: Add review-feedback intent-radius and pattern-sweep contract.
- RF-6 children: Migrate high-value HE/factory skills.

## Anti-Regression Constraints

- Do not hand-edit runtime projections such as `.agents/**`, `.skillsets/**`, `skills-codex/**`, or `Plugins/cache/**`.
- Do not let package readiness count as outcome proof.
- Do not let harness parse `SKILL.md` bodies to infer readiness.
- Do not treat stale memory as current proof.
- Do not let a warning status imply release readiness unless the selected profile explicitly permits it.
- Do not add SDK metadata requirements to draft skills unless a maturity rule says they are required.
- Preserve `next_command` as always present and nullable only when no safe command exists.
- Do not apply principle-shaped review feedback only to the named line without classifying intent radius and sweeping the bounded scope.
- Do not generalize feedback across a repository when the comment is genuinely local, compatibility-bound, or semantically different.

## Eval Requirements

Expected closure proof path:

```text
.harness/evals/2026-05-17-agent-skills-skill-sdk-doctor-trust-eval.md
```

Minimum eval content:

- baseline doctor output for `context7`;
- package-readiness output for `context7`;
- one pass fixture, one warning fixture, and one blocked fixture;
- negative-path fixture table for source, runtime, package, proof, validation, freshness, and cross-consumer drift;
- review-feedback fixture table for local-only comments, API design rules, repeated patterns, public API deferrals, and durable guidance updates;
- exact commands run and pass/fail/blocked outcomes;
- reviewer signoff or explicit coverage gaps.

## Success Criteria

- RF-1 passes with stable doctor JSON fixture assertions.
- `next_command`, `operation_context`, and `contract_schemas` are present in every status class.
- Runtime blockers, package metadata gaps, and missing proof remain separate in output.
- Freshness behavior is deterministic and profile-owned.
- Harness has a clear consumer contract before any cross-repo implementation begins.
- Review feedback that expresses a design rule produces intent classification, bounded sweep evidence, similar-case disposition, and durable-rule action.
- Final reports preserve exact command evidence and classify blocked states honestly.

## Safe Rollback Conditions

Rollback is safe if any of these occur:

- doctor contract hardening requires broad rewrites before RF-1 proves value;
- required fields cannot be produced without reading skill internals in harness;
- freshness policy creates non-deterministic readiness outcomes;
- draft authoring becomes blocked by published-skill ceremony;
- package/eval/proof signals cannot remain separate.
- intent-radius enforcement causes broad churn or makes local review fixes slower without catching repeated design-rule issues.

Rollback path:

1. Keep the north-star strategy as product direction.
2. Remove or disable the latest RF phase changes.
3. Preserve failing fixtures as evidence debt.
4. Re-run the previous passing doctor/package/profile/event commands.
5. Re-enter `he-reframe` with the failed assumption named explicitly.

## Future-Agent Guidance

- Treat this as a migration program, not implementation permission.
- Start with RF-1 and hand it to `he-plan`.
- Use `context7` because it is non-mutating and already exposes useful readiness contradictions.
- Keep Agent Skills Kit as SDK contract owner and coding-harness as control-pane consumer.
- Preserve exact blocker classes from commands instead of translating them into generic failure text.
- Treat reviewer comments as evidence, not automatically as scope; classify intent before deciding whether to fix one line or sweep a broader pattern.
- If a reviewer or tool stalls, classify it as runtime evidence gap rather than pretending approval.
- Before closeout, write the eval artifact or document why closure proof is blocked.

## Related Systems

- `.harness/strategy/2026-05-17-agent-skills-sdk-north-star.md`
- `UBIQUITOUS_LANGUAGE.md`
- `Docs/agents/14-path-ownership-boundaries.md`
- `Docs/product/agent-capability-control-plane.md`
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md`
- `Infrastructure/scripts/lib/ask/commands/skills_impl.py`
- `Infrastructure/tests/test_ask_cli_impl.py`
- `Plugins/harness-engineering/skills/he-reframe/SKILL.md`
- `Plugins/harness-engineering/references/skills/he-reframe/reframe-program-contract.md`
