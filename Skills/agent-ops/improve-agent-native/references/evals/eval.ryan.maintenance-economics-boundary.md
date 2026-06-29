# eval.ryan.maintenance-economics-boundary: Cheap Code Still Needs Maintenance Boundaries

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.maintenance-economics-boundary.md

Knowledge claim: Principle under test: The agent evaluates maintenance burden, supply-chain risk, toolchain surface area, pinning, cooldown policy, and whether the dependency should be removed, internalized, or avoided.
Behavior under test: Observable agent behavior when an agent proposes adding a dependency or tool because code generation makes implementation cheap.
Failure mode: The agent treats low implementation cost as sufficient reason to expand the dependency or tool surface.
Expected agent move: The agent evaluates maintenance burden, supply-chain risk, toolchain surface area, pinning, cooldown policy, and whether the dependency should be removed, internalized, or avoided.
Skill lift before failure: The agent treats low implementation cost as sufficient reason to expand the dependency or tool surface.
Skill lift after behavior: The agent evaluates maintenance burden, supply-chain risk, toolchain surface area, pinning, cooldown policy, and whether the dependency should be removed, internalized, or avoided.
Observable delta: The response avoids the weak pattern (The agent treats low implementation cost as sufficient reason to expand the dependency or tool surface) and instead shows the expected behavior (The agent evaluates maintenance burden, supply-chain risk, toolchain surface area, pinning, cooldown policy, and whether the dependency should be removed, internalized, or avoided).

Given: An agent proposes adding a dependency or tool because code generation makes implementation cheap.
Should: The agent evaluates maintenance burden, supply-chain risk, toolchain surface area, pinning, cooldown policy, and whether the dependency should be removed, internalized, or avoided.
Expected failure: The agent treats low implementation cost as sufficient reason to expand the dependency or tool surface.

Bad answer patterns:
- The agent treats low implementation cost as sufficient reason to expand the dependency or tool surface.

Good answer patterns:
- The agent evaluates maintenance burden, supply-chain risk, toolchain surface area, pinning, cooldown policy, and whether the dependency should be removed, internalized, or avoided.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
