# Skills SDK Skill Construction Contract

This reference captures the SDK-owned construction rules extracted from the
`writing-great-skills` source material. Use it when creating, installing,
hardening, refactoring, skillifying, or validating a skill package.

The root quality is **Predictability**: the agent should follow the same
process on each run, even when the output varies. The SDK enforces
Predictability through four axes: Invocation, Information Hierarchy, Steering,
and Pruning.

## Invocation

Invocation decides how the skill is reached and which load the system pays.

- A **model-invoked** skill keeps a model-facing `description`. The description
  is always loaded and acts as the top-level context pointer. It must earn that
  context load by using concrete trigger language and a leading word the user
  or adjacent skills actually use.
- A **user-invoked** skill sets `disable-model-invocation: true`. It pays no
  model context load, but the human pays cognitive load because the human must
  remember when to invoke it.
- A **router skill** is the pressure release for many user-invoked skills. It
  names the user-invoked skills and their reach conditions, but it cannot fire
  those skills for the model.

Validator implications:

- Model-invoked descriptions must include action-shaped trigger wording.
- Descriptions must avoid catch-all terms such as "anything", "everything",
  "stuff", and generic "help" unless the skill is deliberately a router.
- Description branches should be distinct. Synonyms that describe the same
  branch are duplication.

## Information Hierarchy

A skill is arranged as Steps and Reference.

- **Steps** are ordered actions in `SKILL.md`. They are the primary tier when a
  skill performs a workflow.
- **Reference** is material the agent consults: facts, definitions, examples,
  parameters, rules, and conditional instructions.
- **Progressive disclosure** moves branch-specific Reference out of
  `SKILL.md` and behind a context pointer so the entrypoint stays legible.
- **Co-location** keeps a concept's definition, rules, and caveats together
  once the material is loaded.

Validator implications:

- A procedural skill must declare an executable Workflow, Procedure, or Steps
  section with action-shaped work.
- Support files must be reachable through `SKILL.md`, `references/contract.yaml`,
  `references/knowledge-capsule-routing.md`, or another package entrypoint.
- Markdown Reference files, including vendored KnowledgeOS capsule bodies, must
  have specific H1 headings aligned to the filename and routing purpose. Generic
  titles such as "Details" or headings that hide the capsule's trigger phrase
  are not invocable enough for package readiness.
- Conditional Reference should not be loaded by default. Inline only material
  needed by every branch.
- Long entrypoints with package references should block until phase detail,
  examples, or branch-specific context move behind pointers.

## Steering

Steering shapes runtime behavior toward Predictability.

- A **leading word** recruits an existing model prior and should appear where it
  anchors invocation or execution. Prefer a known concept over a sentence that
  restates the same behavior repeatedly.
- A **completion criterion** tells the agent when a step is complete. Strong
  criteria are checkable and, when needed, exhaustive.
- **Legwork** is the work the agent does inside a step. Raise it with demand in
  the completion criterion, not by adding vague exhortations.
- **Post-completion steps** can pull the agent into premature completion. First
  sharpen the completion criterion; split the sequence only when the later
  steps must be hidden across a real context boundary.

Validator implications:

- Phase or step-based skills must state advancement blockers, stop conditions,
  or evidence gates.
- Completion criteria must be observable through output, evidence, validation,
  or a routed validation reference.
- Scenario cases must test premature-completion and thin-legwork risks when the
  skill has staged workflows.

## Pruning

Pruning keeps the skill lean enough to stay predictable.

- **Single source of truth** means each behavioral meaning lives in one place.
- **Duplication** repeats the same meaning across places and should be removed
  or collapsed into a leading word.
- **Sediment** is stale or irrelevant accumulated prose.
- **Sprawl** is excessive entrypoint length, even when every line is live.
- **No-op** instructions are lines the model already obeys by default; validate
  them by asking whether the line changes behavior compared with the default.

Validator implications:

- Long paragraphs must carry an action, context pointer, completion criterion,
  output, evidence, or safety obligation.
- Repeated instruction-shaped lines should block package readiness until
  deduplicated or moved into one routed reference.
- Skill edits should prefer deletion, routed references, or leading-word
  collapse before adding more prose.

## SDK Enforcement

The package verifier consumes these rules through `writing_quality` checks:

- `construction_trigger_boundary` covers Invocation.
- `construction_steps_reference_structure` covers Information Hierarchy.
- `construction_steering_phase_gate` covers Steering.
- `construction_pruning_sediment` covers Pruning.

These checks do not prove runtime behavior, OSS profile success, Tessl score, or
registry readiness. They block the package earlier when construction defects
would make later eval evidence noisy or expensive.
