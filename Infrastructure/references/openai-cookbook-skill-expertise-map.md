# OpenAI Cookbook Skill Expertise Map

Use this map when deciding where OpenAI Cookbook examples should strengthen the
skill system. The Cookbook is an expertise source, not content to paste into
skills: extract small decision lenses, evaluator checks, and reference paths;
do not copy notebook code, outputs, images, datasets, prompts, or long examples
into repository skill files.

Companion reusable lens pack:
[openai-cookbook-expert-lens-pack.md](./openai-cookbook-expert-lens-pack.md).

Initial intake:
[openai-cookbook-skill-opportunities.md](./openai-cookbook-skill-opportunities.md).

## Source Inventory

| Cookbook source | Expertise lens to extract | Best use |
| --- | --- | --- |
| examples/evaluation/Building_resilient_prompts_using_an_evaluation_flywheel.md | failure taxonomy, labeled examples, graders, prompt optimization, monitoring handoff | Eval program design, prompt resilience, and skill eval hardening. |
| examples/evaluation/use-cases/responses-evaluation.ipynb, regression.ipynb, bulk-experimentation.ipynb, completion-monitoring.ipynb | platform eval lifecycle, bulk runs, regression checks, stored completion monitoring | Evals Router and release-readiness evidence. |
| examples/Custom-LLM-as-a-Judge.ipynb | judge prompt structure, label calibration, advisory scoring | Subjective reviewer and judge prompts. |
| examples/Optimize_Prompts.ipynb, examples/gpt-5/prompt-optimization-cookbook.ipynb | baseline-vs-optimized prompt comparison, iterative prompt repair | Skill Builder, Skillify, and prompt migration hardening. |
| examples/agents_sdk/agent_improvement_loop.ipynb | trace-backed agent improvement, feedback loops, eval generation | Agent, skill, and reviewer improvement loops. |
| examples/codex/using_goals_in_codex.ipynb | native goal state, long-running objective receipts, completion proof | Goal Governor and goal-aware Harness Engineering work. |
| articles/codex_exec_plans.md | multi-hour execution plans, living progress, idempotent steps | Harness Engineering plans, work execution, and coding-harness guidance. |
| examples/codex/Build_iterative_repair_loops_with_Codex.ipynb, examples/codex/Autofix-github-actions.ipynb | repair loops, CI-driven fixes, bounded validation | Autofix, Codex Review, PR Green Sweep, and HE work. |
| examples/codex/build_code_review_with_codex_sdk.md, examples/codex/secure_quality_gitlab.md | code review automation, secure quality gates, review accounting | Codex Review, security review, and PR readiness skills. |
| examples/mcp/mcp_tool_guide.ipynb, examples/mcp/databricks_mcp_cookbook.ipynb | MCP tool/resource/prompt design, auth, tool verification | MCP Builder and backend integration skills. |
| examples/responses_api/responses_api_tool_orchestration.ipynb, responses_example.ipynb, reasoning_items.ipynb | Responses API state, tool orchestration, reasoning item handling | Backend Platform, MCP Builder, and possible Responses API skill. |
| examples/Structured_Outputs_Intro.ipynb, examples/Structured_outputs_multi_agent.ipynb | schema-first outputs, multi-agent contracts, parser-backed validation | Evals, agent workflows, review reports, and handoff artifacts. |
| examples/agents_sdk/session_memory.ipynb, building_reliable_agents_memory_compaction.ipynb, context_personalization.ipynb | trimming, compression, summary evals, personalization boundaries | Keep Codex Fast, Project Brain, and agent memory workflows. |
| examples/evaluation/use-cases/EvalsAPI_Image_Inputs.ipynb, EvalsAPI_Audio_Inputs.ipynb, examples/multimodal/image_evals.ipynb | multimodal evals, media provenance, artifact-specific repair | Frontend UI, visual explainer, imagegen, voice, and document skills. |
| articles/what_makes_documentation_good.md, examples/gpt-5/gpt-5_prompting_guide.ipynb, gpt-5_troubleshooting_guide.ipynb | direct documentation, prompt migration, troubleshooting flow | Docs, skill front doors, and user-facing instruction cleanup. |
| examples/Developing_hallucination_guardrails.ipynb, examples/How_to_use_guardrails.ipynb, articles/gpt-oss-safeguard-guide.md | guardrails, safety boundaries, adversarial validation | Security Ops and quality gate review. |

## Primary Skill Targets

| Skill | Add these Cookbook lenses | Why it helps |
| --- | --- | --- |
| Skills/agent-ops/evals-router | Evaluation Flywheel Builder, Structured Judge Calibrator, Multimodal Eval Designer | This is the main owner for turning Cookbook eval patterns into local failure taxonomies, judge checks, regression runs, and prompt or RAG evaluation routes. |
| Plugins/skill-factory/skills/code_quality_review/skill-builder | Skill Improvement Loop Operator, Documentation Interface Editor, Structured Output Contract Keeper | Skill hardening should use trace/eval-backed before-after comparisons, keep entrypoints compact, and avoid unstructured prose reports. |
| Plugins/skill-factory/skills/scaffolding_templates/skillify | Skill Improvement Loop Operator, Documentation Interface Editor, Evaluation Flywheel Builder | New skills should start with repeatable evidence, negative cases, validation routes, and Cookbook-derived patterns only when existing skill ownership does not fit. |
| Skills/agent-ops/goal-governor | Codex Goal Steward, Execution Plan Steward | Goal workflows need native state reconciliation, receipts, validation freshness, and careful completion proof. |
| Plugins/harness-engineering/skills/he-plan | Execution Plan Steward, Evaluation Flywheel Builder | Plans should be living, idempotent, handoff-ready, and tied to exact validation. |
| Plugins/harness-engineering/skills/he-work | Execution Plan Steward, Iterative Repair Operator | Implementation work should follow small validated slices, retryable steps, and repair loops grounded in current failures. |
| Skills/agent-ops/coding-harness | Execution Plan Steward, Secure Quality Gate Reviewer | Harness work benefits from clear multi-hour plan contracts and gate ownership classification. |
| Skills/agent-ops/codex-review | Iterative Repair Operator, Structured Output Contract Keeper, Secure Quality Gate Reviewer | Review should account for accepted/rejected findings, structured reports, current evidence, and scoped reruns. |
| Skills/agent-ops/autofix | Iterative Repair Operator, Secure Quality Gate Reviewer | Autofix should inventory every actionable item, patch only accepted failure classes, and rerun affected gates. |
| Skills/agent-ops/pr-green-sweep | Iterative Repair Operator, Secure Quality Gate Reviewer | PR rotation needs live CI/review truth, blocker classification, and merge-readiness evidence. |
| Skills/agent-ops/keep-codex-fast | Context Memory Curator, Evaluation Flywheel Builder | Cleanup and compaction should preserve durable context and evaluate whether summaries lose important decisions. |
| Skills/agent-ops/project-brain | Context Memory Curator, Documentation Interface Editor | Project Brain should separate durable project knowledge from disposable transcript noise. |
| Skills/backend-platform/mcp-builder | Tool Orchestration Designer, Structured Output Contract Keeper, Guardrail System Reviewer | MCP work is an integration boundary; tools, resources, prompts, schemas, auth, and safety gates must be explicit. |
| Skills/backend-platform/backend-engineer | Tool Orchestration Designer, Structured Output Contract Keeper | Backend OpenAI integrations need schema-first outputs, state handling, and tool orchestration validation. |
| Skills/frontend-ui/frontend-ui-design | Multimodal Eval Designer, Documentation Interface Editor | Visual implementation can borrow spec-first visual eval and artifact repair patterns. |
| Skills/content-publishing/visual-explainer | Multimodal Eval Designer, Documentation Interface Editor | Visual artifacts need source provenance, artifact checks, and readability-first documentation behavior. |
| Skills/security-ops/* | Guardrail System Reviewer, Secure Quality Gate Reviewer | Security workflows need explicit guardrail ownership, adversarial validation, and fail-closed blocker behavior. |

## Candidate New Skill Decisions

Create these only after checking fold confidence and repeated demand.

| Candidate | Prefer existing owner first | Build when |
| --- | --- | --- |
| responses-api-builder | Skills/backend-platform/backend-engineer, Skills/backend-platform/mcp-builder | Repeated work needs OpenAI Responses API-specific state, tool orchestration, structured output, web/file search, or reasoning-item guidance. |
| agents-sdk-workflow-builder | OpenAI Developers plugin, Harness Engineering skills, mcp-builder | Jamie wants first-party local ownership for Agents SDK orchestration, tracing, handoffs, sessions, guardrails, or deployment workflows. |
| multimodal-eval-builder | Skills/agent-ops/evals-router | Two or more repeated modality-specific eval workflows need media provenance, artifact QA, and modality-specific checks. |
| voice-agent-builder | OpenAI Developers plugin, content/media skills | Realtime voice, transcription, audio eval, and speech prompt repair become active local workflows. |
| openai-model-selection | evals-router, backend-engineer | Model choice becomes a standalone repeated decision requiring local benchmarks and cost/quality tradeoff artifacts. |

## How To Use The Material

1. Start from the target skill's purpose and pick at most two Cookbook lenses.
2. Convert each lens into local checks, not notebook summaries.
3. Keep active SKILL.md files compact and link to this map or the lens pack.
4. Put longer examples, eval rubrics, and source-path matrices in references.
5. Add eval prompts that prove the lens changed behavior.
6. Never claim local readiness from Cookbook examples alone.

## Good Extraction Shape

Use this shape when turning one Cookbook area into skill material:

~~~yaml
source_area: OpenAI Cookbook evaluation flywheel
skill_targets:
  - Skills/agent-ops/evals-router
  - Plugins/skill-factory/skills/code_quality_review/skill-builder
lenses:
  - Name failure taxonomies before graders.
  - Validate binary judges against labeled examples.
  - Compare baseline and optimized outputs before claiming improvement.
eval_checks:
  - Given a vague judge prompt, does the skill require labels before release?
  - Given synthetic cases only, does the skill mark production coverage as blocked?
do_not_do:
  - Do not paste notebook code into SKILL.md.
  - Do not create a new skill before checking existing ownership.
  - Do not replace repo validation with Cookbook authority.
~~~

## Highest-Leverage Wiring Order

1. Skills/agent-ops/evals-router
2. Plugins/skill-factory/skills/code_quality_review/skill-builder
3. Plugins/skill-factory/skills/scaffolding_templates/skillify
4. Skills/agent-ops/goal-governor
5. Skills/backend-platform/mcp-builder
6. Plugins/harness-engineering/skills/he-plan
7. Skills/agent-ops/codex-review
8. Skills/agent-ops/keep-codex-fast

This order gives the biggest compounding return: evals prove behavior,
skill-builder preserves it, skillify packages it, goal/work planning keeps long
runs aligned, MCP/backend skills carry OpenAI API patterns into implementation,
and review/maintenance skills keep the loop honest.
