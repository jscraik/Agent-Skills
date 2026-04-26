# Codex Writer Contract

How `insight-report` asks Codex to write narrative insight from local evidence.

## Table of Contents

- [Pipeline](#pipeline)
- [Evidence Bundle](#evidence-bundle)
- [Required JSON](#required-json)
- [Writing Rules](#writing-rules)
- [Prompting Help](#prompting-help)

## Pipeline

1. Python parses local Codex sessions.
2. Python computes deterministic metrics.
3. Python writes `insight-evidence.json`.
4. Python writes `INSIGHT_PROMPT.md`.
5. Codex writes the narrative JSON.
6. Python validates required sections and renders HTML.

## Evidence Bundle

`insight-evidence.json` contains:

- Period and session counts.
- Tool counts and tool error categories.
- Message timing and response-time data.
- Parallel Codex session detection.
- Bounded transcript excerpts for recent sessions.

The bundle is evidence only. Codex must not invent missing data.

## Required JSON

Codex writes `insights.generated.json` with these top-level sections:

```json
{
  "metadata": {},
  "at_a_glance": {},
  "project_areas": {},
  "interaction_style": {},
  "what_works": {},
  "friction_analysis": {},
  "prompting_help": {},
  "suggestions": {},
  "on_the_horizon": {},
  "actionable_fixes": {},
  "fun_ending": {}
}
```

## Writing Rules

- Return only JSON.
- Use second person.
- Be direct, useful, and evidence-backed.
- Separate Codex-side friction from user-side ambiguity.
- Put weak-evidence caveats in `metadata.limitations`.
- Prefer copyable prompts and concrete next actions.

## Prompting Help

The `prompting_help` section is mandatory because Jamie may know the outcome they want without knowing the technical vocabulary.

Include:

- `plain_english_patterns`: copyable prompts for describing intent, current behavior, expected behavior, and uncertainty.
- `terms_to_learn`: small glossary entries that help Jamie ask for common Codex workflows.
