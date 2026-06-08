# SDK Stage Skill Template

SDK-created deterministic stage skills use this fixed SKILL.md heading order.
The shape is enforced by Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py
for every skill whose frontmatter declares metadata.sdk_stage.

## Required heading order

Stage Contract
When to use
When not to use
Required inputs
Deliverables
Preconditions
Procedure
Allowed writes
Forbidden writes
Exit criteria
Validation
Handoff
Failure modes
Execution boundaries
Gotchas
Examples
References

## Section intent

Stage Contract names the previous, current, and next lifecycle stages and the stage purpose.
When to use states the positive trigger for this exact stage.
When not to use blocks stage blending, skipped lifecycle work, and authority overreach.
Required inputs lists the source evidence needed before the stage can run.
Deliverables names the artifact or response shape this stage must produce.
Preconditions names freshness, authority, and evidence-boundary checks that must happen before work.
Procedure gives the deterministic stage workflow.
Allowed writes scopes writes owned by the current stage.
Forbidden writes names generated surfaces, external systems, and downstream stage work that this stage must not mutate.
Exit criteria defines what must be true before handoff.
Validation names the fail-fast validation posture for the stage.
Handoff names the next stage or blocker handoff rule.
Failure modes names the standard blocker routes.
Execution boundaries carries safety, evidence separation, prompt-injection, and authority boundaries.
Gotchas captures recurring confusion and cache drift.
Examples gives short good and bad examples without expanding the entrypoint into a tutorial.
References links the companion SDK files that make the stage machine-readable.
References must include source-context.yaml, which records template provenance, original reference files, imported context indexes, and archived context locations used to shape the skill.

## Required companion files

- references/contract.yaml
- references/evals.yaml
- references/task-profile.json
- references/source-context.yaml
- agents/openai.yaml

source-context.yaml is the deterministic provenance record for SDK-created stage skills. Use it to capture original reference files, archived context, imported templates, and non-canonical context that should remain discoverable without bloating SKILL.md.

Each original_references entry should include load_when so agents can decide whether to load the file without broad reference-chasing. For example, domain-model-routing.md should be loaded when domain language, product behavior, workflow state, integration, persistence, or closure confidence affects routing or handoff.
