# Skill Workouts

## Purpose

Skill workouts are deterministic eval harnesses for improving skills without
loading telemetry or scorecards into normal runtime context.

Workout source lives under `.workouts/**`. Runtime evidence lives under
`.skill-telemetry/**` and is ignored by git.

## CLI

```bash
./bin/ask workouts list --json --robot
./bin/ask workouts run agent-ops/verification-before-completion --attempts 5 --json --robot
./bin/ask workouts score agent-ops/verification-before-completion --json --robot
./bin/ask workouts promote agent-ops/verification-before-completion --if-better --dry-run --json --robot
```

As of the 2026-05-13 refresh, `./bin/ask workouts list --json --robot` reports
three ready workouts: `agent-ops/verification-before-completion`,
`harness-engineering/he-spec`, and `skill-factory/skill-refactor`.

## Contract

Each workout run:

- runs `seed.sh`;
- runs `verify.py`;
- hashes the verifier before and after execution;
- fails if the verifier changes during the workout;
- writes `runs.jsonl`, `workout-results.jsonl`, and a scorecard;
- records context-token estimates.

Promotion dry-run validates rollback before writing amendment metadata.

## Amendment Records

`ask workouts promote <id> --if-better --dry-run` returns an amendment proposal
without writing runtime evidence. The proposal includes:

- `previous_hash`, `new_hash`, and `current_version`;
- `score_before` and `score_after`;
- rationale and evidence paths;
- rollback command and rollback validation;
- context-budget status and rejection reasons.

Non-dry-run promotion writes local runtime records under:

```text
.skill-telemetry/amendments/accepted/
.skill-telemetry/amendments/rejected/
```

Rejected records are written when a proposal would regress the context budget,
even if the latest workout pass rate is high.

## Diagnostic Fixtures

The first diagnostic fixture set is:

```text
.workouts/agent-ops/verification-before-completion/
.workouts/harness-engineering/he-spec/
.workouts/skill-factory/skill-refactor/
```

These fixtures validate one agent-ops atom, one Harness Engineering stage, and
one factory workflow. Together they exercise the scorecard writer and rollback
dry-run path used by promotion while keeping runtime telemetry out of normal
skill context.
