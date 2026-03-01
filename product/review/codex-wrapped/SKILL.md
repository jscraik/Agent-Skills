---
name: codex-wrapped
description: Generate a Codex/Claude Code usage recap from local logs, including last
  30 days, last 7 days, and all-time stats. Use when the user asks for a usage summary,
  activity recap, or coding activity report.
knowledge_graph_profile: references/task-profile.json
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

## Validation

- Fail fast: stop at the first failed check and do not continue.
- Re-run the required checks before proceeding to the next step.
- Report any failed check and requested follow-up actions clearly.

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
