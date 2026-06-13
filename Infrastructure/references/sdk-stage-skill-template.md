# SDK Stage Skill Template

SDK-created deterministic stage skills use this fixed SKILL.md heading order.
The shape is enforced by Infrastructure/scripts/validation-and-linting/check_sdk_stage_skill_shape.py
for every skill whose frontmatter declares metadata.sdk_stage.
The current compact contract is sdk-compact-stage-v1; governance detail lives in
the required companion files instead of expanding the SKILL.md entrypoint.

## Required heading order

When to use
Required inputs
Deliverables
Procedure
Validation
Handoff
Failure modes
Gotchas
References

## Section intent

When to use states the positive trigger for this exact stage.
Required inputs lists the source evidence needed before the stage can run.
Deliverables names the artifact or response shape this stage must produce.
Procedure gives the deterministic stage workflow.
Validation names the fail-fast validation posture for the stage.
Handoff names the next stage or blocker handoff rule.
Failure modes names the standard blocker routes.
Gotchas captures recurring confusion and cache drift.
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
