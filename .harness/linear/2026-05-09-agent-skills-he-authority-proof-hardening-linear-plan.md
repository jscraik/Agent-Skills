---
schema_version: 1
artifact_id: agent-skills-he-authority-proof-hardening-linear-plan
artifact_type: he-linear-plan
canonical_slug: agent-skills-he-authority-proof-hardening
title: HE Authority And Proof Hardening Linear Plan
harness_stage: he-linear-plan
status: active
date: 2026-05-09
traceability_required: false
origin: .harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md
linear_issue: ""
linear_milestone: "HE Authority And Proof Hardening"
---

# HE Authority And Proof Hardening Linear Plan

## Executive Linear Routing Summary

Route this work to the existing `agent-skills` Linear project as a small
repo-specific execution slice. Do not create new initiatives, projects, labels,
or Linear objects from this artifact without explicit post-plan approval.

The source strategy and refactor program both say the same thing: fix current
trust defects before adding new HE stages. Linear should therefore track the
smallest executable slice first, not the full roadmap.

Recommended active set:

| Window | Linear objects |
| --- | --- |
| Now | 1 milestone, 1 parent issue, 4 minimal sub-issues |
| Next | 2 parent issues, sequenced after Now proves clean release/eval behavior |
| Later | Routed threat model/tool audit/parallel-agent capability |
| Do Not Create | Universal threat modeling, full historical `.harness` indexing, automatic Linear mutation, one issue per observation |

Payload status:

- ready-to-create plan data only;
- no Linear mutation performed;
- destination confidence is high for repo-specific work and medium for exact
  project active/backlog state because no live Linear connector lookup was
  requested in this step.

```yaml
linear_mutation_status: confirmation_required
live_linear_blocker: "No explicit post-plan approval was provided for live Linear mutation, and live project/milestone state was not refreshed in this step."
required_confirmation: "Confirm creation of the HE Authority And Proof Hardening milestone, Parent Issue 1, and the four Phase 1 sub-issues in the agent-skills project before any live Linear write."
ready_to_create_payload_status: unapplied
live_objects_created_or_updated: []
```

## Target Linear Destination

| Classification | Target | Applies To | Confidence | Reason |
| --- | --- | --- | --- | --- |
| Repo-specific work | `agent-skills` project | HE plugin skills, HE scripts, HE eval/release gates, repo `.harness` proof artifacts | High | The affected systems all live in this repository. |
| Cross-repo work | `Portfolio Ops` | Shared HE policy only if this later becomes a portfolio-wide standard | Low for this slice | Current evidence is repo-local. |
| Top-level initiative | `Dev Portfolio` | Visibility parent for repo execution | Medium | Existing operating model in prior Linear plan uses `Dev Portfolio`; no new initiative is justified. |

Do not route this slice to `Portfolio Ops` unless future evidence shows the
same authority/proof hardening must be applied across multiple repos.

## Existing Project Match

| Expected Linear object | Match Decision | Recommendation | Reactivation Posture |
| --- | --- | --- | --- |
| `agent-skills` project | Expected existing repo control surface | Use for all `Now` and `Next` repo work | Reactivate only for the `Now` milestone if currently inactive. |
| `Portfolio Ops` project | Existing cross-repo control surface | Do not use for this first slice | Keep out unless shared standards are admitted later. |
| `Dev Portfolio` initiative | Existing portfolio container | Attach milestone for visibility only if project practice requires it | Do not create a new initiative. |

## Source Prompt Coverage

This Linear plan consumes the upstream strategy and refactor program. It
therefore inherits their authority limits and confidence downgrades rather than
claiming complete repo-wide execution coverage.

```yaml
source_prompt_status: summarized
evidence_depth: representative
coverage_scope: subsystem
claim_scope: slice
coverage_gaps:
  - gap: "The original user roadmap is represented through the upstream strategy and refactor artifacts, not preserved verbatim in this Linear plan."
    impact: "The plan can safely route the HE authority/proof hardening slice, but it must not claim full source-prompt equivalence or repo-wide closure."
    blocks_downstream_authority: no
not_inspected:
  - evidence_class: "live Linear project, milestone, issue, and label state"
    impact: "Ready-to-create payloads require confirmation and live refresh before mutation."
  - evidence_class: "current CI and PR status"
    impact: "Validation gates remain planned until the selected issue is implemented."
authority_limited_to:
  - allowed_claim: "execution-disciplined Linear plan for the selected HE authority/proof hardening slice"
    forbidden_claim: "live Linear objects exist, implementation is approved, or the broader HE roadmap is tracked"
repo_specific_drift_signals:
  - signal: "silent local-plan stop when live Linear is expected"
    severity: high
    indicator: "ready-to-create payloads can be mistaken for applied Linear state"
    corrective_action: "record linear_mutation_status and require explicit post-plan confirmation before live mutation"
    blocks: "claiming live tracker coverage"
  - signal: "issue explosion"
    severity: high
    indicator: "roadmap bands could become one issue per observation"
    corrective_action: "create only one Now parent issue and four Phase 1 sub-issues; classify later work as Next/Later/Do Not Create"
    blocks: "broad Linear creation"
  - signal: "evidence-depth laundering"
    severity: high
    indicator: "closure or plugin confidence can be claimed before eval gates exist"
    corrective_action: "make eval artifact and release/eval gates closure blockers"
    blocks: "Linear completion and milestone closure"
original_prompt_coverage: partial
downstream_confidence: medium
next_route: continue
```

## Proposed Milestones

| Object type | Name/title | Target project | Parent initiative | Priority | Labels | Execution route | Blocks | Blocked by | Source artifacts | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Milestone | HE Authority And Proof Hardening | `agent-skills` | `Dev Portfolio` | 2 | Architecture, Agent-Native, Eval, Governance, Refactor, Drift-Risk | Agent-assisted; human-review required | HE plugin confidence claims, broader risk capability, future parallel-agent workflows | None for Phase 1 | `.harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md`; `.harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md` | Converts HE authority and closure proof from prose trust toward measurable gates. |

Milestone scope:

- Fix current hard trust defects first.
- Make release/eval failure modes deterministic.
- Do not add new HE stages inside the first execution slice.

Out of scope:

- Creating `he-threat-model`.
- Creating `he-tool-audit`.
- Building parallel-agent execution workflows.
- Full historical `.harness` artifact indexing.
- Mutating Linear from HE skills.

## Proposed Parent Issues

### Parent Issue 1: Now

| Field | Value |
| --- | --- |
| Object type | Parent issue |
| Name/title | `[agent-skills] Repair HE trust defects before new capability` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | HE Authority And Proof Hardening |
| Priority | 2 |
| Labels | Eval, Governance, Reliability, Agent-Native |
| Execution route | Agent-assisted; human-review required |
| Blocks | Measurable `he-work` authority; active proof infrastructure; routed HE risk capability |
| Blocked by | None |
| Source artifacts | `.harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md`; `.harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md` |
| Reason | Current trust defects undermine later plugin confidence and should be repaired before new capability. |

```markdown
## Objective
Repair current HE trust defects before adding new lifecycle stages, risk
capability, or broader artifact/evidence infrastructure.

## Source Artifacts
- .harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md
- .harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md

## Why This Matters
The HE plugin cannot honestly claim production-grade lifecycle confidence while
packaging hygiene, eval closure blocking, ask-missing degraded behavior, or
router sample execution can fail ambiguously.

## Scope
- Fix packaging hygiene gate failures.
- Ensure he-eval-report blocks closure when required side-effect validators are
  missing or not-run.
- Make lifecycle release evals fail cleanly when ask is unavailable.
- Make router sample execution skip/failure semantics blocking when sample
  execution is required.

## Out of Scope
- he-threat-model.
- he-tool-audit.
- parallel-agent workflows.
- full .harness historical indexing.
- Linear mutation.
- broad trigger/authority fixture rollout beyond what is needed for this trust
  defect repair.

## Execution Notes
Start with the current failing or ambiguous gates. Preserve existing HE closure
doctrine; harden the enforcement path rather than redesigning the lifecycle.

## Validation Gates
- `python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json`
- focused he-eval-report validator test for not-run side-effect validators
- lifecycle release eval runner degraded-mode test for missing ask
- router sample skip/fail test
- `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/evals/YYYY-MM-DD-agent-skills-he-authority-proof-hardening-eval.md`
- `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/evals/YYYY-MM-DD-agent-skills-he-authority-proof-hardening-eval.md`

## Rollback Conditions
Stop or revert the active change if the runner cannot distinguish environment
unavailability from skill failure, or if a new gate blocks unrelated lifecycle
work without actionable diagnostics.

## Linear Routing
Project: agent-skills
Milestone: HE Authority And Proof Hardening
Labels: Eval, Governance, Reliability, Agent-Native
Priority: 2
Blocks: measurable HE authority and proof hardening
Blocked by: none
```

### Parent Issue 2: Next

| Field | Value |
| --- | --- |
| Object type | Parent issue |
| Name/title | `[agent-skills] Make HE routing and work authority measurable` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | HE Authority And Proof Hardening |
| Priority | 2 |
| Labels | Architecture, Agent-Native, Refactor, Drift-Risk |
| Execution route | Agent-assisted; human-review required |
| Blocks | Active proof infrastructure and later risk capability |
| Blocked by | Parent Issue 1 |
| Source artifacts | `.harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md` |
| Reason | Removes subjective `tiny and low risk` authority and route ambiguity after current trust defects are repaired. |

### Parent Issue 3: Next

| Field | Value |
| --- | --- |
| Object type | Parent issue |
| Name/title | `[agent-skills] Add active proof gates for HE closure` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | HE Authority And Proof Hardening |
| Priority | 3 |
| Labels | Eval, Governance, Drift-Risk |
| Execution route | Agent-assisted; human-review required |
| Blocks | Routed threat model/tool audit capability |
| Blocked by | Parent Issue 1; preferably Parent Issue 2 |
| Source artifacts | `.harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md` |
| Reason | Adds only the active artifact/evidence checks needed to block known false-closure modes. |

### Parent Issue 4: Later

| Field | Value |
| --- | --- |
| Object type | Parent issue candidate |
| Name/title | `[agent-skills] Add routed HE risk capability only after proof gates` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | HE Authority And Proof Hardening or later successor milestone |
| Priority | 3 |
| Labels | Security, Agent-Native, Eval, Architecture |
| Execution route | Human-review required |
| Blocks | Nothing in the current Now slice |
| Blocked by | Parent Issues 1-3 |
| Source artifacts | `.harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md`; `.harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md` |
| Reason | Valid production-grade capability, but over-engineering before routing, authority, and proof gates exist. |

## Proposed Sub-Issues

Sub-issues for Parent Issue 1 only:

| Object type | Name/title | Target project | Parent issue | Priority | Labels | Execution route | Blocks | Blocked by | Source artifacts | Reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sub-issue | `[agent-skills] Clear HE packaging hygiene defects` | `agent-skills` | `[agent-skills] Repair HE trust defects before new capability` | 2 | Reliability, Governance | Agent-safe | Release confidence | None | Refactor Phase 1 | Packaging junk or hygiene failures undermine trust. |
| Sub-issue | `[agent-skills] Block eval closure on not-run side-effect validators` | `agent-skills` | `[agent-skills] Repair HE trust defects before new capability` | 2 | Eval, Governance | Agent-assisted | Eval closure proof | None | Refactor Phase 1 | Missing/not-run validators must not become pass-with-warning. |
| Sub-issue | `[agent-skills] Make lifecycle release evals fail cleanly when ask is unavailable` | `agent-skills` | `[agent-skills] Repair HE trust defects before new capability` | 2 | Reliability, Agent-Native | Agent-assisted | Release runner trust | None | Refactor Phase 1 | Missing command surface must be classified, not confused with skill failure. |
| Sub-issue | `[agent-skills] Treat required router sample skip as release-blocking` | `agent-skills` | `[agent-skills] Repair HE trust defects before new capability` | 2 | Eval, Agent-Native | Agent-assisted | Router/release confidence | None | Refactor Phase 1 | Skipped route samples should not silently support release confidence. |

Do not create sub-issues for Parent Issues 2-4 yet. They need a clean Phase 1
eval result first.

## Now / Next / Later / Do Not Create

| Classification | Work | Reason |
| --- | --- | --- |
| Now | Parent Issue 1 and its 4 sub-issues | Smallest feedback-producing slice; repairs hard trust defects before adding surfaces. |
| Next | Parent Issue 2 | Needed after Phase 1 to remove subjective execution authority and route ambiguity. |
| Next | Parent Issue 3 | Valuable after authority/routing gates exist; should stay active-artifact scoped. |
| Later | Parent Issue 4 | Valid but should wait until downstream proof gates can consume risk artifacts. |
| Do Not Create | Universal threat modeling for every task | Violates first-principles filter; high context cost without per-task proof value. |
| Do Not Create | Full historical `.harness` artifact index | Starts with clutter rather than active closure proof. |
| Do Not Create | Automatic Linear mutation from HE skills | Violates HE Linear mutation boundary. |
| Do Not Create | One issue per observation from the strategy/refactor | Creates backlog noise and hides execution sequencing. |
| Do Not Create | Parallel-agent execution workflow now | Requires authority, ownership, evidence, and merge-review gates first. |

## Dependency Map

| Work | Dependency Type | Blocks | Blocked By | Can Run In Parallel | Notes |
| --- | --- | --- | --- | --- | --- |
| Parent Issue 1 | blocking | Parent Issues 2-4 | none | no | Establishes trustworthy release/eval failure semantics. |
| Packaging hygiene sub-issue | soft | release confidence | none | yes | Can run alongside eval-report test if files do not overlap. |
| Eval closure sub-issue | blocking | eval report confidence | none | yes | Must prove not-run validators block completion. |
| Ask unavailable degraded-mode sub-issue | blocking | release runner confidence | none | no with router sample work if same script changes | Distinguishes environment blocker from skill failure. |
| Router sample skip sub-issue | blocking | router/release confidence | ask unavailable classification if same runner path | no if same script changes | Must not silently skip required sample execution. |
| Parent Issue 2 | migration | Parent Issue 3 | Parent Issue 1 | no | Fix trigger/authority ambiguity after hard defects are clean. |
| Parent Issue 3 | eval | Parent Issue 4 | Parent Issue 1; preferably Parent Issue 2 | yes after gates exist | Keep active artifact scope only. |
| Parent Issue 4 | governance/security | future risk capability | Parent Issues 1-3 | no | Add only if consumed downstream. |

## Eval Gate Map

| Gate | Applies To | Expected | Blocks Closure |
| --- | --- | --- | --- |
| Packaging hygiene | Parent Issue 1 | `check_packaging_hygiene.py --json` reports pass and no blocked paths | yes |
| HE eval-report validator | Parent Issue 1 | not-run required side-effect validators produce blocked/unsafe closure | yes |
| Release eval degraded mode | Parent Issue 1 | missing `ask` is classified cleanly with recovery action | yes |
| Router sample execution | Parent Issue 1 | required sample execution skip/fail blocks release confidence | yes |
| Artifact identity/frontmatter | Parent Issue 1 eval artifact | eval artifact passes identity and parser-safety lint | yes |
| Work authority threshold fixtures | Parent Issue 2 | `he-work` shortcut authority is measurable and tested | yes for Parent Issue 2 |
| Active proof gate | Parent Issue 3 | closure report cites concrete validation/tool/CI evidence or blocks | yes for Parent Issue 3 |
| Risk capability consumption | Parent Issue 4 | threat/tool risk artifact changes spec, plan, review, and eval gates | yes for Parent Issue 4 |

## Human vs Agent Execution Map

| Work | Execution Route | Human Review Required | Rationale |
| --- | --- | --- | --- |
| Parent Issue 1 | Agent-assisted | yes | Release/eval behavior affects plugin confidence claims. |
| Packaging hygiene sub-issue | Agent-safe | no unless deletion touches unexpected source | Low-risk cleanup/gate fix. |
| Eval closure sub-issue | Agent-assisted | yes | Completion semantics are closure-critical. |
| Ask unavailable degraded-mode sub-issue | Agent-assisted | yes | Runner failure semantics affect confidence reporting. |
| Router sample skip sub-issue | Agent-assisted | yes | Release gate behavior affects lifecycle confidence. |
| Parent Issue 2 | Agent-assisted | yes | Authority thresholds can over-block or under-block work. |
| Parent Issue 3 | Agent-assisted | yes | Artifact/evidence gates can create workflow friction if too broad. |
| Parent Issue 4 | Human-review required | yes | Adds or rejects new risk-stage capability. |

## Story / Value Basis

| Now Work | Operator Value | Feedback Signal | Risk Reduction |
| --- | --- | --- | --- |
| Repair HE trust defects | Jamie can trust HE release/eval outcomes before adding more plugin capability. | Packaging, eval-report, ask degraded-mode, and router sample gates return deterministic pass/fail/blocked results. | Prevents false plugin confidence and blocks completion without evidence. |

Next work has value, but it depends on Now proving the release/eval lane can
tell the truth.

## First-Principles Check

```yaml
first_principles_check:
  verified_failure: "HE authority and closure proof gaps are identified in the upstream strategy/refactor, but live execution tracking does not yet exist for the smallest repair slice."
  fundamental_constraint: "Linear should track execution state only for the smallest active work that needs sequencing, ownership, and closure proof."
  assumption_being_challenged: "Every roadmap band or observation deserves its own issue now."
  smallest_effective_mechanism: "One milestone, one Now parent issue, and four Phase 1 sub-issues; keep later bands as Next/Later payloads."
  analogy_or_template_rejected: "One issue per observation and broad portfolio governance."
  proof_required: "Phase 1 validation gates pass and an eval artifact records closure proof before later parent issues activate."
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed
```

## Recommended Labels

Use existing labels first:

- Developer Experience
- Reliability
- Governance
- Automation

Recommended additional labels only if they already exist or will be reused:

- Architecture
- Agent-Native
- Eval
- Refactor
- Drift-Risk
- Security

Do not create one-off labels for each HE phase.

## Priority Mapping

| Priority | Work |
| --- | --- |
| 1 Urgent | None from this plan unless a current HE release is actively blocked. |
| 2 High | Parent Issue 1; Parent Issue 2 |
| 3 Normal | Parent Issue 3; Parent Issue 4 candidate |
| 4 Low | Documentation-only refinements after gates pass |
| 0 No priority | Rejected observations and broad future ideas retained only in `.harness` |

## Project Reactivation Recommendation

If `agent-skills` is active:

- add the milestone and Parent Issue 1 only;
- keep Parent Issues 2-4 as planned payloads until Phase 1 closes.

If `agent-skills` is backlog/inactive:

- reactivate only for the `HE Authority And Proof Hardening` milestone;
- activate Parent Issue 1 only.

If `agent-skills` is completed:

- do not reopen the full project casually;
- create/reactivate a bounded milestone only if the user confirms this HE
  hardening is the next active repo slice.

## Portfolio Ops Items

No `Portfolio Ops` work should be created now.

Potential future `Portfolio Ops` item:

- Only after HE authority/proof hardening proves useful in `agent-skills`, draft
  a shared pattern for other repos.

Classification: Later.

## Dev Portfolio Impact

Attach the milestone to `Dev Portfolio` for visibility if the existing Linear
model requires initiative linkage.

Do not create a new top-level initiative. This is repo-specific execution, not
a separate portfolio strategy.

## Ready-To-Create Payload Summary

| Object | Create Now? | Reason |
| --- | --- | --- |
| Milestone: HE Authority And Proof Hardening | yes, after user approval | Bounded repo-specific execution container. |
| Parent Issue 1 | yes, after user approval | Smallest active execution slice. |
| Four Parent Issue 1 sub-issues | yes, after user approval | Independently verifiable trust defects. |
| Parent Issue 2 | no | Wait for Phase 1 eval. |
| Parent Issue 3 | no | Wait for Phase 1 and preferably Phase 2. |
| Parent Issue 4 | no | Later; depends on proof infrastructure. |
| New labels | no by default | Use existing labels unless missing labels are approved and reusable. |
| Portfolio Ops item | no | Repo-specific slice first. |

## Unapplied Ready-To-Create Payloads

These payloads are plan data only. They were not applied to Linear.

```yaml
milestone:
  title: "HE Authority And Proof Hardening"
  project: "agent-skills"
  initiative: "Dev Portfolio"
  priority: 2
  labels:
    - Architecture
    - Agent-Native
    - Eval
    - Governance
    - Refactor
    - Drift-Risk
  source_artifacts:
    - ".harness/strategy/2026-05-09-agent-skills-he-plugin-control-plane-hardening-strategy.md"
    - ".harness/refactors/2026-05-09-agent-skills-he-authority-proof-hardening.md"
  mutation_status: "confirmation_required"

parent_issue_now:
  title: "[agent-skills] Repair HE trust defects before new capability"
  project: "agent-skills"
  milestone: "HE Authority And Proof Hardening"
  priority: 2
  labels:
    - Eval
    - Governance
    - Reliability
    - Agent-Native
  issue_type: "improvement"
  execution_route: "agent-assisted; human-review required"
  blocked_by: []
  blocks:
    - "[agent-skills] Make HE routing and work authority measurable"
    - "[agent-skills] Add active proof gates for HE closure"
    - "[agent-skills] Add routed HE risk capability only after proof gates"
  body_sections:
    - "Problem / actual behavior: HE trust defects can leave release/eval confidence ambiguous before new capability is added."
    - "Expected behavior or decision needed: Phase 1 gates return deterministic pass/fail/blocked outcomes and closure is blocked when proof is missing."
    - "Acceptance criteria: packaging hygiene, he-eval-report validator blocking, ask-unavailable classification, router sample skip/fail behavior, and eval artifact identity/frontmatter gates pass."
    - "Source artifacts and HE stage links: strategy and refactor artifacts listed above."
  mutation_status: "confirmation_required"

sub_issues_now:
  - title: "[agent-skills] Clear HE packaging hygiene defects"
    parent: "[agent-skills] Repair HE trust defects before new capability"
    project: "agent-skills"
    priority: 2
    labels: ["Reliability", "Governance"]
    execution_route: "agent-safe"
    validation_gates:
      - "python3 Plugins/harness-engineering/scripts/check_packaging_hygiene.py --json"
    mutation_status: "confirmation_required"
  - title: "[agent-skills] Block eval closure on not-run side-effect validators"
    parent: "[agent-skills] Repair HE trust defects before new capability"
    project: "agent-skills"
    priority: 2
    labels: ["Eval", "Governance"]
    execution_route: "agent-assisted; human-review required"
    validation_gates:
      - "focused he-eval-report validator test for not-run side-effect validators"
    mutation_status: "confirmation_required"
  - title: "[agent-skills] Make lifecycle release evals fail cleanly when ask is unavailable"
    parent: "[agent-skills] Repair HE trust defects before new capability"
    project: "agent-skills"
    priority: 2
    labels: ["Reliability", "Agent-Native"]
    execution_route: "agent-assisted; human-review required"
    validation_gates:
      - "lifecycle release eval runner degraded-mode test for missing ask"
    mutation_status: "confirmation_required"
  - title: "[agent-skills] Treat required router sample skip as release-blocking"
    parent: "[agent-skills] Repair HE trust defects before new capability"
    project: "agent-skills"
    priority: 2
    labels: ["Eval", "Agent-Native"]
    execution_route: "agent-assisted; human-review required"
    validation_gates:
      - "router sample skip/fail test"
    mutation_status: "confirmation_required"
```

## Evidence & Traceability Matrix

| Conclusion | Evidence Type | Source | Confidence | Operational Impact |
| --- | --- | --- | --- | --- |
| Work routes to `agent-skills`, not `Portfolio Ops`. | source artifact | Strategy/refactor affected systems are HE plugin files and scripts in this repo. | High | Keeps execution repo-local. |
| Active set should be only Phase 1. | source artifact | Strategy `Next Stage Recommendation`; refactor `Smallest Reversible Step`. | High | Prevents roadmap explosion. |
| Parent Issue 1 should block later work. | source artifact | Refactor Phase 1 blocks confidence in release/eval semantics. | High | Avoids building new capability on untrusted gates. |
| `he-work` authority hardening is Next, not Now. | source artifact | Refactor Phase 2 depends on Phase 1 trust defect repair. | Medium | Keeps first slice smaller. |
| Threat-model/tool-audit/parallel-agent work is Later. | first-principles check | Strategy and refactor both defer new capability until proof gates consume it. | High | Prevents over-engineering. |
| No Linear mutation should occur from this skill. | skill contract | `he-linear-plan` execution boundary. | High | Preserves user approval boundary. |

## Validation Record

| Command | Outcome |
| --- | --- |
| `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md` | pass |
| `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/linear/2026-05-09-agent-skills-he-authority-proof-hardening-linear-plan.md` | pass |
| `./bin/ask skills audit Plugins/harness-engineering/skills/he-linear-plan --level strict --json --robot` | pass |
