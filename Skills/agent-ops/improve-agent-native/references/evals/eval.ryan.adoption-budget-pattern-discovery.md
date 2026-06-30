# eval.ryan.adoption-budget-pattern-discovery: Adoption Budget Pattern Discovery

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.adoption-budget-pattern-discovery.md

Knowledge claim: Principle under test: The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.
Behavior under test: Observable agent behavior when an leader asks whether to cap agent token spend tightly across the whole organization before teams know which workflows create leverage.
Failure mode: The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows.
Expected agent move: The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.
Skill lift before failure: The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows.
Skill lift after behavior: The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.
Observable delta: The response avoids the weak pattern (The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows) and instead shows the expected behavior (The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success).

Given: A leader asks whether to cap agent token spend tightly across the whole organization before teams know which workflows create leverage.
Should: The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.
Expected failure: The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows.

Bad answer patterns:
- The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows.

Good answer patterns:
- The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
