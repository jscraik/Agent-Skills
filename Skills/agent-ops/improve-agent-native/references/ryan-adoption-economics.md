# Adoption Economics

Treat token spend and uncapped expert use as pattern-discovery investment that becomes reusable practice while preserving human authority boundaries.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: adoption_economics
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.token-budgets-rd: Token Budgets Behave Like R&D

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Organizational token budgets can behave like R&D investment before ROI patterns are fully legible.

Interpretation notes:
- This is an adoption and governance claim, not a validation claim.

### claim.ryan.uncapped-systems-thinkers: Systems Thinkers Need Uncapped Exploration

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

High-leverage systems thinkers can have room to explore agent use deeply so the organization can later operationalize effective patterns.

Interpretation notes:
- This supports pattern discovery as an explicit adoption phase.

### claim.ryan.ai-priors-monthly: AI Working Patterns Need Frequent Prior Updates

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

AI capability changes fast enough that teams need to update assumptions and working patterns frequently.

Interpretation notes:
- This supports scheduled capability reviews and workflow refreshes.

### claim.ryan.zero-human-code-forces-harness: Zero Human Code Forces Harness Investment

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Banning direct human-written code can pressure teams to convert every agent failure into permanent repository capability.

Interpretation notes:
- This is an extreme adoption pattern and can be used as a lens, not a universal rule.

### claim.ryan.non-engineers-can-ship-with-harness: Harnesses Can Expand Who Ships

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Once repository legibility, constraints, and evaluation loops mature, non-engineers can safely participate in shipping changes through agents.

Interpretation notes:
- This depends on strong repo constraints and review loops, not merely access to an agent.

### claim.harness.human-authority-boundaries: High-Impact Boundaries Need Human Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Agent autonomy still requires human or governance authority at high-impact boundaries such as release, security policy, identity, authorization, revocation, secrets, and compliance.

Interpretation notes:
- This claim prevents overgeneralizing post-merge review and zero-human-code patterns.

### claim.ryan.practitioner-head-evals: Practitioners Carry Domain Evals In Their Heads

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Practitioners often have strong implicit domain evals derived from the hardest work they have personally done.

Interpretation notes:
- This supports eliciting human expert judgment into eval scenarios and review rubrics.

### claim.ryan.codex-product-research-vehicle: Codex Is Both Product And Research Vehicle

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Codex can be understood as both a scaled product surface and a high-velocity research delivery vehicle.

Interpretation notes:
- This supports frequent reassessment of product behavior, workflows, and operator patterns.

## Principles

### principle.ryan.exploration-budget-for-systems-thinkers: Fund Systems Thinkers To Discover Patterns

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.token-budgets-rd, claim.ryan.uncapped-systems-thinkers

Organizations can give high-leverage systems thinkers enough AI budget to discover reusable operating patterns before optimizing spend.

Rationale: Early agent adoption behaves like R&D; the highest-leverage operators can convert exploration into repeatable workflows for the wider organization.

Application notes:
- Separate exploration budgets from mature ROI tracking.
- Capture discovered patterns into workflows, tools, and training surfaces.
- Move from uncapped discovery to operational guardrails once patterns stabilize.

### principle.ryan.ai-priors-refresh-continuously: Refresh AI Priors Continuously

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.ai-priors-monthly, claim.ryan.codex-product-research-vehicle

Principal engineers can regularly refresh assumptions about AI capability and update working patterns accordingly.

Rationale: Agent products and research surfaces change rapidly enough that old workflows can become stale within weeks.

Application notes:
- Schedule recurring workflow and capability reviews.
- Treat surprising product behavior as a prompt to update operating practice.
- Distinguish stable principles from model- or product-version assumptions.

### principle.ryan.ban-handwork-to-force-system-improvement: Ban Handwork To Force System Improvement

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.zero-human-code-forces-harness, claim.ryan.non-engineers-can-ship-with-harness

Temporarily using a bounded no-direct-human-implementation experiment can expose missing agent capabilities and surface durable system improvements.

Rationale: If humans does not route around the agent inside a deliberately bounded experiment, every failure becomes pressure to improve repo legibility, primitives, lints, review personas, and workflows.

Application notes:
- Use this deliberately as a harness-building constraint, not as performative purity.
- Scope the experiment to reversible, low-blast-radius work and name the human owner who can approve exceptions.
- Set a timebox, rollback path, success metric, and exit criteria before beginning.
- Exclude safety, legal, secret-handling, destructive, customer-impacting, and irreversible production boundaries unless an enforceable review process already covers them.
- Track the missing primitives discovered by agent failure.
- Relax or stop the rule when delivery risk rises faster than the harness is learning.

## Heuristics

### heuristic.ryan.extract-practitioner-head-evals: Extract Practitioner Head Evals

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.practitioner-head-evals

Ask practitioners for the two or three hardest real cases they have solved, then convert those cases into evals, rubrics, or review scenarios.

Use when:
- Building domain evals for agent work.
- A team says quality is obvious but does not yet measure it.
- Expert judgment is tacit and not represented in tests.

Avoid when:
- The cases contain secrets, private customer data, or unsafe operational details.
- The examples are anecdotes without a reproducible input and expected behavior.

## Eval Scenarios

### eval.ryan.adoption-budget-pattern-discovery: Adoption Budget Pattern Discovery

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.token-budgets-rd, claim.ryan.uncapped-systems-thinkers, claim.ryan.non-engineers-can-ship-with-harness

Knowledge claim: Principle under test: The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.
Behavior under test: Observable agent behavior when an leader asks whether to cap agent token spend tightly across the whole organization before teams know which workflows create leverage.
Failure mode: The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows.
Expected agent move: The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.
Skill lift target: The response avoids the weak pattern (The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows) and instead shows the expected behavior (The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.adoption-budget-pattern-discovery.md
Promotion status: candidate
Capsule refs: principal-engineering
Weak eval flags: none

Given: A leader asks whether to cap agent token spend tightly across the whole organization before teams know which workflows create leverage.
Can: The agent distinguishes exploration budget from permanent spend, recommends giving proven systems thinkers enough room to discover reusable patterns, names human authority and ROI-review boundaries, and avoids treating token volume itself as success.
Expected failure: The agent recommends a blanket cap or blanket unlimited spend without a learning loop, ownership model, or route for non-engineers to adopt proven workflows.
Reproduce with: references/evals/eval.ryan.adoption-budget-pattern-discovery.md
