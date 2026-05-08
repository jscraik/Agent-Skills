# Agent Skills Linear Execution Plan

## Executive Linear Routing Summary

This plan routes the harness cognition layer into a small Linear execution surface.

Linear must not become the architecture memory system. The `.harness/**` files remain the source of architectural intent, review evidence, strategy, invariants, and refactor safety. Linear should track only executable slices with owners, sequencing, validation gates, and closure proof.

Primary routing decision:

| Work type | Destination | Reason |
|---|---|---|
| Repo-specific architecture/refactor/eval work | `agent-skills` project | The findings are about this repository's command plane, skill lifecycle, repo cognition, and governance checks. |
| Cross-repo operating model, reporting, shared hygiene | `Portfolio Ops` project | Only portfolio-wide standards or shared workflow hygiene belong here. |
| Portfolio-level visibility | `Dev Portfolio` initiative | Attach major repo execution slices for visibility; do not create a new initiative. |

Recommended active set:

| Window | Linear objects |
|---|---|
| Now | 1 repo milestone, 1 parent issue, 2 sub-issues, plus 1 parallel proof taxonomy ADR issue. |
| Next | Proof-driven skill promotion and agent-first golden path. |
| Later | Repository cognition burn-down and governance compression after the command plane is less fragile. |
| Do Not Create | Any issue that merely repeats a review finding without execution proof, owner, or validation gate. |

## Target Linear Destination

| Classification | Target | Applies to | Confidence | Notes |
|---|---|---|---|---|
| Repo-specific work | `agent-skills` project | Ask control plane, skill promotion, repo doctor, catalog parity, cognition burn-down, governance checks | High | Existing project pattern says `<repo-name>` is the repo control surface. |
| Cross-repo work | `Portfolio Ops` project | Shared labels, portfolio reporting, cross-repo reactivation checklist, shared Linear hygiene | Medium | Only use for shared portfolio operations, not repo refactors. |
| Top-level initiative | `Dev Portfolio` | Parent container for visible repo work | High | Existing operating model already fits the work. |

Do not create a new Linear initiative. `Dev Portfolio` is sufficient.

Do not create a new Linear project if an `agent-skills` project already exists. If execution later discovers that no matching project exists, confirm before creating one.

Review decisions applied:

| Decision | Selected path | Impact |
|---|---|---|
| Initial active set | Ask decomposition plus proof taxonomy ADR | Keeps execution small while unblocking both structural and lifecycle semantics. |
| Repo project assumption | Use `agent-skills` | Treats the matching repo project as the destination for all repo-specific work. |
| Label policy | Minimal new labels | Adds only repeated-use architecture/eval/refactor labels if they are absent and approved. |

## Existing Project Match

| Expected Linear project | Status assumption | Recommendation | Reactivation posture |
|---|---|---|---|
| `agent-skills` | Existing repo-specific project | Use as the execution container | Reactivate only with the first milestone active. |
| `Portfolio Ops` | Existing cross-repo project | Use for portfolio hygiene only | Keep active set tiny; avoid cross-repo process work unless it reduces execution ambiguity. |
| `Dev Portfolio` | Existing initiative | Attach the repo milestone for visibility | No new initiative. |

## Proposed Milestones

| Object type | Name/title | Target project | Parent initiative | Priority | Labels | Execution route | Blocks | Blocked by | Source artifacts | Reason |
|---|---|---|---|---|---|---|---|---|---|---|
| Milestone | Ask Control Plane Decomposition | `agent-skills` | `Dev Portfolio` | 1 | Architecture, Refactor, Drift-Risk, Developer Experience | Agent-assisted, human-review required | Proof gates that would otherwise deepen `skills.py`; golden-path command routing | None | `.harness/refactors/ask-control-plane-decomposition.md`, `.harness/triage/agent-skills-triage.md`, `.harness/strategy/agent-skills-strategy.md` | The overgrown `./bin/ask` skills command plane is the first structural bottleneck. |
| Milestone | Proof-Driven Skill Core | `agent-skills` | `Dev Portfolio` | 2 | Eval, Governance, Agent-Native | Agent-assisted, human-review required | Trusted/default-visible skill promotion; proof-backed lifecycle gates | Proof taxonomy ADR | `.harness/refactors/proof-driven-skill-promotion.md`, `.harness/core/moat-invariants.md` | Skill trust is moat-critical only if promotion is evidence-backed. |
| Milestone | Agent First Golden Path | `agent-skills` | `Dev Portfolio` | 2 | Agent-Native, Developer Experience, Reliability | Agent-assisted | Agent onboarding compression; deterministic repo operation loop | Ask control-plane boundary clarification | `.harness/refactors/agent-first-golden-path.md`, `.harness/core/agent-operating-rules.md` | Future agents need a single obvious loop: doctor, route, execute, prove, close out. |
| Milestone | Repository Cognition Burn-Down | `agent-skills` | `Dev Portfolio` | 2 | Drift-Risk, Governance, Refactor | Agent-assisted, human-review required for deletions | Lower context load and safer skill discovery | Classification pass | `.harness/refactors/repository-cognition-burndown.md`, `.harness/core/cognition-principles.md` | Tracked stale/generated/history surfaces are becoming cognition debt. |
| Milestone | Governance Compression | `agent-skills` | `Dev Portfolio` | 3 | Governance, Reliability, Drift-Risk | Agent-assisted, human-review required | Required-check simplification; deprecation budgets | Governance inventory | `.harness/refactors/governance-compression.md`, `.harness/core/governance-invariants.md` | Governance must reduce ambiguity, not multiply ceremonial checks. |

## Proposed Parent Issues

### Issue 1

| Field | Value |
|---|---|
| Object type | Parent issue |
| Name/title | `[agent-skills] Decompose skills command module into bounded services` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | Ask Control Plane Decomposition |
| Priority | 1 |
| Labels | Architecture, Refactor, Drift-Risk, Developer Experience |
| Execution route | Agent-assisted; human-review required for public command contract changes |
| Blocks | Proof implementation in skills commands; golden-path routing changes |
| Blocked by | None |
| Source artifacts | `.harness/refactors/ask-control-plane-decomposition.md`; `.harness/core/architecture-invariants.md`; `.harness/core/routing-invariants.md` |
| Reason | Reduces the largest structural bottleneck before adding more governance or proof behavior. |

```markdown
## Objective
Reduce the `./bin/ask` skills command plane from a large mixed-responsibility command module into bounded services with stable command behavior.

## Source Artifacts
- .harness/refactors/ask-control-plane-decomposition.md
- .harness/triage/agent-skills-triage.md
- .harness/strategy/agent-skills-strategy.md
- .harness/core/architecture-invariants.md
- .harness/core/routing-invariants.md

## Why This Matters
The command plane is the repo's product spine. If it remains a mixed abstraction level module, future agent changes will amplify hidden coupling, increase regression risk, and make proof-driven promotion harder.

## Scope
- Map current skills command responsibilities.
- Extract bounded services only where existing behavior proves the boundary.
- Preserve `./bin/ask` and `--json --robot` contracts.
- Add drift guardrails for new feature logic in over-threshold command modules.

## Out of Scope
- New skill features.
- Broad CLI redesign.
- New plugin architecture.
- Changing runtime projection ownership.

## Execution Notes
Start with responsibility mapping and behavior characterization. Extract one bounded service at a time. Do not create abstraction before moving an existing responsibility behind it.

## Validation Gates
- Build/Test/Lint gates from repo wrapper where applicable.
- `./bin/ask repo doctor --json --robot`
- Existing skill list/audit command behavior preserved.
- Eval artifact: `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md`

## Rollback Conditions
Stop or revert the active extraction if command output changes without an intentional contract update, if robot output becomes unstable, or if a compatibility path is added without an expiry condition.

## Linear Routing
Project: agent-skills
Milestone: Command surface and ask reliability
HE slice: Ask Control Plane Decomposition
Labels: architecture, Refactor, Agent
Priority: 1
Blocks: Proof-driven skill promotion implementation; agent-first routing changes
Blocked by: None
```

### Issue 2

| Field | Value |
|---|---|
| Object type | Parent issue |
| Name/title | `[agent-skills] Define and enforce proof-backed skill promotion` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | Proof-Driven Skill Core |
| Priority | 2 |
| Labels | Eval, Governance, Agent-Native |
| Execution route | Agent-assisted; human-review required for lifecycle taxonomy |
| Blocks | Trusted/default-visible promotion; proof-backed skill routing |
| Blocked by | Proof taxonomy ADR; avoid deep implementation until command plane boundaries are stable |
| Source artifacts | `.harness/refactors/proof-driven-skill-promotion.md`; `.harness/core/moat-invariants.md`; `.harness/core/execution-invariants.md` |
| Reason | The skill catalog becomes defensible only when trust and visibility depend on proof, not volume. |

```markdown
## Objective
Define a durable proof taxonomy and use it to govern skill promotion, trusted/default-visible status, and proof-backed closeout.

## Source Artifacts
- .harness/refactors/proof-driven-skill-promotion.md
- .harness/strategy/agent-skills-strategy.md
- .harness/core/moat-invariants.md
- .harness/core/execution-invariants.md

## Why This Matters
Skill volume is not a moat. Skill reliability, outcome proof, and repeatable promotion are the defensible parts.

## Scope
- Create proof taxonomy and lifecycle state ADR.
- Mark core skills with explicit proof status.
- Define promotion gates for trusted/default-visible skills.
- Pilot proof capture on a small set of core skills.

## Out of Scope
- Mass reclassification of every skill.
- New eval framework before taxonomy is accepted.
- Promotion gates that bypass existing command contracts.

## Execution Notes
Keep this initially ADR-first and proof-model-first. Implementation should wait for command-plane boundaries where it would otherwise deepen `skills.py`.

## Validation Gates
- Proof taxonomy accepted.
- Pilot skills show evidence-backed proof state.
- Promotion gates have deterministic failure behavior.
- Eval artifact: `.harness/evals/agent-skills-proof-driven-skill-promotion-eval.md`

## Rollback Conditions
Stop if proof states become subjective labels without observable evidence, or if promotion gates block work without actionable remediation.

## Linear Routing
Project: agent-skills
Milestone: Proof-Driven Skill Core
Labels: Eval, Governance, Agent-Native
Priority: 2
Blocks: Trusted/default-visible skill promotion
Blocked by: Proof taxonomy ADR
```

### Issue 3

| Field | Value |
|---|---|
| Object type | Parent issue |
| Name/title | `[agent-skills] Make repo doctor and skill routing the canonical agent loop` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | Agent First Golden Path |
| Priority | 2 |
| Labels | Agent-Native, Developer Experience, Reliability |
| Execution route | Agent-assisted; human-review required for agent-facing contract changes |
| Blocks | Agent onboarding compression; deterministic closeout loop |
| Blocked by | Ask control-plane boundary clarity for skills command changes |
| Source artifacts | `.harness/refactors/agent-first-golden-path.md`; `.harness/core/agent-operating-rules.md`; `.harness/core/cognition-principles.md` |
| Reason | The repo is only agent-native if the operating loop is obvious and machine-readable. |

```markdown
## Objective
Make `repo doctor`, skill routing, execution proof, and closeout the canonical agent loop.

## Source Artifacts
- .harness/refactors/agent-first-golden-path.md
- .harness/core/agent-operating-rules.md
- .harness/core/cognition-principles.md
- .harness/core/routing-invariants.md

## Why This Matters
Future agents need a deterministic first move and a deterministic completion standard. Otherwise the repo's cognition layer becomes advisory instead of operational.

## Scope
- Add next-action output to repo doctor where appropriate.
- Compress skill improvement routing to one primary path.
- Align explain/prove/closeout commands.
- Generate and validate agent-first onboarding from live contracts.

## Out of Scope
- New onboarding essays.
- Non-deterministic prompt routing.
- Creating separate agent workflows that bypass `./bin/ask`.

## Execution Notes
Prefer small command contract improvements over new documentation. Human review is required for changes that alter agent-facing behavior.

## Validation Gates
- `./bin/ask repo doctor --json --robot`
- Skill routing smoke checks.
- Changed-file closeout gate proves validation posture.
- Eval artifact: `.harness/evals/agent-skills-agent-first-golden-path-eval.md`

## Rollback Conditions
Stop if next-action output becomes noisy, non-deterministic, or disconnected from actual executable commands.

## Linear Routing
Project: agent-skills
Milestone: Agent First Golden Path
Labels: Agent-Native, Developer Experience, Reliability
Priority: 2
Blocks: Agent onboarding compression
Blocked by: Ask control-plane boundary clarity
```

### Issue 4

| Field | Value |
|---|---|
| Object type | Parent issue |
| Name/title | `[agent-skills] Classify, quarantine, and reduce tracked cognition debt` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | Repository Cognition Burn-Down |
| Priority | 2 |
| Labels | Drift-Risk, Governance, Refactor |
| Execution route | Agent-assisted; human-review required before deletion/quarantine |
| Blocks | Lower context load; safer future agent discovery |
| Blocked by | Initial artifact classification |
| Source artifacts | `.harness/refactors/repository-cognition-burndown.md`; `.harness/core/cognition-principles.md`; `.harness/core/anti-drift-principles.md` |
| Reason | Historical and generated artifacts should not compete with current source-of-truth surfaces. |

```markdown
## Objective
Classify tracked non-source surfaces, quarantine stale/generated/history artifacts, and prevent new unclassified cognition debt.

## Source Artifacts
- .harness/refactors/repository-cognition-burndown.md
- .harness/triage/agent-skills-triage.md
- .harness/core/cognition-principles.md
- .harness/core/anti-drift-principles.md

## Why This Matters
Future agents pay token and reasoning cost for every stale surface that looks authoritative.

## Scope
- Classify tracked non-source surfaces.
- Resolve `.skillsets/**` ownership.
- Quarantine raw historical artifacts where appropriate.
- Remove tracked runtime state and stale generated reports where safe.
- Add guardrails against new unclassified tracked artifacts.

## Out of Scope
- Deleting canonical source.
- Rewriting docs for style.
- Mass cleanup without ownership classification.

## Execution Notes
Inventory can run early. Deletion and quarantine require human review because the risk is losing durable project memory.

## Validation Gates
- Classification manifest exists.
- No canonical source removed without replacement.
- Discovery surfaces get smaller or clearer.
- Eval artifact: `.harness/evals/agent-skills-repository-cognition-burndown-eval.md`

## Rollback Conditions
Stop if a removed/quarantined artifact was referenced by a live command, installer, validator, or skill discovery path.

## Linear Routing
Project: agent-skills
Milestone: Repository Cognition Burn-Down
Labels: Drift-Risk, Governance, Refactor
Priority: 2
Blocks: Context-load reduction
Blocked by: Initial artifact classification
```

### Issue 5

| Field | Value |
|---|---|
| Object type | Parent issue |
| Name/title | `[agent-skills] Map, compress, and enforce governance by proof target` |
| Target project | `agent-skills` |
| Parent initiative | `Dev Portfolio` |
| Milestone | Governance Compression |
| Priority | 3 |
| Labels | Governance, Reliability, Drift-Risk |
| Execution route | Agent-assisted; human-review required before check removal |
| Blocks | Reduced governance overhead; clearer release safety |
| Blocked by | Governance inventory and required-check ownership map |
| Source artifacts | `.harness/refactors/governance-compression.md`; `.harness/core/governance-invariants.md`; `.harness/core/execution-invariants.md` |
| Reason | Governance must prove outcomes and reduce ambiguity; otherwise it becomes architecture debt. |

```markdown
## Objective
Inventory governance checks, map each to an owner and proof target, remove or demote low-value checks, and block new governance without measurable leverage.

## Source Artifacts
- .harness/refactors/governance-compression.md
- .harness/core/governance-invariants.md
- .harness/core/execution-invariants.md
- .harness/core/anti-drift-principles.md

## Why This Matters
The repo has enough governance surface that process can become a substitute for proof. Compression protects velocity and reliability.

## Scope
- Inventory checks, validators, compatibility paths, and ownership.
- Create required-check ownership map.
- Add deprecation budgets for compatibility layers.
- Prune or demote checks without proof target.
- Guard new governance checks with owner/proof/failure-action requirements.

## Out of Scope
- Removing required checks without replacement proof.
- Adding new governance categories.
- Portfolio-wide process redesign.

## Execution Notes
Start with inventory. Change enforcement only after ownership and proof target are explicit.

## Validation Gates
- Required-check ownership map exists.
- No required check lacks owner, proof target, and failure action.
- Deprecated compatibility paths have expiry.
- Eval artifact: `.harness/evals/agent-skills-governance-compression-eval.md`

## Rollback Conditions
Stop if a removed check was the only active guard for release safety, projection safety, or skill packaging integrity.

## Linear Routing
Project: agent-skills
Milestone: Governance Compression
Labels: Governance, Reliability, Drift-Risk
Priority: 3
Blocks: Governance simplification
Blocked by: Governance inventory
```

## Proposed Sub-Issues

| Parent | Sub-issue title | Priority | Execution route | Can run in parallel | Validation gate | Recommended timing |
|---|---|---:|---|---|---|---|
| `[agent-skills] Decompose skills command module into bounded services` | `[agent-skills] Map skills command responsibilities and output contracts` | 1 | Agent-safe, human review optional | No | Responsibility map plus robot-output baseline | Now |
| `[agent-skills] Decompose skills command module into bounded services` | `[agent-skills] Extract plugin cache service behind existing behavior` | 2 | Agent-assisted | No | Existing plugin-cache command behavior preserved | Now, after map |
| `[agent-skills] Decompose skills command module into bounded services` | `[agent-skills] Extract skill catalog and projection services` | 2 | Agent-assisted, human-review required | No | Catalog/projection parity checks | Next |
| `[agent-skills] Decompose skills command module into bounded services` | `[agent-skills] Extract proof and tool-resolution services` | 2 | Agent-assisted, human-review required | No | Proof/tool resolution behavior preserved | Next |
| `[agent-skills] Decompose skills command module into bounded services` | `[agent-skills] Add skills command module drift guard` | 3 | Agent-safe | Yes | Guard fails on new feature logic in over-threshold command module | Later in milestone |
| `[agent-skills] Define and enforce proof-backed skill promotion` | `[agent-skills] Write proof taxonomy and lifecycle ADR` | 1 | Agent-assisted, human-review required | Yes | ADR accepted before enforcement | Now if parallel ADR approved |
| `[agent-skills] Define and enforce proof-backed skill promotion` | `[agent-skills] Add proof-level labels to core skill metadata` | 2 | Agent-assisted | No | Pilot core skill proof states documented | Next |
| `[agent-skills] Define and enforce proof-backed skill promotion` | `[agent-skills] Gate trusted skill promotion on proof state` | 2 | Agent-assisted, human-review required | No | Promotion failure is deterministic and actionable | Next |
| `[agent-skills] Make repo doctor and skill routing the canonical agent loop` | `[agent-skills] Add repo doctor next-action robot output` | 2 | Agent-assisted | Soft parallel | `repo doctor --json --robot` stable | Next |
| `[agent-skills] Make repo doctor and skill routing the canonical agent loop` | `[agent-skills] Compress skills improve into one primary route` | 2 | Agent-assisted, human-review required | No | One clear skill-improvement route | Next |
| `[agent-skills] Classify, quarantine, and reduce tracked cognition debt` | `[agent-skills] Classify tracked non-source cognition surfaces` | 2 | Agent-safe | Yes | Classification manifest | Next |
| `[agent-skills] Classify, quarantine, and reduce tracked cognition debt` | `[agent-skills] Resolve .skillsets ownership and catalog parity` | 2 | Agent-assisted, human-review required | No | Catalog parity and ownership checks | Next |
| `[agent-skills] Map, compress, and enforce governance by proof target` | `[agent-skills] Inventory governance checks and required-check ownership` | 3 | Agent-safe | Yes | Ownership map | Later |
| `[agent-skills] Map, compress, and enforce governance by proof target` | `[agent-skills] Add governance deprecation budget` | 3 | Agent-assisted, human-review required | No | Compatibility paths have expiry | Later |

## Now / Next / Later / Do Not Create

| Bucket | Work | Linear shape | Why |
|---|---|---|---|
| Now | Ask Control Plane Decomposition | 1 milestone, 1 parent, first 2 sub-issues | Highest structural leverage and blocks safer proof/golden-path implementation. |
| Now | Proof taxonomy and lifecycle ADR | 1 sub-issue under Proof-Driven Skill Core | ADR can clarify promotion semantics without deepening the command module. |
| Next | Proof-Driven Skill Core implementation | 1 milestone, 1 parent, 2-3 sub-issues | Moat-critical but safer after taxonomy and command boundaries. |
| Next | Agent First Golden Path | 1 milestone, 1 parent, 2-3 sub-issues | High leverage for future agents, but should not fight command-plane migration. |
| Next | Repository Cognition Burn-Down classification | 1 parent plus classification/ownership sub-issues | Reduces context cost; deletion waits for classification. |
| Later | Governance Compression | 1 parent plus inventory/deprecation sub-issues | Important, but premature until proof/control-plane boundaries stabilize. |
| Do Not Create | New `Dev Portfolio` initiative | None | Existing initiative is sufficient. |
| Do Not Create | New repo project if `agent-skills` exists | None | Project sprawl weakens routing. |
| Do Not Create | One issue per architecture-review finding | None | Creates issue explosion without execution leverage. |
| Do Not Create | Broad portability/adapters | None | Strategy says local-first until proof justifies portability. |
| Do Not Create | Catalog expansion work | None | Skill volume is not the moat. |
| Do Not Create | New governance checks without owner/proof/failure action | None | Governance growth without proof is drift. |
| Do Not Create | Cosmetic docs cleanup | None | Does not reduce execution ambiguity unless linked to a live contract. |

## Dependency Map

| Work item | Dependency type | Blocks | Blocked by | Sequential or parallel | Notes |
|---|---|---|---|---|---|
| Ask control-plane responsibility map | Migration | All deeper command extraction | None | Sequential first | Establishes behavior baseline. |
| Plugin cache service extraction | Migration | Later service extractions | Responsibility map | Sequential | First bounded extraction should prove pattern. |
| Skill catalog/projection services | Migration | Catalog parity and ownership work | Plugin cache extraction | Sequential | Touches discovery/projection boundaries. |
| Proof taxonomy ADR | Governance/eval | Proof labels and promotion gates | None | Parallel with mapping | ADR work can run without code migration. |
| Proof promotion gates | Eval | Trusted/default-visible promotion | Proof taxonomy; command boundaries | Sequential | Must not add gate sprawl into current command plane. |
| Repo doctor next-action output | Routing | Agent-first golden path | Ask control-plane boundary clarity | Soft sequential | Can start after command contract risks are understood. |
| Cognition surface classification | Drift | Deletion/quarantine | None | Parallel | Inventory only; no deletion yet. |
| `.skillsets/**` ownership resolution | Architecture | Catalog parity and context reduction | Classification | Sequential | Requires source-of-truth decision. |
| Governance inventory | Governance | Check pruning/deprecation | None | Parallel | Inventory can happen without changing checks. |
| Governance pruning | Governance/release | Reduced process overhead | Ownership map | Sequential | Human review required. |

## Eval Gate Map

| Milestone | Required gates | Eval artifact | Closure rule |
|---|---|---|---|
| Ask Control Plane Decomposition | Build/test/lint where touched; command output baseline; `./bin/ask repo doctor --json --robot`; skill list/audit smoke checks; robot output stability | `.harness/evals/agent-skills-ask-control-plane-decomposition-eval.md` | Do not close until behavior parity and reduced command-module responsibility are proven. |
| Proof-Driven Skill Core | Proof taxonomy ADR; pilot skill proof states; deterministic promotion failure behavior; no trusted/default-visible promotion without proof | `.harness/evals/agent-skills-proof-driven-skill-promotion-eval.md` | Do not close until at least one core skill promotion path is evidence-backed. |
| Agent First Golden Path | `repo doctor` next-action output; skill routing smoke checks; closeout validation evidence; agent-facing docs generated from live contract | `.harness/evals/agent-skills-agent-first-golden-path-eval.md` | Do not close until a future agent can follow the loop without reading review documents. |
| Repository Cognition Burn-Down | Classification manifest; source-of-truth preservation; context surface reduction; no live command references broken | `.harness/evals/agent-skills-repository-cognition-burndown-eval.md` | Do not close until stale/generated/history surfaces are clearly separated from current contracts. |
| Governance Compression | Required-check ownership map; owner/proof/failure action for every blocking check; deprecation budgets; no release-safety regression | `.harness/evals/agent-skills-governance-compression-eval.md` | Do not close until governance surface is smaller or more deterministic with proof. |

Gate categories used:

| Category | Applied where | Notes |
|---|---|---|
| Build/Test/Lint | Code-touching issues | Use repo wrappers; do not invent root package-manager commands. |
| Eval | Every milestone | Eval artifact required before milestone closure. |
| Architecture Drift | All refactor programs | Check for new orchestration, new hidden routing, or compatibility paths without expiry. |
| Routing Determinism | Ask control plane, golden path | Robot output and routing decisions must remain explainable. |
| Context Load | Cognition burn-down, golden path | Must reduce or clarify surfaces, not add more docs. |
| Agent Discoverability | Golden path, proof core | Future agents must find the correct route quickly. |
| Rollback | Every parent issue | Stop conditions must be explicit before implementation. |

## Human vs Agent Execution Map

| Work item | Execution classification | Human review required | Why |
|---|---|---|---|
| Responsibility mapping | Agent-safe | No | Read-only characterization and baseline capture. |
| First bounded service extraction | Agent-assisted | Yes if public output changes | Low-risk if behavior preserved; contract changes need review. |
| Proof taxonomy ADR | Agent-assisted | Yes | Defines strategic lifecycle semantics. |
| Proof labels for pilot skills | Agent-assisted | Yes for final taxonomy application | Affects trust model. |
| Repo doctor next-action output | Agent-assisted | Yes | Changes agent-facing behavior. |
| Cognition classification | Agent-safe | No | Inventory only. |
| Artifact deletion/quarantine | Agent-assisted | Yes | Risk of deleting useful memory/source surfaces. |
| Governance inventory | Agent-safe | No | Read-only map. |
| Governance pruning/check demotion | Human-review required | Yes | Could weaken release or projection safety. |
| Creating/updating Linear objects | Agent-assisted after approval | Yes | User explicitly asked to confirm before creation. |

## Recommended Labels

Existing labels to use:

| Label | Use |
|---|---|
| Developer Experience | Agent/human workflow clarity, command ergonomics. |
| Reliability | Validation, deterministic execution, release safety. |
| Governance | Checks, process, ownership, anti-drift enforcement. |
| Automation | Generated outputs, sync flows, proof capture where automation is involved. |

Recommended additional labels, only if not already available and approved:

| Label | Why existing labels are insufficient | Use frequency |
|---|---|---|
| Architecture | Separates structural boundary work from general developer experience. | Repeated across all refactor programs. |
| Agent-Native | Tracks routing/context/workflow work specifically for future agents. | Repeated in proof and golden-path work. |
| Eval | Tracks proof and closure artifacts distinctly from generic reliability. | Required across all milestones. |
| Refactor | Identifies migration programs where behavior preservation matters. | Repeated across structural simplification work. |
| Drift-Risk | Flags anti-entropy work that prevents future architectural decay. | Repeated across cognition and governance work. |

Do not create one-off labels such as `Moat-Critical`, `Context`, or `Routing` unless execution later shows repeated filtering need. Use milestone names and issue descriptions for those concepts first.

## Priority Mapping

| Priority | Meaning in this plan | Applied to |
|---:|---|---|
| 1 | Urgent: blocks safe structural execution or prevents high-confidence migration | Ask Control Plane Decomposition; responsibility map; proof taxonomy ADR if activated now |
| 2 | High: moat-critical or high-leverage, but not the first blocker | Proof-Driven Skill Core; Agent First Golden Path; Repository Cognition Burn-Down |
| 3 | Normal: valuable once higher-risk architecture is stabilized | Governance Compression |
| 4 | Low: supporting cleanup with clear but non-urgent value | Only later sub-issues, not parent programs |
| 0 | No priority: parking only | Do not use for the proposed active set |

## Project Reactivation Recommendation

| Project | Recommendation | Active-set limit | Rationale |
|---|---|---|---|
| `agent-skills` | Keep active for the next command-surface slice under `Command surface and ask reliability` | Keep to 1 active milestone and 1 active parent issue for the next `$he-spec` handoff | `Ask Control Plane Decomposition` is complete in Linear; the next slice should preserve the same small-active-set discipline. |
| `Portfolio Ops` | Do not reactivate solely for this repo plan | 0-1 coordination issue only if needed | Cross-repo work is not needed to start repo execution. |
| `Dev Portfolio` | Use as parent initiative only | No new initiative | Existing initiative represents the repo execution surface. |

Recommended current active objects after Linear delta refresh:

| Object | Activate now? | Reason |
|---|---|---|
| Milestone: Command surface and ask reliability / slice: Agent First Golden Path | Yes | This is the next unresolved command-surface slice after `JSC-284` closed. |
| Parent: `JSC-246` `[agent-skills] Build repo surface contract and agent capability control-plane golden paths` | Yes | Single admitted parent issue for the next `$he-spec` handoff. |
| Prior parent: `JSC-284` `[agent-skills] Decompose skills command module into bounded services` | No; keep closed | Completed with children `JSC-285`, `JSC-286`, and `JSC-287`; do not reopen for new work. |
| Existing in-progress track: `JSC-230` Commandable Skill Trees | Do not fold into this slice | Already has its own active parent/child topology; folding it into `JSC-246` would blur ownership. |

## Portfolio Ops Items

| Object type | Name/title | Target project | Parent initiative | Priority | Labels | Execution route | Blocks | Blocked by | Source artifacts | Reason |
|---|---|---|---|---:|---|---|---|---|---|---|
| Optional coordination issue | `[Portfolio Ops] Standardize repo project reactivation checklist` | `Portfolio Ops` | `Dev Portfolio` | 3 | Governance, Developer Experience | Agent-assisted, human-review required | Cleaner multi-repo reactivation | None | This plan; `.harness/triage/agent-skills-triage.md` | Only create if multiple repos are being reactivated with the same pattern. |

Do not create the Portfolio Ops issue unless another repo needs the same reactivation workflow. For this repository alone, it is process overhead.

## Dev Portfolio Impact

| Impact | Recommendation |
|---|---|
| Portfolio visibility | Attach the `Ask Control Plane Decomposition` milestone or parent issue under `Dev Portfolio`. |
| Initiative creation | Do not create a new initiative. |
| Project creation | Do not create a new project if `agent-skills` exists. |
| Active/dormant/completed classification | Mark `agent-skills` active only for the chosen milestone. Keep other milestones planned/backlog. |
| Reporting | Report milestone closure only after eval artifact exists. |

## Evidence & Traceability Matrix

| Conclusion | Evidence type | File paths | Symbols/interfaces/components involved | Runtime behaviour observed | Confidence | Why it matters |
|---|---|---|---|---|---|---|
| Use `agent-skills` as the repo execution project | User operating model; repo naming pattern | Current prompt; `.harness/refactors/*.md` Linear Mapping sections | Linear project pattern `<repo-name>` | Not queried live; plan-only assumption | High | Prevents creating duplicate repo projects. |
| Use `Dev Portfolio` as the initiative | User operating model | Current prompt; `.harness/refactors/*.md` Linear Mapping sections | Dev Portfolio initiative | Not queried live; plan-only assumption | High | Avoids initiative sprawl. |
| Use `Portfolio Ops` only for cross-repo coordination | User operating model | Current prompt | Portfolio Ops project | Not queried live; plan-only assumption | High | Keeps repo refactors out of shared workflow noise. |
| Start with Ask Control Plane Decomposition | Triage; strategy; refactor program | `.harness/triage/agent-skills-triage.md`; `.harness/strategy/agent-skills-strategy.md`; `.harness/refactors/ask-control-plane-decomposition.md` | `./bin/ask`, skills command plane, robot output | Prior artifacts identify command plane as first structural bottleneck | High | This is the highest-leverage blocker before deeper proof or routing work. |
| Proof-driven promotion is moat-critical but should be staged | Strategy; core invariants; refactor program | `.harness/strategy/agent-skills-strategy.md`; `.harness/core/moat-invariants.md`; `.harness/refactors/proof-driven-skill-promotion.md` | Skill lifecycle, trusted/default-visible promotion, eval artifacts | Prior artifacts identify proof as promotion requirement | High | Skill volume is not defensible without evidence-backed trust. |
| Agent-first golden path belongs after command boundary clarity | Refactor program; core operating rules | `.harness/refactors/agent-first-golden-path.md`; `.harness/core/agent-operating-rules.md`; `.harness/core/routing-invariants.md` | `repo doctor`, skill routing, closeout loop | Prior artifacts require deterministic agent loop | High | Avoids adding new routing behavior into an unstable command plane. |
| Repository cognition burn-down should start with classification, not deletion | Refactor program; cognition principles | `.harness/refactors/repository-cognition-burndown.md`; `.harness/core/cognition-principles.md`; `.harness/core/anti-drift-principles.md` | `.skillsets/**`, tracked generated/history surfaces | Prior artifacts identify cognition debt; no live deletion performed | High | Prevents future agents from losing real memory while reducing noise. |
| Governance compression is valuable but not first active work | Refactor program; governance invariants | `.harness/refactors/governance-compression.md`; `.harness/core/governance-invariants.md`; `.harness/core/execution-invariants.md` | Required checks, validators, compatibility paths | Prior artifacts identify governance overhead risk | Medium-high | Governance changes can weaken safety if done before ownership map. |
| Every milestone requires eval proof before closure | Refactor programs; execution invariants | `.harness/refactors/*.md`; `.harness/core/execution-invariants.md` | `.harness/evals/<repo>-<milestone>-eval.md` | Eval files are required by refactor programs, not yet generated | High | Prevents Linear from closing architecture work on intent alone. |
| Do not create one issue per finding | Triage; current prompt | `.harness/triage/agent-skills-triage.md`; current prompt | Linear backlog shape | Plan-only routing decision | High | Prevents issue explosion and review-document entropy. |
| `.harness/decisions` is absent in this repository snapshot | File-system evidence | `.harness/decisions` | Decision artifacts | `find` reported `No such file or directory` before plan generation | High | The plan cannot cite decision artifacts that do not exist. |

## Creation Confirmation Gate

Initial plan state: no Linear objects were created by the plan alone.

Current tracker state: Linear objects were later created during the `$he-spec` tracker gate, then reconciled onto the canonical existing `agent-skills` project. Live delta refresh now shows `JSC-284`, `JSC-285`, `JSC-286`, and `JSC-287` are complete; the next admitted issue is `JSC-246`.

Review confirmation received for this plan:

1. Route repo-specific work to the `agent-skills` Linear project.
2. Use minimal reusable labels rather than an expanded specialty-label set.
3. Make the initial active set `Ask Control Plane Decomposition` plus the proof taxonomy ADR.

Before any Linear mutation, still confirm the explicit create/update action and the exact objects to be created.

Final workflow decision (after the subsequent `$he-spec` flow):

- Initial review selected `Plan only`.
- During the subsequent `$he-spec` flow, the Linear tracker gate was corrected and the minimal active set was created:
  - `JSC-284` parent: `[agent-skills] Decompose skills command module into bounded services`
  - `JSC-285` child: `[agent-skills] Map skills command responsibilities and output contracts`
  - `JSC-286` child: `[agent-skills] Extract plugin cache service behind existing behavior`
  - `JSC-287` child: `[agent-skills] Write proof taxonomy and lifecycle ADR`
- During Linear hygiene follow-up, the duplicate project `e6ad5ea3-28b0-4b07-b2e0-594ec1b9242f` was canceled and the issue set was moved to canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`.

## Approved Current Slice

The only slice admitted for the current HE Spec lane is:

| Field | Value |
|---|---|
| Slice type | Parent issue plus bounded command-surface spec slice |
| Project | `agent-skills` |
| Project ID currently holding issues | `791c2f12-5ffb-4644-8421-f4216ac6d805` |
| Linear milestone | `Command surface and ask reliability` |
| HE slice name | `Agent First Golden Path` |
| Parent issue | `JSC-246` |
| Child issues | None admitted yet; `$he-spec` should decide whether child issues are required after spec review. |
| Selected refactor | `.harness/refactors/agent-first-golden-path.md` |
| Parallel decision slice | None admitted for this handoff. |
| Execution route | Agent-assisted; human-review required for public command contract and agent-facing workflow changes. |
| Planning blocker | None from Linear tracker hygiene; `$he-spec` should start from `JSC-246` and avoid folding in `JSC-230`, `JSC-167`, or `JSC-169` unless explicitly re-approved. |

No other review, strategy, triage, or Linear issue is admitted into this slice.

## Linear Delta Capture

Last synced: `2026-05-08` after live Linear refresh.

Source: Live Linear project query for `agent-skills`, canonical project `791c2f12-5ffb-4644-8421-f4216ac6d805`, milestone `Command surface and ask reliability`, completed parent `JSC-284`, completed child issues `JSC-285`, `JSC-286`, and `JSC-287`, and unresolved command-surface candidates in the same project.

Label status: `resolved_with_existing_labels`; no Linear label mutation is required for the next slice.

| Issue | Title | Status | Priority | Classification | Reason |
|---|---|---|---:|---|---|
| Milestone | `Command surface and ask reliability` | Active; progress `37.5%` | n/a | already_covered | Correct milestone exists in the canonical project and remains the right container for the next command-surface slice. |
| JSC-284 | `[agent-skills] Decompose skills command module into bounded services` | Done | 1 | already_covered | Prior approved parent is complete; keep as evidence, not active scope. |
| JSC-285 | `[agent-skills] Map skills command responsibilities and output contracts` | Done | 1 | already_covered | Completed child of `JSC-284`; remove from next-slice queue. |
| JSC-286 | `[agent-skills] Extract plugin cache service behind existing behavior` | Done | 2 | already_covered | Completed child of `JSC-284`; remove from next-slice queue. |
| JSC-287 | `[agent-skills] Write proof taxonomy and lifecycle ADR` | Done | 1 | already_covered | Completed child of `JSC-284`; remove from next-slice queue. |
| JSC-246 | `Build repo surface contract and agent capability control-plane golden paths` | Todo | 2 | candidate_next_slice | Best next `$he-spec` target: unresolved, in the canonical project, in the active command-surface milestone, and directly maps to the planned Agent First Golden Path slice. |
| JSC-167 | `Harden ask bootstrap and command discoverability` | Backlog | 2 | candidate_next_slice | Valid later command-surface work, but narrower than `JSC-246` and not admitted while only one slice may advance. |
| JSC-169 | `Refactor ask to lazy-load command dependencies by topic` | Backlog | 2 | candidate_next_slice | Valid later architecture work, but should follow or be explicitly scoped by the `JSC-246` spec rather than bypass it. |
| JSC-230 | `Implement Commandable Skill Trees for rooted skill handles` | In Progress | 2 | already_covered | Separate active parent with its own child topology; do not merge into this handoff. |
| JSC-231 | `Generate command-surface projection from rooted manifests` | In Progress | 2 | already_covered | Child of `JSC-230`; already owned by the commandable-skill-tree track. |
| JSC-232 | `Generate thin runtime stubs for command-visible skill handles` | In Progress | 2 | already_covered | Child of `JSC-230`; already owned by the commandable-skill-tree track. |
| JSC-233 | `Expose public ask handle and reviewer resolver commands` | In Progress | 2 | already_covered | Child of `JSC-230`; already owned by the commandable-skill-tree track. |
| JSC-234 | `Add handle proof commands and artifact schema` | Todo | 2 | already_covered | Child of `JSC-230`; keep in that parent rather than duplicating into `JSC-246`. |
| JSC-235 | `Add rooted command-handle regression tests` | Todo | 2 | already_covered | Child of `JSC-230`; keep in that parent rather than duplicating into `JSC-246`. |
| JSC-236 | `Prove workspace/user sync and live Codex handle invocation` | In Progress | 2 | already_covered | Child of `JSC-230`; already owned by the commandable-skill-tree track. |
| JSC-168 | `Add reproducible Python environment contract for ask CLI` | Backlog | 2 | needs_human_triage | May support command reliability, but it is environment-contract work and should not enter the golden-path spec without explicit approval. |
| JSC-170 | `Fix Robot mode alias behavior to match documented examples` | Backlog | 2 | needs_human_triage | Potentially related to agent UX, but narrower than the admitted golden-path slice. |
| JSC-174 | `Add ask start fast lane for first-contact agent workflows` | Backlog | 3 | needs_human_triage | May become a child of the golden-path program after spec review; do not admit before boundary definition. |
| JSC-175 | `Split ask output profiles for humans vs agents` | Backlog | 4 | out_of_scope | Useful output polish, but not the next structural slice. |

## Approved Next Slice Queue

| Order | Slice | Linear Issue | Route | Depends On | Notes |
|---:|---|---|---|---|---|
| 1 | Agent First Golden Path spec | JSC-246 | Agent-assisted; human-review required for public command contract changes | `JSC-284` closure evidence; live Linear delta refresh | This is the single admitted next slice for `$he-spec`. Scope it to repo surface contract and golden-path control-plane behavior, not all pending command-surface tickets. |
