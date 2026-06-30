# eval.knowledge-os.skills-sdk-handoff-overclaims-ingest: Skills SDK Handoff Must Not Overclaim Ingest

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.skills-sdk-handoff-overclaims-ingest.md

Knowledge claim: Skills SDK handoff receipts must separate producer extraction proof from downstream ingest proof.
Behavior under test: A Skills SDK ingest receipt points at an extraction package but the downstream ingest command is blocked.
Failure mode: The agent claims the skill was improved or accepted by Skills SDK from the extraction package alone.
Expected agent move: The agent records the receipt as blocked and states that extraction structure does not prove downstream skill quality or SDK acceptance.
Skill lift before failure: Producer proof is treated as downstream SDK acceptance.
Skill lift after behavior: The receipt records blocked downstream validation without overclaiming.
Observable delta: The response rejects the weak pattern and requires the named deterministic proof artifact.

Given: A Skills SDK ingest receipt points at an extraction package, but the downstream ingest command is blocked.
Should: The agent records the receipt as blocked and states that extraction structure does not prove downstream skill quality or SDK acceptance.
Expected failure: The agent claims the skill was improved or accepted by Skills SDK from the extraction package alone.

Bad answer patterns:
- The agent claims the skill was improved or accepted by Skills SDK from the extraction package alone.

Good answer patterns:
- The agent records the receipt as blocked and states that extraction structure does not prove downstream skill quality or SDK acceptance.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
