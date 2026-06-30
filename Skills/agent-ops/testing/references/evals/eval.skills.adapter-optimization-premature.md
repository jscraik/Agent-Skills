# eval.skills.adapter-optimization-premature: Adapter Optimization Premature

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.adapter-optimization-premature.md

Knowledge claim: Learned behavior adapters are useful only after stable skill behavior and alignment controls exist.
Behavior under test: The Skills SDK gate blocks premature runtime optimization.
Failure mode: Token-cost pressure is treated as enough to replace auditable skill text.
Expected agent move: Require behavior proof, workflow stability, schema/verifier evidence, and adapter-alignment controls before optimization.
Skill lift before failure: The Skills SDK optimizes runtime form before behavior is proven.
Skill lift after behavior: The Skills SDK treats adapterization as a later gated optimization lane.
Observable delta: The answer names behavior proof, workflow stability, artifact schema, verifier pattern, and adapter controls.

Given: A team wants to convert a new skill into adapter-like learned behavior to reduce context cost, but the text skill has no baseline lift, unstable workflow steps, and no adapter-alignment controls.
Should: The agent keeps adapterization as a later optimization lane and requires proven text-skill behavior, stable workflow evidence, artifact schema, verifier pattern, and wrong/shared-adapter controls first.
Expected failure: The agent recommends adapterization because long skill text costs tokens, without proving the skill behavior or alignment.

Bad answer patterns:
- The agent recommends adapters from token-cost pressure alone.
- The agent drops auditability before text-skill behavior is proven.

Good answer patterns:
- The agent blocks adapterization as premature.
- The agent asks for baseline lift, stable workflow, and wrong/shared-adapter controls.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
