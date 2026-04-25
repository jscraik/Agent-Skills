# Configuration Guide

Codex-only configuration for `insight-report`.

## Table of Contents

- [Environment Variables](#environment-variables)
- [CLI Options](#cli-options)
- [Outputs](#outputs)
- [Codex Browser Launch](#codex-browser-launch)
- [Troubleshooting](#troubleshooting)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `INSIGHTS_CODEX_TIMEOUT` | `900` | Timeout in seconds for Codex JSON generation |
| `INSIGHTS_CODEX_COMMAND` | auto-detected `codex` | Codex CLI executable/command used for JSON generation |
| `INSIGHT_REPORT_USAGE_DIR` | `$HOME/dev/configs/codex/usage-data` | Output directory for report artifacts |
| `CODEX_SESSIONS_DIR` | `$HOME/.codex/sessions` | Session input directory |
| `CODEX_HISTORY_FILE` | `$HOME/.codex/history.jsonl` | History input file |

## CLI Options

```bash
python3 Skills/agent-ops/insight-report/scripts/run_insight_report.py [options]

Options:
  --days N                    Days of data to analyze (default: 7)
  --max-sessions N            Max sessions to scan (default: 200)
  --max-evidence-sessions N   Max transcript excerpts for Codex (default: 30)
  --prepare-only              Write evidence and prompt, then stop before invoking Codex
  --render-only               Render HTML from existing evidence and insights JSON
  --evidence-out PATH         Evidence JSON path
  --prompt-out PATH           Codex prompt path
  --insights-out PATH         Codex-written insights JSON path
  --insights-in PATH          Existing insights JSON for --render-only
  --no-open                   Compatibility flag; the runner never opens the OS browser
  --verbose                   Show progress details
```

## Outputs

Default output root:

```text
$HOME/.codex/usage-data/
```

Files:

```text
insight-evidence.json
INSIGHT_PROMPT.md
insights.generated.json
report.html
```

The runner prints a stable launch line:

```text
REPORT_URL=file://$HOME/dev/configs/codex/usage-data/report.html
```

## Codex Browser Launch

When used as a skill inside Codex, open the printed `REPORT_URL=` in the Codex in-app browser after the report is complete.

The Python runner never calls the OS browser opener. When Browser tooling is not available, leave the `REPORT_URL` visible and say the in-app launch was skipped.

## Troubleshooting

### No session data found

```bash
ls -la ~/.codex/sessions/
```

Run a few Codex sessions first, then regenerate the report.

### Codex command unavailable

```bash
codex --version
```

If the command is unavailable, run with `--prepare-only`, ask the current Codex session to write `insights.generated.json` from `INSIGHT_PROMPT.md`, then rerun with `--render-only`.

### Invalid JSON from Codex

Open `INSIGHT_PROMPT.md`, ask Codex to repair the JSON to match the required schema, save it to `insights.generated.json`, then run:

```bash
python3 Skills/agent-ops/insight-report/scripts/run_insight_report.py --render-only --no-open
```
