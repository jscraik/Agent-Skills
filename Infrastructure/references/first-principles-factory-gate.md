# First-Principles Factory Gate

Use this reference before non-trivial Skill Factory or Plugin Factory work that
could create, harden, refactor, skillify, route, package, or expand an agent
capability.

The gate exists to reduce surface area. It should identify the smallest
effective mechanism, including the option to improve an existing artifact,
stay docs-only, or stop.

## Trigger

Run the gate when factory work:

- creates or reshapes a skill or plugin;
- adds scripts, assets, agents, hooks, MCP servers, apps, evals, or other
  package surfaces;
- converts workflow notes or session evidence into durable guidance;
- makes release-readiness, hardening, or routing claims;
- could copy an existing template without proving it fits this user's actual
  job.

For narrow audit-only or read-only analysis, record
`first_principles_gate_status: not_applicable` with the reason.

## Decisions

Select exactly one decision:

- `BUILD_SKILL`: create or reshape a skill because a reusable cognitive move is
  the smallest useful artifact.
- `BUILD_PLUGIN`: create or reshape a plugin because a capability product needs
  package-level ownership or multiple coordinated surfaces.
- `ADD_HOOK`: add hook behavior because lifecycle context, guardrails, or
  validation should travel with an enabled plugin.
- `ADD_MCP_TOOL`: add a tool because the behavior needs structured runtime
  action or data access instead of prose instructions.
- `ADD_APP`: add an app/UI surface because the workflow is visual, stateful, or
  too interactive for text-only operation.
- `ADD_EVAL`: add eval coverage because proof is missing and implementation
  would otherwise be guesswork.
- `IMPROVE_EXISTING`: update an existing skill, plugin, reference, validator,
  hook, or eval instead of creating another artifact.
- `DOCS_ONLY`: capture the knowledge as reference documentation or handoff
  notes without adding runtime behavior.
- `DO_NOT_BUILD`: stop because evidence, ownership, safety, or value is
  insufficient.

## Schema

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

## Fields

- `desired_outcome`: the user-visible result the factory output must improve.
- `user_specific_constraints`: repo, user, workflow, safety, runtime, audience,
  or context-budget constraints.
- `copied_assumption_rejected`: the template, habit, or inherited shape the
  factory refuses to copy without proof.
- `fundamental_constraints`: irreducible facts such as side effects, trigger
  shape, trust boundary, runtime availability, validation surface, and context
  budget.
- `smallest_effective_mechanism`: the smallest artifact or change that can
  produce the desired outcome.
- `artifact_decision`: one decision from the decision list.
- `rejected_alternatives`: plausible options rejected with short reasons.
- `evidence_required`: evidence needed before build, hardening, or route
  selection continues.
- `validation_proof`: command, artifact, review, or eval proof required before
  handoff or readiness claims.
- `stop_or_pivot_condition`: the condition that should stop, route, shrink, or
  defer the work.

## Output Snippet

Use this shape in durable handoffs for non-trivial factory work:

```yaml
first_principles_gate:
  desired_outcome: "<outcome>"
  user_specific_constraints:
    - "<constraint>"
  copied_assumption_rejected: "<copied pattern not accepted as proof>"
  fundamental_constraints:
    - "<constraint>"
  smallest_effective_mechanism: "<smallest useful change>"
  artifact_decision: "BUILD_SKILL|BUILD_PLUGIN|ADD_HOOK|ADD_MCP_TOOL|ADD_APP|ADD_EVAL|IMPROVE_EXISTING|DOCS_ONLY|DO_NOT_BUILD"
  rejected_alternatives:
    - alternative: "<option>"
      reason: "<why rejected>"
  evidence_required:
    - "<evidence>"
  validation_proof:
    - "<proof>"
  stop_or_pivot_condition: "<stop condition>"
```

Chat responses may abbreviate the gate, but durable artifacts and factory
handoffs should preserve enough fields for later validation.

## Examples

### BUILD_SKILL

Use when the reusable value is a compact thinking pattern, routing procedure, or
repair loop that Codex can load only when relevant.

Example decision:

```yaml
artifact_decision: BUILD_SKILL
smallest_effective_mechanism: "Add a focused skill that preserves the review loop and links heavy examples from references."
rejected_alternatives:
  - alternative: BUILD_PLUGIN
    reason: "No package-level runtime behavior or multi-surface ownership is needed."
```

### BUILD_PLUGIN

Use when the capability needs package-level ownership, plugin metadata, bundled
skills, optional hooks, install visibility, or coordinated surfaces.

```yaml
artifact_decision: BUILD_PLUGIN
smallest_effective_mechanism: "Create one plugin that owns the related child skills and package metadata."
rejected_alternatives:
  - alternative: BUILD_SKILL
    reason: "A single skill would hide package ownership and future bundled-hook behavior."
```

### ADD_HOOK

Use when lifecycle behavior should travel with an enabled plugin, such as
SessionStart context or a guardrail before risky tool use.

```yaml
artifact_decision: ADD_HOOK
smallest_effective_mechanism: "Ship plugin-bundled hooks/hooks.json plus a plugin-scoped script path."
validation_proof:
  - "Focused hook contract test proves scoped paths and hook JSON shape."
```

Hooks remain advisory unless later validation and eval proof make enforcement
safe.

### ADD_MCP_TOOL

Use when the capability needs structured runtime action, deterministic data
lookup, or machine-readable output that prose instructions cannot reliably
provide.

```yaml
artifact_decision: ADD_MCP_TOOL
smallest_effective_mechanism: "Expose a read-only tool with stable JSON output instead of asking agents to parse logs manually."
rejected_alternatives:
  - alternative: BUILD_SKILL
    reason: "Instructions alone cannot provide deterministic data access."
```

### ADD_APP

Use when the workflow is visual, stateful, or benefits from direct
manipulation.

```yaml
artifact_decision: ADD_APP
smallest_effective_mechanism: "Add a small UI surface for inspecting and selecting package changes."
rejected_alternatives:
  - alternative: ADD_MCP_TOOL
    reason: "The user needs visual comparison and selection, not only structured output."
```

### ADD_EVAL

Use when the next useful artifact is proof, not more capability surface.

```yaml
artifact_decision: ADD_EVAL
smallest_effective_mechanism: "Add one benchmark case that proves the factory chooses improve-existing instead of new-build when evidence is weak."
stop_or_pivot_condition: "Do not change factory behavior until the eval exposes the failure mode."
```

### IMPROVE_EXISTING

Use when an existing skill, plugin, reference, hook, validator, or eval can be
made better with less surface area than a new artifact.

```yaml
artifact_decision: IMPROVE_EXISTING
smallest_effective_mechanism: "Patch the existing router reference and add a focused test."
rejected_alternatives:
  - alternative: BUILD_SKILL
    reason: "A new skill would duplicate an existing lane."
```

### DOCS_ONLY

Use when the information is useful but does not need runtime routing,
automation, or validation.

```yaml
artifact_decision: DOCS_ONLY
smallest_effective_mechanism: "Record the decision in a reference document and link it from the relevant skill."
validation_proof:
  - "Artifact identity lint passes."
```

### DO_NOT_BUILD

Use when the user job, evidence, ownership, or safety boundary is not clear
enough to justify a new artifact or package change.

```yaml
artifact_decision: DO_NOT_BUILD
evidence_required:
  - "Concrete recurring task evidence"
  - "Clear owner and validation path"
stop_or_pivot_condition: "Resume only after evidence proves this is recurring and valuable."
```

## Phase Boundary

Phase 2 defines the procedure and wires it into factory lanes. It does not add
strict validators, eval fixtures, generated package behavior, MCP/app surfaces,
or hook enforcement.

Phase 3 decides validation warning/failure policy. Phase 4 proves whether the
gate changes factory behavior.
