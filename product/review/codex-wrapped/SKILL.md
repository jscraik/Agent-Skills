---
name: codex-wrapped
description: Generate a Codex/Claude Code usage recap from local logs, including last
  30 days, last 7 days, and all-time stats. Use when the user asks for a usage summary,
  activity recap, or coding activity report.
metadata:
  short-description: Generate a Codex/Claude Code usage recap from local logs, including
    last 30 d...
---

# Codex Wrapped

Generate a text-only usage report from local agent logs (Codex CLI or Claude Code).

## Scope and triggers

- User asks for "wrapped" report, usage summary, or activity recap
- User wants to see coding statistics over time
- User asks "how much have I used Codex/Claude?"

## Required inputs

- Local agent log directory (auto-detected):
  - Codex: `~/.codex/logs/` or `~/.codex/`
  - Claude Code: `~/.claude/logs/` or `~/.claude/`
- Timezone (optional, defaults to system timezone)

## Deliverables

- Text report with:
  - Last 7 days activity
  - Last 30 days activity
  - All-time focus hours estimate
  - Top file types edited
  - Most active repositories

## Philosophy
- Prefer evidence from logs over assumptions; call out coverage gaps.
- Summaries should be reproducible, honest, and privacy-preserving.

## Procedure

1. **Compute stats**
   ```bash
   python3 scripts/get_stats.py --output /tmp/wrapped_stats.json
   ```

2. **Render report**
   ```bash
   python3 scripts/render_report.py --stats-file /tmp/wrapped_stats.json
   ```

## Notes

- Report is text-only (no image generation)
- Stats are computed from local log files, not external APIs
- Sensitive data is redacted from output

## Anti-patterns
- Claiming metrics without reading logs or verifying coverage.
- Exposing raw log contents or secrets in the report.
- Ignoring timezone or partial log ranges when summarizing.

## Resources

- `scripts/get_stats.py` — computes rolling-window stats
- `scripts/render_report.py` — text report renderer
- `references/evals.yaml` — evaluation cases

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Examples
- "Provide a concise response for this task."
- "Follow the workflow and summarize outputs."

## Variation
- Vary tone, depth, and structure based on context.
- Avoid repeating the same outline across outputs.

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.
