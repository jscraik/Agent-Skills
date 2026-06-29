# Sociotechnical Adoption

Account for perception lag, pair-programming lock-in, capability refresh, and product education as part of agent adoption.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: sociotechnical_adoption
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.public-perception-lag: Public Perception Lags AI Capability

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Public perception of AI tools can remain anchored to early modality failures long after frontier capability has changed.

Interpretation notes:
- This is an adoption and product-education claim.

### claim.ryan.coding-agent-perception-lock: Coding Agents Risk Pair-Programming Perception Lock

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Coding agents risk being publicly understood as interactive pair-programming tools even when frontier use has moved beyond that mode.

Interpretation notes:
- This suggests that product education and workflow design are part of adoption.

### claim.ryan.ai-priors-monthly: AI Working Patterns Need Frequent Prior Updates

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

AI capability changes fast enough that teams need to update assumptions and working patterns frequently.

Interpretation notes:
- This supports scheduled capability reviews and workflow refreshes.

### claim.ryan.codex-product-research-vehicle: Codex Is Both Product And Research Vehicle

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Codex should be understood as both a scaled product surface and a high-velocity research delivery vehicle.

Interpretation notes:
- This supports frequent reassessment of product behavior, workflows, and operator patterns.

## Principles

### principle.ryan.sociotechnical-priors-need-education: Sociotechnical Priors Need Product Education

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.public-perception-lag, claim.ryan.coding-agent-perception-lock, claim.ryan.ai-priors-monthly

AI adoption requires active product education and workflow updates because user priors lag rapidly changing capability.

Rationale: If the modality looks unchanged, users may keep judging tools by early failure modes or narrow usage patterns.

Application notes:
- Teach users what new capability changes in the workflow.
- Show frontier usage patterns in-product where possible.
- Track whether operators are using the tool at current capability level.

### principle.ryan.ai-priors-refresh-continuously: Refresh AI Priors Continuously

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.ai-priors-monthly, claim.ryan.codex-product-research-vehicle

Principal engineers should regularly refresh assumptions about AI capability and update working patterns accordingly.

Rationale: Agent products and research surfaces change rapidly enough that old workflows can become stale within weeks.

Application notes:
- Schedule recurring workflow and capability reviews.
- Treat surprising product behavior as a prompt to update operating practice.
- Distinguish stable principles from model- or product-version assumptions.

## Heuristics

### heuristic.ryan.educate-users-past-perception-lock: Educate Users Past Perception Lock

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.public-perception-lag, claim.ryan.coding-agent-perception-lock

When capability changes inside the same product modality, explicitly teach the new workflow rather than assuming users will update priors themselves.

Use when:
- A tool's capability has improved but users keep applying old mental models.
- Product behavior looks familiar while the operating model has changed.
- Adoption depends on users moving from pair programming to delegated agent workflows.

Avoid when:
- The new capability is not reliable enough to recommend broadly.
- The education would overclaim readiness beyond current evidence.

## Eval Scenarios

### eval.ryan.perception-lock-adoption-decision: Perception Lock Adoption Decision

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.public-perception-lag, claim.ryan.coding-agent-perception-lock

Knowledge claim: Principle under test: The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.
Behavior under test: Observable agent behavior when users still treat a current coding agent as an interactive pair-programming assistant and avoid longer-horizon delegated workflows.
Failure mode: The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence.
Expected agent move: The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.
Skill lift target: The response avoids the weak pattern (The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence) and instead shows the expected behavior (The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.perception-lock-adoption-decision.md
Promotion status: candidate
Capsule refs: principal-engineering
Weak eval flags: none

Given: Users still treat a current coding agent as an interactive pair-programming assistant and avoid longer-horizon delegated workflows.
Should: The agent distinguishes stale capability priors from genuine product reliability gaps, checks current evidence before making adoption claims, proposes in-product examples or workflow education, defines adoption metrics, and avoids overclaiming unsupported capability.
Expected failure: The agent assumes adoption resistance is only user education, or assumes the product is unreliable without checking current capability evidence.
Reproduce with: references/evals/eval.ryan.perception-lock-adoption-decision.md
