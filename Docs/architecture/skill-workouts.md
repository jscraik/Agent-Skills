# Skill Workouts

## Purpose

Skill workouts are deterministic eval harnesses for improving skills without
loading telemetry or scorecards into normal runtime context.

Workout source lives under `.workouts/**`. Runtime evidence lives under
`.skill-telemetry/**` and is ignored by git.

## CLI

```bash
python3 bin/ask workouts list --json
python3 bin/ask workouts run agent-ops/verification-before-completion --attempts 5 --json
python3 bin/ask workouts score agent-ops/verification-before-completion --json
python3 bin/ask workouts promote agent-ops/verification-before-completion --if-better --dry-run --json
```

## Contract

Each workout run:

- runs `seed.sh`;
- runs `verify.py`;
- hashes the verifier before and after execution;
- fails if the verifier changes during the workout;
- writes `runs.jsonl`, `workout-results.jsonl`, and a scorecard;
- records context-token estimates.

Promotion dry-run validates rollback before writing amendment metadata.

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
