---
name: better-icons
description: "Create and retrieve SVG icons via Better Icons (CLI/MCP). Use when you need icon lookup or SVG retrieval from Iconify libraries for UI work."
metadata:
  tags: icons, svg, iconify, cli, mcp
  short-description: "Find and fetch SVG icons."
---

# Better Icons

## When to use
- You need to search icons across multiple libraries (Iconify) and retrieve SVGs.
- You want a CLI workflow to fetch icons for design or UI implementation.
- You want to use the Better Icons MCP server for AI-assisted icon lookup.

## Inputs
- Icon query (keywords, or specific prefix:name ID).
- Optional: library prefix (e.g., `lucide`, `mdi`, `heroicons`).
- Optional: output size or color.
- Optional: JSON output preference.

## Outputs
- CLI command guidance for search/get.
- Suggested icon IDs or SVG output steps.
- Include `schema_version: 1` if outputs are contract-bound.

## Philosophy
- Why: icon choice shapes user comprehension; clarity beats novelty.
- Principle: prefer explicit IDs and libraries to avoid ambiguity.
- Mental model: search -> shortlist -> select -> fetch -> verify in context.
- Framework: constraints + library choice + consistent usage = coherent iconography.
- Keep icon usage consistent across a feature (one library per surface when possible).
- Fetch SVGs deterministically to avoid visual drift.

## Variation
- Vary output to the consumer: design exploration (many options) vs implementation (single choice).
- Adapt by platform: mobile needs bolder silhouettes, desktop tolerates finer detail.
- Avoid generic patterns; tailor suggestions to the UI context (navigation, status, action).
- If the query is vague, return 3–5 candidate icons with rationale.
- For strict design systems, constrain to approved libraries only.

## Procedure
1) Clarify the icon goal (concept, UI context, and target library).
2) Use `better-icons search` to find candidates.
3) Pick the best icon IDs and fetch SVGs with `better-icons get`.
4) If needed, output JSON for tooling pipelines.

## Validation
- Fail fast: stop at the first failed validation gate.
- Ensure the suggested IDs exist in the target library.
- Provide a minimal verification command (`better-icons get <id>`).

## Anti-patterns
- Guessing icon IDs without searching first.
- Mixing icon libraries in the same UI surface without justification.
- Using raw SVGs that violate brand or licensing constraints.
- Mistake: choosing icons by name only without checking shape semantics.
- Avoid generic icons that conflict with established product metaphors.
- DO NOT claim an icon exists without a `search` confirmation.
- NEVER ignore library prefix conflicts.

## Constraints
- Redact secrets/PII by default.
- Do not add dependencies without explicit approval.
- Prefer library‑approved icons where a design system exists.

## CLI Quick Reference
```bash
# Search icons
better-icons search <query> [--prefix <prefix>] [--limit <n>] [--json]

# Get icon SVG (outputs to stdout)
better-icons get <icon-id> [--color <color>] [--size <px>] [--json]

# Setup MCP server for AI agents
better-icons setup [-a cursor,claude-code] [-s global|project]
```

## Examples
```bash
better-icons search arrow --limit 10
better-icons search home --json | jq '.icons[0]'
better-icons get lucide:home > icon.svg
better-icons get mdi:home --color '#333' --json
```

## Resources
- `references/contract.yaml`
- `references/evals.yaml`

## Remember
The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they do not constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.
