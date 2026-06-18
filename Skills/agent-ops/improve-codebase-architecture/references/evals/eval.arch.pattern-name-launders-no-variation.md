# eval.arch.pattern-name-launders-no-variation: Pattern Name Launders No Variation

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.pattern-name-launders-no-variation.md

Knowledge claim: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Behavior under test: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Failure mode: The reviewer praises the pattern because it matches a book category while ignoring local forces and liabilities.
Expected agent move: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Skill lift before failure: The reviewer praises the pattern because it matches a book category while ignoring local forces and liabilities.
Skill lift after behavior: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Observable delta: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.

Given: A refactor proposal introduces a factory, strategy, broker, plugin, or layered pattern around one implementation with no stable variation, compatibility test, or caller simplification.
Should: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Expected failure: The reviewer praises the pattern because it matches a book category while ignoring local forces and liabilities.

Bad answer patterns:
- The reviewer praises the pattern because it matches a book category while ignoring local forces and liabilities.

Good answer patterns:
- The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
