---
schema_version: 1
artifact_id: agent-skills-harness-trace-ledger-strategy
artifact_type: he-strategy-strategic-compression
canonical_slug: agent-skills-harness-trace-ledger
title: Agent Skills Harness Trace Ledger Strategy
harness_stage: he-strategy
status: active
date: 2026-05-10
traceability_required: false
origin: user-provided-harness-trace-ledger-full-pipeline-request
linear_issue: ""
linear_milestone: ""
---

# Agent Skills Harness Trace Ledger Strategy

## Executive Strategic Summary

The Harness Trace Ledger should become the smallest shared truth surface for a
meaningful Harness Engineering run.

The strategic move is not to create a dashboard, a broad memory platform, or a
new lifecycle stage. It is to make the existing HE lifecycle produce one
validated receipt that ties together:

```text
request -> issue/source -> spec/plan -> media -> tasks -> files -> validation
        -> session evidence -> PR -> heartbeat continuation state
```

The ledger is valuable because it addresses a concrete HE failure mode: future
agents currently have to reconstruct run state from chat, scattered `.harness`
Markdown, generated image caches, session bundles, validation prose, and PR
bodies. That reconstruction is expensive and unsafe. A small ledger makes the
work inspectable, lintable, and resumable without pretending chat memory is
durable state.

Recommendation:

```text
Adopt Harness Trace Ledger as an active-run traceability spine.
Start with one per he-phase-heartbeat collector bundle.
Promote to a cross-run index only after the active-run shape is validated.
```

This artifact is a strategy output only. It does not authorize implementation.
The next executable step should be an `he-spec` or `he-plan` artifact that
defines the first proof-producing slice.

## Selected Mode

User request:

```text
[$he-strategy] full pipeline
```

Selected HE strategy mode:

```yaml
selected_mode: strategic-compression
full_pipeline_lenses_applied:
  - intent
  - architecture-review
  - triage
  - strategic-compression
  - decision-compression
  - core-compression
```

Reason:

- The user asked for the full pipeline, but the output contract supports a
  bounded strategic-compression artifact.
- A single strategy artifact is enough to preserve the decision, risks, first
  slice, and future-agent guidance.
- Separate intent, triage, ADR, and core files would add artifact weight before
  the ledger contract has proof.

## Source Artifacts Read

| Source | Inspection Method | Evidence Use |
| --- | --- | --- |
| User-provided Harness Trace Ledger proposal | direct prompt input | Defined the target idea, proposed JSON shape, stage ownership, media handling, PR loop, builder, and validator. |
| `UBIQUITOUS_LANGUAGE.md` | direct read | Confirmed canonical source/projection language and that running a skill means executing its workflow, not reading the handle only. |
| `Plugins/harness-engineering/skills/he-strategy/SKILL.md` | direct read | Confirmed strategy is cognition compression, not implementation authority, and full pipeline requests may apply multiple lenses. |
| `Plugins/harness-engineering/skills/he-strategy/references/strategy-output-contract.md` | direct read | Confirmed required sections, artifact naming, and strategic-compression scope. |
| `Plugins/harness-engineering/skills/he-strategy/references/contract.yaml` | direct read | Confirmed `he-strategy` inputs, outputs, observability expectations, non-goals, and authority rules. |
| `Plugins/harness-engineering/references/first-principles-contract.md` | direct read | Confirmed new HE surfaces must prevent a verified failure, reduce drift, improve proof, or reduce future-agent reasoning load. |
| `Plugins/harness-engineering/references/agent-native-audit-scorecard.md` | direct read | Confirmed shared truth surface and deterministic completion are blocking dimensions for agent-facing workflows. |
| `Plugins/harness-engineering/references/xp-operating-contract.md` | direct read | Confirmed smallest feedback-producing slice, stop or pivot condition, and stale heartbeat stop behavior. |
| `Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md` | prior targeted read | Confirmed heartbeat already checks collector evidence and must stop on missing or stale evidence. |
| `Plugins/harness-engineering/skills/he-phase-heartbeat/references/phase-gate-contract.md` | prior targeted read | Confirmed collector bundle file expectations and phase gate reporting. |
| `Plugins/harness-engineering/references/session-evidence-contract.md` | prior targeted read | Confirmed normalized session collector evidence is preferred over raw transcript scanning. |
| `Plugins/harness-engineering/references/session-evidence-trace-context.md` | prior targeted read | Confirmed trace context should resolve repo, branch, PR, Linear, artifact chain, bundle path, time range, and redaction status. |
| `Plugins/harness-engineering/references/artifact-routing-contract.md` | prior targeted read | Confirmed `.harness` artifact identity, stable `canonical_slug`, dated filenames, and handoff evidence expectations. |
| `.harness/media/harness-media-guidance.md` | prior targeted read | Confirmed generated planning images should keep source cache files, copy selected PNGs into `.harness/media`, create sidecars, and reference repo copies. |
| `Plugins/harness-engineering/skills/he-plan/SKILL.md` | prior targeted read | Confirmed planning owns durable plan and handoff artifacts. |
| `Plugins/harness-engineering/skills/he-work/SKILL.md` | prior targeted read | Confirmed implementation handoffs already require traceability, validation, blockers, and safe-to-continue state. |
| `.harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md` | direct read | Confirmed adjacent HE strategy already favors active-artifact proof and warns against broad, unlinted artifact indexes. |
| `.harness/strategy/agent-skills-strategy.md` | direct read | Confirmed repo strategy values a small proof-backed local control plane and warns against raw artifact sprawl. |

## Fact / Interpretation / Assumption

Fact:

- `he-phase-heartbeat` already has a collector-evidence requirement and should
  stop rather than continue when evidence is absent or stale.
- Existing HE contracts already require stable artifact identity, canonical
  slugs, session evidence context, handoff evidence, and validation outcomes.
- The local media guidance already says generated HE images should be copied
  into `.harness/media` with sidecar Markdown instead of relying only on the
  generated image cache.
- `he-work` already requires proof-oriented handoff fields, but there is no
  single machine-readable run receipt tying tasks, created artifacts, session
  evidence, media, validation, PR state, and heartbeat state together.
- Existing strategic guidance warns that broad artifact indexes and raw
  artifact sprawl become false authority when they are not linted or scoped.

Interpretation:

- The Harness Trace Ledger is strategically stronger than an "Agent Work
  Ledger" name because it covers more than work performed by agents. It also
  covers media, PR traceability, session evidence, source context, and heartbeat
  safety.
- The first useful ledger should be scoped to the active collector bundle, not
  global repository history.
- The ledger should be built and validated by deterministic scripts wherever
  possible. An agent may propose or append deltas, but the closure signal should
  not depend on the agent narrating that evidence exists.
- Media handling belongs to `he-plan` as creator, `he-phase-heartbeat` as gate,
  and `he-work` as consumer and carrier.
- PR traceability should be bidirectional: ledger points to PR, and PR body
  points back to the ledger and core HE artifacts.

Assumption:

- The user wants this strategy to become the basis for a later HE spec or plan,
  not for immediate implementation in this turn.
- No Linear issue is currently selected for this strategy artifact, so the
  artifact remains untracked by Linear and `traceability_required` is false.
- The first implementation can tolerate `pr_status: pending` until a PR exists,
  as long as pending is explicit and linted.
- Deep links to local session evidence may not always be available, so the
  ledger should require session IDs and source paths while allowing deep links
  to be optional.

## Affected Systems And Modules

Directly affected by a future implementation:

- `Plugins/harness-engineering/skills/he-plan/SKILL.md`
- `Plugins/harness-engineering/skills/he-phase-heartbeat/SKILL.md`
- `Plugins/harness-engineering/skills/he-work/SKILL.md`
- `Plugins/harness-engineering/references/artifact-routing-contract.md`
- `Plugins/harness-engineering/references/session-evidence-contract.md`
- `Plugins/harness-engineering/references/session-evidence-trace-context.md`
- `.harness/media/**`
- `.harness/session-evidence/he-phase-heartbeat/**`

New surfaces likely needed:

- `Plugins/harness-engineering/references/harness-trace-ledger-contract.md`
- `Plugins/harness-engineering/references/media-artifact-contract.md`
- `Plugins/harness-engineering/scripts/build_harness_trace_ledger.py`
- `Infrastructure/scripts/validation-and-linting/he_harness_trace_ledger_lint.py`

Adjacent surfaces:

- PR body templates or PR closeout guidance, if the repo decides to enforce
  Harness Traceability sections in PR descriptions.
- `he-code-review` or PR closeout guidance, if PR status and checks become
  ledger fields that must be refreshed before closure.

## Full Pipeline Compression

### Intent Lens

The ledger's purpose is to preserve the story of a run in one durable, bounded,
machine-readable artifact.

The user value is direct:

- future agents know what happened;
- humans can inspect what evidence supports continuation;
- recurring heartbeats cannot coast on chat memory;
- PRs can be traced back to the exact HE plan, media, tasks, validation, and
  session evidence that produced them.

The stable interface should be:

```text
.harness/session-evidence/he-phase-heartbeat/<run-id>/harness-trace-ledger.json
```

This keeps the first version close to the collector bundle that already gates
`he-phase-heartbeat`.

### Architecture Review Lens

The right architecture is a layered evidence chain:

```text
raw sessions
  -> normalized collector bundle
  -> Harness Trace Ledger
  -> heartbeat and PR decisions
```

Do not invert this relationship. The ledger should not replace collector
evidence, raw sessions, Markdown plans, media sidecars, validation output, or PR
state. It should point to them and summarize their traceability status.

The ledger should be:

- generated or refreshed deterministically where possible;
- narrow to one active run first;
- linted before heartbeat continuation can claim safety;
- explicit when fields are pending, unavailable, blocked, or stale;
- free of raw transcript text and secrets;
- small enough for future agents to read without broad context loading.

Risky architecture moves:

- global cross-run indexing before active-run proof exists;
- letting LLM-authored prose become the only validation source;
- embedding raw transcript excerpts in the ledger;
- treating missing PR links as failure before a PR is expected;
- making every HE stage own ledger orchestration instead of giving each stage a
  small, stage-specific responsibility.

### Triage Lens

Strategic risks:

- Without the ledger, HEARTBEAT decisions can drift from actual artifact,
  media, validation, and PR state.
- Without media traceability, planning infographics can stay in local generated
  image caches and disappear from repo-readable HE evidence.
- Without PR traceability, PRs become the shipping surface but not the
  explanation surface.

Operational risks:

- Builder/validator complexity can outgrow the benefit.
- PR status is drift-prone and needs refresh semantics, not permanent truth
  claims.
- The first implementation could accidentally create broad historical indexing
  work.

Governance risks:

- Another artifact contract can become ceremony unless it blocks a real false
  continuation or reduces future-agent context load.
- If every stage is told to maintain the full ledger, ownership will blur.

Deletion or collapse candidates:

- A separate "agent work ledger" should collapse into this Harness Trace Ledger.
- A dashboard should be deferred until the ledger shape is proven and consumed.
- A global historical `.harness` artifact index should be rejected for the first
  slice.

### Strategic Compression Lens

Core thesis:

```text
HE needs one active-run receipt that is small enough to validate and complete
enough to stop unsafe continuation.
```

Actual moat:

- proof-backed local control plane;
- durable shared truth surface;
- deterministic continuation gates;
- future-agent resumability;
- bidirectional PR and HE artifact traceability.

False moat signals:

- more stage names;
- more Markdown artifacts without linted links;
- broad indexes that cannot block or unblock decisions;
- PR body prose that is not checked against repo artifacts;
- media files present in caches but absent from `.harness/media`.

Non-negotiables:

- A heartbeat must not claim healthy continuation when the ledger, collector
  bundle, required media, or required validation evidence is missing.
- Implementation may continue by explicit user instruction, but the ledger must
  preserve the separate truth that recurring heartbeat health is blocked.
- Generated or selected planning media must be repo-readable under
  `.harness/media` when it supports a plan.
- PR fields must be either real or explicitly pending, never silently omitted.
- Validation outcomes must be exact command/tool outcomes or explicit blocked
  reasons.

### Decision Compression Lens

This strategy does not create an ADR yet.

ADR candidate if the first slice proves useful:

```text
ADR: Adopt Harness Trace Ledger As Active-Run HE Traceability Spine
```

ADR trigger:

- `he-phase-heartbeat` consumes the ledger in at least one real run, and
  missing or invalid ledger evidence changes a continuation decision.

Do not write the ADR before that proof. Until then, this strategy is enough.

### Core Compression Lens

Potential future core invariant:

```text
Harness Engineering continuation depends on durable evidence, not chat memory.
```

This could later live under `.harness/core/**` only if multiple HE stages
consume the ledger and the invariant proves stable. For now, keep it inside the
strategy and future spec/plan artifacts.

## First Principles Check

```yaml
first_principles_check:
  verified_failure: "HE evidence exists across plans, media, session bundles, validation, PRs, and heartbeat state without one compact validated run receipt."
  fundamental_constraint: "Future agents need a small repo-readable truth surface before they can safely continue, review, or trace work."
  assumption_being_challenged: "More HE stages or more Markdown prose would solve traceability."
  smallest_effective_mechanism: "One active-run harness-trace-ledger.json plus a contract, builder, validator, and stage ownership rules."
  analogy_or_template_rejected: "A broad dashboard or global memory platform."
  proof_required: "A heartbeat fixture where missing or invalid ledger evidence blocks recurring continuation, plus a passing fixture where linked media/session/PR state is accepted."
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed
```

## Agent-Native Audit

```yaml
agent_native_scorecard_status: partial
scorecard_dimensions:
  action_parity: partial
  capability_discovery: partial
  context_injection: pass
  shared_truth_surface: pass
  entity_completion: partial
  integration_feedback: partial
  prompt_native_composability: pass
  deterministic_completion: partial
scorecard_evidence: "Strategy inspected HE contracts, heartbeat/session evidence contracts, media guidance, work/plan stage duties, and existing HE strategy artifacts."
scorecard_blocks_closure: no
scorecard_required_action: "Future spec must define builder, validator, and heartbeat evals before claiming agent-native readiness."
```

Interpretation:

- The idea is agent-native because it creates a shared truth surface and reduces
  chat-only state.
- Readiness remains partial because no builder, validator, heartbeat output
  field, or eval case exists yet.

## Recommended Shape

Ledger path:

```text
.harness/session-evidence/he-phase-heartbeat/<run-id>/harness-trace-ledger.json
```

Minimum root fields:

```json
{
  "schema_version": 1,
  "ledger_id": "...",
  "canonical_slug": "...",
  "repo": "...",
  "branch": "...",
  "source": {},
  "session_evidence": {},
  "media_artifacts": [],
  "tasks": [],
  "pull_requests": [],
  "heartbeat": {}
}
```

Stage ownership:

| Stage | Ownership |
| --- | --- |
| `he-plan` | Starts the ledger when planning closes, records spec/plan source context, stores planning infographic PNG and sidecar in `.harness/media`, records media in handoff. |
| `he-phase-heartbeat` | Checks collector bundle, ledger status, required media, required validation, and PR trace when expected; blocks recurring continuation when invalid. |
| `he-work` | Consumes plan and media links, implements approved task, emits a task delta with changed files, created artifacts, validation, blockers, and safe-to-continue state. |
| `he-code-review` or PR closeout | Validates PR body and ledger agree, refreshes PR URL/status/checks/review state, and preserves links to Linear/spec/plan/media/session evidence. |

Media rule:

```text
If he-plan creates or selects a planning infographic:
1. keep the original image in /Users/jamiecraik/.codex/generated_images/
2. copy the selected PNG into .harness/media/
3. create .harness/media/<same-name>.md sidecar
4. add both paths to the Harness Trace Ledger
5. include both paths in post_plan_handoff
```

PR traceability rule:

```text
Ledger points to PR.
PR body points to ledger.
Plan, media sidecar, eval, and review artifacts carry pending or real PR fields
when the lifecycle stage owns that refresh.
```

## Smallest Feedback-Producing Next Slice

Create an `he-spec` for the active-run ledger only.

The spec should require:

1. `harness-trace-ledger-contract.md`
2. `media-artifact-contract.md`
3. `he_harness_trace_ledger_lint.py`
4. `build_harness_trace_ledger.py`
5. `he-phase-heartbeat` output fields:
   - `harness_trace_ledger`
   - `ledger_status`
   - `media_artifacts`
   - `pr_trace_status`
6. Three heartbeat eval cases:
   - missing ledger blocks heartbeat;
   - explicit user proceed allows implementation but not heartbeat health;
   - created docs and media are linked.

Do not include:

- a dashboard;
- global historical indexing;
- automatic PR mutation;
- Linear mutation;
- broad migration of old `.harness` artifacts.

## Stop Or Pivot Condition

Stop if:

- the first slice requires scanning every historical `.harness` artifact;
- the ledger cannot be linted without LLM judgment;
- heartbeat cannot distinguish "work may continue by explicit user request"
  from "recurring heartbeat is healthy";
- media support requires inventing a new stage instead of adding a shared media
  contract and `he-plan` handoff responsibility;
- PR traceability requires live GitHub mutation before the repo has a PR
  closeout owner.

Pivot to a narrower active-artifacts index if:

- the ledger shape becomes too large for one run;
- PR fields prove too drift-prone for heartbeat gating;
- media sidecars are useful but not universally available at planning time.

## Drift And Moat Impact

Positive drift impact:

- Reduces future-agent context loading.
- Makes missing evidence visible instead of narratable.
- Keeps media artifacts from living only in generated-image caches.
- Lets heartbeat block for concrete missing proof.
- Makes PRs part of the evidence loop instead of an external endpoint.

Moat impact:

- Strengthens the proof-backed local control plane.
- Turns repeated HE work into inspectable operational evidence.
- Creates a small mechanism future agents can trust before reading long
  transcripts.

Negative drift risk:

- If too broad, the ledger becomes a stale artifact index.
- If too manual, agents will forget to update it.
- If too strict too early, heartbeat may block on fields that are legitimately
  pending.

Mitigation:

- First version is active-run only.
- Pending state is explicit and linted.
- Builder/validator own mechanical proof.
- Heartbeat gates only fields that the active phase should already own.

## Future-Agent Guidance

When continuing this idea:

- Start from this strategy, then write an `he-spec`; do not jump directly to
  implementation.
- Keep the first slice scoped to
  `.harness/session-evidence/he-phase-heartbeat/<run-id>/harness-trace-ledger.json`.
- Treat `.harness/media` as a durable artifact root for selected planning
  infographics.
- Treat `/Users/jamiecraik/.codex/generated_images/` as source cache, not the
  linked HE artifact path.
- Preserve the distinction between:
  - heartbeat blocked by missing evidence;
  - implementation continuing by explicit user instruction.
- Prefer deterministic builder/validator behavior over LLM-authored evidence
  claims.
- Do not create an ADR, dashboard, or global index until the active-run ledger
  affects at least one real continuation decision.

## Evidence And Traceability Matrix

| Claim | Evidence | Confidence | Impact |
| --- | --- | --- | --- |
| The ledger should be active-run scoped first. | Existing HE strategy warns against broad unlinted indexes; phase heartbeat already centers collector bundles. | High | Reduces artifact sprawl and keeps proof near the gate that uses it. |
| `he-plan` should own planning infographic storage. | Media is produced at planning closeout; `he-plan` owns durable plan handoff. | High | Prevents `he-work` from inheriting missing media. |
| `he-phase-heartbeat` should check, not create, media/ledger evidence. | Heartbeat owns scheduling/gating and stale evidence stop behavior. | High | Keeps heartbeat from becoming an artifact authoring stage. |
| PR traceability should be bidirectional but pending-aware. | PR may not exist during planning, but PR becomes the shipping surface later. | Medium | Avoids false failure before PR creation while preserving closeout traceability. |
| Builder and validator should be deterministic. | Agent-native scorecard requires deterministic completion and shared truth surfaces. | High | Prevents chat narration from becoming proof. |
| A dashboard is premature. | No consumer has proven the ledger shape yet. | High | Avoids adding UI/process before proof. |

## Validation Record

| Command | Outcome |
| --- | --- |
| `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/strategy/2026-05-10-agent-skills-harness-trace-ledger-strategy.md` | pass |
| `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/strategy/2026-05-10-agent-skills-harness-trace-ledger-strategy.md` | pass |
