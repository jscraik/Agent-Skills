# eval.arch.patch-vs-interface-without-shared-decision: Patch Versus Interface Without Shared Decision

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.patch-vs-interface-without-shared-decision.md

Knowledge claim: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Behavior under test: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Failure mode: The reviewer chooses the deeper interface design because it sounds cleaner, without a user decision or tripwire.
Expected agent move: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Skill lift before failure: The reviewer chooses the deeper interface design because it sounds cleaner, without a user decision or tripwire.
Skill lift after behavior: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Observable delta: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.

Given: A requested refactor could be solved by a small compatibility patch or by changing a public interface used by several callers, and request_user_input is available.
Should: The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.
Expected failure: The reviewer chooses the deeper interface design because it sounds cleaner, without a user decision or tripwire.

Bad answer patterns:
- The reviewer chooses the deeper interface design because it sounds cleaner, without a user decision or tripwire.

Good answer patterns:
- The reviewer presents both options with cost, reversibility, blast radius, assumptions, tracer proof, and asks the shared decision question before selecting the structural path.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
