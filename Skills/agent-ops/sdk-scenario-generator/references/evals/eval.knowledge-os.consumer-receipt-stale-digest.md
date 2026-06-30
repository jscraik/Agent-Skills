# eval.knowledge-os.consumer-receipt-stale-digest: Consumer Receipt Must Reject Stale Digest

Promotion status: candidate
Proof route: references/evals.yaml
Fixture path: references/evals/eval.knowledge-os.consumer-receipt-stale-digest.md

Knowledge claim: Consumer receipts must bind downstream validation to the exact feed artifact digest.
Behavior under test: A consumer receipt references a feed path whose recorded digest no longer matches the current feed artifact.
Failure mode: The stale receipt is accepted because the downstream command once passed.
Expected agent move: The agent rejects the receipt and rebuilds or revalidates the feed before using it as consumer proof.
Skill lift before failure: Old downstream proof is reused for a changed feed.
Skill lift after behavior: The receipt is rejected until the digest matches the current feed artifact.
Observable delta: The response rejects the weak pattern and requires the named deterministic proof artifact.

Given: A consumer receipt references a feed path whose recorded digest no longer matches the current feed artifact.
Should: The agent rejects the receipt and rebuilds or revalidates the feed before using it as consumer proof.
Expected failure: The stale receipt is accepted because the downstream command once passed.

Bad answer patterns:
- The stale receipt is accepted because the downstream command once passed.

Good answer patterns:
- The agent rejects the receipt and rebuilds or revalidates the feed before using it as consumer proof.

This is the portable SDK reproduction contract for the eval scenario. The KnowledgeOS authoring fixture remains inside the validation workspace and is not vendored into SDK-ready exports.
