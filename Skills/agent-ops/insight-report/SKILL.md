---
name: insight-report
description: "WHAT: Generate comprehensive HTML insights from Codex OTEL data using local Ollama LLMs. WHEN: Use when the user asks for usage analytics, workflow patterns, Codex session summaries, or recommendations for improving their development workflow."
metadata:
  skill-type: data_fetch_analysis
---

# Insight Report

## Table of Contents

- [Philosophy](#philosophy)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Examples](#examples)
- [Implementation details](#implementation-details)
- [References](#references)
- [See Also](#see-also)

Full-featured Codex analytics with local LLM-powered session analysis. Uses **local Ollama LLMs** for intelligent session analysis.

## Philosophy

- **Evidence over intuition** — OTEL telemetry, not guesswork
- **Local LLM analysis** — Privacy-first with Ollama
- **Actionable recommendations** — Specific, contextual advice
- **Visual clarity** — Clean charts, structured presentation

## When to use

- "Show me my Codex analytics"
- "Generate my weekly insights report"
- "What am I doing well?"
- "Where am I getting stuck?"

**Requirements:** `CODEX_OTEL_ENABLED=1`, Ollama installed

## Required inputs

- Session data in `~/.codex/sessions/` (primary) or OTEL data in `~/.agents/otel-collector/`
- Time window: `--days N` (default: 7)
- Ollama model: `--model MODEL` (default: qwen3-coder)

Optional:
- `--skip-llm` — Basic metrics only (faster)
- `--verbose` — Show progress
- `--no-open` — Don't launch browser

## Deliverables

- HTML report: `file://$HOME/dev/configs/codex/usage-data/report.html`
- Facet cache: `$HOME/dev/configs/codex/usage-data/facets-cache.json`
- Report includes:
  - Session stats (count, duration, success rate)
  - Tool usage charts
  - **At a Glance** summary (4 sections)
  - Project areas analysis
  - Interaction style narrative
  - Friction point analysis
  - AGENTS.md suggestions
  - Feature recommendations
  - Ambitious workflows for future AI

## Quick Start

```bash
# 1. Enable OTEL
export CODEX_OTEL_ENABLED=1
codex

# 2. Install Ollama
curl -fsSL https://ollama.com/install.sh | sh
# Uses your installed models (qwen3-coder recommended)

# 3. Generate report
python3 Skills/insight-report/Infrastructure/scripts/run_insight_report.py
```

## Report Sections

| Section | Description |
|---------|-------------|
| **At a Glance** | 4 summaries: working, hindering, quick wins, ambitious workflows |
| **What You Work On** | Project areas with session counts |
| **How You Use Codex** | Narrative analysis of interaction style |
| **Impressive Things** | Your wins and effective workflows |
| **Where Things Go Wrong** | Friction categories with examples |
| **AGENTS.md Suggestions** | Rules you repeat that should be in AGENTS.md |
| **Features to Try** | MCP, Skills, Hooks, Headless, Agent recommendations |
| **On the Horizon** | Ambitious workflows for upcoming AI capabilities |

## LLM Analysis

### Facet Extraction (per session)

```json
{
  "underlying_goal": "What user wanted",
  "goal_categories": {"implement_feature": 2},
  "outcome": "fully_achieved",
  "user_satisfaction": "happy",
  "assistant_helpfulness": "essential",
  "session_type": "iterative_refinement",
  "friction_counts": {"misunderstood_request": 1},
  "friction_summary": "Description",
  "primary_success": "correct_edits",
  "brief_summary": "One sentence"
}
```

### Parallel Insight Generation

6 sections generated concurrently via Ollama:
- at_a_glance, project_areas, interaction_style
- what_works, friction_analysis, suggestions, on_the_horizon

**Time:** ~60s with qwen3-coder, ~3 parallel workers

### Model Recommendations

| Model | Speed | Quality |
|-------|-------|---------|
| `qwen3-coder` | Fast | ★★★☆ |
| `phi4` | Fast | ★★★☆ |
| `qwen3.5` | Medium | ★★★★ |

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `CODEX_OTEL_ENABLED` | `0` | Enable OTEL collection |
| `INSIGHTS_MODEL` | `qwen3-coder` | Ollama model |
| `OLLAMA_HOST` | `http://localhost:11434` | API endpoint |
| `INSIGHTS_WORKERS` | `3` | Parallel workers |

## Workflow

```bash
python3 Skills/insight-report/Infrastructure/scripts/run_insight_report.py [options]

# Process:
# 1. Parse OTEL spans from ~/.agents/otel-collector/
# 2. Group by session, extract metrics
# 3. [LLM] Extract facets from transcripts
# 4. [LLM] Generate 6 insight sections in parallel
# 5. Render HTML with charts
# 6. Open in browser
```

## Validation

- [ ] OTEL directory exists with span files
- [ ] Ollama running (if using LLM)
- [ ] Model available
- [ ] Sessions parsed successfully
- [ ] Insights generated
- [ ] HTML renders correctly

## Failure mode

**No tool data available:**
```
Top Tools Used: Not available — Codex runs tools server-side
```
OpenAI Codex runs tools server-side for security. Tool execution data is not stored 
locally (unlike Codex's ~/.codex/projects/ format).

**To enable general analytics:**
```bash
codex features enable general_analytics
```

Or add to `~/.codex/config.toml`:
```toml
general_analytics = true
```

Note: `general_analytics` is currently under development (default: false).

**Ollama not running:**
```
⚠ Ollama not available. Install: curl -fsSL https://ollama.com/install.sh | sh
  Uses your installed models (qwen3-coder recommended)
```

**Model not found:**
```
⚠ Model not found. Run: ollama pull qwen3-coder
```

## Constraints

- OTEL must be enabled before collection (can't retroactively collect)
- LLM requires Ollama running locally
- First report may show "no data" (wait for sessions)
- Large windows (30+ days) with LLM: 2-5 minutes
- Facet extraction limited to 50 recent sessions
- Secrets and sensitive data are redacted by default in session content

## Safety

- Session data is processed locally by Ollama and never sent to external APIs
- API keys and secrets in session content are redacted by default in the HTML report
- Reports are saved to local filesystem only (`$HOME/dev/configs/codex/usage-data/`)

## Anti-patterns

| Anti-pattern | Why it fails | Do instead |
|--------------|--------------|------------|
| Not enabling telemetry | Missing analytics data | Run `codex features enable general_analytics` |
| Skipping LLM always | Miss personalized insights | Use LLM for weekly reviews |
| Ignoring AGENTS.md suggestions | Repeat instructions | Add repeated rules to AGENTS.md |
| Not acting on friction | Miss improvements | Address high-priority friction |

## Examples

**Standard weekly review:**
```
User: "Generate my weekly insights"
→ python3 Skills/insight-report/Infrastructure/scripts/run_insight_report.py
→ Full analysis with qwen3-coder
```

**Quick metrics (no LLM):**
```
User: "Just the numbers"
→ python3 Skills/insight-report/Infrastructure/scripts/run_insight_report.py --skip-llm
→ 5 seconds vs 60 seconds
```

**Monthly with better model:**
```
User: "Monthly report"
→ python3 Skills/insight-report/Infrastructure/scripts/run_insight_report.py \
    --days 30 --model llama3.1:8b --no-open
```

## References

- Generator: `Infrastructure/scripts/run_insight_report.py`
- Facet cache: `$HOME/dev/configs/codex/usage-data/facets-cache.json`
- OTEL paths: `~/.agents/otel-collector/`

## See Also

| Skill | When to use |
|-------|-------------|
| [[codex-automation-architect]] | Convert recommendations into automations |
| [[codex-home-audit]] | Check Codex setup health |
| [[skill-refactor]] | Analyze skill usage |
| [[visual-explainer]] | Convert outcomes into visual explainers |

**Topic map:** [[agent-ops]]

## Gotchas

- **OTEL first** — Enable before running sessions
- **Ollama running** — Start with `ollama serve`
- **Uses your installed models** — qwen3-coder, phi4, or qwen3.5
- **Large models need VRAM** — 8B needs ~8GB GPU
- **50 session limit** — Only recent sessions analyzed
- **Facet cache speeds reruns** — Same sessions not re-analyzed

## Implementation

**Comparison:**

| Feature | Cloud Analytics | This (Local) |
|---------|-----------------|--------------|
| Data source | Remote collection | `~/.agents/otel-collector/*.jsonl` |
| LLM backend | Cloud API | Local Ollama |
| Privacy | Data leaves machine | Fully local |
| Facet extraction | Yes | Yes (async/parallel) |
| Parallel insights | 6 sections | 6 sections |
| Charts | 8+ | 2-3 |
| Remote hosts | Yes | No |
| Lines | ~1,600 | ~865 |

**Key differences:** Local Ollama (privacy), Python, focused scope.
