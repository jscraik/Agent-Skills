# eval.ryan.long-term-coherence-governance: Long-Term Coherence Governance

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.long-term-coherence-governance.md

Knowledge claim: Principle under test: The agent reviews precedent across generated surfaces, identifies the durable ownership boundary, decides whether to promote the learning into a ledger, validator, runbook, or skill, and defines pruning or review criteria so the artifact stays coherent over future changes.
Behavior under test: Observable agent behavior when an repeated agent mistake has already been fixed locally, but similar generated artifacts and steering patterns are likely to recur across future work.
Failure mode: The agent adds another local note or one-off fix without deciding how the learning scales to future agents and future generated artifacts.
Expected agent move: The agent reviews precedent across generated surfaces, identifies the durable ownership boundary, decides whether to promote the learning into a ledger, validator, runbook, or skill, and defines pruning or review criteria so the artifact stays coherent over future changes.
Skill lift before failure: The agent adds another local note or one-off fix without deciding how the learning scales to future agents and future generated artifacts.
Skill lift after behavior: The agent reviews precedent across generated surfaces, identifies the durable ownership boundary, decides whether to promote the learning into a ledger, validator, runbook, or skill, and defines pruning or review criteria so the artifact stays coherent over future changes.
Observable delta: The response avoids the weak pattern (The agent adds another local note or one-off fix without deciding how the learning scales to future agents and future generated artifacts) and instead shows the expected behavior (The agent reviews precedent across generated surfaces, identifies the durable ownership boundary, decides whether to promote the learning into a ledger, validator, runbook, or skill, and defines pruning or review criteria so the artifact stays coherent over future changes).

Given: A repeated agent mistake has already been fixed locally, but similar generated artifacts and steering patterns are likely to recur across future work.
Should: The agent reviews precedent across generated surfaces, identifies the durable ownership boundary, decides whether to promote the learning into a ledger, validator, runbook, or skill, and defines pruning or review criteria so the artifact stays coherent over future changes.
Expected failure: The agent adds another local note or one-off fix without deciding how the learning scales to future agents and future generated artifacts.

Bad answer patterns:
- The agent adds another local note or one-off fix without deciding how the learning scales to future agents and future generated artifacts.

Good answer patterns:
- The agent reviews precedent across generated surfaces, identifies the durable ownership boundary, decides whether to promote the learning into a ledger, validator, runbook, or skill, and defines pruning or review criteria so the artifact stays coherent over future changes.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
