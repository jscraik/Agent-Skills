# Agent-Native Skill Contract

Use this reference when creating, hardening, auditing, or refactoring any skill. A skill is agent-native when another Codex thread can run it from the visible `SKILL.md` contract without private context, hidden assumptions, or fabricated completion evidence.

This contract is enforced by `bash Infrastructure/scripts/lint_progressive_disclosure.sh --mode strict`. Every canonical skill must expose:

- execution boundaries
- expected artifacts
- repair or failure behavior
- validation or acceptance criteria

## Source Patterns

This contract extracts reusable patterns from OpenAI-authored operational skills:

- `hatch-pet`: strong model for generated artifacts, manifest ownership, subagent handoff, provenance, visual/domain QA, and smallest-scope repair.
- `cli-creator`: strong model for durable command surfaces, auth/config precedence, stable JSON, install smoke tests, fixture/live separation, and companion-skill handoff.

Do not copy either skill verbatim as the default house style. Copy the operating contracts and adapt the length to the real workflow.

## Required Surfaces

### Execution Boundaries

Every skill must make ownership explicit:

- what this skill owns
- what it delegates to another skill, tool, script, CLI, or subagent
- what deterministic helpers may and may not do
- what requires explicit user approval
- what blocks the run instead of allowing a silent fallback

Good boundary language names tempting shortcuts directly. For generated artifacts, prohibit hand-editing manifests, copying files into expected output paths, fabricating missing outputs, or claiming external jobs completed without source evidence. For CLIs and automations, prohibit broad write commands, unsafe shell interpolation, token printing, and live writes without explicit approval or a draft/dry-run path.

### Expected Artifacts

Every skill must define the output contract:

- final files, reports, manifests, package paths, generated assets, or command outputs
- machine-readable fields such as `schema_version`, `validation_evidence`, `context_routes`, or `selected_source`
- required source provenance, such as original generated-image paths, API response IDs, command names, issue URLs, or fixture paths
- where intermediate and QA artifacts live when the workflow is multi-step

Advisory-only skills still need an artifact contract: the response shape, evidence fields, finding format, or handoff status they return.

### Repair Or Failure Behavior

Every skill must say how to recover when validation fails:

- fix the smallest failing scope first
- preserve the canonical source of truth and provenance
- rerun the focused failed validation before broader gates
- report exact blockers when permissions, source artifacts, credentials, toolchains, or runtime capabilities are missing
- avoid restarting a whole workflow when one row, command, fixture, or output phase failed

No silent fallback is part of this contract. If a workflow requires subagents, a live API, a browser artifact, or a trusted CLI install, the skill must stop and name the blocker when that dependency is unavailable unless the user explicitly authorizes a lower-fidelity path.

### Validation Or Acceptance Criteria

Every skill must define done:

- automated command outcomes recorded as `pass`, `fail`, or `blocked`
- domain review criteria that automation cannot fully judge
- artifact existence and non-empty checks
- provenance checks for generated or external outputs
- residual risk and rollback/follow-up ownership

Validation is necessary but not always sufficient. For visual, editorial, migration, security, or CLI usability workflows, include the human/domain review that must pass before completion is claimed.

## Advanced Operational Skill Shape

Use the fuller operational shape when a skill has generated artifacts, subagents, live services, credentials, external state, install steps, or multi-phase repair.

Recommended sections:

- `Start` or `When to use`: classify the request and first real job.
- `Execution Boundaries`: ownership, delegation, approvals, and invalid shortcuts.
- `Command/Artifact Contract`: stable verbs or file paths, JSON/error policy, manifests, and QA outputs.
- `Auth and Config`: precedence, redaction, offline/fixture mode, and missing setup reporting.
- `Workflow`: source inventory, scaffold/build, install/package, smoke test, validation.
- `Delegation Contract`: parent-owned writes, worker input, worker QA, return format, and no manifest races.
- `Repair Workflow`: smallest failing scope, provenance-preserving repair, and rerun command.
- `Acceptance Criteria`: exact artifacts, validation results, domain review, and risks.
- `Companion Skill` or `Handoff`: how future Codex threads should use the tool or artifact safely.

Keep the entrypoint compact enough to route and execute. Move deep policy, examples, API details, prompt details, schemas, fixtures, and long command matrices into `references/` with `Read when:` signposts.

## CLI-Specific Extraction

For skills that create or rely on durable CLIs, preserve these `cli-creator` patterns:

- Check whether the target command already exists before scaffolding.
- Choose the least surprising installed toolchain and state why before coding.
- Sketch the command surface before implementation: discovery, resolve, read, narrow write, doctor, raw escape hatch, auth/config, and install path.
- Require `--json` to be stable and credential-safe, including machine-readable errors.
- Prefer auth precedence of standard environment variable, simple user config, then explicit one-off flag.
- Implement `doctor --json` so future agents can classify auth, config, version, endpoint reachability, fixture/offline mode, and missing setup.
- Keep write commands narrow, named, and draft/dry-run first when possible.
- Install the CLI on `PATH` and smoke-test from another repo or `/tmp`, not just through source-folder wrappers.
- Keep deterministic extraction separate from model interpretation for log or artifact tools.
- Pair durable CLIs with a companion skill that tells future Codex threads which command to run first, the safe read path, the intended draft/write path, the raw escape hatch, and what needs explicit approval.

## Generated-Artifact Extraction

For skills that create images, media, reports, packages, migrations, or other generated outputs, preserve these `hatch-pet` patterns:

- Separate creative/generative work from deterministic assembly and validation.
- Treat manifests and provenance files as parent-owned when workers or subagents are involved.
- Attach grounding inputs whenever a generated row, phase, or artifact depends on a previous source of truth.
- Review generated outputs for identity, intent, and forbidden artifacts even when deterministic validation passes.
- Use targeted repair queues instead of regenerating the whole output.
- Return exact package paths and QA artifacts before claiming the workflow is done.

## Validator Mapping

The strict progressive-disclosure lint accepts equivalent section names so existing concise skills do not need duplicate headings:

- Execution boundaries: `Execution boundaries`, `Boundary map`, `Safety`, `Safety Rules`, `Constraints`, `Rules`, `Avoid`, `Do not use`, or `Anti-Patterns`.
- Expected artifacts: `Expected artifacts`, `Deliverables`, `Outputs`, `Output contract`, or `Acceptance Criteria`.
- Repair or failure loop: `Repair loop`, `Repair workflow`, `Failure mode`, `Validation`, `Gotchas`, `Safety`, or `Anti-Patterns`.
- Validation or acceptance criteria: `Validation`, `Acceptance Criteria`, `Deliverables`, `Outputs`, or `Output contract`.

Use the clearer explicit headings for new complex skills. Use equivalent headings only when they already fit the skill's domain language.
