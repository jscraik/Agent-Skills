---
schema_version: 1
run_tag: 2026-05-13-autoresearch-eval-runtime-loop
target: Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py
metric_direction: lower_runtime_waste_with_same_failure_classification
decision: keep
---

# Autoresearch Eval Runtime Loop

## Contract

- Goal: improve the smoke/release eval validation runtime by bounding live Codex split-case execution without editing fixed eval prompts, datasets, or acceptance criteria.
- Editable boundary: \`Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py\` and its regression tests.
- Fixed boundary: HE skill \`references/evals.yaml\` files, skill-builder runner scoring, Codex runner artifacts, and acceptance regexes.
- Stop condition: one reversible runtime-control patch plus focused tests and one bounded CLI diagnostic.
- Keep policy: keep only if focused regression tests pass and the CLI diagnostic reports bounded execution metadata with the correct runner-preflight classification.

## Baseline

Command: \`python3 Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py\` -> pass (7 tests).

Command: \`python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py Infrastructure/tests/test_ask_evals_command.py -q\` -> pass (6 tests).

Baseline finding: the runner already split Codex release cases and classified tool preflight failures, but a split release run could still continue across every discovered case after a live runner preflight failure. That made smoke/release validation slower and noisier when the runtime was unhealthy.

## Hypothesis

Add two explicit bounds to split Codex release execution:

- \`--max-cases\` for diagnostic breadth.
- \`--max-tool-preflight-failures\` for fail-fast behavior when the live Codex runner cannot produce usable output.

Expected outcome: a bounded diagnostic can execute only the first selected case, preserve \`ERR_CODEX_RUNNER_PREFLIGHT\`, report discovered/executed/skipped counts, and avoid spending runtime on remaining cases when the same runner preflight defect controls the result.

## Patch

Changed \`Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py\`:

- added split-run metadata: \`bounded_run\`, \`max_cases\`, \`max_tool_preflight_failures\`, \`discovered_case_count\`, \`executed_case_count\`, \`skipped_case_count\`, and \`early_stop_reason\`;
- added \`--max-cases\`;
- added \`--max-tool-preflight-failures\` with default \`1\`;
- stopped split execution after the configured runner-preflight failure limit.
- fixed direct Codex eval execution to always pass \`--model gpt-5.3-codex-spark\` and never add reasoning flags.

Changed \`Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py\`:

- covered max-case bounded execution;
- covered early stop after runner-preflight failure limit.

## Verification

Command: \`python3 Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py\` -> pass (9 tests).

Command: \`python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py Infrastructure/tests/test_ask_evals_command.py -q\` -> pass (6 tests).

Command: \`python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode release --eval-runner codex --skill he-router --category happy --max-cases 1 --per-skill-timeout-sec 2 --json\` -> fail as expected because the live Codex runner produced no final output, but the bounded runtime behavior worked.

Observed diagnostic fields:

- \`discovered_case_count\`: 4
- \`executed_case_count\`: 1
- \`skipped_case_count\`: 3
- \`bounded_run\`: true
- \`early_stop_reason\`: \`tool_preflight_failure_limit\`
- controlling error: \`ERR_CODEX_RUNNER_PREFLIGHT\`
- direct case command included \`--model gpt-5.3-codex-spark\` and no reasoning flag
- artifact root: \`Infrastructure/artifacts/skills/he-router/20260513-023753-152554\`

## Decision

Keep. The patch does not weaken eval scoring or acceptance criteria; it bounds the validation loop and preserves the controlling runtime blocker. The remaining live-runner failure is classified as runtime/tool preflight, not a HE skill content failure.

## Residual Risk

This improves split Codex release runtime behavior. It does not make the live Codex runner healthy, and it does not prove full release coverage when \`--max-cases\` is used. Full release readiness still requires an unbounded run or an explicitly selected complete case set after the runner preflight issue is resolved.

## 12-Loop Extension

Run tag: \`2026-05-13-autoresearch-eval-runtime-loop-12\`

Stop condition: exactly 12 bounded loops, no fixed eval prompt or acceptance edits, final focused gates pass, live-runner failures classified as runtime preflight.

### Loop Ledger

| Loop | Hypothesis | Evidence | Decision |
| --- | --- | --- | --- |
| 1 | Current edited runner can serve as baseline if focused tests pass. | \`python3 Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py\` -> pass (10 tests); \`python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py Infrastructure/tests/test_ask_evals_command.py -q\` -> pass (6 tests). | keep baseline |
| 2 | The skill-builder runner supports pass-through Codex args, so direct HE evals can ignore user config. | Read \`run_skill_evals.pyw\` and confirmed \`--codex-arg\` support. | keep candidate |
| 3 | Add \`--codex-arg --ignore-user-config\` to direct Codex evals to preserve no-reasoning behavior from user config drift. | \`python3 Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py\` -> pass (10 tests). | keep |
| 4 | Extend model/no-reasoning regression test to require \`--ignore-user-config\`. | Plugin-local test command -> pass (10 tests). | keep |
| 5 | Make the fixed runtime contract visible in top-level JSON. | Added \`eval_runtime.codex_model\`, \`eval_runtime.codex_args\`, and empty \`reasoning_flags\`; plugin-local tests -> pass (11 tests). | keep |
| 6 | \`--max-tool-preflight-failures 0\` should explicitly disable early stop for full diagnostic sweeps. | Added plugin-local regression; plugin-local tests -> pass (11 tests). | keep |
| 7 | Central Infrastructure tests should also protect the summary runtime contract. | \`python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py -q\` -> pass (5 tests). | keep |
| 8 | Central Infrastructure tests should also protect direct Spark + ignore-user-config command construction. | \`python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py Infrastructure/tests/test_ask_evals_command.py -q\` -> pass (8 tests). | keep |
| 9 | Plugin-local CLI parser should reject any model other than \`gpt-5.3-codex-spark\`. | Added subprocess CLI regression; \`python3 Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py\` -> pass (12 tests). | keep |
| 10 | Manual CLI probe should reject model drift before running evals. | \`python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode release --eval-runner codex --skill he-router --model gpt-5.4 --json\` -> exit 2 with fixed-model error. | keep |
| 11 | Parser guards should reject invalid bounded-loop parameters and keep ask-runner filter errors classified. | Wrong smoke model -> exit 2; \`--max-cases 0\` -> exit 2; ask runner with model -> structured \`ERR_UNSUPPORTED_FILTER\`. | keep |
| 12 | Accepted fixed-model bounded live diagnostic should show Spark, ignore-user-config, no reasoning flags, bounded counts, and preflight classification. | \`python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode release --eval-runner codex --skill he-router --model gpt-5.3-codex-spark --category happy --max-cases 1 --per-skill-timeout-sec 2 --json\` -> expected fail with \`ERR_CODEX_RUNNER_PREFLIGHT\`; command included \`--model gpt-5.3-codex-spark --codex-arg --ignore-user-config\`; summary reported \`reasoning_flags: []\`, discovered 4, executed 1, skipped 3. | keep as runtime blocker evidence |

### Final 12-Loop Verification

Command: \`python3 Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py\` -> pass (12 tests).

Command: \`python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py Infrastructure/tests/test_ask_evals_command.py -q\` -> pass (8 tests).

Command: \`git diff --check -- Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py .harness/evals/2026-05-13-agent-skills-autoresearch-eval-runtime-loop.md\` -> pass.

### Final Decision

Keep the runtime patch set. It improves the validation runtime by bounding live eval waste, making the fixed model/no-reasoning contract executable and visible, and preserving live-runner failures as tool preflight blockers instead of content failures.

## Runtime Repair Follow-Up

Observed blocker after the 12-loop pass:

- direct `codex exec` inherited the real Codex home and failed before model execution with `failed to initialize in-process app-server client: Operation not permitted`;
- `codex exec` succeeded with `CODEX_HOME` set to a writable isolated home under `/private/tmp`;
- the HE wrapper was always forwarding `~/.codex` as `--codex-home`, bypassing the shared skill eval runner's isolated-home path.

Patch:

- changed `Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py` so `--codex-home` is forwarded only when explicitly supplied;
- left omitted `--codex-home` to the shared skill eval runner, which creates a writable isolated live-eval `CODEX_HOME`;
- extended runner-preflight classification to scan `stderr`, `stdout`, `final`, and `jsonl` artifacts;
- classified Spark usage-limit JSONL events as `ERR_CODEX_RUNNER_PREFLIGHT`;
- made isolated Codex home cleanup best-effort in `Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/run_skill_evals.pyw`.

Verification:

- `python3 Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/test_run_skill_evals.pyw` -> pass (21 tests).
- `python3 Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py` -> pass (14 tests).
- `python3 -m pytest Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py Infrastructure/tests/test_ask_evals_command.py -q` -> pass (10 tests).
- `git diff --check -- Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts/run_skill_evals.pyw Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py Plugins/harness-engineering/scripts/test_run_lifecycle_release_evals.py Infrastructure/scripts/testing/test_run_lifecycle_release_evals.py .harness/evals/2026-05-13-agent-skills-autoresearch-eval-runtime-loop.md` -> pass.
- `python3 Plugins/harness-engineering/scripts/run_lifecycle_release_evals.py --mode release --eval-runner codex --skill he-router --case explicit-eval-route --max-cases 1 --json` -> expected fail with `ERR_CODEX_RUNNER_PREFLIGHT` because Spark is currently usage-limited; no `Operation not permitted` app-server failure; no cleanup traceback.

Current live blocker:

- `Infrastructure/artifacts/skills/he-router/20260513-025145-631488/01-explicit-eval-route/codex/codex_events.jsonl` reports `You've hit your usage limit for GPT-5.3-Codex-Spark. Switch to another model now, or try again at 3:11 AM.`
