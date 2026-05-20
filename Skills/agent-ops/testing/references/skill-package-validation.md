# Skill Package Validation

Read when: testing, creating, hardening, or validating a skill package in
agent-skills.

## Canonical Source Boundary

Edit canonical skill source under Skills or plugin-owned Plugins sources. Do not
hand-edit generated runtime projections under .agents, .skillsets, Plugins/cache,
or copied runtime mirrors.

## First Checks

For a fresh checkout, prove wrapper availability before relying on repo commands:

- bash scripts/bootstrap-ask.sh --json
- python3 bin/ask repo status --json

Use ./bin/ask for repo operations when it is available.

## Skill Quality Ladder

For skill hardening or readiness, run the ladder in order and stop at the first
failed rung unless the user asks for a full matrix:

1. ./bin/ask skills audit <skill-path> --level strict --json --robot
2. ./bin/ask evals run <skill-path> --mode smoke --json --robot
3. ./bin/plugin-eval analyze <skill-path> --format json
4. ./bin/ask skills external-review <skill-path> --json --robot

When any rung is blocked, record the exact command, blocker class, and next
minimal diagnostic. Do not substitute a different tool and call the ladder
complete.

## Tessl Eval Boundary

When repo policy requires Tessl:

- run the installed local tessl CLI through the repo wrapper;
- stage controlled input under /tmp;
- synthesize scenarios/<case-id>/task.md from canonical references/evals.yaml;
- include a tessl.json project marker;
- never point Tessl at the live source tree;
- do not use npx tessl, publish, registry upload, or package upload commands.

Treat Tessl as part of the eval ladder, not an optional afterthought. When a
user asks for full skill evals or the repo contract names Tessl, run the wrapper
with Tessl enabled and report the actual Tessl status. Use --skip-tessl only
for an explicitly documented Tessl outage, policy block, or intentionally
scoped debug run, and never call that a full eval.

If Tessl reports no safe workspace/project link, classify that as a Tessl setup
blocker instead of looping through auth or sandbox explanations.

If Tessl reports authentication is required, prompt the user with the concrete
terminal command `tessl login`, run it interactively when possible, and rerun
the Tessl-enabled wrapper after login. Do not request network permission up
front for the Tessl eval lane; let the local Tessl CLI and repo wrapper produce
the real blocker or result from the temp-staged project.

## Structural Expectations

A new operational skill should expose:

- precise trigger and non-trigger intent;
- explicit inputs and outputs;
- execution boundaries and side effects;
- failure or repair behavior;
- validation or acceptance criteria;
- references/evals.yaml with happy, edge, negative, and pressure coverage when
  the skill is non-trivial.

## Agent-Native Proof

Validation is not only formatting. A skill is ready when another agent can use
its visible SKILL.md without hidden context, can find deeper references only
when needed, and can report exact pass/fail/blocked evidence without inventing
completion.
