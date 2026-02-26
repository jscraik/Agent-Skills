# Skill Knowledge Graph Operating Model

This guide maps the skill-graph runtime to a practical knowledge-graph model and adds delegation metadata so operators can explain **why** a run was autopilot, co-pilot, or manual override.

## Table of Contents

- [Why this model exists](#why-this-model-exists)
- [Runtime architecture (SKILL + MCP split)](#runtime-architecture-skill--mcp-split)
- [Cockpit Rule + cost-benefit metadata](#cockpit-rule--cost-benefit-metadata)
- [Graph entities and edges](#graph-entities-and-edges)
- [Progressive disclosure in practice](#progressive-disclosure-in-practice)
- [Operator workflow](#operator-workflow)
- [Workflow archetypes](#workflow-archetypes)
- [Validation checklist](#validation-checklist)

## Why this model exists

Skills provide the procedure layer (“recipe”), MCP/tools provide execution access (“hands”), and agents perform scoped runtime work (“chef”).
The skill knowledge graph preserves this procedural learning over time so future runs start from reviewed lessons instead of rediscovering the same fixes.

## Runtime architecture (SKILL + MCP split)

Every recursive run uses:

- **LLM processor**: reasoning over objective, evaluation output, and improvement options.
- **Skill recipe**: `SKILL.md` + policy docs + schemas that define deterministic steps.
- **Tools/MCP handoff layer**: command/script runners, trace emitters, and validation tools.

Default behavior: invoke the recipe first, then allow MCP tools only when the recipe explicitly requires them.

## Cockpit Rule + cost-benefit metadata

Task profiles can include an optional `delegation` block to record decision intent:

- `mode`: `autopilot | co-pilot | manual`
  - alias note: legacy value `collaboration` = `co-pilot`
- `human_baseline_minutes` (HBT)
- `ai_process_minutes` (APT)
- `probability_of_success` (Ps)
- `rationale`

### Mode mapping

- **Autopilot**: full automatic run path, no manual approvals.
- **Co-pilot**: automatic run with structured review checkpoints.
- **Manual override**: requires explicit human decision points before high-risk actions.

When present, loop outputs copy this to `run.json`, `promotion_decision.json`, and lesson candidates as `delegation_context`.

## Graph entities and edges

| Entity | Source artifact | Key edges |
| --- | --- | --- |
| Task profile | `docs/skill-graphs/schemas/task-profile.schema.md` | profile -> run |
| Run | `artifacts/skill-graphs/runs/<run_id>/run.json` | run -> iteration, run -> decision |
| Iteration | `iteration_journal.jsonl` | iteration -> candidate lesson |
| Candidate lesson | `lesson_candidates.json` | candidate -> promotion decision |
| Canonical lesson | `artifacts/skill-graphs/lessons/canonical-lessons.jsonl` | lesson -> supersedes lesson |
| Promotion decision | `promotion_decision.json` | decision -> canonical lesson |

## Progressive disclosure in practice

1. **Discovery**: route by SKILL frontmatter (`name`, `description`).
2. **Execution SOP**: load `SKILL.md` for the selected skill.
3. **Deep context**: load only the referenced schema/workflow/script needed for the current step.

This keeps context lean while retaining deterministic script-backed behavior.

## Operator workflow

1. Configure profile + delegation assumptions.
2. Run recursive loop (`recursive_skill_loop.py`).
3. Review promotion decision + evidence packet.
4. Promote approved lessons via human gate.
5. Use telemetry outputs to tune thresholds and routing.

## Workflow archetypes

Map phase pipeline to deck archetypes:

- **Sequential**: ordered execution (`configure -> generate -> evaluate -> diagnose -> improve -> rescore`).
- **Router**: branch by profile/objective into alternate evaluation paths or specialist review tracks.
- **Orchestrator**: one coordinator run that delegates bounded subtasks (e.g., capture, evaluate, gate) and merges findings.

## Validation checklist

- `python3 utilities/skill-creator/scripts/test_recursive_skill_loop_capture.py`
- `python3 utilities/skill-creator/scripts/test_validate_recursive_promotion.py`
- `python3 utilities/skill-creator/scripts/validate_recursive_promotion.py --run-dir <run_dir>`
- `python3 utilities/skill-creator/scripts/build_recursive_skill_shadow_report.py --runs-root artifacts/skill-graphs/runs --window-days 3`
