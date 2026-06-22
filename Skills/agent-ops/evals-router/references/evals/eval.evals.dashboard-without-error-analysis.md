# eval.evals.dashboard-without-error-analysis: Dashboard Without Error Analysis

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.evals.dashboard-without-error-analysis.md

Knowledge claim: The testing skill redirects to a bounded trace review, dimensional sample, and failure taxonomy before recommending dashboard metrics.
Behavior under test: The testing skill redirects to a bounded trace review, dimensional sample, and failure taxonomy before recommending dashboard metrics.
Failure mode: The testing skill designs broad generic metrics and skips failure discovery.
Expected agent move: The testing skill redirects to a bounded trace review, dimensional sample, and failure taxonomy before recommending dashboard metrics.
Skill lift before failure: The testing skill designs broad generic metrics and skips failure discovery.
Skill lift after behavior: The testing skill redirects to a bounded trace review, dimensional sample, and failure taxonomy before recommending dashboard metrics.
Observable delta: The testing skill redirects to a bounded trace review, dimensional sample, and failure taxonomy before recommending dashboard metrics.

Given: A team asks for a generic helpfulness dashboard before reviewing traces or naming product-specific failure modes.
Should: The testing skill redirects to a bounded trace review, dimensional sample, and failure taxonomy before recommending dashboard metrics.
Expected failure: The testing skill designs broad generic metrics and skips failure discovery.

Bad answer patterns:
- The testing skill designs broad generic metrics and skips failure discovery.

Good answer patterns:
- The testing skill redirects to a bounded trace review, dimensional sample, and failure taxonomy before recommending dashboard metrics.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
