# OpenAI Cookbook Skill Opportunity Intake

Source snapshot: local snapshot of the OpenAI Cookbook repository

This intake maps OpenAI Cookbook material to Agent Skills Kit changes. Treat it
as an external pattern extraction surface: improve canonical skill sources when
an owner already exists; create a new skill only when no existing route owns the
repeatable workflow.

## Snapshot Notes

- A direct `git clone https://github.com/openai/openai-cookbook.git` was
  attempted first, but Git transport stalled and left only temporary pack state.
- The usable working tree came from
  `https://github.com/openai/openai-cookbook/archive/refs/heads/main.tar.gz`.
- The snapshot is large, roughly 1 GB after extraction, and should stay in
  a local scratch directory; do not vendor Cookbook files into this repository.

## Highest-Value Existing Skill Improvements

| Priority | Target canonical source | Cookbook evidence | Recommended improvement |
| --- | --- | --- | --- |
| P0 | `Skills/agent-ops/evals-router` | `examples/evaluation/Building_resilient_prompts_using_an_evaluation_flywheel.md`, `examples/evaluation/use-cases/responses-evaluation.ipynb`, `examples/evaluation/use-cases/regression.ipynb`, `examples/evaluation/use-cases/bulk-experimentation.ipynb`, `examples/evaluation/use-cases/completion-monitoring.ipynb`, `examples/evaluation/use-cases/web-search-evaluation.ipynb` | Add a Cookbook-backed eval flywheel reference: failure taxonomy, labeled examples, binary grader calibration, prompt/model comparison, synthetic coverage only after known gaps, and CI/monitoring handoff. This should strengthen existing routes instead of becoming a separate generic eval skill. |
| P0 | `Plugins/skill-factory/skills/code_quality_review/skill-builder` and `Plugins/skill-factory/skills/scaffolding_templates/skillify` | `examples/Optimize_Prompts.ipynb`, `examples/gpt-5/prompt-optimization-cookbook.ipynb`, `examples/Custom-LLM-as-a-Judge.ipynb`, `examples/Unit_test_writing_using_a_multi-step_prompt.ipynb` | Extend the skill hardening loop with a measurable prompt/eval improvement ladder: baseline current skill behavior, generate or select realistic cases, critique weak assertions, validate a judge only when deterministic checks cannot score the outcome, then patch the smallest source surface. |
| P0 | `Skills/agent-ops/goal-governor` | `examples/codex/using_goals_in_codex.ipynb` | Fold Cookbook goal mechanics into the durable-goal workflow: native goal state, progress receipts, stale-goal reconciliation, and evidence required before marking a goal complete. |
| P1 | `Plugins/harness-engineering/skills/he-plan`, `Plugins/harness-engineering/skills/he-work`, and `Skills/agent-ops/coding-harness` | `articles/codex_exec_plans.md`, `examples/codex/Build_iterative_repair_loops_with_Codex.ipynb`, `examples/Build_a_coding_agent_with_GPT-5.1.ipynb`, `examples/codex/code_modernization.md` | Add an execution-plan quality reference for multi-hour implementation: beginner-readable current-state narrative, living progress, idempotent steps, validation per milestone, and additive migration strategy. |
| P1 | `Skills/agent-ops/codex-review`, `Skills/agent-ops/autofix`, and `Skills/agent-ops/pr-green-sweep` | `examples/codex/Autofix-github-actions.ipynb`, `examples/codex/build_code_review_with_codex_sdk.md`, `examples/codex/secure_quality_gitlab.md`, `examples/third_party/Code_quality_and_security_scan_with_GitHub_Actions.md` | Improve review-to-fix accounting with Cookbook repair-loop patterns: current CI/review truth, accepted/rejected findings, minimal patch bundles, rerun only affected gates, and stop when the review helper has no actionable findings. |
| P1 | `Skills/agent-ops/keep-codex-fast` and `Skills/agent-ops/project-brain` | `examples/agents_sdk/session_memory.ipynb`, `examples/agents_sdk/building_reliable_agents_memory_compaction.ipynb`, `examples/agents_sdk/context_personalization.ipynb` | Add a memory-compaction decision reference: trim versus summarize, what must remain audit-visible, summary evals, and avoiding silent loss of durable repo context. |
| P1 | `Skills/backend-platform/mcp-builder` | `examples/mcp/mcp_tool_guide.ipynb`, `examples/mcp/databricks_mcp_cookbook.ipynb`, `examples/codex/codex_mcp_agents_sdk/building_consistent_workflows_codex_cli_agents_sdk.ipynb` | Strengthen MCP design with tool/resource/prompt separation, auth and redaction checks, structured output expectations, Inspector-ready probes, and agent workflow compatibility. |
| P2 | `Skills/frontend-ui/frontend-ui-design` and `Skills/content-publishing/visual-explainer` | `examples/gpt-5/gpt-5_frontend.ipynb`, `examples/multimodal/grounded_spatial_reasoning_layouts.ipynb`, `examples/multimodal/image_evals.ipynb` | Borrow visual/spec-first evaluation patterns: explicit target layout spec, screenshot or image eval criteria, deterministic checks where possible, and repair queues for visual misses. |
| P2 | `Skills/security-ops/*` and `Skills/agent-ops/pr-green-sweep` | `articles/gpt-oss-safeguard-guide.md`, `examples/Developing_hallucination_guardrails.ipynb`, `examples/How_to_use_guardrails.ipynb`, `examples/partners/agentic_governance_guide/agentic_governance_cookbook.ipynb` | Add guardrail language only where it maps to existing safety scopes: threat boundary, input/output guardrail ownership, grader validation, and blocker-first handling when a guardrail cannot run. |

## Candidate New Skills

Prefer these only after checking fold confidence against existing routes.

| Priority | Candidate skill | Why existing routes may not be enough | Cookbook evidence | First-principles gate |
| --- | --- | --- | --- | --- |
| P1 | `responses-api-builder` | Current backend and MCP skills cover general implementation, but no local skill appears to own Responses API tool orchestration, structured outputs, previous response state, built-in web/file search, and reasoning-item handling as one repeatable workflow. | `examples/responses_api/responses_example.ipynb`, `examples/responses_api/responses_api_tool_orchestration.ipynb`, `examples/responses_api/reasoning_items.ipynb`, `examples/Structured_Outputs_Intro.ipynb`, `examples/Structured_outputs_multi_agent.ipynb` | Build only if repeated work needs OpenAI Responses API-specific design, validation, and migration guidance; otherwise add a reference under `backend-engineer`. |
| P1 | `agents-sdk-workflow-builder` | Harness Engineering owns Codex execution, and MCP Builder owns protocol surfaces, but Agents SDK app orchestration, tracing, handoffs, sessions, guardrails, and deployment examples are broader than either. | `examples/agents_sdk/evaluate_agents.ipynb`, `examples/agents_sdk/parallel_agents.ipynb`, `examples/agents_sdk/session_memory.ipynb`, `examples/agents_sdk/deployment_manager/README.md`, `examples/agents_sdk/sandboxed-code-migration/sandboxed_code_migration_agent.ipynb` | Build only if Jamie wants first-party local skills for OpenAI Agents SDK work instead of relying on the OpenAI Developers plugin. |
| P2 | `multimodal-eval-builder` | `evals-router` can route text/RAG evals, but Cookbook has image, audio, video, spatial, and document examples that may need modality-specific artifacts and acceptance checks. | `examples/evaluation/use-cases/EvalsAPI_Image_Inputs.ipynb`, `examples/evaluation/use-cases/EvalsAPI_Audio_Inputs.ipynb`, `examples/multimodal/image_evals.ipynb`, `examples/GPT_with_vision_for_video_understanding.ipynb`, `examples/multimodal/document_and_multimodal_understanding_tips.ipynb` | Start as an `evals-router` reference; promote to skill only after two or more modality-specific workflows repeat. |
| P2 | `voice-agent-builder` | Existing skills do not clearly own Realtime voice/audio agent setup, evaluation, transcription routing, or speech-specific prompt repair. | `examples/Realtime_prompting_guide.ipynb`, `examples/Realtime_eval_guide.ipynb`, `examples/Realtime_out_of_band_transcription.ipynb`, `examples/Speech_transcription_methods.ipynb`, `examples/voice_solutions/steering_tts.ipynb` | Build only when voice work becomes active; otherwise keep as future backlog. |
| P3 | `openai-model-selection` | Model selection appears scattered across platform, eval, and prompt workflows; a separate skill may be useful only if model choice becomes a common standalone request. | `examples/partners/model_selection_guide/model_selection_guide.ipynb`, `examples/stripe_model_eval/selecting_a_model_based_on_stripe_conversion.ipynb`, `examples/gpt-5/gpt-5_new_params_and_tools.ipynb`, `examples/gpt-5/gpt-5_troubleshooting_guide.ipynb` | Prefer an `evals-router` or `backend-engineer` reference unless standalone model-selection decisions repeat. |

## Immediate Implementation Order

1. Add an `evals-router` reference for the Cookbook eval flywheel and wire it
   from the active `SKILL.md`.
2. Add a `goal-governor` reference for Cookbook Codex goals and stale-goal
   reconciliation.
3. Add a shared Codex execution-plan reference for `he-plan`, `he-work`,
   and `coding-harness`.
4. Decide whether `responses-api-builder` should be a new first-party skill or
   a backend-platform reference after checking live repeated use.

## Anti-Patterns

- Do not copy Notebook code into skill entrypoints.
- Do not vendor Cookbook media or datasets into this repository.
- Do not create a new skill when an existing route can be improved with one
  compact reference and one eval.
- Do not treat Cookbook examples as validation for local skill behavior; each
  local skill still needs repo-owned audit/eval evidence.
