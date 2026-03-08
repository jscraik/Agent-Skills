# Quality analysis tools

Use these scripts to upgrade skill quality before packaging.

## skill_gate.py

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/skill_gate.py <path/to/skill-folder>
```

Use when:
- enforcing frontmatter constraints and trigger quality
- enforcing progressive disclosure limits
- requiring references/contract.yaml and references/evals.yaml

Outputs:
- PASS/FAIL result with findings

## run_skill_evals.py

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/run_skill_evals.py <path/to/skill-folder>
```

Use when:
- running eval cases from references/evals.yaml with Codex, Claude (Kimi/Zai), and/or Gemini runners
- capturing final output and applying acceptance assertions
- generating scorecards for CI/regression tracking

Notes:
- Single runner:
  - `--runner codex|claude-kimi|claude-zai|gemini`
- Explicit multi-runner matrix (recommended for model parity checks):
  - `--runners codex,claude-kimi,claude-zai,gemini`
  - or repeat: `--runners codex --runners claude-kimi --runners gemini`
- For cross-runner coverage, use dual-run mode:
  - `--dual-run --capture-jsonl`
- `--capture-jsonl` is required for deterministic Codex trace checks and dual-run mode.
- Codex profile compatibility fallback (enabled by default):
  - `--codex-fallback-profile d`
  - This auto-retries when the active Codex profile/model rejects `reasoning.summary` (for example Spark profile mismatches).
- Claude provider routing best-practice:
  - Plain `claude` runner is removed; use explicit provider runners only:
    - `claude-kimi`
    - `claude-zai`
  - Runner execution prefers interactive wrapper commands by default:
    - `claude-kimi` command for `claude-kimi`
    - `claude-zai` command for `claude-zai`
  - Override command names when needed:
    - `--claude-kimi-command <cmd>`
    - `--claude-zai-command <cmd>`
  - Use first-class settings flags:
    - `--claude-kimi-settings kimi_settings.json`
    - `--claude-zai-settings zai_settings.json`
- Runner role policy for agents (what to use what for):
  - `codex`: baseline deterministic checks, JSONL trace capture, and tiered gates.
  - `claude-kimi`: primary alternative reasoning pass and quality comparison.
  - `claude-zai`: adversarial/edge-case second opinion and disagreement detection.
  - `gemini`: breadth/variance pass to detect rubric blind spots.
- Tiered gating:
  - `--tier2-mode warn` (default): style/efficiency findings are non-blocking
  - `--tier2-mode fail`: style/efficiency findings fail the run
  - `--tier2-mode off`: suppress tier-2 findings
- Write merged scorecards with:
  - `--scorecard-out /absolute/or/relative/path.json`
- In CI, prefer `--ask-for-approval never` to avoid prompts.
- Keep `--sandbox read-only` unless the eval requires edits.
- If Codex evals time out during MCP startup, increase the subprocess timeout via:
  - `CODEX_EVAL_TIMEOUT_SEC=600` (or higher)
- If you run Claude evals (`--runner claude-kimi` or `--runner claude-zai`), Claude Code must be authenticated. If you see `Not logged in · Please run /login`, open an interactive Claude session and run `/login` (or use `claude setup-token`).

Outputs:
- PASS/FAIL per case with report artifacts under artifacts/reports/skills/
- merged scorecard JSON (default: `<run>/scorecard.json`, or `--scorecard-out`)

## analyze_skill.py

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/analyze_skill.py <path/to/skill-folder>
```

Use when:
- scoring a skill on philosophy, anti-pattern coverage, variation guidance, and organization
- comparing multiple skills for quality

Output:
- overall score out of 100 plus per-category scoring
- score bands: 80+ strong, 60-79 acceptable, 40-59 needs work, <40 redesign needed

## openclaw_skill_guard.py

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/openclaw_skill_guard.py <path/to/skill-folder> --mode both
```

Use when:
- you want OpenClaw-style **operational readiness** + **security risk** checks
- producing severity output in `critical/warn/info` format before install/publish

Output:
- readiness findings (missing SKILL.md/frontmatter/references artifacts)
- security findings from script pattern scan (dangerous exec/eval/env-harvesting/network)

## upgrade_skill.py

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/upgrade_skill.py <path/to/skill-folder>
```

Use when:
- generating targeted improvement suggestions grouped by priority
- modernizing an older skill to current practices

Output:
- priority buckets (HIGH/MEDIUM/LOW) with actionable suggestions

## generate_pressure_tests.py

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/generate_pressure_tests.py <path/to/skill-folder>
```

Use when:
- generating **A/B/C pressure scenarios** that tempt rationalization around constraints
- hardening discipline/safety skills during **REFACTOR** (after baseline evals pass)

Notes:
- Default output is **Markdown to stdout**.
- Use `--out` + `--overwrite` to write a file.
- Paste the best scenarios into your `references/evals.yaml` (or keep as a human review checklist).

## migrate_evals_v2.py

```bash
~/.venvs/pyyaml/bin/python utilities/skill-builder/scripts/migrate_evals_v2.py --root /absolute/repo --apply --normalize-existing
```

Use when:
- backfilling missing `references/contract.yaml` or `references/evals.yaml`
- upgrading existing eval suites to schema v2 fields (`id`, `should_trigger`, `category`, `deterministic_checks`, `budgets`)

## ci_skill_quality_gate.py

```bash
python utilities/skill-builder/scripts/ci_skill_quality_gate.py artifacts/reports/skills --tier2-mode warn
```

Use when:
- enforcing tiered scorecard policy over one or more scorecards
- integrating pass/fail behavior in CI

## build_skill_eval_dashboard.py

```bash
python utilities/skill-builder/scripts/build_skill_eval_dashboard.py --reports-root artifacts/reports/skills
```

Use when:
- building baseline/regression dashboards from stored scorecards
- tracking tier1/tier2 trend deltas over time

## run_repo_skill_quality.py

```bash
python utilities/skill-builder/scripts/run_repo_skill_quality.py \
  --root /absolute/repo \
  --baseline-file utilities/skill-builder/references/skill-quality-baseline.json
```

Use when:
- enforcing repo-wide structure gates with baseline-aware drift detection
- running optional eval sweeps (`--run-evals --dual-run --capture-jsonl`)

## Contract and evals (gold standard)

When creating a new skill, add these files under `references/`:

- `contract.yaml` -- a concise contract describing purpose, triggers, inputs, outputs, non-goals, and risks
- `evals.yaml` -- at least 3 evaluation cases with prompts and acceptance criteria (happy path, edge case, failure mode)

Start from the templates in:
- `references/contract.template.yaml`
- `references/evals.template.yaml`
