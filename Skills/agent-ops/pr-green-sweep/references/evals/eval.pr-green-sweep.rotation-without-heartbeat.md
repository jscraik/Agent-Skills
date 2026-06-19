# eval.pr-green-sweep.rotation-without-heartbeat: Rotation Without Heartbeat

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.pr-green-sweep.rotation-without-heartbeat.md

Knowledge claim: Until-green PR sweeps require a heartbeat gate before rotation.
Behavior under test: Heartbeat creation, reuse, update, or blocked reporting before PR mutation.
Failure mode: The agent starts PR rotation without a heartbeat status and stop rule.
Expected agent move: Report heartbeat_status first with a heartbeat id or blocker and stop before edits when heartbeat setup is blocked.
Skill lift before failure: The agent treats until-green as ordinary PR triage.
Skill lift after behavior: The agent gates rotation on heartbeat status and stop rule.
Observable delta: The response starts with heartbeat_status before the action queue.

Given: A user asks the agent to keep rotating through open PRs until they are green.
Should: The agent reports heartbeat_status first and creates, reuses, updates, or blocks on exactly one heartbeat before PR rotation.
Expected failure: The agent skips heartbeat handling and starts patching or summarizing PRs.

Bad answer patterns:
- The agent begins editing or summarizing PRs without heartbeat_status.
- The agent creates duplicate monitors without checking for reuse.

Good answer patterns:
- The agent reports heartbeat_status as created, updated, reused, or blocked before rotation.
- The agent stops before edits when heartbeat creation or reuse cannot be attempted.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
