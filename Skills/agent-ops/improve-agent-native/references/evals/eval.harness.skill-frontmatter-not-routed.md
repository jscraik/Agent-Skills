# eval.harness.skill-frontmatter-not-routed: Skill Frontmatter Not Routed

Given: A detailed skill contains correct instructions, but cold agents often do not select it for the tasks it is meant to govern.
Should: The agent treats the short description and trigger surface as the first thing to test and repair.
Expected failure: The agent keeps adding detail to the skill body even though routing is the failing layer.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.

## Skill-Local Evidence Boundary

Failure category: seed eval requires behavioural scenario conversion.
Evidence boundary: this fixture is skill-local evidence at references/evals/eval.harness.skill-frontmatter-not-routed.md; it does not by itself prove repository, pull request, remote-check, merge-readiness, or Tessl-readiness outcomes.
Durable mechanism: use this fixture to generate scenario criteria that require the agent to test the skill description, handle, and routing metadata as the first failure surface before editing deeper skill content.
Validation status: not_run_with_reason until the scenario is executed by the local pipeline and private Tessl eval lane.
