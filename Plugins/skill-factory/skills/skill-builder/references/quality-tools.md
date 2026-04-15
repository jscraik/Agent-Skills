# Quality analysis tools

Use these scripts to upgrade skill quality before packaging.

## check-see-also.py

```bash
python3 Infrastructure/scripts/check-see-also.py . --changed-files <skill>/SKILL.md
```

Use when:
- validating that new or materially changed skills include a `## See Also` table
- enforcing the minimum related-skill link count for graph traversal quality

Outputs:
- PASS/FAIL for changed skills in CI mode
- audit report of weakly linked skills in full-scan mode

## validate_skill_graph_profiles.py

```bash
python3 Skills/skill-builder/Infrastructure/scripts/validate_skill_graph_profiles.py --repo-root . --expected-count 0
```

Use when:
- creating or improving active skills that should participate in the recursive skill graph
- checking `Infrastructure/references/task-profile.json` completeness and onboarding-contract validity

Outputs:
- `Infrastructure/artifacts/skill-graphs/onboarding/profile-index.json`
- `Infrastructure/artifacts/skill-graphs/onboarding/wave-readiness.json`
- non-zero exit when graph profile contracts fail

## build-adjacency-yaml.py + validate-adjacency.py

```bash
python3 Infrastructure/scripts/build-adjacency-yaml.py
python3 Infrastructure/scripts/validate-adjacency.py
```

Use when:
- `## See Also` tables changed materially across one or more skills
- refreshing and validating the repository adjacency artifact after graph-link updates

Outputs:
- updated `docs/skill-graphs/adjacency.yaml`
- PASS/FAIL drift check between `SKILL.md` links and adjacency output

## skill_gate.py

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/skill_gate.py <path/to/skill-folder>
```

Use when:
- enforcing frontmatter constraints and trigger quality
- enforcing progressive disclosure limits
- requiring Infrastructure/references/contract.yaml and Infrastructure/references/evals.yaml
- checking that the skill bundle is structurally ready before graph-specific gates run

Outputs:
- PASS/FAIL result with findings
- machine-readable envelope in `--format json` with `schema_version`, `decision`, and `exit_code`
- optional artifact write with `--output /path/to/report.json`
- optional SARIF output with `--sarif-out /path/to/report.sarif`

## run_skill_evals.py

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/run_skill_evals.py <path/to/skill-folder>
```

Use when:
- running eval cases from Infrastructure/references/evals.yaml with Codex, Claude (Kimi/Zai), and/or Gemini runners
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
- Eval suite modes:
  - `--eval-mode standard` preserves the current full default behavior.
  - `--eval-mode smoke` runs the faster pre-release subset for local iteration.
  - `--eval-mode release` runs the release-grade suite and auto-enables Codex JSONL capture when relevant.
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
- Write JUnit XML for CI test ingestion with:
  - `--junit-out /absolute/or/relative/path.xml`
- In CI, set approval behavior in `~/.codex/config.toml` or a profile; avoid passing legacy `--ask-for-approval` unless your Codex CLI explicitly supports it.
- Keep `--sandbox read-only` unless the eval requires edits.
- If Codex evals time out during MCP startup, increase the subprocess timeout via:
  - `CODEX_EVAL_TIMEOUT_SEC=600` (or higher)
- If you run Claude evals (`--runner claude-kimi` or `--runner claude-zai`), Claude Code must be authenticated. If you see `Not logged in · Please run /login`, open an interactive Claude session and run `/login` (or use `claude setup-token`).

Outputs:
- PASS/FAIL per case with report artifacts under Infrastructure/artifacts/skills/
- merged scorecard JSON (default: `<run>/scorecard.json`, or `--scorecard-out`)
- release manifest JSON (default: `<run>/release_manifest.json`)
- JUnit XML (default: `<run>/junit.xml`, or `--junit-out`)

Iteration-upgrade artifact expectations:
- case `result.json` includes additive round metadata when provided in eval cases:
  - `baseline_type`
  - `comparison_inputs`
  - `iteration_round_state`
  - `metric_availability`
  - `readiness_state`
  - optional `comparison_review_artifact`
  - optional `neutral_baseline_approval`
- run `summary.json` includes readiness rollup and blocked-round visibility.
- `release_manifest.json` stays thin and points to richer artifacts rather than duplicating all per-case evidence.

## analyze_skill.py

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/analyze_skill.py <path/to/skill-folder>
```

Use when:
- scoring a skill on philosophy, anti-pattern coverage, variation guidance, and organization
- comparing multiple skills for quality

Output:
- overall score out of 100 plus per-category scoring
- score bands: 80+ strong, 60-79 acceptable, 40-59 needs work, <40 redesign needed
- machine-readable envelope in `--format json|yaml` with `schema_version`, `decision`, and `exit_code`
- optional artifact write with `--output /path/to/report.json`

## openclaw_skill_guard.py

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/openclaw_skill_guard.py <path/to/skill-folder> --mode both
```

Use when:
- you want OpenClaw-style **operational readiness** + **security risk** checks
- producing severity output in `critical/warn/info` format before install/publish

Output:
- readiness findings (missing SKILL.md/frontmatter/references artifacts)
- security findings from script pattern scan (dangerous exec/eval, env-harvesting, file-read exfiltration, obfuscation, crypto-mining, suspicious websocket, network)

## upgrade_skill.py

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/upgrade_skill.py <path/to/skill-folder>
```

Use when:
- generating targeted improvement suggestions grouped by priority
- modernizing an older skill to current practices

Output:
- priority buckets (HIGH/MEDIUM/LOW) with actionable suggestions

## generate_pressure_tests.py

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/generate_pressure_tests.py <path/to/skill-folder>
```

Use when:
- generating **A/B/C pressure scenarios** that tempt rationalization around constraints
- hardening discipline/safety skills during **REFACTOR** (after baseline evals pass)

Notes:
- Default output is **Markdown to stdout**.
- Use `--out` + `--overwrite` to write a file.
- Paste the best scenarios into your `Infrastructure/references/evals.yaml` (or keep as a human review checklist).

## migrate_evals_v2.py

```bash
~/.venvs/pyyaml/bin/python Skills/skill-builder/Infrastructure/scripts/migrate_evals_v2.py --root /absolute/repo --apply --normalize-existing
```

Use when:
- backfilling missing `Infrastructure/references/contract.yaml` or `Infrastructure/references/evals.yaml`
- upgrading existing eval suites to schema v2 fields (`id`, `should_trigger`, `category`, `deterministic_checks`, `budgets`)

## ci_skill_quality_gate.py

```bash
python Skills/skill-builder/Infrastructure/scripts/ci_skill_quality_gate.py Infrastructure/artifacts/skills --tier2-mode warn
```

Use when:
- enforcing tiered scorecard policy over one or more scorecards
- integrating pass/fail behavior in CI

## build_skill_eval_dashboard.py

```bash
python Skills/skill-builder/Infrastructure/scripts/build_skill_eval_dashboard.py --reports-root Infrastructure/artifacts/skills
```

Use when:
- building baseline/regression dashboards from stored scorecards (regression coverage)
- tracking tier1/tier2 trend deltas over time
## benchmark_skill_portfolio.py

```bash
python Skills/skill-builder/Infrastructure/scripts/benchmark_skill_portfolio.py \
  --root /absolute/repo \
  --config Skills/skill-builder/Infrastructure/references/benchmark-policy.json \
  --mode warn \
  --format text \
  --output-json Infrastructure/artifacts/industry-benchmark-latest.json
```

Use when:
- enforcing portfolio marker distribution (not only single-skill pass/fail checks)
- measuring cluster coverage for modern baselines (frontend, GitHub, Cloudflare, OpenAI, security, MCP)
- generating benchmark artifacts that CI and local quality gates can read

Notes:
- `--mode warn` blocks on hard-fail conditions and reports warning conditions.
- `--mode fail` blocks on both hard-fail and warning conditions (strict ratchet mode).
- Keep policy changes in `Infrastructure/references/benchmark-policy.json` under version control with a short rationale in the related PR.

## Release manifest template

When you need a stable production artifact contract, start from:

- `Infrastructure/references/release-manifest.template.json`

Use it for:
- documenting generated release metadata fields (`version`, `source_commit`, `release_channel`)
- standardizing artifact locations across eval/reporting workflows

## refresh_benchmark_policy.py

```bash
python Skills/skill-builder/Infrastructure/scripts/refresh_benchmark_policy.py \
  --root /absolute/repo \
  --policy Skills/skill-builder/Infrastructure/references/benchmark-policy.json \
  --benchmark-json Infrastructure/artifacts/industry-benchmark-latest.json \
  --schedule-days 7 \
  --apply \
  --report-json Infrastructure/artifacts/benchmark-policy-refresh-report.json
```

Use when:
- pulling version baselines from Context7 (for configured marker sources)
- ratcheting benchmark thresholds from observed portfolio performance
- keeping benchmark policy fresh in scheduled governance runs

Notes:
- Reads `CONTEXT7_API_KEY` by default (override with `--context7-env`).
- Context pull is schedule-window aware (`--schedule-days`, override with `--force-context-refresh`).
- Ratcheting is one-way only (tightens gates, never loosens).
- Use `--require-context7` when you want missing key/API failures to hard-fail the run.

## run_repo_skill_quality.py

```bash
python Skills/skill-builder/Infrastructure/scripts/run_repo_skill_quality.py \
  --root /absolute/repo \
  --baseline-file Skills/skill-builder/Infrastructure/references/skill-quality-baseline.json \
  --benchmark-mode warn \
  --benchmark-config Skills/skill-builder/Infrastructure/references/benchmark-policy.json \
  --benchmark-output-json Infrastructure/artifacts/industry-benchmark-latest.json
```

Use when:
- enforcing repo-wide structure gates with baseline-aware drift detection
- running optional eval sweeps (`--run-evals --dual-run --capture-jsonl`)
- enforcing portfolio benchmark policy in the same pass as structure/eval gates

Outputs:
- per-skill structure JSON reports at `<reports-dir>/<skill>/structure-gate.json`
- per-skill structure SARIF reports at `<reports-dir>/<skill>/structure-gate.sarif`
- per-skill eval JUnit reports at `<reports-dir>/<skill>/latest-junit.xml` when `--run-evals` is enabled
- aggregate structure SARIF at `<reports-dir>/skill-structure-gates.sarif` (or `--sarif-out`)
- repo artifact index at `<reports-dir>/repo-quality-artifacts.json`

## Contract and evals (gold standard)

When creating a new skill, add these files under `Infrastructure/references/`:

- `contract.yaml` -- a concise contract describing purpose, triggers, inputs, outputs, non-goals, and risks
- `evals.yaml` -- at least 3 evaluation cases with prompts and acceptance criteria (happy path, edge case, failure mode)

Start from the templates in:
- `Infrastructure/references/contract.template.yaml.tmpl` -> rendered to `Infrastructure/references/contract.template.yaml`
- `Infrastructure/references/evals.template.yaml.tmpl` -> rendered to `Infrastructure/references/evals.template.yaml`

Render / refresh:

```bash
python3 Plugins/skill-factory/skills/skill-builder/Infrastructure/scripts/render_reference_templates.py
python3 Plugins/skill-factory/skills/skill-builder/Infrastructure/scripts/check_reference_template_drift.py --update
```

Verify no drift:

```bash
python3 Plugins/skill-factory/skills/skill-builder/Infrastructure/scripts/check_reference_template_drift.py
```
