# Tiered gating policy (rollout and hardening)

## Default policy

- **Week 0 (baseline):** report-only scorecards
- **Weeks 1-2:**
  - Tier 1 hard fail (structure + deterministic checks)
  - Tier 2 warn (rubric + efficiency budgets)
- **Week 3+:** promote stable tier-2 checks to hard fail per skill

## Tier definitions

### Tier 1 (hard fail)

- Eval runner non-zero exit
- Acceptance assertion failures
- Deterministic trace check failures:
  - required/forbidden commands
  - command ordering
  - required/forbidden events
  - command thrash limits in `deterministic_checks`

### Tier 2 (warn/fail by mode)

- Token/turn/command budgets (`budgets.*`)
- Rubric quality thresholds (`min_rubric_score`, `require_overall_pass`)
- Cross-run efficiency regressions (dashboard review)

## Operational commands

Warn mode (default):

```bash
~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py <skill> \
  --dual-run --capture-jsonl --tier2-mode warn
```

Strict mode:

```bash
~/.venvs/pyyaml/bin/python utilities/skill-creator/scripts/run_skill_evals.py <skill> \
  --dual-run --capture-jsonl --tier2-mode fail
```

Repo gate over generated scorecards:

```bash
python utilities/skill-creator/scripts/ci_skill_quality_gate.py \
  artifacts/reports/skills --tier2-mode warn
```

Baseline-aware structure gate:

```bash
python utilities/skill-creator/scripts/run_repo_skill_quality.py \
  --root /absolute/repo \
  --baseline-file utilities/skill-creator/references/skill-quality-baseline.json
```
