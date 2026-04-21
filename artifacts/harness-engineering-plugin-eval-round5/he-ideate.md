# Plugin Eval Report: he-ideate

## At a Glance
- Score: 81/100
- Grade: C
- Risk: high
- Checks: 1 fail, 1 warn, 2 info
- Active budget: 854 tokens (heavy)
- Observed usage: not supplied

## Why It Matters
- 1 failing error check are driving the highest-confidence problems.
- 1 warning signal still need cleanup before this feels polished.
- budget is the largest source of score loss at -18.5 points.
- Active budget pressure is high enough that token cost may dominate the user experience.
- No observed usage is attached yet, so budget conclusions are still based on static estimates.

## Fix First
- [fail/error] deferred_cost_tokens is excessive relative to the current Codex baseline. Why: Budget pressure matters because always-loaded or frequently-loaded text can make the workflow feel expensive fast. Fix: Reduce repeated instruction text and move detail into deferred supporting files.
- [warn/warning] invoke_cost_tokens is heavy relative to the current Codex baseline. Why: Budget pressure matters because always-loaded or frequently-loaded text can make the workflow feel expensive fast. Fix: Reduce repeated instruction text and move detail into deferred supporting files.

## Recommended Next Step
- Measure real token usage next
- Why: The static budget looks heavy, so live usage is the fastest way to confirm whether the cost is acceptable.
- Chat request: "Measure the real token usage of this skill."
- Local command: `plugin-eval start ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate --request 'Measure the real token usage of this skill.' --format markdown`

## Details
<details>
<summary>Watch next</summary>

- No secondary findings queued.
</details>
<details>
<summary>Improvement brief</summary>

- Raise the evaluation from grade C (81/100) with a focus on the highest-signal structural and budget issues first.
- Goal: Reduce repeated instruction text and move detail into deferred supporting files.
- Measure: token-usage-observer
- Measure: task-outcome-scorecard
- Measure: latency-efficiency
- Suggested prompt: Use the skill-creator guidance to improve he-ideate. Keep the structure compact and move bulky details into references or scripts. Define success measures with these toolsets: token-usage-observer, task-outcome-scorecard, latency-efficiency. Address deferred_cost_tokens-budget-high: deferred_cost_tokens is excessive relative to the current Codex baseline. Address invoke_cost_tokens-budget-high: invoke_cost_tokens is heavy relative to the current Codex baseline.
</details>
<details>
<summary>Budgets and observed usage</summary>

- trigger_cost_tokens: 61 (moderate)
- invoke_cost_tokens: 793 (heavy)
- deferred_cost_tokens: 6566 (excessive)
- total_tokens: 7420 (excessive)

- No observed usage supplied.
</details>
<details>
<summary>Measurement plan</summary>

Combine cost, outcome, and trust signals so you can tell whether the skill or plugin is genuinely helping instead of only looking well-structured on paper.

- Token Usage Observer [high] Measure how many tokens the skill or plugin actually burns in representative runs. Signals: observed_usage_sample_count, observed_input_tokens_avg, observed_total_tokens_avg, estimate_vs_observed_input_ratio. Evidence: Responses API usage logs, Codex-like session exports, JSONL traces captured from local benchmarking harnesses.
- Task Outcome Scorecard [high] Measure whether the skill helps users finish the intended job with fewer retries and less cleanup. Signals: task_success_rate, first_pass_success_rate, retry_rate, human_override_rate. Evidence: Task run logs, Structured user acceptance checklist, Before/after comparison runs on the same prompts.
- Tool Call Audit [medium] Check whether the agent uses the right tools, arguments, and sequencing when the skill is active. Signals: tool_call_success_rate, invalid_tool_argument_rate, recoverable_tool_failure_rate. Evidence: Tool invocation traces, Recorded sessions, Golden-path scenario replays.
- Latency And Efficiency [high] Track whether the skill speeds users up enough to justify its cost. Signals: p50_time_to_first_acceptable_answer_seconds, p95_time_to_task_completion_seconds, tokens_per_successful_run. Evidence: Benchmark harness timings, Manual stopwatch runs on canonical tasks, Responses API timestamps combined with usage logs.
- Human Rubric Review [medium] Capture clarity, trust, and usefulness signals that automated checks will miss. Signals: clarity_score_avg, confidence_score_avg, follow_up_question_rate. Evidence: Reviewer scorecards, Team rubric sheets, Annotated transcripts.
</details>
<details>
<summary>Use From Codex Chat</summary>

Start with a natural chat request, then let plugin-eval show the exact local command sequence behind it.

Start with this chat request: "Evaluate this skill."
Why this path: Plugin Eval recommended Evaluate Skill from the current local state for this skill.
Quick local entrypoint: plugin-eval start ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate --request 'Evaluate this skill.' --format markdown
Plugin Eval will run first: plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate --format markdown

Other chat requests you can use:
- Full Skill Analysis: say "Give me a full analysis of this skill, including benchmark setup." -> plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate --format markdown
- Evaluate Skill: say "Evaluate this skill." -> plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate --format markdown
- Explain Token Budget: say "Explain the token budget for this skill." -> plugin-eval explain-budget ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate --format markdown
- Measure Real Token Usage: say "Measure the real token usage of this skill." -> plugin-eval init-benchmark ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate
- Benchmark With Starter Scenarios: say "Help me benchmark this skill." -> plugin-eval init-benchmark ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate
- Start Here: say "What should I run next?" -> plugin-eval analyze ~/.codex/worktrees/b79d/agent-skills/Plugins/harness-engineering/skills/team_automation/he-ideate --format markdown
</details>
<details>
<summary>Checks</summary>

- [WARN] invoke_cost_tokens-budget-high: invoke_cost_tokens is heavy relative to the current Codex baseline. Evidence: Value: 793 tokens Baseline samples: skills=2, plugins=108 Remediation: Reduce repeated instruction text and move detail into deferred supporting files.
- [FAIL] deferred_cost_tokens-budget-high: deferred_cost_tokens is excessive relative to the current Codex baseline. Evidence: Value: 6566 tokens Baseline samples: skills=2, plugins=108 Remediation: Reduce repeated instruction text and move detail into deferred supporting files.
- [INFO] coverage-artifacts-unavailable: No coverage artifacts were found for this target. Evidence: Plugins/harness-engineering/skills/team_automation/he-ideate Remediation: Generate `lcov.info`, `coverage.xml`, or an Istanbul coverage JSON file if you want coverage scoring.
</details>
<details>
<summary>Metrics</summary>

- skill_line_count: 77 lines (good)
- description_length_chars: 232 chars (good)
- relative_link_count: 8 links (good)
- code_fence_count: 0 blocks (good)
- support_file_count: 8 files (good)
- trigger_cost_tokens: 61 tokens (moderate)
- invoke_cost_tokens: 793 tokens (heavy)
- deferred_cost_tokens: 6566 tokens (excessive)
- coverage_artifact_count: 0 files (info)
</details>
<details>
<summary>Score details</summary>

- Starting score: 100
- Total deductions: -18.75
- Final score: 81
- Risk: Contains 1 failing error check (deferred_cost_tokens-budget-high).
- Risk: Contains 1 warning signal that still need attention.

- -14 points: deferred_cost_tokens-budget-high [fail/error] deferred_cost_tokens is excessive relative to the current Codex baseline.
- -4.5 points: invoke_cost_tokens-budget-high [warn/warning] invoke_cost_tokens is heavy relative to the current Codex baseline.
- -0.25 points: coverage-artifacts-unavailable [info/info] No coverage artifacts were found for this target.

- budget: -18.5 points across 2 checks
- coverage: -0.25 points across 1 check
</details>
