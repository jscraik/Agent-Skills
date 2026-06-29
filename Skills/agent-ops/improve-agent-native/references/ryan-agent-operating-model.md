# Agent Operating Model

Design long-horizon agent work around context seeking, paved workflows, hooks, compaction recovery, and continuous capability refresh.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: agent_operating_model
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.codex-product-research-vehicle: Codex Is Both Product And Research Vehicle

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Codex can be understood as both a scaled product surface and a high-velocity research delivery vehicle.

Interpretation notes:
- This supports frequent reassessment of product behavior, workflows, and operator patterns.

### claim.ryan.multi-trajectory-ooda: Agent OODA Needs to Scale Across Trajectories

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent decision loops need to scale beyond one turn or one trajectory into organizational awareness and stacked-trajectory awareness.

Interpretation notes:
- This is a forward-looking operating-model claim.

### claim.ryan.work-is-iterative-game: Work Is An Iterative Game

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Work can be treated as iterative rather than a single-pass production act.

Interpretation notes:
- This short claim anchors OODA and evaluation-loop assets.

### claim.ryan.context-seeking-framework: Agents Need Context-Seeking Frameworks

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Effective agent harnesses can teach agents how to seek task-relevant context through tools and workflows rather than relying on large piles of static rules.

Interpretation notes:
- This extends repo knowledge from storage into active context-retrieval behavior.

### claim.ryan.context-not-persistent: Long-Horizon Context Is Not Persistent

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Long-horizon agent systems does not assume relevant information will remain in context because compaction and trajectory length continuously change available context.

Interpretation notes:
- This supports resumption keys, context-recovery commands, and durable handoff artifacts.

### claim.ryan.prompt-to-paved-workflow: Prompts Can Collapse To Paved Workflows

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent prompts can route into known workflows that explain what matters, common task shapes, and where to learn more.

Interpretation notes:
- This maps directly to skill routing and workflow front doors.

### claim.ryan.autonomy-threshold-tooling: Autonomy Rises With Encoded Development Loops

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent autonomy can increase as the development loop is encoded into tools, including state validation, bug reproduction, evidence capture, fixes, validation, PR creation, feedback handling, build remediation, escalation, and merge.

Interpretation notes:
- This turns autonomy into an evidence-backed tooling threshold rather than a model-confidence claim.

### claim.ryan.jit-context-management: Harness Engineering Is JIT Context Management

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Harness engineering can be understood as just-in-time context management across long-horizon, headless agent trajectories.

Interpretation notes:
- This is a compact definition useful for the downstream skill's theory of operation.

### claim.ryan.hooks-context-delivery: Hooks Can Deliver Context During Runs

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Runtime hooks can be used as context delivery points during an agent run.

Interpretation notes:
- Hook usage remains environment-specific and can preserve runtime support boundaries.

### claim.harness.progressive-disclosure-routing: Progressive Disclosure Needs Routing Proof

- Type: claim-card
- Status: reviewed
- Claim strength: inferred
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

Short skill descriptions and front matter can be tested as routing surfaces, because detailed instructions only help when the agent loads them at the right time.

Interpretation notes:
- The routing-proof phrasing is an inference from the progressive-disclosure practice.

### claim.ryan.ai-priors-monthly: AI Working Patterns Need Frequent Prior Updates

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

AI capability changes fast enough that teams need to update assumptions and working patterns frequently.

Interpretation notes:
- This supports scheduled capability reviews and workflow refreshes.

### claim.ryan.merge-gates-depend-on-recovery-loops: Merge Gates Depend On Recovery Loops

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent throughput changes merge-gate tradeoffs; short-lived pull requests, cheap follow-up correction, and minimal blocking gates can be reasonable only when validation and remediation systems are strong enough.

Interpretation notes:
- The claim is conditional; it does not justify loosening gates without strong recovery loops.

### claim.harness.small-skill-set: Shared Skills Can Stay Few And Dense

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Harness behavior can be concentrated into a small shared set of high-density skills before creating many fragmented workflow artifacts.

Interpretation notes:
- This claim supports skill-surface consolidation guidance.

### claim.harness.source-prompt-coverage: Source Prompt Coverage Limits Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Sampled or partial artifacts may support local work, but they can not become repo-wide authority without equivalent source-prompt coverage evidence.

Interpretation notes:
- This claim is especially relevant when turning research into operational doctrine.

## Principles

### principle.ryan.multi-trajectory-ooda: Design For Multi-Trajectory OODA

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.multi-trajectory-ooda, claim.ryan.work-is-iterative-game, claim.ryan.context-not-persistent

Agent operating systems can support observing, orienting, deciding, and acting across multiple turns, trajectories, and organizational signals.

Rationale: Real work is iterative and often spans stacked trajectories, so agents need durable awareness beyond a single prompt-response loop.

Application notes:
- Preserve decisions, observations, and proof across trajectories.
- Document agent access to visibility into relevant parallel organizational activity where safe.
- Distinguish local trajectory state from program-level state.

### principle.ryan.context-seeking-over-rule-piles: Context Seeking Beats Rule Piles

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified, local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.ryan.context-seeking-framework, claim.ryan.prompt-to-paved-workflow, claim.harness.progressive-disclosure-routing

Agent instructions can define how to seek, select, and apply context instead of trying to preload every rule.

Rationale: Stochastic agents and long-running trajectories need repeatable context-recovery behavior more than static context volume.

Application notes:
- Document for agents what kind of context matters for common task shapes.
- Route prompts to paved workflows and deeper references.
- Prefer context maps, tools, hooks, and validation loops over instruction sprawl.

### principle.ryan.long-horizon-context-is-designed: Long-Horizon Context Is Designed

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.jit-context-management, claim.ryan.context-not-persistent, claim.ryan.hooks-context-delivery

Long-horizon agent work needs deliberate context delivery, recovery, and refresh mechanisms across the trajectory.

Rationale: Agents can lose or reshape context over time, so the harness needs to provide just-in-time context and resumption surfaces.

Application notes:
- Design for compaction, interruption, and resumed execution.
- Use hooks or workflow steps where supported to deliver timely context.
- Keep durable state outside the transient model context.

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

## Heuristics

### heuristic.ryan.collapse-prompts-to-paved-workflows: Collapse Prompts To Paved Workflows

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.prompt-to-paved-workflow, claim.ryan.context-seeking-framework

For recurring work, make the agent translate an open-ended prompt into a named workflow with known context sources, checks, and closeout proof.

Use when:
- The task belongs to a repeated delivery, review, repair, or research pattern.
- The repo already has docs, scripts, skills, or validators for the pattern.
- Agents often ask for or miss the same context.

Avoid when:
- The task is genuinely novel and needs exploration before workflow capture.
- The workflow would hide a human decision that has not been made.

### heuristic.ryan.design-for-context-loss: Design For Context Loss

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.context-not-persistent, claim.ryan.jit-context-management

Assume the future agent may not remember the current context, and leave durable recovery surfaces before the work depends on memory.

Use when:
- Work may span compaction, retries, handoffs, child agents, or long-running trajectories.
- State, decisions, or validation proof needs to survive beyond one model context.
- A downstream workflow will need to resume without chat history.

Avoid when:
- The task is trivial and fully resolved in a single command or edit.
- The recovery artifact would duplicate an existing authoritative source.

### heuristic.ryan.use-hooks-for-context-delivery: Use Hooks For Context Delivery

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.hooks-context-delivery, claim.ryan.jit-context-management

Where the runtime supports hooks, use them to inject timely, bounded context at the point where the agent can act on it.

Use when:
- The needed context depends on event timing, file path, command, or workflow phase.
- Static instructions are too early, too broad, or too easy to lose.
- Hook outputs can remain deterministic, safe, and bounded.

Avoid when:
- The hook behavior is not supported by the runtime in question.
- The hook would expose secrets, private telemetry, or unstable local state.

### heuristic.ryan.scale-autonomy-through-recovery-loops: Scale Autonomy Through Recovery Loops

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.merge-gates-depend-on-recovery-loops, claim.ryan.autonomy-threshold-tooling

Assess merge gates or increase agent autonomy only to the level that validation, remediation, feedback handling, escalation, and rollback loops can reliably absorb.

Use when:
- A team wants higher agent throughput without turning every PR into synchronous human review.
- Validation and recovery loops are observable enough to catch and repair mistakes quickly.
- Gate ceremony is slowing safe, short-lived changes more than it is reducing risk.

Avoid when:
- The system does not reproduce failures, capture evidence, remediate builds, or escalate ambiguous risk.
- Human authority boundaries for release, security, compliance, identity, or irreversible decisions are unclear.
- The argument for autonomy is based on model capability rather than encoded tooling and recovery evidence.

## Anti-Patterns

### anti-pattern.ryan.rule-pile-harness: Rule-Pile Harness

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.context-seeking-framework, claim.ryan.context-not-persistent

Problem: A harness tries to control stochastic agents by adding more static rules instead of teaching context-seeking and workflow selection.

Failure mode: Agents lose, miss or misapply static guidance during long-horizon work, especially after compaction or context shifts.

Avoidance: Encode context maps, workflow routing, tool discovery, hooks, resumption artifacts, and validation loops that help agents recover the right context when needed.

## Checklists

### checklist.ryan.long-horizon-agent-context: Long-Horizon Agent Context

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.context-not-persistent, claim.ryan.jit-context-management, claim.ryan.hooks-context-delivery, claim.ryan.prompt-to-paved-workflow

- [ ] Name the workflow a prompt can collapse into.
- [ ] Tell the agent what context type matters and where to seek it.
- [ ] Provide durable resumption state outside transient model context.
- [ ] Use runtime-supported hooks or workflow steps for just-in-time context delivery.
- [ ] Keep static rules small and route to deeper references.
- [ ] Validate that closeout proof survives compaction, handoff, and resumed work.

## Rubrics

### rubric.ryan.agent-operating-model: Agent Operating Model

- Type: rubric
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.context-seeking-framework, claim.ryan.context-not-persistent, claim.ryan.prompt-to-paved-workflow

- workflow-collapse: Does the system turn prompts into named workflows with known context sources and proof expectations?
  - pass: Common task prompts route to explicit workflows with context, tools, validation, and closeout guidance.
  - fail: Agents receive broad goals and static rules without a paved execution path.
- context-recovery: Can the agent recover relevant context after compaction, interruption, or handoff?
  - pass: Durable state, source maps, hooks, and resumption artifacts make context recoverable.
  - fail: The trajectory depends on transient chat context or hidden human memory.

## Eval Scenarios

### eval.ryan.compaction-context-recovery: Compaction Requires Context Recovery

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.context-not-persistent, claim.ryan.prompt-to-paved-workflow

Knowledge claim: Principle under test: The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.
Behavior under test: Observable agent behavior when an agent resumes a long-horizon task after context compaction with only a partial summary.
Failure mode: The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context.
Expected agent move: The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.
Skill lift target: The response avoids the weak pattern (The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context) and instead shows the expected behavior (The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.compaction-context-recovery.md
Promotion status: candidate
Capsule refs: principal-engineering
Weak eval flags: none

Given: An agent resumes a long-horizon task after context compaction with only a partial summary.
Can: The agent reconstructs state from repo files, manifests, generated artifacts, recent validation output, and source notes before continuing.
Expected failure: The agent assumes the compressed chat summary is sufficient and continues from stale or incomplete context.
Reproduce with: references/evals/eval.ryan.compaction-context-recovery.md

### eval.ryan.autonomy-gate-threshold: Autonomy Follows Recovery Evidence

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.merge-gates-depend-on-recovery-loops, claim.ryan.autonomy-threshold-tooling

Knowledge claim: Principle under test: The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture.
Behavior under test: Observable agent behavior when an team asks whether to let agents merge low-risk pull requests with fewer blocking human gates.
Failure mode: The agent recommends either more ceremony or more autonomy based only on model capability, team preference, or generic throughput goals.
Expected agent move: The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture.
Skill lift target: The response avoids the weak pattern (The agent recommends either more ceremony or more autonomy based only on model capability, team preference, or generic throughput goals) and instead shows the expected behavior (The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.ryan.autonomy-gate-threshold.md
Promotion status: candidate
Capsule refs: principal-engineering
Weak eval flags: none

Given: A team asks whether to let agents merge low-risk pull requests with fewer blocking human gates.
Can: The agent evaluates current validation, remediation, feedback handling, escalation, rollback, and human-authority boundaries before recommending a gate posture.
Expected failure: The agent recommends either more ceremony or more autonomy based only on model capability, team preference, or generic throughput goals.
Reproduce with: references/evals/eval.ryan.autonomy-gate-threshold.md
