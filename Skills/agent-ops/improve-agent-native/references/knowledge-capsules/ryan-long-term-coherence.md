# Long-Term Coherence

Convert repeated steering, latent prompt principles, self-observability, and artifact precedent into durable environment changes.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: long_term_coherence
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.zero-setup-agent-workspace: Agents Should Set Up The Workspace

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent products should be able to enter a workspace with minimal customer setup and perform their own setup discovery.

Interpretation notes:
- This is a product expectation for agent platforms and repo readiness.

### claim.ryan.prompts-carry-latent-principles: Prompts Carry Latent Principles

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Human prompts often carry unstated higher-level principles that agents should infer and apply beyond the immediate instruction.

Interpretation notes:
- This supports steering capture and principle extraction as part of agent behavior.

### claim.ryan.repeated-steering-environment-failure: Repeated Steering Signals Environment Failure

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Repeated human steering should be treated as high-signal evidence that the agent environment needs refinement.

Interpretation notes:
- This reinforces feedback-to-guardrails as an agent operating contract.

### claim.ryan.long-term-coherence-agent-artifacts: Agent Artifacts Need Long-Term Coherence

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent-produced artifacts should be designed for long-term coherence across thousands of future changes.

Interpretation notes:
- This is an architectural quality bar for agent-generated repos.

### claim.ryan.agent-self-observability-ledgers: Agents Should Record Mistakes Desires And Learnings

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agents can be instructed to record mistakes, missing tools or context, and environment learnings as telemetry surfaces.

Interpretation notes:
- This should be bounded to avoid leaking secrets or local-only sensitive details.

### claim.harness.feedback-becomes-guardrails: Repeated Feedback Should Become Guardrails

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Repeated agent review feedback should be encoded into durable guardrails rather than handled as one-off correction.

Interpretation notes:
- This supports assets about learned fixes and validation-first closeout.

### claim.ryan.work-is-iterative-game: Work Is An Iterative Game

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Work should be treated as iterative rather than a single-pass production act.

Interpretation notes:
- This short claim anchors OODA and evaluation-loop assets.

### claim.ryan.oss-maintenance-runbooks: Agent Maintenance Needs Checked-In Runbooks

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent-maintained repositories should keep golden workflows, onboarding commands, automations, and guardrails in checked-in documentation and runbooks.

Interpretation notes:
- This connects repo knowledge architecture to recurring maintenance work.

## Principles

### principle.ryan.repeated-steering-becomes-environment-change: Repeated Steering Becomes Environment Change

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified, local_source_reference
- Derived from claims: claim.ryan.repeated-steering-environment-failure, claim.harness.feedback-becomes-guardrails

When the same steering recurs, stop treating it as prompt correction and encode the smallest environment change that prevents recurrence.

Rationale: Repeated steering is evidence that the system has failed to absorb an operating principle into docs, tools, validation, or behavior.

Application notes:
- Classify recurring feedback by failure mode.
- Choose the narrowest durable surface: docs, validator, test, hook, runbook, or skill.
- Prove the new surface would have caught or routed the previous failure.

### principle.ryan.long-term-coherence-of-agent-artifacts: Preserve Long-Term Coherence Of Agent Artifacts

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.long-term-coherence-agent-artifacts, claim.ryan.work-is-iterative-game

Optimize agent-produced artifacts for coherence across many future changes, not just acceptance of the current patch.

Rationale: Agent repositories compound local patterns; a change that passes today can still damage the next thousands of PRs if it weakens naming, ownership, boundaries, or generated-surface discipline.

Application notes:
- Review changes for precedent, copyability, and ownership clarity.
- Prefer local fixes that strengthen future agent behavior.
- Reject one-off artifact shapes that future agents are likely to replicate poorly.

## Heuristics

### heuristic.ryan.design-zero-setup-agent-onboarding: Design Zero-Setup Agent Onboarding

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.zero-setup-agent-workspace, claim.ryan.oss-maintenance-runbooks

Design agent products and repos so the agent can discover setup, tools, workflows, and validation without customer integration work.

Use when:
- Building agent workspace onboarding, repo setup, or agent product integrations.
- The user would otherwise need to configure toolchains, commands, or workflow context by hand.
- The repo has enough structure for the agent to inspect and bootstrap.

Avoid when:
- Setup requires explicit credentials, approvals, or organization-specific policy choices.
- Automatic setup would mutate external systems without a permission boundary.

### heuristic.ryan.extract-principles-from-steering: Extract Principles From Steering

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.prompts-carry-latent-principles, claim.ryan.repeated-steering-environment-failure

When a human gives corrective steering, infer the higher-level principle and decide whether it belongs in a durable repo surface.

Use when:
- The steering sounds transferable beyond the current task.
- The same correction has appeared before.
- The correction reveals a missing quality bar, ownership rule, or workflow expectation.

Avoid when:
- The steering is a one-off personal preference or local secret.
- The inferred principle would overgeneralize from weak evidence.

### heuristic.ryan.instrument-agent-self-observability: Instrument Agent Self-Observability

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.agent-self-observability-ledgers

Ask agents to record mistakes, missing tools or context, and environment learnings in durable ledgers that can be reviewed and turned into harness changes.

Use when:
- A repo wants telemetry about recurring agent failure modes.
- Operators need to know what context or tools agents wished they had.
- Learnings can be reviewed before being promoted into durable guidance.

Avoid when:
- The ledgers would capture secrets, private telemetry, credentials, or local-only provenance.
- The repo lacks a review loop to prune or act on the accumulated notes.

## Checklists

### checklist.ryan.long-term-coherence-review: Long-Term Coherence Review

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.long-term-coherence-agent-artifacts, claim.ryan.repeated-steering-environment-failure, claim.ryan.agent-self-observability-ledgers

- [ ] Identify what precedent the change creates for future agents.
- [ ] Check whether ownership, authority, and invariants are encoded in the artifact shape.
- [ ] Convert repeated steering into a durable environment change or record why not.
- [ ] Verify generated or tool-owned files are changed only through the correct ownership path.
- [ ] Record mistakes, missing tools, or environment learnings in reviewed ledgers when useful.
- [ ] Ask whether this artifact remains coherent after thousands of similar future changes.

## Eval Scenarios

### eval.ryan.long-term-coherence-governance: Long-Term Coherence Governance

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.long-term-coherence-agent-artifacts, claim.ryan.agent-self-observability-ledgers

Given: A repeated agent mistake has already been fixed locally, but similar generated artifacts and steering patterns are likely to recur across future work.
Should: The agent reviews precedent across generated surfaces, identifies the durable ownership boundary, decides whether to promote the learning into a ledger, validator, runbook, or skill, and defines pruning or review criteria so the artifact stays coherent over future changes.
Expected failure: The agent adds another local note or one-off fix without deciding how the learning scales to future agents and future generated artifacts.
Reproduce with: references/evals/eval.ryan.long-term-coherence-governance.md
