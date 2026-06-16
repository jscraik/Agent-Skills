# Harness Readiness Rubric

Use this reference when the user asks to score, benchmark, audit, or compare a repository's agent-native readiness. Score the repository and any agent-facing product or workflow surface as one system: context, capabilities, validation, recovery, and evidence.

## Scoring

Score each dimension from 0 to 4.

- 0: missing or actively harmful.
- 1: present only as prose, habit, or ad hoc practice.
- 2: usable in common cases with visible gaps.
- 3: documented and repeatable for most relevant work.
- 4: mechanically supported, easy for a cold agent to run, and improved when failures repeat.

Convert the total to N/100 when a score is useful. If evidence is too thin, return a no-score rationale instead.

## Dimensions

### Context Routing

- A cold agent can identify which files, docs, prompts, tools, and app state matter.
- Root and nested AGENTS.md files are short, current, and non-duplicative.
- Nested rules exist only where local boundary rules differ materially.
- Agent runtime prompts include current resources, domain vocabulary, available capabilities, and relevant app state when the product itself has an agent surface.

### Durable Repo Knowledge

- Architecture, active plans, decisions, prompts, capability maps, and stable reference facts live in repo files.
- Volatile instructions stay out of root guidance.
- Docs change when behavior, tools, prompts, or UI capabilities change.

### Autonomous Execution Loop

- Agents can move from intent to implementation, validation, docs, and cleanup without repeated human prompting.
- Escalation boundaries are clear.
- The repo encourages full-job completion rather than partial file edits.
- Repeated proof-loop misses have a visible stop condition: classify the failure, identify the missing enforcement point, and add or recommend the smallest durable mechanism before claiming readiness.
- Agent-facing products have explicit completion, checkpoint, resume, or handoff signals.
- Multi-step tasks expose enough state for agents to continue, recover, or report partial completion.

### Capability Parity And Tool Design

- Meaningful user actions have equivalent agent capabilities, or an explicit reason they do not.
- Tools are primitive capabilities rather than workflow-shaped business logic.
- Core entities expose create, read, update, and delete coverage where appropriate.
- Tool names and prompt capability descriptions use user vocabulary.
- Tool outputs provide enough state for the agent to verify and iterate.

### Mechanical Guardrails

- Important invariants are enforced by tests, lints, scripts, hooks, schemas, CI, capability-map checks, prompt/tool parity checks, or product outcome tests.
- Fast and full checks are discoverable where the repo needs both.
- Repeated mistakes become durable enforcement.
- Knowledge-capsule or pack-backed guidance is routed by manifest signals and loaded as the smallest relevant slice, not as a broad context dump.
- Agent-facing apps test parity, context injection, and expected product outcomes.

### Proof Of Work

- Work closes with compact evidence of commands, artifacts, product paths, logs, screenshots, or CI status as appropriate.
- Skipped checks are named with a reason.
- Product-facing agent behavior is proven by outcome evidence, not only lint, typecheck, or unit tests.

### Recovery And Safety

- High-permission work is recoverable.
- Temporary files, generated artifacts, and rollback paths are understood.
- Secrets and irreversible external effects have explicit boundaries.
- Agent tools expose safe failure modes and contextual errors instead of silent partial success.

### Feedback-To-Harness Compounding

- Human corrections, broken checks, flaky tests, missing capabilities, repeated user requests, latent product demand, and repeated confusion become docs, tools, tests, prompts, skills, clearer errors, capability-map updates, or better workflow affordances.
- Deferred harness gaps have a lightweight tracking surface.

## Output Shape

For scorecard audits, return:

1. Overall score or no-score rationale.
2. Dimension table with score, evidence, and one-line rationale.
3. Top blockers that limit agent autonomy.
4. Immediate, near-term, and later next moves.
5. Evidence paths and commands inspected.

Weight proof, autonomous execution, capability parity and tool design, and mechanical guardrails heavily for solo high-permission repositories. Do not penalize a repo for skipping enterprise ceremony when the repo has fast recovery and clear proof loops.
