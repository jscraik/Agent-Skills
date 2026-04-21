# Plugin Eval Report: he-compound-refresh

## At a Glance
- Score: 100/100
- Grade: A
- Risk: low
- Checks: 0 fail, 0 warn, 2 info
- Active budget: 514 tokens (moderate)
- Observed usage: not supplied

## Why It Matters
- coverage is the largest source of score loss at -0.25 points.
- Budget pressure is not the dominant issue right now.
- No observed usage is attached yet, so budget conclusions are still based on static estimates.

## Fix First
- No urgent fixes were identified.

## Recommended Next Step
- Choose the next workflow from chat
- Why: The report is clean enough that the best next step depends on whether you want budgets, benchmarks, or comparisons.
- Chat request: "What should I run next?"
- Local command: `plugin-eval start ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh --request 'What should I run next?' --format markdown`

## Details
<details>
<summary>Watch next</summary>

- No secondary findings queued.
</details>
<details>
<summary>Improvement brief</summary>

- Raise the evaluation from grade A (100/100) with a focus on the highest-signal structural and budget issues first.
- Measure: token-usage-observer
- Measure: task-outcome-scorecard
- Suggested prompt: Use the skill-creator guidance to improve he-compound-refresh. Keep the structure compact and move bulky details into references or scripts. Define success measures with these toolsets: token-usage-observer, task-outcome-scorecard.
</details>
<details>
<summary>Budgets and observed usage</summary>

- trigger_cost_tokens: 61 (moderate)
- invoke_cost_tokens: 453 (moderate)
- deferred_cost_tokens: 0 (good)
- total_tokens: 514 (moderate)

- No observed usage supplied.
</details>
<details>
<summary>Measurement plan</summary>

Combine cost, outcome, and trust signals so you can tell whether the skill or plugin is genuinely helping instead of only looking well-structured on paper.

- Token Usage Observer [high] Measure how many tokens the skill or plugin actually burns in representative runs. Signals: observed_usage_sample_count, observed_input_tokens_avg, observed_total_tokens_avg, estimate_vs_observed_input_ratio. Evidence: Responses API usage logs, Codex-like session exports, JSONL traces captured from local benchmarking harnesses.
- Task Outcome Scorecard [high] Measure whether the skill helps users finish the intended job with fewer retries and less cleanup. Signals: task_success_rate, first_pass_success_rate, retry_rate, human_override_rate. Evidence: Task run logs, Structured user acceptance checklist, Before/after comparison runs on the same prompts.
- Tool Call Audit [medium] Check whether the agent uses the right tools, arguments, and sequencing when the skill is active. Signals: tool_call_success_rate, invalid_tool_argument_rate, recoverable_tool_failure_rate. Evidence: Tool invocation traces, Recorded sessions, Golden-path scenario replays.
- Latency And Efficiency [medium] Track whether the skill speeds users up enough to justify its cost. Signals: p50_time_to_first_acceptable_answer_seconds, p95_time_to_task_completion_seconds, tokens_per_successful_run. Evidence: Benchmark harness timings, Manual stopwatch runs on canonical tasks, Responses API timestamps combined with usage logs.
- Human Rubric Review [medium] Capture clarity, trust, and usefulness signals that automated checks will miss. Signals: clarity_score_avg, confidence_score_avg, follow_up_question_rate. Evidence: Reviewer scorecards, Team rubric sheets, Annotated transcripts.
</details>
<details>
<summary>Use From Codex Chat</summary>

Start with a natural chat request, then let plugin-eval show the exact local command sequence behind it.

Start with this chat request: "Evaluate this skill."
Why this path: Plugin Eval recommended Evaluate Skill from the current local state for this skill.
Quick local entrypoint: plugin-eval start ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh --request 'Evaluate this skill.' --format markdown
Plugin Eval will run first: plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh --format markdown

Other chat requests you can use:
- Full Skill Analysis: say "Give me a full analysis of this skill, including benchmark setup." -> plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh --format markdown
- Evaluate Skill: say "Evaluate this skill." -> plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh --format markdown
- Explain Token Budget: say "Explain the token budget for this skill." -> plugin-eval explain-budget ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh --format markdown
- Measure Real Token Usage: say "Measure the real token usage of this skill." -> plugin-eval init-benchmark ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh
- Benchmark With Starter Scenarios: say "Help me benchmark this skill." -> plugin-eval init-benchmark ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh
- Start Here: say "What should I run next?" -> plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-compound-refresh --format markdown
</details>
<details>
<summary>Checks</summary>

- [INFO] coverage-artifacts-unavailable: No coverage artifacts were found for this target. Evidence: Plugins/harness-engineering/skills/team_automation/he-compound-refresh Remediation: Generate `lcov.info`, `coverage.xml`, or an Istanbul coverage JSON file if you want coverage scoring.
</details>
<details>
<summary>Metrics</summary>

- skill_line_count: 35 lines (good)
- description_length_chars: 222 chars (good)
- relative_link_count: 5 links (good)
- code_fence_count: 0 blocks (good)
- support_file_count: 2 files (good)
- trigger_cost_tokens: 61 tokens (moderate)
- invoke_cost_tokens: 453 tokens (moderate)
- deferred_cost_tokens: 0 tokens (good)
- coverage_artifact_count: 0 files (info)
</details>
<details>
<summary>Score details</summary>

- Starting score: 100
- Total deductions: -0.25
- Final score: 100
- Risk: No failing or warning checks were found; remaining items are informational only.

- -0.25 points: coverage-artifacts-unavailable [info/info] No coverage artifacts were found for this target.

- coverage: -0.25 points across 1 check
</details>
