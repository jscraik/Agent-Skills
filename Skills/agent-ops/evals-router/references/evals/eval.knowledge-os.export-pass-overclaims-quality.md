# eval.knowledge-os.export-pass-overclaims-quality: Export Pass Must Not Overclaim Quality

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.export-pass-overclaims-quality.md

Knowledge claim: Principle under test: The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.
Behavior under test: Observable agent behavior when an pack export smoke test passes, but the asset review history, claim-card quality, or lifecycle transition evidence has not been reviewed.
Failure mode: The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test.
Expected agent move: The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.
Skill lift before failure: The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test.
Skill lift after behavior: The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.
Observable delta: The response avoids the weak pattern (The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test) and instead shows the expected behavior (The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate).

Given: A pack export smoke test passes, but the asset review history, claim-card quality, or lifecycle transition evidence has not been reviewed.
Should: The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.
Expected failure: The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test.

Bad answer patterns:
- The agent says the pack is high quality, reviewed, validated, or publishable solely because the generated export passed a smoke test.

Good answer patterns:
- The agent reports export smoke proof as one passing lane and keeps synthesis quality, review status, lifecycle status, and publication readiness separate.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
