# Proof-Driven Skill Promotion

# Refactor Classification

- eval stabilization
- moat reinforcement
- governance reduction
- skill discoverability improvement
- execution determinism
- anti-drift hardening

# Problem Statement

The repository treats skill quality and governance seriously, but the prior artifacts identify a strategic gap: structural audit and reachability proof can be mistaken for outcome proof. That weakens the moat because the defensible value is not that skills exist or pass shape checks; it is that skills measurably improve agent behavior on real work.

Operational issue:

- skill promotion can become catalog expansion;
- proof terms can blur;
- default visibility can imply trust before outcome evidence exists.

Future-agent issue:

- agents may treat a structurally valid skill as operationally proven;
- agents may choose broad/unproven skills;
- agents cannot tell whether proof means "loads", "passes audit", "routes correctly", or "improved a task outcome".

Moat risk:

If proof remains mostly structural, the moat becomes performative. Competitors can copy a skill catalog and claim similar coverage.

# Root Cause Analysis

Why it emerged:

- Structural validation is easier to automate than outcome validation.
- Skill authoring needed audits before realistic outcome data existed.
- Catalog growth created pressure to validate shape and reachability first.

Why it survived:

- Structural audits are useful and produce fast signal.
- Outcome proof is more expensive and requires scenarios, traces, or closeout evidence.
- The architecture had not yet separated proof levels into promotion gates.

Why current boundaries are insufficient:

- proof vocabulary is not yet a hardened domain boundary;
- promotion states are not encoded as lifecycle policy;
- eval artifacts are not yet mandatory closure evidence for promotion.

Nature of issue:

- strategic and governance-critical;
- not just test coverage;
- moat-defining.

# Evidence

Facts:

- `.harness/features/agent-skills-intent.md` recommends not promoting core/default-visible skills without reachability, structural, and outcome proof.
- `.harness/review/agent-skills-architecture-review.md` says structural audit must not be treated as outcome proof.
- `.harness/triage/agent-skills-triage.md` ranks proof taxonomy and skill promotion gates as P0/P1.
- `.harness/strategy/agent-skills-strategy.md` says proof is the promotion mechanism and catalog size is a false moat.

Interpretation:

- Skill lifecycle states need a proof taxonomy.
- Promotion to trusted/default-visible should be blocked without proof status.

Assumptions:

- The repo can start with a small proof set for core skills rather than proving the entire catalog.
- Proof metadata can be introduced before all eval automation exists.

# Architectural Impact

Affected systems:

- skill lifecycle policy;
- default-visible selection;
- `skills prove`;
- skill audit outputs;
- eval/workout artifacts;
- docs describing quality/trust;
- Linear closure criteria for skill work.

Blast radius:

- medium-high, because it affects promotion semantics rather than command plumbing only.

Migration complexity:

- moderate; can be staged with metadata and a small core set.

Rollback difficulty:

- low for metadata changes;
- medium once promotion gates become blocking.

Likely files/directories touched:

- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- skill audit/proof command modules or services
- `Skills/**/SKILL.md` metadata surfaces where applicable
- `.harness/evals/**`
- docs describing skill promotion

Systems that must not be touched:

- default-visible budget semantics except through explicit promotion policy;
- command handles as invocation pointers;
- structural audit value as a separate proof level.

# Desired End State

Skills have explicit lifecycle/proof states:

- experimental;
- latent;
- structurally valid;
- reachable;
- outcome-proven;
- trusted;
- default-visible;
- deprecated.

Proof levels are separate:

- reachability: the skill can be found and loaded;
- structural: the package shape and instructions pass audit;
- quality: the skill meets local quality heuristics;
- outcome: the skill improves a realistic task result or prevents a known failure.

Promotion rule:

- no trusted/default-visible promotion without explicit proof status;
- no outcome claim without eval or closeout evidence;
- structural audit remains valuable but never sufficient.

# Migration Strategy

Sequence:

1. Write ADR for proof taxonomy and lifecycle states.
2. Add non-blocking proof metadata/report fields.
3. Pick 3-5 core skills for pilot proof artifacts.
4. Update `skills prove` to label proof level explicitly.
5. Add promotion gate for new default-visible skills.
6. Backfill existing default-visible skills gradually.
7. Turn warnings into blockers only after pilot is stable.

Coexistence rules:

- existing skills remain usable;
- unproven skills are not deleted automatically;
- unproven skills may remain experimental/latent;
- default-visible additions require proof after gate adoption.

Rollback strategy:

- demote blocking gates to warnings if false positives block valid work;
- keep proof labels even if enforcement is paused;
- do not remove structural audit checks.

Linear milestone/parent issue shape:

- milestone: `Proof-Driven Skill Core`
- parent issue: `Define and enforce proof-backed skill promotion`

# Execution Phases

## Phase 1 — Proof Taxonomy ADR

Objective:

Define proof levels and lifecycle states.

Affected systems:

- strategy/governance docs;
- future proof commands.

Expected risk:

- low.

Can run in parallel:

- yes.

Validation requirements:

- ADR reviewed;
- terms match `UBIQUITOUS_LANGUAGE.md` or update it.

Rollback conditions:

- taxonomy creates more ambiguity than it removes.

Linear mapping:

- child issue: `Write proof taxonomy and skill lifecycle ADR`

Agent-safe:

- yes.

Human review required:

- yes.

## Phase 2 — Non-Blocking Proof Labels

Objective:

Make proof outputs label reachability, structural, quality, and outcome evidence.

Affected systems:

- `skills prove`;
- proof/eval output.

Expected risk:

- medium.

Can run in parallel:

- after Phase 1.

Validation requirements:

- sample proof payloads;
- no structural audit regression.

Rollback conditions:

- labels misrepresent proof level.

Linear mapping:

- child issue: `Add explicit proof-level labels`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 3 — Core Skill Pilot

Objective:

Create outcome proof artifacts for 3-5 highest-value skills.

Affected systems:

- selected core skills;
- eval artifacts;
- closeout evidence.

Expected risk:

- medium.

Can run in parallel:

- yes, with bounded skill set.

Validation requirements:

- one realistic scenario per skill;
- before/after or prevented-failure evidence;
- exact validation commands.

Rollback conditions:

- pilot cannot distinguish outcome from structural proof.

Linear mapping:

- child issue: `Pilot outcome proof for core skills`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 4 — Promotion Gate

Objective:

Block new default-visible/trusted promotions without proof status.

Affected systems:

- selection policy;
- runtime budget;
- skill lifecycle metadata.

Expected risk:

- medium-high.

Can run in parallel:

- no.

Validation requirements:

- default-visible addition scenario;
- unproven latent skill scenario;
- warning-to-blocker transition evidence.

Rollback conditions:

- gate blocks legitimate emergency skill routing;
- proof metadata cannot be maintained.

Linear mapping:

- child issue: `Gate trusted/default-visible promotion on proof status`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 5 — Backfill And Drift Guard

Objective:

Backfill proof status for existing trusted/default-visible skills and prevent regression.

Affected systems:

- existing default-visible skills;
- selection policy;
- docs.

Expected risk:

- medium.

Can run in parallel:

- yes, after gate semantics are stable.

Validation requirements:

- proof status report;
- no runtime budget regression;
- docs updated or generated.

Rollback conditions:

- backfill becomes catalog archaeology instead of core proof.

Linear mapping:

- child issue: `Backfill proof status for trusted skills`

Agent-safe:

- yes for individual skills, assisted for policy.

Human review required:

- yes for default-visible status.

# Linear Mapping

Workspace/team: Jscraik

Team key: JSC

Top-level initiative: Dev Portfolio

Cross-repo project: Portfolio Ops

Repo-specific work: `agent-skills`

Target Linear project:

- `Agent Skills — Proof-Driven Skill Core`

Scope:

- repo-specific, with cross-repo governance pattern value.

Belongs under `Portfolio Ops`:

- yes.

Affects `Dev Portfolio`:

- yes.

Recommended milestone:

- `Proof-Driven Skill Core`

Recommended parent issue title:

- `Define and enforce proof-backed skill promotion`

Recommended sub-issues:

- `Write proof taxonomy and skill lifecycle ADR`
- `Add explicit proof-level labels`
- `Pilot outcome proof for core skills`
- `Gate trusted/default-visible promotion on proof status`
- `Backfill proof status for trusted skills`

Suggested priority:

- urgent / P0.

Suggested labels:

- `moat`
- `eval`
- `skills`
- `governance`
- `agent-native`

Dependencies:

- none for ADR;
- proof command implementation may depend on ask control-plane service boundaries.

Project reactivation:

- yes if a skill quality or eval project already exists.

Active set:

- keep pilot small; 3-5 skills maximum.

# Anti-Regression Constraints

Must not regress:

- structural audit remains available;
- reachability remains a distinct useful signal;
- default-visible budget;
- command handles;
- existing skills remain usable while proof metadata is introduced.

Must not reappear:

- invocation counted as success;
- structural audit described as outcome proof;
- default-visible promotion without proof status;
- broad skill categories promoted because they sound important.

# Eval Requirements

Expected eval artifact:

`.harness/evals/agent-skills-proof-driven-skill-promotion-eval.md`

Required proof:

- ADR exists and is linked;
- proof payload examples for each proof level;
- core skill pilot artifacts;
- promotion gate scenario;
- no default-visible budget regression;
- evidence that unproven skills remain experimental/latent rather than trusted.

# Success Criteria

- Proof levels are explicit and machine-readable where practical.
- Trusted/default-visible status requires proof status.
- At least 3-5 core skills have outcome proof artifacts.
- Agents can tell what kind of proof exists before using a skill.
- Catalog growth no longer implies trust.

# Safe Rollback Conditions

Rollback enforcement if:

- proof gate blocks critical workflows incorrectly;
- proof metadata creates widespread false negatives;
- output labels mislead agents;
- maintaining proof status becomes manual ceremony without eval value.

Linear status if rollback is triggered:

- move enforcement issue to blocked;
- keep ADR and non-blocking labels;
- record failed gate evidence in eval artifact.

# Future-Agent Guidance

Preserve:

- proof taxonomy;
- distinction between structural and outcome proof;
- promotion gates.

Simplify further:

- verbose proof prose;
- duplicated proof metadata;
- low-signal proof artifacts.

Intentional complexity:

- proof levels;
- lifecycle states.

Accidental complexity:

- ambiguous "prove" language;
- catalog trust without evidence.

Human review required:

- proof taxonomy changes;
- default-visible promotion changes;
- outcome proof acceptance.

# Related Systems

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `.harness/review/agent-skills-architecture-review.md`
- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- `Skills/**/SKILL.md`
- `.harness/evals/**`
- future eval: `.harness/evals/agent-skills-proof-driven-skill-promotion-eval.md`
