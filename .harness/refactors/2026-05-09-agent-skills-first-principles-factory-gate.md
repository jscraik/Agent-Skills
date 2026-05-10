# First Principles Factory Gate Refactor Program

schema_version: 1

Repository: `agent-skills`

Program date: 2026-05-09

Selected candidate: first-principles factory gate for `skill-factory` and
`plugin-factory`

Output path:
`.harness/refactors/2026-05-09-agent-skills-first-principles-factory-gate.md`

Source strategy:
`.harness/strategy/2026-05-09-agent-skills-first-principles-factory-strategy.md`

Status: ready for downstream `he-spec` or `he-plan`, not implementation
authority by itself.

## Refactor Classification

- Type: staged factory-behavior migration
- Side-effect class: artifact-write for this program; future implementation is
  repo-write
- Leverage area: routing precision, proof-backed artifact selection, context
  budget, factory validation, eval quality
- High-leverage threshold: met
- Reason: completion would materially reduce the chance that the factories
  create structurally valid but low-value skills/plugins copied from existing
  templates.

## Problem Statement

`skill-factory` and `plugin-factory` can already route, scaffold, harden, and
validate package shape. The gap is earlier: deciding whether a requested skill
or plugin should exist at all, and what artifact type should carry the behavior.

Without a first-principles gate, factory work can pass structural checks while
still increasing catalog breadth, prompt load, routing ambiguity, or governance
ceremony. That weakens the repository's stated moat: proof-backed local control
with small deterministic surfaces.

## Root Cause Analysis

- Factory routers emphasize lane selection and package design contracts, but do
  not yet require an explicit artifact-selection decision before build work.
- Current factory hooks inject helpful context, but hooks are advisory context
  and cannot provide deterministic readiness proof by themselves.
- Existing validation can prove manifest/hook/skill shape, but it does not yet
  prove that a new skill/plugin is the smallest effective mechanism.
- Existing strategy already rejects skill/plugin count as moat, but that
  principle has not been converted into a factory-stage gate.

## Evidence

- `.harness/strategy/agent-skills-strategy.md` defines the repository moat as
  proof-backed local control, not skill/plugin volume.
- `.harness/strategy/2026-05-09-agent-skills-first-principles-factory-strategy.md`
  identifies the desired shift from valid packages to smallest proof-backed
  agent capability.
- `Plugins/skill-factory/skills/skill-factory-router/SKILL.md` already requires
  one primary lane and design-contract handoff.
- `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md` already names
  package boundary, bundled hook surface, side-effect classes, install
  determinism, and eval coverage.
- `Plugins/skill-factory/hooks/session_start_routing.py` and
  `Plugins/plugin-factory/hooks/session_start_contract.py` provide context
  injection but no enforcement.
- `Infrastructure/references/openai-style-plugin-design-contract.md` already
  requires narrow capability surfaces, side-effect classes, minimized context,
  structured outputs, and retry-safe behavior.

## Architectural Impact

This refactor changes factory behavior at the decision boundary, not the
underlying package model.

Expected impact:

- Better routing: factory requests first choose artifact type instead of
  defaulting to scaffold/build work.
- Lower context load: copied patterns and broad prose are rejected before they
  become always-loaded skill/plugin text.
- Better proof: factory output records why the chosen artifact is the smallest
  effective mechanism.
- Safer plugin hook adoption: hooks remain context injection unless validator
  and eval evidence justify runtime behavior.
- Better future automation: MCP/app surfaces can be deferred until a stable gate
  schema proves useful.

## Desired End State

Factory runs that create, harden, refactor, or design skills/plugins include a
compact `first_principles_gate` decision before package work.

The gate chooses exactly one result:

```text
BUILD_SKILL
BUILD_PLUGIN
ADD_HOOK
ADD_MCP_TOOL
ADD_APP
ADD_EVAL
IMPROVE_EXISTING
DOCS_ONLY
DO_NOT_BUILD
```

The minimum recorded fields are:

```yaml
first_principles_gate:
  desired_outcome: ""
  user_specific_constraints: []
  copied_assumption_rejected: ""
  fundamental_constraints: []
  smallest_effective_mechanism: ""
  artifact_decision: ""
  rejected_alternatives: []
  evidence_required: []
  validation_proof: []
  stop_or_pivot_condition: ""
```

Factory readiness is not claimed until tests, validation, or eval fixtures prove
the gate is emitted and influences at least one build/do-not-build decision.

## Migration Strategy

Use a four-phase migration. Each phase is small, reversible, and produces
observable feedback before the next phase is allowed.

Do not add MCP tools, apps, or new factory plugins in this program. Those are
downstream automation candidates after the schema proves useful.

## Smallest Reversible Step

Add the compact gate language to the two router entrypoints and the two existing
factory SessionStart hook scripts, then add a test that checks the hook context
contains the decision terms.

What it teaches:

- Whether the concept can be injected without bloating always-loaded context.
- Whether the existing hook tests can guard drift.
- Whether the language is clear enough before deeper validator/eval work.

Rollback:

- Revert the router and hook text only.
- Leave the strategy and refactor artifacts as rejected/paused context if the
  gate proves too noisy.

## Execution Phases

### Phase 1: Router And Hook Checkpoint

- Objective: make the first-principles gate visible at the factory decision
  boundary without changing package generation.
- Affected systems:
  - `Plugins/skill-factory/skills/skill-factory-router/SKILL.md`
  - `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md`
  - `Plugins/skill-factory/hooks/session_start_routing.py`
  - `Plugins/plugin-factory/hooks/session_start_contract.py`
  - `Infrastructure/tests/test_plugin_bundled_hooks_contract.py`
- Expected risk: low
- Feedback expected from this phase: tests prove the gate terms are present and
  hook output remains valid JSON.
- Stop or pivot condition: stop if router/hook context becomes long enough to
  weaken progressive disclosure.
- Can run in parallel: no
- Validation requirements:
  - `python3 -m py_compile` on changed hook/test scripts
  - focused pytest for factory bundled hook tests
  - changed-file authoring-family gate when practical
- Rollback conditions: revert router/hook/test edits if context bloat or test
  brittleness appears.
- Linear mapping: candidate sub-issue, "Add first-principles gate checkpoint to
  factory routers and hooks"
- Agent-safe: yes
- Human review required: no

### Phase 2: Reference Schema And Factory Procedure

- Objective: move full schema/examples into references and wire the gate into
  factory create/harden/refactor procedures.
- Affected systems:
  - factory router references
  - skill-factory creation/hardening/refactor lane docs
  - plugin-factory creator/builder references
- Expected risk: medium
- Feedback expected from this phase: factory procedures can cite the reference
  without expanding always-loaded skill bodies.
- Stop or pivot condition: pivot to reference-only if procedure edits duplicate
  existing OpenAI-style design contract language without changing decisions.
- Can run in parallel: partially, after Phase 1 lands
- Validation requirements:
  - progressive-disclosure lint
  - authoring-family validation
  - targeted grep/assertion that references, not entrypoints, carry long schema
- Rollback conditions: revert procedural text while retaining reference schema
  if the procedure load is too high.
- Linear mapping: candidate sub-issue, "Add first-principles gate reference
  schema and procedure wiring"
- Agent-safe: assisted
- Human review required: no

### Phase 3: Validator And Test Enforcement

- Objective: add deterministic warning/failure checks for missing gate evidence
  in factory-created or factory-hardened artifacts.
- Affected systems:
  - `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
  - factory-specific Python tests
  - plugin-builder/skill-builder validation surfaces as needed
- Expected risk: medium
- Feedback expected from this phase: validation reports missing gate evidence
  without blocking unrelated packages prematurely.
- Stop or pivot condition: pivot to warning-only if strict failure creates too
  many false positives on existing historical fixtures.
- Can run in parallel: no
- Validation requirements:
  - focused validator unit tests
  - authoring-family gate
  - `git diff --check`
- Rollback conditions: downgrade enforcement from fail to warn or scope it only
  to new factory output.
- Linear mapping: candidate sub-issue, "Enforce first-principles gate evidence
  in factory validation"
- Agent-safe: assisted
- Human review required: yes

### Phase 4: Eval Proof And Closure Artifact

- Objective: prove the gate changes decisions, including one case where the
  factory should build and one where it should not.
- Affected systems:
  - factory eval fixtures
  - `.harness/evals/**` closure proof artifact
  - authoring-family benchmark configuration
- Expected risk: medium
- Feedback expected from this phase: evals show the gate can choose
  `BUILD_SKILL` and `DO_NOT_BUILD` or `IMPROVE_EXISTING` based on evidence.
- Stop or pivot condition: stop if evals only prove the phrase appears, not
  that the artifact decision changes.
- Can run in parallel: after Phase 2, no earlier
- Validation requirements:
  - relevant eval/plugin-eval gate when available
  - authoring-family gate
  - write closure proof to
    `.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md`
- Rollback conditions: keep gate as advisory if eval behavior is inconclusive;
  do not claim readiness.
- Linear mapping: candidate sub-issue, "Prove first-principles gate changes
  factory decisions"
- Agent-safe: assisted
- Human review required: yes

## Linear Mapping

No Linear objects were created.

Suggested mapping if tracked:

- Parent: "Implement first-principles factory gate"
- Labels: `harness-engineering`, `agent-skills`, `factory`, `validation`
- Priority: medium-high
- Sub-issues:
  1. Add gate checkpoint to factory routers and hooks.
  2. Add reference schema and procedure wiring.
  3. Add validator/test enforcement.
  4. Add eval proof and closure artifact.

## Anti-Regression Constraints

- The gate must reduce wrong-build decisions, not add ceremony.
- Entry-point router additions must stay compact; full schema belongs in
  references.
- Hooks may inject context but must not be treated as enforcement.
- Static validation may prove the gate is present; evals must prove behavior
  changed.
- Existing factory package generation must remain valid for the plugin hook
  contract: `hooks/hooks.json`, top-level `hooks`, command handlers, `timeout`
  in seconds, and `${PLUGIN_ROOT}` for plugin-owned hook scripts.
- Generated/runtime projections must not become the edited source of truth.

## Eval Requirements

Expected closure proof artifact:

```text
.harness/evals/2026-05-09-agent-skills-first-principles-factory-gate-eval.md
```

Minimum eval evidence:

- Positive case: a repeated, validated workflow becomes `BUILD_SKILL` with a
  smallest reusable cognitive move and validation proof.
- Plugin case: a runtime behavior package becomes `BUILD_PLUGIN` or `ADD_HOOK`
  only when the behavior should travel with the plugin.
- Negative case: a copied template request becomes `DO_NOT_BUILD`,
  `DOCS_ONLY`, or `IMPROVE_EXISTING`.
- Drift case: a request to add hooks because hooks are available is rejected
  unless runtime behavior and trust boundary prove the need.

## Success Criteria

- Both factory routers require the gate before create/harden/refactor/package
  decisions.
- Both factory SessionStart hooks mention the compact gate without bloating
  context.
- A reference schema exists and is used by factory procedures.
- Tests or validators catch missing/malformed gate evidence for new factory
  output.
- At least one eval proves the gate changes artifact selection.
- Closure proof exists in `.harness/evals/**` before readiness is claimed.

## Safe Rollback Conditions

Rollback is safe if:

- gate language increases confusion or context load;
- validation creates false positives on existing packages;
- evals fail to show artifact-selection improvement;
- hook context becomes noisy or unreliable while `plugin_hooks` remains gated.

Rollback path:

1. Revert router and hook checkpoint text.
2. Disable or downgrade validator enforcement to warning-only.
3. Keep reference schema as archived context only if it remains useful.
4. Mark the eval artifact as inconclusive and do not claim factory readiness.

## Future-Agent Guidance

Start with Phase 1 only. Do not implement MCP tools, apps, or new package
surfaces until the gate schema proves useful through validation/eval evidence.

When moving to implementation, route to exactly one downstream slice. The first
approved slice should be:

```text
Phase 1: Router And Hook Checkpoint
```

Do not consume the entire strategy stack as implementation scope. Use this
refactor program as the selected migration source, and treat the strategy
artifact as context.

## Related Systems

- `.harness/strategy/2026-05-09-agent-skills-first-principles-factory-strategy.md`
- `.harness/strategy/agent-skills-strategy.md`
- `Plugins/skill-factory/skills/skill-factory-router/SKILL.md`
- `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md`
- `Plugins/skill-factory/hooks/session_start_routing.py`
- `Plugins/plugin-factory/hooks/session_start_contract.py`
- `Infrastructure/references/openai-style-plugin-design-contract.md`
- `Infrastructure/references/agent-native-skill-contract.md`
- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
