# Agent-First Golden Path

# Refactor Classification

- orchestration simplification
- routing redesign
- cognition compression
- execution determinism
- skill discoverability improvement
- context-load reduction
- moat reinforcement

# Problem Statement

The repository has the right golden-path concepts, but the path is not yet dominant enough. Prior artifacts converge on this loop:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

The problem is that agents can still encounter many adjacent health, proof, routing, docs, and validation surfaces before they know what to do. This creates execution ambiguity and token-heavy workflows.

Operational issue:

- multiple valid commands compete for first action;
- validation layers are not compressed into one daily loop;
- proof, explain, closeout, and doctor concepts can be discovered in the wrong order.

Future-agent issue:

- agents may read docs instead of asking the repo for current truth;
- agents may run partial checks and claim completion;
- agents may choose a skill by browsing instead of routed recommendation.

Moat risk:

The actual moat is a trusted local control plane. If the control plane does not guide agents deterministically, it becomes documentation plus hope.

# Root Cause Analysis

Why it emerged:

- Capabilities were added as the repo learned new agent failure modes.
- Each command was locally useful.
- The repo accumulated multiple health and validation surfaces before a single user journey was enforced.

Why it survived:

- Expert users can navigate the surface area.
- Docs are accurate enough that the ambiguity is survivable.
- Existing commands provide value individually.

Why current boundaries are insufficient:

- `repo doctor` is strong but not yet the enforced first truth surface.
- `skills improve`, `skills explain`, and `skills prove` need sharper sequencing.
- Closeout needs to become completion pressure, not optional advice.

Nature of issue:

- strategic and operational;
- not a rewrite problem;
- a routing and cognition compression problem.

# Evidence

Facts:

- The intent artifact recommends making `repo doctor -> skills improve -> skills explain -> skills prove -> repo closeout` the canonical public loop.
- The review recommends promoting `repo doctor` to the canonical agent entrypoint.
- The triage ranks `repo doctor --next` and golden-path routing as high-priority.
- The strategy says the five-command path is the product spine.

Interpretation:

- The architecture should route first-contact and closeout through this loop.
- Adjacent commands should become advanced/reference unless they strengthen the loop.

Assumptions:

- Existing command internals can be enhanced without renaming the public surface.
- `repo doctor --next` or equivalent can be implemented without requiring all downstream commands to be complete first.

# Architectural Impact

Affected systems:

- `./bin/ask repo doctor`
- `./bin/ask skills improve`
- `./bin/ask skills explain`
- `./bin/ask skills prove`
- `./bin/ask repo closeout --changed`
- README/AGENTS/onboarding docs that mention first action
- CI artifact reporting for doctor output

Blast radius:

- medium-high, because it affects user/agent entrypoints.

Migration complexity:

- moderate if implemented as additive command behavior and docs rerouting.

Rollback difficulty:

- low-medium if existing commands remain available.

Likely files/directories touched:

- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py` or extracted services after decomposition
- `Infrastructure/bin/ask`
- `AGENTS.md`
- `README.md`
- `Docs/agents/**`

Systems that must not be touched:

- source/projection model;
- public command contracts except additive fields;
- validation gates without clear proof target.

# Desired End State

Agents can start with one command and follow exact next actions.

Desired behavior:

- `repo doctor` gives current truth.
- `repo doctor --next` gives one highest-priority next action.
- `skills improve` returns one primary capability unless real ambiguity exists.
- `skills explain` gives canonical source, handle, visibility, limitations, and smallest validation.
- `skills prove` labels proof type: reachability, structural, quality, outcome.
- `repo closeout --changed` determines completion readiness from actual changed files.

Improved cognition model:

- agents do not browse the repo to infer workflow;
- the repo routes agents through current command truth;
- docs point to commands instead of duplicating command behavior.

# Migration Strategy

Sequence:

1. Add `repo doctor --next` or equivalent next-action output.
2. Update primary docs to make doctor the first action.
3. Tighten `skills improve` output to one primary route where possible.
4. Tighten `skills explain` around canonical source and smallest validation.
5. Integrate proof labels after proof taxonomy exists.
6. Add `repo closeout --changed` behavior or strengthen existing closeout path.
7. Generate/validate onboarding docs from command output.

Coexistence rules:

- existing commands remain callable;
- advanced commands are not deleted until golden path works;
- docs may reference advanced commands only after the primary loop.

Rollback strategy:

- rollback additive flags/fields if they misroute;
- keep old command behavior available;
- preserve snapshots of doctor output before changing docs.

Linear milestone/parent issue shape:

- milestone: `Agent First Golden Path`
- parent issue: `Make repo doctor and skill routing the canonical agent loop`

# Execution Phases

## Phase 1 — Doctor Next Action

Objective:

Make `repo doctor` return one highest-priority next action.

Affected systems:

- repo doctor signal composition;
- robot JSON output;
- docs references.

Expected risk:

- medium.

Can run in parallel:

- yes, with `skills.py` decomposition only if command output ownership is clear.

Validation requirements:

- doctor JSON snapshot;
- next action for known blocker states;
- docs lint.

Rollback conditions:

- next action is wrong or non-deterministic;
- output breaks robot consumers.

Linear mapping:

- child issue: `Add repo doctor next-action output`

Agent-safe:

- assisted.

Human review required:

- yes for output contract.

## Phase 2 — Skill Route Compression

Objective:

Make `skills improve` return one primary recommendation unless ambiguity is real.

Affected systems:

- skill routing;
- selection policy;
- skill discoverability.

Expected risk:

- medium-high.

Can run in parallel:

- no, if it touches `skills.py` before service extraction boundary is established.

Validation requirements:

- representative goal-to-skill routing examples;
- ambiguity cases documented;
- no default-visible budget regression.

Rollback conditions:

- route quality worsens;
- too many false single recommendations.

Linear mapping:

- child issue: `Compress skills improve to one primary route`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 3 — Explain And Prove Contract Alignment

Objective:

Make `skills explain` and `skills prove` support safe routing and proof interpretation.

Affected systems:

- skill explain output;
- proof labels;
- validation guidance.

Expected risk:

- medium.

Can run in parallel:

- after proof taxonomy ADR starts.

Validation requirements:

- sample explain output includes canonical source and smallest validation;
- proof output states proof level.

Rollback conditions:

- proof labels are misleading;
- explain output becomes too verbose.

Linear mapping:

- child issue: `Align skills explain and prove with golden path`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 4 — Closeout Integration

Objective:

Make closeout the completion-readiness gate.

Affected systems:

- repo closeout command;
- changed-file validation;
- completion guidance.

Expected risk:

- medium.

Can run in parallel:

- yes, after doctor next action is stable.

Validation requirements:

- changed-file scenarios;
- sync-needed detection where applicable;
- exact blocker output.

Rollback conditions:

- closeout blocks unrelated work;
- false readiness claims.

Linear mapping:

- child issue: `Strengthen repo closeout changed-file gate`

Agent-safe:

- assisted.

Human review required:

- yes.

## Phase 5 — Generated Onboarding

Objective:

Replace repeated first-contact prose with generated or validated command-derived guidance.

Affected systems:

- README/AGENTS/docs;
- docs lint;
- command output examples.

Expected risk:

- low-medium.

Can run in parallel:

- yes.

Validation requirements:

- docs lint;
- generated output freshness check.

Rollback conditions:

- generated docs become noisier than the prose they replace.

Linear mapping:

- child issue: `Generate or validate agent-first onboarding from command output`

Agent-safe:

- yes.

Human review required:

- no unless public copy changes materially.

# Linear Mapping

Workspace/team: Jscraik

Team key: JSC

Top-level initiative: Dev Portfolio

Cross-repo project: Portfolio Ops

Repo-specific work: `agent-skills`

Target Linear project:

- `Agent Skills — Agent First Golden Path`

Scope:

- repo-specific with cross-repo pattern implications.

Belongs under `Portfolio Ops`:

- yes.

Affects `Dev Portfolio`:

- yes.

Recommended milestone:

- `Agent First Golden Path`

Recommended parent issue title:

- `Make repo doctor and skill routing the canonical agent loop`

Recommended sub-issues:

- `Add repo doctor next-action output`
- `Compress skills improve to one primary route`
- `Align skills explain and prove with golden path`
- `Strengthen repo closeout changed-file gate`
- `Generate or validate agent-first onboarding from command output`

Suggested priority:

- high / P1.

Suggested labels:

- `agent-native`
- `routing`
- `golden-path`
- `determinism`
- `cognition`

Dependencies:

- `skills.py` decomposition for deeper skill routing changes;
- proof taxonomy for `skills prove` semantics.

Project reactivation:

- yes if a golden-path or agent-first project already exists.

Active set:

- keep small; doctor next-action should be first active child.

# Anti-Regression Constraints

Must not regress:

- current doctor signals;
- robot JSON compatibility;
- existing command availability;
- source/projection warnings;
- validation/closeout honesty.

Must not reappear:

- multiple "first" commands in docs;
- blockers without exact next action;
- skill recommendations as unranked buffets;
- proof output that hides proof type;
- docs that duplicate stale command examples.

# Eval Requirements

Expected eval artifact:

`.harness/evals/agent-skills-agent-first-golden-path-eval.md`

Required proof:

- doctor output before/after snapshot;
- at least five representative goals routed through `skills improve`;
- explain/prove examples for a core skill;
- closeout changed-file scenario;
- docs lint;
- evidence that a fresh agent can follow one next command without reading multiple docs.

# Success Criteria

- `repo doctor --next` or equivalent exists and is deterministic.
- `skills improve` returns one primary route for common goals.
- `skills explain` identifies canonical source and smallest validation.
- `skills prove` labels proof type.
- `repo closeout --changed` is the completion pressure surface.
- First-contact docs point to the golden path.

# Safe Rollback Conditions

Rollback if:

- next-action output misroutes common blocker states;
- skill recommendation quality worsens;
- robot output breaks consumers;
- closeout blocks unrelated changes;
- docs become more verbose without reducing ambiguity.

Linear status if rollback is triggered:

- keep parent open;
- mark failed child issue blocked;
- capture failure in eval artifact.

# Future-Agent Guidance

Preserve:

- one current truth command;
- one primary route;
- exact next commands;
- closeout as completion evidence.

Simplify further:

- docs that explain what commands can output directly;
- routing options that do not affect execution.

Intentional complexity:

- deterministic signal ordering;
- proof-level distinctions.

Accidental complexity:

- multiple valid first paths;
- manual docs repeating live commands.

Human review required:

- command output contract changes;
- route-ranking policy changes;
- proof semantics changes.

# Related Systems

- `.harness/strategy/agent-skills-strategy.md`
- `.harness/triage/agent-skills-triage.md`
- `Infrastructure/scripts/lib/ask/commands/repo.py`
- `Infrastructure/scripts/lib/ask/commands/skills.py`
- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`
- `AGENTS.md`
- `README.md`
- future eval: `.harness/evals/agent-skills-agent-first-golden-path-eval.md`
