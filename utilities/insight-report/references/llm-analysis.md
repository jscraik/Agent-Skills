# LLM Analysis Deep Dive

How the insight report uses local Ollama LLMs for intelligent session analysis.

## Facet Extraction

Each session is analyzed to extract structured facets:

```json
{
  "underlying_goal": "What the user was trying to achieve",
  "goal_categories": {
    "implement_feature": 2,
    "debug_issue": 1,
    "refactor_code": 0
  },
  "outcome": "fully_achieved",
  "user_satisfaction": "happy",
  "assistant_helpfulness": "essential",
  "session_type": "iterative_refinement",
  "friction_counts": {
    "misunderstood_request": 1,
    "wrong_tool": 0,
    "hallucination": 0
  },
  "friction_summary": "Brief description of friction",
  "primary_success": "correct_edits",
  "brief_summary": "One sentence summary"
}
```

### Extraction Prompt

```
You are analyzing a Codex session transcript to extract structured facets.

USER TRANSCRIPT:
{transcript}

Extract this JSON structure:
{
  "underlying_goal": "What was the user trying to achieve?",
  "goal_categories": {"implement_feature": 0-3, "debug_issue": 0-3, ...},
  "outcome": "fully_achieved|mostly_achieved|partially_achieved|not_achieved",
  "user_satisfaction": "happy|neutral|frustrated",
  "assistant_helpfulness": "essential|helpful|neutral|unhelpful",
  "session_type": "exploratory|focused|iterative_refinement|debugging",
  "friction_counts": {"misunderstood_request": N, ...},
  "friction_summary": "Brief description of friction",
  "primary_success": "correct_edits|good_suggestions|time_saved",
  "brief_summary": "One sentence summary"
}
```

## Parallel Insight Generation

Six insight sections are generated concurrently:

1. **at_a_glance** — 4 summaries: working well, hindering, quick wins, ambitious workflows
2. **project_areas** — What domains you work in (backend, frontend, devops, etc.)
3. **interaction_style** — How you use Codex (hands-off, collaborative, precise, etc.)
4. **what_works** — Patterns that lead to successful sessions
5. **friction_analysis** — Categories of friction with examples
6. **suggestions_and_horizon** — AGENTS.md suggestions + on-the-horizon features

### Example Prompt (What Works)

```
Based on these session facets, identify patterns in successful sessions:

FACETS:
{facets}

Output JSON:
{
  "impressive_things": ["thing 1", "thing 2", ...],
  "what_works": ["pattern 1", "pattern 2", ...],
  "confidence": "high|medium|low"
}
```

## Model Recommendations

| Model | Speed | VRAM | Quality |
|-------|-------|------|---------|
| `qwen3-coder` | Fast (~2s/facet) | 4GB | Good |
| `phi4` | Fast (~2s/facet) | 4GB | Good |
| `qwen3.5` | Medium (~3s/facet) | 8GB | Better |
| `mistral:7b` | Medium (~3s/facet) | 8GB | Good |
| `gemma2:9b` | Slow (~6s/facet) | 10GB | Best |

**Default:** `qwen3-coder` for speed/quality balance.

## Performance

- Facet extraction: ~2-4 seconds per session
- Parallel workers: 3 (configurable via `INSIGHTS_WORKERS`)
- Session limit: 50 most recent (for LLM analysis)
- Total time with LLM: ~60-120 seconds for 50 sessions
- Time without LLM: ~5 seconds

## Caching

Extracted facets are cached in `~/.codex/usage-data/facets-cache.json`:
- Key: Session ID
- Value: Facet data + extraction timestamp
- Reruns skip already-analyzed sessions
- Cache invalidated when sessions exceed 7 days
