# Governance Compression

# Refactor Classification

- governance reduction
- anti-drift hardening
- execution determinism
- Linear execution hygiene
- cognition compression
- moat reinforcement

# Problem Statement

The repository has serious governance: validation scripts, CI workflows, docs lint, repo doctor, path ownership, runtime budget, catalog parity, and harness contracts. The risk is not lack of governance. The risk is governance breadth without compressed proof semantics.

Operational issue:

- required checks can be hard to map to what they prove;
- GitHub Actions and CircleCI ownership is not self-evident;
- compatibility paths can survive without expiry;
- docs/checklists can grow instead of command/eval proof.

Future-agent issue:

- agents may patch the wrong workflow;
- agents may treat advisory checks as blocking or blocking checks as optional;
- agents may add governance language instead of measurable enforcement.

Moat risk:

Governance is only moat-reinforcing when it catches real drift without slowing execution unnecessarily. Governance breadth without proof target becomes false sophistication.

# Root Cause Analysis

Why it emerged:

- The repo accumulated real drift risks and added checks to catch them.
- Multiple providers and scripts solved local problems as they appeared.
- Compatibility layers avoided breaking users during evolution.

Why it survived:

- Checks provide real safety.
- Removing governance is risky without ownership mapping.
- Compatibility paths reduce immediate migration pressure.

Why current boundaries are insufficient:

- required-check ownership is not compressed into one current matrix;
- provider responsibilities are visible only after reading workflow files and docs;
- deprecation/compatibility paths lack consistent owner, expiry, and removal condition.

Nature of issue:

- governance and operational;
- not a CI optimization project;
- a compression and ownership project.

# Evidence

Facts:

- `.harness/review/agent-skills-architecture-review.md` flags CI provider ambiguity and governance ceremony risk.
- `.harness/triage/agent-skills-triage.md` recommends CI ownership map and deprecation budgets.
- `.harness/strategy/agent-skills-strategy.md` says new governance gates require owner, proof target, failure action, and blocking semantics.
- The strategy explicitly says governance breadth is not a strategic asset.

Interpretation:

- Governance should be kept, but compressed around proof targets and failure actions.
- Compatibility paths need expiry to avoid becoming permanent architecture.

Assumptions:

- Existing checks can be mapped before being pruned.
- Some checks may remain advisory if they have diagnostic value but no merge-blocking proof target.

# Architectural Impact

Affected systems:

- `.github/workflows/**`
- `.circleci/config.yml`
- `harness.contract.json`
- `.harness/ci-required-checks.json` if present/created
- validation scripts;
- docs describing validation;
- compatibility/legacy paths;
- Linear project hygiene.

Blast radius:

- medium-high, because CI and governance affect merge confidence.

Migration complexity:

- moderate if mapping precedes pruning.

Rollback difficulty:

- low for docs/maps;
- medium for check blocking changes.

Likely files/directories touched:

- `.github/workflows/**`
- `.circleci/config.yml`
- `harness.contract.json`
- `Docs/agents/04-validation.md`
- `Docs/agents/**`
- validation/gate scripts
- deprecation manifest if introduced.

Systems that must not be touched:

- existing required checks without mapping;
- validation semantics without proof target;
- branch protection assumptions without explicit review.

# Desired End State

Governance is smaller, sharper, and easier to operate.

Each required check has:

- owner;
- source contract;
- proof target;
- failure action;
- blocking/advisory status;
- provider;
- expected artifact or output.

Each compatibility path has:

- owner;
- caller;
- reason;
- removal condition;
- max age or review date;
- validation coverage.

Linear shape:

- few initiatives;
- projects only when sequencing is required;
- issues only for next executable slices;
- eval artifact required before parent closure.

# Migration Strategy

Sequence:

1. Build check ownership inventory without changing CI.
2. Classify each check as blocking, advisory, diagnostic, duplicate, or stale.
3. Add or update required-check ownership map.
4. Introduce deprecation budget manifest for legacy/compat paths.
5. Prune or demote redundant checks only after mapping.
6. Add guard against new governance checks without proof target.
7. Align Linear closure with eval artifacts.

Coexistence rules:

- no check removal before ownership map;
- no compatibility deletion before caller scan;
- advisory checks can remain while evidence is gathered.

Rollback strategy:

- restore check if removal causes missed failure;
- demote new blocker to advisory if false positives appear;
- keep deprecation manifest even if enforcement pauses.

Linear milestone/parent issue shape:

- milestone: `Governance Compression`
- parent issue: `Map, compress, and enforce governance by proof target`

# Execution Phases

## Phase 1 — Governance Inventory

Objective:

Inventory checks, validators, workflows, and compatibility paths.

Affected systems:

- CI workflows;
- validation scripts;
- docs.

Expected risk:

- low.

Can run in parallel:

- yes.

Validation requirements:

- no behavior change;
- inventory includes owner/proof guess/confidence.

Rollback conditions:

- none unless inventory is committed incorrectly.

Linear mapping:

- child issue: `Inventory governance checks and compatibility paths`

Agent-safe:

- yes.

Human review required:

- no for inventory, yes for classification.

## Phase 2 — Required-Check Ownership Map

Objective:

Create or update a map from checks to owner, proof target, provider, and failure action.

Affected systems:

- CI docs;
- harness contract;
- required-check metadata.

Expected risk:

- medium.

Can run in parallel:

- no.

Validation requirements:

- check-name parity;
- docs lint;
- branch/required-check names remain accurate.

Rollback conditions:

- map conflicts with actual CI behavior.

Linear mapping:

- child issue: `Create required-check ownership map`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 3 — Deprecation Budget

Objective:

Introduce owner/reason/removal-condition policy for legacy and compatibility paths.

Affected systems:

- legacy/compat scripts;
- docs;
- validation.

Expected risk:

- medium.

Can run in parallel:

- yes after inventory.

Validation requirements:

- manifest validates;
- no live caller is marked removable without evidence.

Rollback conditions:

- policy blocks urgent compatibility fixes.

Linear mapping:

- child issue: `Add deprecation budget for compatibility paths`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 4 — Prune Or Demote Governance Noise

Objective:

Remove, merge, or demote checks that lack unique proof value.

Affected systems:

- CI workflows;
- docs;
- validation scripts.

Expected risk:

- medium-high.

Can run in parallel:

- no.

Validation requirements:

- before/after check map;
- no required behavior unowned;
- representative CI validation.

Rollback conditions:

- removed check catches a real issue missed by remaining gates;
- branch protection fails due check-name drift.

Linear mapping:

- child issue: `Prune or demote governance checks without unique proof value`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 5 — Governance Drift Guard

Objective:

Prevent new gates/checks from entering without owner/proof/failure semantics.

Affected systems:

- CI docs;
- validation;
- PR/review guidance.

Expected risk:

- low-medium.

Can run in parallel:

- after ownership map.

Validation requirements:

- new-check scenario fails without ownership metadata;
- existing checks pass.

Rollback conditions:

- guard blocks legitimate workflow maintenance.

Linear mapping:

- child issue: `Guard new governance checks with proof-target metadata`

Agent-safe:

- yes.

Human review required:

- yes for blocker policy.

# Linear Mapping

Workspace/team: Jscraik

Team key: JSC

Top-level initiative: Dev Portfolio

Cross-repo project: Portfolio Ops

Repo-specific work: `agent-skills`

Target Linear project:

- `Agent Skills — Governance Compression`

Scope:

- repo-specific, with portfolio governance implications.

Belongs under `Portfolio Ops`:

- yes.

Affects `Dev Portfolio`:

- yes.

Recommended milestone:

- `Governance Compression`

Recommended parent issue title:

- `Map, compress, and enforce governance by proof target`

Recommended sub-issues:

- `Inventory governance checks and compatibility paths`
- `Create required-check ownership map`
- `Add deprecation budget for compatibility paths`
- `Prune or demote governance checks without unique proof value`
- `Guard new governance checks with proof-target metadata`

Suggested priority:

- medium-high / P2.

Suggested labels:

- `governance`
- `ci`
- `anti-drift`
- `linear-hygiene`
- `validation`

Dependencies:

- none for inventory;
- pruning depends on ownership map.

Project reactivation:

- yes if CI/check parity or governance project exists.

Active set:

- small; do not run pruning and ownership-map changes as separate broad efforts.

# Anti-Regression Constraints

Must not regress:

- security/quality coverage;
- required-check accuracy;
- branch protection expectations;
- docs validation;
- repo doctor trust.

Must not reappear:

- new checks without owner/proof target;
- compatibility paths without expiry;
- governance docs that do not change execution;
- Linear issue explosion for every check.

# Eval Requirements

Expected eval artifact:

`.harness/evals/agent-skills-governance-compression-eval.md`

Required proof:

- check ownership matrix;
- before/after CI/check list;
- deprecation manifest or equivalent;
- evidence no required check was orphaned;
- docs lint;
- validation command outcomes;
- Linear parent closure references eval artifact.

# Success Criteria

- Every required check maps to owner, provider, proof target, failure action, and blocking status.
- Compatibility paths have owner and expiry/removal condition.
- Redundant/no-proof governance is pruned or demoted.
- New governance checks cannot be added without metadata.
- Linear work remains initiative/project shaped, not finding-per-issue sprawl.

# Safe Rollback Conditions

Rollback if:

- branch protection/check names break;
- a pruned check catches unique failures;
- ownership map conflicts with actual provider behavior;
- deprecation enforcement blocks live compatibility.

Linear status if rollback is triggered:

- keep parent open;
- mark pruning/enforcement issue blocked;
- retain inventory and ownership map for correction.

# Future-Agent Guidance

Preserve:

- gates with clear proof target;
- required-check ownership;
- deprecation budgets;
- small Linear active sets.

Simplify further:

- duplicate checks;
- verbose governance docs;
- advisory checks that never inform decisions.

Intentional complexity:

- branch protection alignment;
- proof-target mapping.

Accidental complexity:

- provider lore;
- compatibility without expiry;
- checklist recursion.

Human review required:

- required-check changes;
- check pruning;
- deprecation enforcement.

# Related Systems

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `.github/workflows/**`
- `.circleci/config.yml`
- `harness.contract.json`
- `Docs/agents/04-validation.md`
- future eval: `.harness/evals/agent-skills-governance-compression-eval.md`
