# Quality analysis tools

Use these scripts to upgrade skill quality before packaging.

## skill_gate.py

```bash
python scripts/skill_gate.py <path/to/skill-folder>
```

Use when:
- enforcing frontmatter constraints and trigger quality
- enforcing progressive disclosure limits
- requiring references/contract.yaml and references/evals.yaml

Outputs:
- PASS/FAIL result with findings

## run_skill_evals.py

```bash
python scripts/run_skill_evals.py <path/to/skill-folder>
```

Use when:
- running eval cases from references/evals.yaml using Codex CLI (`codex exec`)
- capturing final output and applying acceptance assertions

Notes:
- In CI, prefer `--ask-for-approval never` to avoid prompts.
- Keep `--sandbox read-only` unless the eval requires edits.

Outputs:
- PASS/FAIL per case with report artifacts under artifacts/reports/skills/

## analyze_skill.py

```bash
python scripts/analyze_skill.py <path/to/skill-folder>
```

Use when:
- scoring a skill on philosophy, anti-pattern coverage, variation guidance, and organization
- comparing multiple skills for quality

Output:
- overall score out of 100 plus per-category scoring
- score bands: 80+ strong, 60-79 acceptable, 40-59 needs work, <40 redesign needed

## upgrade_skill.py

```bash
python scripts/upgrade_skill.py <path/to/skill-folder>
```

Use when:
- generating targeted improvement suggestions grouped by priority
- modernizing an older skill to current practices

Output:
- priority buckets (HIGH/MEDIUM/LOW) with actionable suggestions

## Contract and evals (gold standard)

When creating a new skill, add these files under `references/`:

- `contract.yaml` -- a concise contract describing purpose, triggers, inputs, outputs, non-goals, and risks
- `evals.yaml` -- at least 3 evaluation cases with prompts and acceptance criteria (happy path, edge case, failure mode)

Start from the templates in:
- `references/contract.template.yaml`
- `references/evals.template.yaml`
