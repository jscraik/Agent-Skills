---
name: insight-report
description: Generate a high-fidelity Codex usage insights HTML report from local Codex session data when asked for "insights report", "usage report", or "analyze my Codex sessions".
knowledge_graph_profile: references/task-profile.json
---

# Insight Report (Codex)

## When to use
- User asks for a Codex usage insights report
- User wants a shareable HTML summary from local Codex session data

## Inputs
- Optional arg: `open` or `launch`
- Optional arg: `days=N` (lookback window)
- Optional arg: `closed-loop` (auto-execute top recommendation + before/after delta)

## Safety constraints
- Use local files only
- Do not send private usage data to external services
- Do not modify unrelated files

## Procedure
1) Run the local report generator script:
   - Default:
     - `python3 /Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py`
   - If user requests a custom window:
     - `python3 /Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py --days N`
   - If user asked to open/launch:
     - `python3 /Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py --open`
   - If both custom window and open are requested:
     - `python3 /Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py --days N --open`
   - If closed-loop is requested:
     - `python3 /Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py --closed-loop`
   - If both custom window and closed-loop are requested:
     - `python3 /Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py --days N --closed-loop`
   - If open and closed-loop are both requested:
     - `python3 /Users/jamiecraik/dev/config/codex/scripts/generate-insight-report.py --open --closed-loop`
2) Confirm output files exist:
   - `/Users/jamiecraik/dev/config/codex/usage-data/report.html`
   - `/Users/jamiecraik/dev/config/codex/usage-data/facets/latest.json`
3) Verify report contains high-fidelity sections:
   - At a Glance, What You Work On, How You Use Codex, Impressive Things, Friction, Features, Patterns, On the Horizon, Team Feedback
4) Final response must be exactly:

Your shareable insights report is ready:
file:///Users/jamiecraik/dev/config/codex/usage-data/report.html

Want to dig into any section or try one of the suggestions?

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- For non-trivial outcomes, collect user feedback via AskQuestion parity (`request_user_input`) before closing the run.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-creator/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
