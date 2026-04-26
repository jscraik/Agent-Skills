---
name: insight-report
description: "WHAT: Generate Codex-authored HTML insights from local Codex sessions and telemetry. WHEN: Use when the user asks for Codex usage analytics, workflow patterns, session summaries, prompting help, or recommendations for improving how they use Codex."
metadata:
  skill-type: data_fetch_analysis
---

# Insight Report

## Table of Contents

- [Philosophy](#philosophy)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Workflow](#workflow)
- [Codex Writer Contract](#codex-writer-contract)
- [Codex Browser Launch](#codex-browser-launch)
- [Validation](#validation)
- [Failure Modes](#failure-modes)
- [Gotchas](#gotchas)
- [Safety](#safety)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [See Also](#see-also)

Generate a local Codex usage report where **Codex is the only narrative insight writer**. The Python runner collects evidence and renders HTML; Codex writes the analysis JSON.

## Philosophy

- **Evidence over intuition**: use local sessions and telemetry, not guesswork.
- **Codex-authored insight**: Codex writes the narrative, recommendations, and prompting help.
- **Plain-English coaching**: translate technical patterns into language Jamie can reuse without needing specialist vocabulary.
- **Auditable artifacts**: keep the evidence bundle, prompt, generated insight JSON, and HTML report on disk.

## When to use

- "Show me my Codex analytics"
- "Generate my weekly insights report"
- "What am I doing well with Codex?"
- "Where am I getting stuck?"
- "Help me prompt better when I don't know the technical terms"

## Required inputs

- Session data in `~/.codex/sessions/`.
- Optional telemetry data in `~/.agents/otel-collector/` when available.
- Time window: `--days N` (default: 7).
- Codex CLI available as `codex` unless using `--prepare-only`.

## Deliverables

- Evidence bundle: `${INSIGHT_REPORT_USAGE_DIR:-$HOME/.codex/usage-data}/insight-evidence.json`
- Codex prompt: `${INSIGHT_REPORT_USAGE_DIR:-$HOME/.codex/usage-data}/INSIGHT_PROMPT.md`
- Codex-written insight JSON: `${INSIGHT_REPORT_USAGE_DIR:-$HOME/.codex/usage-data}/insights.generated.json`
- HTML report: `file://${INSIGHT_REPORT_USAGE_DIR:-$HOME/.codex/usage-data}/report.html`
- Browser launch: open the final `REPORT_URL=` in the Codex in-app browser when available.

The report includes:

- Session stats and tool usage charts.
- At-a-glance summary.
- Project area analysis.
- Interaction style narrative.
- Friction analysis.
- Plain-English prompting help.
- AGENTS.md suggestions.
- Codex feature recommendations.
- Priority fixes and future workflows.

## Workflow

```bash
python3 Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py --days 7
```

Process:

1. Parse recent sessions from `~/.codex/sessions/`.
2. Compute deterministic metrics, tool counts, errors, response timing, and parallel Codex usage.
3. Write `insight-evidence.json`.
4. Write `INSIGHT_PROMPT.md`.
5. Invoke `codex exec --sandbox read-only` and pass the prompt on stdin.
6. Parse Codex's JSON response into `insights.generated.json`.
7. Render `report.html` from the deterministic metrics and Codex-written insights.
8. Open the printed `REPORT_URL=` in the Codex in-app browser.

Use `--prepare-only` when this live Codex session should write the insight JSON manually instead of invoking `codex exec`:

```bash
python3 Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py --prepare-only --no-open
```

Use `--render-only` after editing or regenerating `insights.generated.json`:

```bash
python3 Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py --render-only --no-open
```

## Codex Browser Launch

After the HTML report is completed, read the runner output line:

```text
REPORT_URL=file://$HOME/.codex/usage-data/report.html
```

Then use the Browser plugin's in-app browser workflow to open that URL. Prefer the Codex browser over macOS `open` when this skill is running inside Codex.

If Browser tooling is unavailable, report the `REPORT_URL` clearly and leave the file on disk.

Do not claim the browser launch happened until the Codex browser has actually navigated to the `REPORT_URL`.

## Codex Writer Contract

Codex must return only valid JSON with these top-level sections:

- `metadata`
- `at_a_glance`
- `project_areas`
- `interaction_style`
- `what_works`
- `friction_analysis`
- `prompting_help`
- `suggestions`
- `on_the_horizon`
- `actionable_fixes`
- `fun_ending`

The writer must:

- Use only the evidence bundle.
- Avoid inventing outcomes, files, tools, or user sentiment.
- Write in second person.
- Separate Codex-side friction from user-side ambiguity.
- Include copyable prompts for situations where Jamie lacks the technical vocabulary.
- Put missing-data caveats in `metadata.limitations`.

## Validation

Stop at the first failed gate. Do not continue to report rendering, browser launch, or final summary if evidence generation, prompt writing, Codex JSON generation, JSON validation, or HTML generation fails.

- Evidence file exists and is valid JSON.
- Prompt file exists and is non-empty.
- `insights.generated.json` exists and is valid JSON.
- Required insight sections are present.
- HTML renders without requiring a network connection.
- Final `REPORT_URL=` was opened in the Codex in-app browser, or Browser unavailability was disclosed.
- Use repo validation before finishing changes to the skill:

```bash
./bin/ask skills audit Skills/agent-ops/insight-report --level strict --json
```

## Failure Modes

**No session data found:**

```text
No session data found in ~/.codex/sessions/
```

Run Codex for a few sessions first, then regenerate the report.

**Codex CLI unavailable:**

Use `--prepare-only`, then ask the current Codex session to read `INSIGHT_PROMPT.md`, write `insights.generated.json`, and rerun with `--render-only`.

**Codex returned invalid JSON:**

Open `INSIGHT_PROMPT.md`, ask Codex to repair the JSON shape, save `insights.generated.json`, and rerun `--render-only`.

## Gotchas

- `--prepare-only` intentionally does not render HTML; it only writes the evidence bundle and prompt for Codex-authored analysis.
- Sparse or missing sessions are not a runner failure. Preserve the limitation in the generated insight JSON instead of inventing patterns.
- The report path is outside this repository under `$HOME/.codex/usage-data/`; do not commit generated reports or prompts to `agent-skills`.
- Browser launch is a separate verification step. The runner printing `REPORT_URL=` is not proof that the Codex in-app browser opened it.

## Safety

- The runner reads local Codex session data and writes local report artifacts only.
- Codex receives a bounded evidence bundle, not unrestricted filesystem access.
- `codex exec` is invoked with `--sandbox read-only`.
- The Python runner saves the generated JSON and HTML locally.
- Sensitive-looking values in sessions should be treated as evidence only, not repeated unless needed for a safe recommendation.

## Anti-patterns

| Anti-pattern | Safer behavior |
|--------------|----------------|
| Asking another model or local service to write the narrative | Use the Codex writer path only, or stop in `--prepare-only` for this Codex session to write it |
| Guessing insights when sessions are missing or sparse | State the evidence gap in `metadata.limitations` and keep claims conservative |
| Passing user-supplied shell commands into the report runner | Use the fixed `codex exec --sandbox read-only` invocation |
| Repeating secrets, tokens, or private prompt fragments from session logs | Summarize the pattern without exposing sensitive strings |
| Saying the report opened in the Codex browser before navigation succeeds | Report the `REPORT_URL` and disclose Browser unavailability or failure |
| Turning report suggestions into automatic cleanup commands | Keep recommendations copyable and non-destructive unless the user explicitly asks for follow-up implementation |

## Examples

**Standard weekly review with browser launch:**

```bash
python3 Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py --days 7
```

After the runner prints `REPORT_URL=file://...`, open that URL in the Codex in-app browser and mention the local path in the summary.

**Prepare artifacts for this Codex conversation to write:**

```bash
python3 Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py --prepare-only --no-open
```

**Render after Codex-written JSON exists:**

```bash
python3 Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py --render-only --no-open
```

## References

- Generator: `Infrastructure/references/deferred-skill-context/agent-ops-insight-report/scripts/run_insight_report.py`
- Configuration: `references/configuration.md`
- Writer contract: `references/codex-writer.md`
- Report format: `references/report-format.md`
- Output root: `$HOME/.codex/usage-data/`

## See Also

| Skill | When to use |
|-------|-------------|
| [[codex-automation-architect]] | Convert recommendations into Codex automations |
| [[skill-refactor]] | Analyze skill usage and improvement opportunities |
| [[ubiquitous-language]] | Extract terminology Jamie can reuse in future prompts |

**Topic map:** [[agent-ops]]
