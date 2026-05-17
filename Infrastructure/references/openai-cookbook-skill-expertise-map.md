# OpenAI Cookbook Skill Expertise Map

Use this map to decide where OpenAI Cookbook patterns should strengthen local
skills. Keep SKILL.md hooks compact and load
Infrastructure/references/openai-cookbook-expert-lens-pack.md only when the
task needs a Cookbook-derived check.

## Primary Skill Targets

| Skill | Lenses | Use |
| --- | --- | --- |
| Skills/agent-ops/evals-router | Evaluation Flywheel Builder, Structured Output Contract Keeper, Multimodal Eval Designer | Eval taxonomies, judge calibration, regression runs, modality-specific artifact checks. |
| Plugins/skill-factory/skills/code_quality_review/skill-builder | Skill Improvement Loop Operator, Documentation Interface Editor, Structured Output Contract Keeper | Trace/eval-backed skill hardening and compact skill contracts. |
| Plugins/skill-factory/skills/scaffolding_templates/skillify | Skill Improvement Loop Operator, Documentation Interface Editor, Evaluation Flywheel Builder | New skills with success criteria, negative cases, and validation routes. |
| Skills/agent-ops/goal-governor | Codex Goal Steward, Execution Plan Steward | Goal state, receipts, validation freshness, completion proof. |
| Skills/agent-ops/coding-harness | Execution Plan Steward, Secure Quality Gate Reviewer | Multi-hour plan contracts and quality gate ownership. |
| Skills/agent-ops/codex-review | Skill Improvement Loop Operator, Structured Output Contract Keeper, Secure Quality Gate Reviewer | Structured review accounting and rerun evidence. |
| Skills/agent-ops/autofix | Skill Improvement Loop Operator, Secure Quality Gate Reviewer | Bounded repair loops and affected-gate reruns. |
| Skills/agent-ops/pr-green-sweep | Skill Improvement Loop Operator, Secure Quality Gate Reviewer | Live CI/review truth, blocker classification, merge-readiness evidence. |
| Skills/agent-ops/keep-codex-fast | Context Memory Curator, Evaluation Flywheel Builder | Compaction and memory quality checks. |
| Skills/agent-ops/project-brain | Context Memory Curator, Documentation Interface Editor | Durable project knowledge vs disposable transcript noise. |
| Skills/backend-platform/mcp-builder | Tool Orchestration Designer, Structured Output Contract Keeper, Secure Quality Gate Reviewer | MCP tools, resources, prompts, schemas, auth, and safety gates. |
| Skills/backend-platform/backend-engineer | Tool Orchestration Designer, Structured Output Contract Keeper | Backend OpenAI integrations, schemas, state, and tool orchestration validation. |
| Skills/frontend-ui/frontend-ui-design | Multimodal Eval Designer, Documentation Interface Editor | Visual QA, rendered artifacts, and repair loops. |
| Skills/content-publishing/visual-explainer | Multimodal Eval Designer, Documentation Interface Editor | Visual artifact provenance and readability checks. |
| Skills/security-ops/* | Secure Quality Gate Reviewer | Guardrail ownership, adversarial validation, fail-closed blockers. |

## Wiring Rules

1. Prefer existing skill ownership before creating a new OpenAI-specific skill.
2. Convert Cookbook patterns into local checks, not notebook summaries.
3. Add eval prompts when a Cookbook lens changes skill behavior.
4. Never claim local readiness from Cookbook examples alone.

## Candidate New Skill Decisions

Create a new skill only after repeated demand and overlap checks:

- responses-api-builder
- agents-sdk-workflow-builder
- multimodal-eval-builder
- voice-agent-builder
- openai-model-selection
