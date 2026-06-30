# eval.skills.routing-scale-regression: Routing Scale Regression

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.routing-scale-regression.md

Knowledge claim: Growing a skill library can degrade selection quality even when individual skill files are valid.
Behavior under test: The Skills SDK gate requires routing regression checks after library growth.
Failure mode: Individual package validation is accepted as library-level routing health.
Expected agent move: Request selection accuracy, negative routing, duplicate-overlap, and library maintenance checks.
Skill lift before failure: The Skills SDK treats individual package validation as library health.
Skill lift after behavior: The Skills SDK requires routing regression and overlap checks.
Observable delta: The answer names selection accuracy, non-trigger, duplicate-overlap, and maintenance checks.

Given: A registry import adds many related skills and the package audit passes, but no one reruns selection accuracy checks, non-trigger cases, or duplicate-overlap analysis after the library size increase.
Should: The agent treats library growth as a routing-regression risk and asks for selection, non-selection, overlap, and maintenance evidence before accepting the import.
Expected failure: The agent accepts the larger library because every individual skill package validates.

Bad answer patterns:
- The agent says library import is ready because package audit passed.
- The agent ignores overlap and non-trigger checks.

Good answer patterns:
- The agent asks for routing regression evidence.
- The agent separates individual package shape from library selection health.
