# eval.ryan.perception-lock-adoption-decision: Perception Lock Adoption Decision

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.perception-lock-adoption-decision.md

Knowledge claim: Principle under test: The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.
Behavior under test: Observable agent behavior when users still treat a current coding agent as an interactive pair-programming assistant and avoid longer-horizon delegated workflows.
Failure mode: The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence.
Expected agent move: The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.
Skill lift before failure: The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence.
Skill lift after behavior: The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.
Observable delta: The response avoids the weak pattern (The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence) and instead shows the expected behavior (The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability).

Given: Users still treat a current coding agent as an interactive pair-programming assistant and avoid longer-horizon delegated workflows.
Should: The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.
Expected failure: The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence.

Bad answer patterns:
- The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence.

Good answer patterns:
- The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
