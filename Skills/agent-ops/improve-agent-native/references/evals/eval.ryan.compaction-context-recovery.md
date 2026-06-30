# eval.ryan.compaction-context-recovery: Compaction Requires Context Recovery

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.compaction-context-recovery.md

Knowledge claim: Principle under test: The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.
Behavior under test: Observable agent behavior when an agent resumes a long-horizon task after context compaction with only a partial summary.
Failure mode: The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context.
Expected agent move: The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.
Skill lift before failure: The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context.
Skill lift after behavior: The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.
Observable delta: The response avoids the weak pattern (The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context) and instead shows the expected behavior (The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing).

Given: An agent resumes a long-horizon task after context compaction with only a partial summary.
Should: The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.
Expected failure: The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context.

Bad answer patterns:
- The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context.

Good answer patterns:
- The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
