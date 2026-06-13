# Harness Readiness Rubric

Use this reference when the user asks to score, benchmark, audit, or compare a repository's agent-native readiness.

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

- A cold agent can identify which files to read first.
- Root and nested AGENTS.md files are short, current, and non-duplicative.
- Nested rules exist only where local boundary rules differ materially.

### Durable Repo Knowledge

- Architecture, active plans, decisions, and stable reference facts live in repo files.
- Volatile instructions stay out of root guidance.
- Docs change when behavior changes.

### Autonomous Execution Loop

- Agents can move from intent to implementation, validation, docs, and cleanup without repeated human prompting.
- Escalation boundaries are clear.
- The repo encourages full-job completion rather than partial file edits.

### Mechanical Guardrails

- Important invariants are enforced by tests, lints, scripts, hooks, schemas, or CI.
- Fast and full checks are discoverable where the repo needs both.
- Repeated mistakes become durable enforcement.

### Proof Of Work

- Work closes with compact evidence of commands, artifacts, product paths, logs, screenshots, or CI status as appropriate.
- Skipped checks are named with a reason.
- Product-facing changes use product-facing proof when possible.

### Recovery And Safety

- High-permission work is recoverable.
- Temporary files, generated artifacts, and rollback paths are understood.
- Secrets and irreversible external effects have explicit boundaries.

### Feedback-To-Harness Compounding

- Human corrections, broken checks, flaky tests, and repeated confusion become docs, tools, tests, skills, clearer errors, or better CLI affordances.
- Deferred harness gaps have a lightweight tracking surface.

## Output Shape

For scorecard audits, return:

1. Overall score or no-score rationale.
2. Dimension table with score, evidence, and one-line rationale.
3. Top blockers that limit agent autonomy.
4. Immediate, near-term, and later next moves.
5. Evidence paths and commands inspected.

Weight proof, autonomous execution, and mechanical guardrails heavily for solo high-permission repositories. Do not penalize a repo for skipping enterprise ceremony when the repo has fast recovery and clear proof loops.
