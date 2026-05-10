# First Principles Factory Strategy

schema_version: 1

Repository: `agent-skills`

Strategy date: 2026-05-09

Selected mode: `strategic-compression`

Output path: `.harness/strategy/2026-05-09-agent-skills-first-principles-factory-strategy.md`

## Source Artifacts Read

Inspection method: bounded source read of the named factory plugins, current
factory hook scripts, HE Strategy contracts, and the existing repository
strategy spine.

- User-provided first-principles proposal in the active thread.
- `Plugins/harness-engineering/skills/he-strategy/SKILL.md`
- `Plugins/harness-engineering/skills/he-strategy/references/strategy-output-contract.md`
- `Plugins/harness-engineering/references/first-principles-contract.md`
- `Plugins/harness-engineering/references/agent-native-audit-scorecard.md`
- `Plugins/harness-engineering/references/xp-operating-contract.md`
- `.harness/strategy/agent-skills-strategy.md`
- `Plugins/skill-factory/skills/skill-factory-router/SKILL.md`
- `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md`
- `Plugins/skill-factory/hooks/session_start_routing.py`
- `Plugins/plugin-factory/hooks/session_start_contract.py`
- `Infrastructure/references/openai-style-plugin-design-contract.md`
- `Infrastructure/references/agent-native-skill-contract.md`

## Hard Evidence

- The existing repository strategy says the core moat is proof-backed local
  control, source/projection separation, deterministic command contracts,
  context-budgeted selection, and outcome proof. It explicitly rejects skill
  count, plugin count, broad governance, and artifact volume as moat signals.
- `skill-factory-router` already routes to one primary lane and requires a
  design contract for skill creation, hardening, audit, and refactor handoff.
- `plugin-factory-router` already includes a plugin design checkpoint with
  package boundary, routing surface, child-skill separation, bundled hook
  surface, side-effect classes, install determinism, and eval coverage.
- The current factory hooks inject useful but narrow context: skill lane routing
  for `skill-factory`, and bundled hook mechanics for `plugin-factory`.
- The shared first-principles HE contract already says new stages, skills,
  evals, governance, and routing should exist only when they prevent a verified
  failure, reduce drift, improve proof, or make future-agent reasoning cheaper.
- The OpenAI-style plugin design contract already contains the local mechanism:
  narrow capability surfaces, explicit side-effect classes, minimized context,
  structured output, user steering, and retry-safe behavior.

## Interpretation

The first-principles idea should not become another broad philosophy section in
factory skills. That would add context load and reward sophistication over
proof. The durable move is a small factory gate that forces artifact selection
before scaffolding: skill, plugin, hook, MCP tool, app, eval, docs-only, improve
existing, or do not build.

The strategic shift is from:

```text
Factory output = valid skill/plugin package
```

to:

```text
Factory output = smallest proof-backed agent capability that changes behavior
```

That means the factories should reject copied shapes early. A skill is justified
only when it preserves a reusable cognitive move. A plugin is justified only
when a capability needs a package boundary and runtime behavior that travels
with it.

## Assumptions

- The active user goal is to improve `skill-factory` and `plugin-factory`, not
  to create a standalone first-principles skill.
- `plugin_hooks` remains gated in Codex, so hook-based improvements are context
  injection and package readiness improvements until the feature is enabled in
  runtime config.
- Factory validators can enforce structural warnings before live outcome evals
  exist, but they should not claim outcome proof from static checks alone.

## Affected Systems Or Modules

- `Plugins/skill-factory/skills/skill-factory-router/SKILL.md`
- `Plugins/plugin-factory/skills/plugin-factory-router/SKILL.md`
- `Plugins/skill-factory/hooks/session_start_routing.py`
- `Plugins/plugin-factory/hooks/session_start_contract.py`
- `Plugins/skill-factory/skills/**` creation, hardening, install, refactor, and
  skillify lanes
- `Plugins/plugin-factory/skills/**` creator, builder, installer, and router
  lanes
- `Infrastructure/scripts/validation-and-linting/validate_skill_authoring_family.sh`
- factory-specific tests and eval fixtures

## First Principles Check

```yaml
first_principles_check:
  verified_failure: "Factories can create structurally valid skills/plugins that still copy templates, broaden context, or lack proof of behavior improvement."
  fundamental_constraint: "Agent capability value comes from lower decision load and better validated behavior, not from more package files."
  assumption_being_challenged: "A new user request for a skill or plugin means the right output is a new skill or plugin."
  smallest_effective_mechanism: "Add a first-principles factory gate before scaffold/build/refactor decisions, backed by hook context and validator warnings."
  analogy_or_template_rejected: "Copying successful-looking skill/plugin shapes without deriving the artifact from the user job."
  proof_required: "A factory run records artifact choice, copied assumption rejected, smallest reusable move, validation proof, and stop/pivot condition."
  context_load_effect: reduced
  routing_effect: clearer
  decision_type: Type 2
  outcome: proceed
```

## Agent-Native Scorecard

```yaml
agent_native_scorecard_status: partial
scorecard_dimensions:
  action_parity: partial
  capability_discovery: pass
  context_injection: partial
  shared_truth_surface: partial
  entity_completion: partial
  integration_feedback: partial
  prompt_native_composability: pass
  deterministic_completion: partial
scorecard_evidence: "Routers, shared contracts, and current SessionStart hooks exist; the proposed first-principles gate does not yet exist as a validator/eval-enforced factory output."
scorecard_blocks_closure: yes
scorecard_required_action: "Implement the gate as a small factory-stage contract plus focused validation before claiming readiness."
```

## Strategic Direction

Add a named `first-principles-gate` to both factories. It should run before
create, harden, refactor, and plugin package design decisions.

The gate should return one decision:

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

The gate should require:

- desired user outcome;
- user-specific constraints;
- copied assumption being challenged;
- fundamental truths or constraints;
- smallest reusable cognitive or runtime move;
- artifact choice and rejected alternatives;
- evidence required before acting;
- validation proof;
- stop or pivot condition.

## Non-Negotiables

- Do not add a broad standalone "first principles" skill unless evidence shows
  repeated cross-factory demand that cannot be solved by routing, hooks,
  references, or validators.
- Do not let the gate become long loaded prose. Keep the always-loaded rule
  short and move examples/schema detail into references.
- Do not claim that structural validation proves usefulness. It only proves the
  gate was recorded and obvious failure modes were checked.
- Do not make hooks responsible for enforcement. Hooks should inject bounded
  context; validators and evals should enforce readiness.

## Safe Rewrite Zones

- Factory router procedures can gain a short mandatory checkpoint.
- Existing SessionStart hook scripts can inject the checkpoint in compact form.
- Factory reference files can carry full schemas and examples.
- Existing validation scripts can add warnings or failures for missing
  first-principles evidence.
- Factory eval fixtures can add cases where the correct answer is
  `IMPROVE_EXISTING` or `DO_NOT_BUILD`.

## Deletion Or Rejection Candidates

- New skill/plugin requests that only restate another package's shape.
- Plugin designs that expose many overlapping root-visible skills without a
  single capability promise.
- Skill drafts that only preserve documentation, not a reusable operating move.
- Hooks added because hooks are now available, rather than because runtime
  behavior should travel with the plugin.
- Governance artifacts that do not change routing, proof, deletion, or drift
  behavior.

## Smallest Feedback-Producing Next Slice

Implement one reversible slice:

1. Add compact first-principles checkpoint text to the two factory router
   entrypoints.
2. Extend the two existing factory SessionStart hook scripts with the same
   compact checkpoint.
3. Add a reference schema for factory gate output.
4. Add tests or validation checks that fail or warn when factory-created
   artifacts omit the gate.
5. Add one positive eval where the gate chooses `BUILD_SKILL` and one negative
   eval where it chooses `DO_NOT_BUILD` or `IMPROVE_EXISTING`.

This is the smallest slice because it changes routing and proof behavior before
building MCP tools, apps, or larger factory infrastructure.

## Stop Or Pivot Condition

Stop if the checkpoint increases loaded context or ceremony without changing a
factory decision in tests or eval fixtures.

Pivot to eval-only enforcement if the router and hook text are enough for human
readability but do not improve generated package decisions.

Pivot to MCP tooling only after the gate's output schema proves useful in at
least one factory validation run.

## Drift Or Moat Impact

Moat impact: high, if implemented as proof-backed artifact selection.

The change strengthens the existing moat because it reinforces the repository's
strategic spine: smaller deterministic command surfaces, proof-backed
promotion, context-budgeted routing, and skepticism of breadth without proof.

Drift risk: medium. The idea can easily drift into another philosophy section.
Keep it as a small gate with validation and eval evidence.

## Future-Agent Guidance

Future agents should treat this strategy as permission to plan the gate, not as
permission to implement broad factory rewrites. Start with the smallest slice:
router checkpoint, hook context, reference schema, and validation/eval proof.

If asked to implement, avoid adding new package surfaces first. The order is:

1. checkpoint contract;
2. hook context;
3. validation/eval proof;
4. only then MCP/app automation if the schema proves useful.

## Evidence And Traceability Matrix

| Claim | Evidence | Confidence | Impact |
|---|---|---:|---|
| Factory value should be proof-backed capability, not package volume | `.harness/strategy/agent-skills-strategy.md` rejects skill/plugin count as moat and names proof-backed local control as the spine | High | High |
| A first-principles gate belongs before factory build decisions | `first-principles-contract.md` requires challenging copied patterns before adding skills, evals, routing, governance, or lifecycle gates | High | High |
| Current hooks are useful but not sufficient enforcement | `session_start_routing.py` and `session_start_contract.py` inject context only; validators/evals provide deterministic completion | High | Medium |
| Plugin Factory should reason about runtime behavior that travels with the plugin | `plugin-factory-router/SKILL.md` already names bundled hook surface, side-effect classes, install determinism, and eval coverage | High | High |
| Skill Factory should reason about the smallest reusable cognitive move | `skill-factory-router/SKILL.md` requires one primary lane and applies the local design contract to skill creation/hardening/refactor handoff | High | High |
| The next slice should be small and reversible | `xp-operating-contract.md` requires the smallest feedback-producing next slice and stop/pivot condition | High | Medium |
