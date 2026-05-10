# Repository Cognition Burn-Down

# Refactor Classification

- cognition compression
- anti-drift hardening
- context-load reduction
- governance reduction
- execution determinism
- moat reinforcement

# Problem Statement

The repository treats cognition as architecture, but its tracked surface currently contains too much ambiguous material: historical artifacts, generated work areas, runtime-like state, unresolved `.skillsets/**` ownership, duplicate infrastructure paths, and stale reports. The prior artifacts call this strategic cognition debt, not housekeeping.

Operational issue:

- agents cannot easily distinguish source, generated output, fixture, archive, or accidental state;
- repo-surface warnings become broad noise;
- stale artifacts can be mistaken for current truth.

Future-agent issue:

- agents may cite old evidence;
- agents may edit generated/runtime surfaces;
- agents may spend context reading artifacts rather than source contracts.

Moat risk:

The moat depends on repository cognition quality. If raw history and generated debris compete with current operating contracts, the repo weakens the very agent reasoning it is meant to improve.

# Root Cause Analysis

Why it emerged:

- Evidence retention was valuable during rapid architecture learning.
- Generated/runtime artifacts helped inspect drift.
- Historical runs preserved useful archaeology.
- Classification policy matured after artifacts already existed.

Why it survived:

- Deleting unknown artifacts is risky.
- Some artifacts may be fixtures or evidence.
- The repo lacked a completed classification-first burn-down path.

Why current boundaries are insufficient:

- `.skillsets/**` ownership is explicitly unresolved in prior artifacts.
- Generated/runtime/source categories are known but not fully enforced across tracked surfaces.
- Historical artifact retention lacks a consistent index/summary policy.

Nature of issue:

- architectural and governance;
- not cosmetic cleanup;
- cognition and anti-drift work.

# Evidence

Facts:

- `.harness/features/agent-skills-intent.md` recommends classifying `.skillsets/**` explicitly.
- Prior artifacts cite repo-surface findings including historical artifacts, generated work areas, runtime database, duplicate infrastructure paths, and ownership decisions.
- `.harness/strategy/agent-skills-strategy.md` says historical artifacts must not compete with current operating contracts.
- `.harness/triage/agent-skills-triage.md` ranks repo-surface burn-down as a core initiative.

Interpretation:

- File ownership is part of the product architecture.
- Burn-down must preserve useful evidence while removing primary-path noise.

Assumptions:

- Repo-surface inventory can classify enough categories to support staged deletion/quarantine.
- Some historical artifacts should remain as indexed summaries or fixtures.

# Architectural Impact

Affected systems:

- `.harness/**`
- `.skillsets/**`
- generated reports/artifacts;
- repo-surface inventory;
- path ownership docs;
- validation/doctor output;
- future-agent source discovery.

Blast radius:

- high if deletion is careless;
- medium if classification-first.

Migration complexity:

- difficult but stageable.

Rollback difficulty:

- high for deleted files if not archived;
- low for classification metadata.

Likely files/directories touched:

- `.harness/**`
- `.skillsets/**`
- `Docs/agents/15-repo-surface-ownership.md`
- repo-surface inventory scripts
- ignore/allowlist files
- generated artifact directories.

Systems that must not be touched:

- canonical skill sources;
- path ownership principles;
- fixtures required by tests;
- indexed evidence summaries required by evals.

# Desired End State

Every tracked non-source file has an explicit role:

- canonical source;
- generated but owned;
- runtime state excluded from source;
- fixture;
- historical archive with index;
- evidence summary;
- deletion candidate;
- migration pending.

Desired operating model:

- raw historical artifacts are not in primary browsing paths;
- runtime databases are not tracked source;
- generated surfaces have generator, inputs, freshness check, and edit rule;
- repo doctor surface warnings are actionable;
- future agents can tell whether a file is current truth.

# Migration Strategy

Sequence:

1. Inventory and classify without deleting.
2. Resolve `.skillsets/**` ownership.
3. Add generated/runtime/fixture/archive categories and thresholds.
4. Quarantine raw historical artifacts behind indexes.
5. Remove tracked runtime state after caller/reference checks.
6. Remove duplicate/stale generated outputs after regeneration proof.
7. Turn new unclassified artifact creation into a blocking drift signal.

Coexistence rules:

- keep existing artifacts until classified;
- no blind deletion;
- archive before deletion when archaeology value is uncertain;
- fixtures stay with explicit fixture ownership.

Rollback strategy:

- keep quarantine branch/archive until burn-down eval passes;
- restore individual files if reference scan missed a caller;
- never rollback to unclassified sprawl as the steady state.

Linear milestone/parent issue shape:

- milestone: `Repository Cognition Burn-Down`
- parent issue: `Classify, quarantine, and reduce tracked cognition debt`

# Execution Phases

## Phase 1 — Classification Inventory

Objective:

Classify tracked non-source surfaces without deleting.

Affected systems:

- repo-surface inventory;
- `.harness/**`;
- `.skillsets/**`.

Expected risk:

- low.

Can run in parallel:

- yes.

Validation requirements:

- inventory report with category counts;
- no file deletions.

Rollback conditions:

- classification categories are too vague to drive action.

Linear mapping:

- child issue: `Classify tracked non-source surfaces`

Agent-safe:

- yes.

Human review required:

- no for inventory, yes for category policy.

## Phase 2 — `.skillsets/**` Ownership Decision

Objective:

Decide whether `.skillsets/**` is generated tracked distribution, fixture subset, or untracked runtime output.

Affected systems:

- `.skillsets/**`;
- generator/validation policy;
- catalog parity.

Expected risk:

- medium-high.

Can run in parallel:

- no.

Validation requirements:

- generator identified;
- source inputs documented;
- freshness validation exists if tracked;
- catalog parity remains meaningful.

Rollback conditions:

- ownership decision breaks runtime/review use;
- generated output cannot be reproduced.

Linear mapping:

- child issue: `Resolve .skillsets generated surface ownership`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 3 — Historical Artifact Quarantine

Objective:

Move raw historical artifacts out of primary source paths while preserving summaries, fixtures, and indexes.

Affected systems:

- `.harness/**`;
- artifact directories;
- evidence references.

Expected risk:

- medium.

Can run in parallel:

- yes after classification.

Validation requirements:

- reference scan;
- index created;
- docs/evals updated if they cite moved artifacts.

Rollback conditions:

- evals/tests depend on raw artifacts;
- important evidence becomes undiscoverable.

Linear mapping:

- child issue: `Quarantine raw historical artifacts behind indexes`

Agent-safe:

- assisted.

Human review required:

- yes for deletion; no for pure indexing.

## Phase 4 — Runtime And Generated Debris Removal

Objective:

Remove or ignore tracked runtime state and stale generated reports after reference checks.

Affected systems:

- runtime DB files;
- generated reports;
- ignore/allowlist rules.

Expected risk:

- medium.

Can run in parallel:

- after classification and reference scans.

Validation requirements:

- caller/reference scan;
- regeneration proof for generated reports;
- repo doctor surface signal improved.

Rollback conditions:

- removed file has live caller;
- regeneration path missing.

Linear mapping:

- child issue: `Remove tracked runtime state and stale generated reports`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 5 — New Artifact Drift Gate

Objective:

Prevent new unclassified artifacts from entering the tracked repo.

Affected systems:

- repo-surface inventory;
- CI/governance;
- docs.

Expected risk:

- low-medium.

Can run in parallel:

- after categories are stable.

Validation requirements:

- check blocks new unclassified generated/runtime artifacts;
- allowlist fixture path works.

Rollback conditions:

- gate blocks valid fixtures or canonical sources.

Linear mapping:

- child issue: `Block new unclassified tracked artifacts`

Agent-safe:

- yes.

Human review required:

- yes for blocking policy.

# Linear Mapping

Workspace/team: Jscraik

Team key: JSC

Top-level initiative: Dev Portfolio

Cross-repo project: Portfolio Ops

Repo-specific work: `agent-skills`

Target Linear project:

- `Agent Skills — Repository Cognition Burn-Down`

Scope:

- repo-specific.

Belongs under `Portfolio Ops`:

- yes, because file-surface hygiene affects portfolio-wide agent cognition patterns.

Affects `Dev Portfolio`:

- yes.

Recommended milestone:

- `Repository Cognition Burn-Down`

Recommended parent issue title:

- `Classify, quarantine, and reduce tracked cognition debt`

Recommended sub-issues:

- `Classify tracked non-source surfaces`
- `Resolve .skillsets generated surface ownership`
- `Quarantine raw historical artifacts behind indexes`
- `Remove tracked runtime state and stale generated reports`
- `Block new unclassified tracked artifacts`

Suggested priority:

- high / P1.

Suggested labels:

- `repo-cognition`
- `anti-drift`
- `artifact-hygiene`
- `agent-native`
- `governance`

Dependencies:

- none for inventory;
- deletion depends on classification and reference scans.

Project reactivation:

- yes if a repo-surface cleanup project exists.

Active set:

- keep deletion issues small and classification-backed.

# Anti-Regression Constraints

Must not regress:

- fixtures required by tests/evals;
- indexed evidence needed by future agents;
- generated surfaces required for runtime/review if explicitly owned;
- catalog parity signal.

Must not reappear:

- tracked runtime state without fixture classification;
- raw historical logs in primary browsing paths;
- generated reports without generator/freshness metadata;
- duplicate infrastructure copies without ownership.

# Eval Requirements

Expected eval artifact:

`.harness/evals/agent-skills-repository-cognition-burndown-eval.md`

Required proof:

- before/after repo-surface counts;
- category inventory;
- `.skillsets/**` ownership decision;
- reference scan evidence for deletion/quarantine;
- repo doctor surface signal improvement or documented remaining blockers;
- docs lint.

# Success Criteria

- Every tracked non-source surface has an ownership category.
- `.skillsets/**` policy is explicit and validated.
- Raw historical artifacts are indexed, quarantined, or removed.
- Runtime state is not tracked as source.
- New unclassified artifacts are blocked.
- Future agents can identify current truth faster.

# Safe Rollback Conditions

Rollback if:

- test/eval fixtures disappear;
- generated runtime/review behavior breaks;
- important evidence becomes undiscoverable;
- drift gate blocks valid work.

Linear status if rollback is triggered:

- keep parent open;
- mark affected child as blocked;
- restore from quarantine/archive;
- record missed reference in eval artifact.

# Future-Agent Guidance

Preserve:

- source truth;
- fixture evidence;
- indexed summaries;
- path ownership categories.

Simplify further:

- raw artifacts;
- stale generated outputs;
- ambiguous archive directories.

Intentional complexity:

- classification-first deletion;
- preservation of indexed evidence.

Accidental complexity:

- raw artifact sprawl;
- generated/runtime ambiguity.

Human review required:

- deletion of uncertain historical evidence;
- `.skillsets/**` ownership decision;
- blocking gate adoption.

# Related Systems

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `Docs/agents/15-repo-surface-ownership.md`
- `.harness/**`
- `.skillsets/**`
- repo-surface inventory scripts
- future eval: `.harness/evals/agent-skills-repository-cognition-burndown-eval.md`
