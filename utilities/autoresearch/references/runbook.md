# Autoresearch Runbook

## Purpose

Operational runbook for improving skills and plugins through controlled experiment loops.

## Run setup

1. Choose the target set and define a stop condition.
2. Initialize run artifacts:

```bash
bash utilities/autoresearch/scripts/init_run.sh --tag <run-tag> --targets "<path1,path2,...>"
```

3. The script prints `run_dir`. Keep it for all logs.
4. Safety guardrails enforced by the initializer:
   - Targets must be existing repo-relative paths.
   - Targets under `plugins/cache/**` are rejected.
   - Run output must stay under `artifacts/autoresearch/`.

## Baseline matrix

Run the relevant baseline checks before any edits.

Baseline policy:
- Run at least one unmodified baseline pass before iteration changes.
- Log the baseline as `iteration=0`, `decision=keep` when gates pass.
- If a required baseline command cannot run, log `iteration=0` as `blocked` and record the exact blocker.

### Skill targets

```bash
python3 plugins/skill-factory/skills/skill-creator/scripts/quick_validate.py <skill-path>
./bin/ask skills audit <skill-path> --level strict --robot
```

### Plugin targets

```bash
./bin/ask plugins harden <plugin-path> --robot
```

### Broad or mixed edits

```bash
bash scripts/verify-work.sh --fast
```

Record outcomes in `journal.md`.

## Iteration loop

For each iteration:

1. Write one hypothesis in `journal.md`.
2. Make one bounded change set.
3. Run mandatory validations for affected targets.
   - If a required command exceeds the agreed runtime cap (recommended: 10 minutes), stop it and classify the iteration as `blocked`.
4. Compute score and choose decision:
   - `keep`: gates pass and score improves, or equal score with lower complexity.
   - `discard`: score regresses or complexity tradeoff is not justified.
   - `blocked`: required validation could not run.
5. Log result:

```bash
python3 utilities/autoresearch/scripts/log_result.py \
  --run-dir <run-dir> \
  --iteration <n> \
  --target <path> \
  --decision keep|discard|blocked \
  --score <float> \
  --status pass|fail|blocked \
  --change-summary "<what changed>" \
  --validation-evidence "<command1=pass;command2=fail>"
```

## Scoring rubric

- Skill quick validate pass: `+1`
- Skill strict audit pass: `+2`
- Plugin harden pass: `+2`
- Repo fast verification pass: `+1` (when executed)
- Any failed mandatory gate: force `discard` for that iteration.

Use the rubric consistently, but prioritize correctness over raw score.

## Safety boundaries

- Edit canonical source paths only; do not edit `plugins/cache/**`.
- `log_result.py` accepts only initialized run directories containing `results.tsv`, `journal.md`, and `targets.txt`.
- Avoid destructive git operations unless explicitly requested.
- Keep command output evidence exact and reproducible.
- Stop immediately if unrelated workspace changes appear unexpectedly mid-run.

## Completion criteria

- Stop condition reached.
- Results log is complete for all attempted iterations.
- Final summary includes:
  - kept/discarded counts,
  - biggest gains,
  - blocked steps,
  - next hypotheses.
