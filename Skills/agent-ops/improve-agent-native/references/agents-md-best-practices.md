# AGENTS.md Best Practices

Use this reference when auditing root or nested AGENTS.md files for agent-native repository readiness.

## Operating Principle

AGENTS.md is a router and precedence contract. It is not the full knowledge base.

## Root AGENTS.md

Keep root guidance focused on rules that apply to most tasks in the repository:

- source-of-truth routing
- required validation entrypoints
- ownership and generated-file boundaries
- safety rules that materially change behavior
- pointers to deeper docs

Move deep rationale, long runbooks, volatile plans, and exact implementation facts to docs, scripts, schemas, or tests.

## Nested AGENTS.md

Add nested guidance only when both conditions are true:

- local mistakes keep recurring in that subtree
- a short local rule would have prevented those mistakes

Nested guidance should describe local boundary differences. It should not repeat the root file.

## Keep, Move, Delete

Keep:

- boundary rules
- precedence rules
- hard constraints
- required tooling sources
- generated-file ownership rules

Move:

- deep rationale to docs/decisions/ or architecture docs
- exact facts to docs/references/
- active execution state to a project tracker
- setup detail to scoped setup docs or scripts

Delete:

- duplicated rules
- temporary task instructions
- reminders better enforced by lint, tests, hooks, or CI
- stale instructions after architecture changes

## Quality Gate

For each section, ask:

- Is it universal for the scope?
- Does it change behavior in a clear way?
- Can it be verified by tooling, inspection, or review?
- Is it durable enough to remain true for weeks?
- Is this the best location?

If a section fails several questions, move or delete it.
