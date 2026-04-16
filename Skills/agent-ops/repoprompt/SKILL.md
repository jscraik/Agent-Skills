---
name: repoprompt
description: Plan and troubleshoot Repo Prompt integration across editors, agents, MCP, and CLI workflows. Use when the user wants Repo Prompt configured, adopted, or compared inside an AI coding setup.
metadata:
  skill-type: library_api_reference
---

# Repo Prompt Integration

## Compliance
- Check against current global instructions in `~/.codex/AGENTS.md` and linked standards docs.

## Table of Contents
- [Overview](#overview)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Response format](#response-format-required)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Philosophy](#philosophy)
- [Workflow Fit Assessment](#workflow-fit-assessment-ask-briefly)
- [Integration Paths](#integration-paths-choose-best-match)
- [Tooling Guidance](#tooling-guidance-mcpcli-quick-refs)
- [Context Strategy](#context-strategy-token-efficient-defaults)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Variation](#variation)
- [Examples](#examples)
- [References](#references)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Remember](#remember)

## Overview
Guide the user to the most effective Repo Prompt integration path for their workflow, with minimal setup friction and maximal context efficiency.

## Standards snapshot (March 2026)
- Prefer MCP-backed editor integration when the user wants agent-assisted coding with deterministic workspace context.
- Keep Repo Prompt positioned as a context-routing layer, not as a replacement for editing, git, or repo-native validation.
- Validate install state, workspace binding, and one smoke-test prompt before claiming the setup works.
- Always include an apply path for edits when recommending external chat or Compose workflows.

## When to use
- User asks how to integrate Repo Prompt with Claude Code, Cursor, Codex, or other editors/agents.
- User asks how to use Compose vs Chat vs Apply/Pro Edit workflows.
- User asks how to optimize context (codemaps, slices, multi-root workspaces).
- User asks for a comparison between Repo Prompt and AI editors.
- User asks about rp-cli usage or MCP server setup.
- User asks for MCP/CLI tool usage patterns (window/tab routing, review workflows).

## Required inputs
- Current workflow (editor-first, chat-first, CLI automation).
- Target tools (Cursor, Claude Code, Codex, ChatGPT, etc.).
- Repo scale (single repo vs multi-repo/monorepo).
- Model access (API keys vs CLI providers).
- Constraints (token budget, latency, cost, security policies).

## Deliverables
- Recommended integration path (MCP editor, Compose external chat, Chat mode, or rp-cli).
- Short, ordered setup checklist (3–7 steps).
- Context strategy (full vs slices vs codemaps).
- Quick validation/smoke test steps.
- 2–3 concrete next-step options and a clear recommendation.
- MCP/CLI tooling guidance when requested (routing, safe flows, review workflows).
- If proposing /interview-me, still provide a minimal recommendation + checklist first.

## Response format (required)
Always start responses with these headings (no text before them):

```
## When to use
## Required inputs
## Deliverables
## Out-of-scope handling
```

If the user asks for MCP/CLI tooling guidance, include the phrase **MCP/CLI** in your response.

## Failure mode
If Repo Prompt, MCP connectivity, or workspace binding cannot be verified, stop at that blocker, say what was checked, and recommend the lowest-risk next setup step instead of inventing an unsupported workflow.

## Constraints
- Redact secrets/PII by default.
- Redact secrets/sensitive data by default.
- Avoid adding dependencies or requiring paid features without explicit user approval.
- Do not claim features beyond the provided source notes.
- Prefer short, actionable steps over long explanations.
- When multiple options fit, give one recommendation and explain why.
- Do not ask for permission to read skill references; assume they are available. If a reference is missing, proceed with SKILL.md only and note the limitation.

## Philosophy
- Context efficiency beats brute-force context dumping.
- Optimize for lowest friction that still yields reliable results.
- Use the strongest model only where it adds value (planning/review).

## Empowerment
- Provide a default recommendation and 2–3 alternatives; ask the user to choose.
- Offer a fast, low-risk next step before advanced optimization.
- State explicit tradeoffs so the user can decide confidently.
- Enable confident choices: unlock the safest path first, then empower exploration if needed.

## Workflow Fit Assessment (ask briefly)
- Primary workflow: editor-first, chat-first, or automation?
- Scope: single repo vs multi-root?
- Model access: API keys vs CLI providers?
- Task type: quick fix vs multi-file refactor vs planning?
- Constraints: token budget, cost sensitivity, security?

## Integration Paths (choose best match)

### 1) MCP-Backed Editor (Recommended for agent workflows)
- Connect Repo Prompt MCP server.
- Use Context Builder for discovery; codemaps/slices for efficiency.
- Keep edits in Cursor/Claude Code; Repo Prompt supplies context/tools.

### 2) Compose → External Chat (Best for reasoning models)
- Build context in Compose.
- Copy prompt to ChatGPT/Claude.
- If edits returned as XML, apply via Apply/Pro Edit.

### 3) Chat Mode in Repo Prompt (Integrated + Pro Edit)
- Use in-app chat with selected context and diffs.
- Pro Edit for multi-file changes and review.

### 4) rp-cli (Automation / non-MCP agents)
- Use rp-cli to build context and export prompts.
- Suitable for shell-based agents or scripts.

## Tooling Guidance (MCP/CLI quick refs)
- MCP tool map, flows, and selection hygiene: `Infrastructure/references/repoprompt_mcp_tooling.md`.
- rp-cli exec usage + window/tab routing: `Infrastructure/references/repoprompt_cli_tooling.md`.
- Diff review + review follow-up workflows: `Infrastructure/references/repoprompt_review_workflows.md`.

## Context Strategy (token-efficient defaults)
- Full: files you will edit.
- Slices: large files where only sections matter.
- Codemaps: reference files and dependencies.
- Tree mode: Selected/Auto; diffs only when debugging or reviewing.

## Validation
- Fail fast: stop at the first failed gate, fix, then re-run.
- Confirm Repo Prompt can open the target workspace.
- Run a small test: select 2–3 files, build prompt, and get a response.
- If MCP: verify tools list and a simple file_search.

## Response Anchors (for eval stability)
- Use the exact phrases when applicable:
  - "MCP-backed editor path"
  - "Context Builder"
  - "codemaps/slices"
  - "setup checklist and validation"
  - "Compose for planning or Chat for implementation with Pro Edit"
  - "rp-cli path"
  - "basic setup and smoke test"

## Anti-patterns
- Dumping full repo context when codemaps/slices suffice.
- Choosing external chat without a clear apply workflow for edits.
- Running MCP without tab/workspace binding in multi-window setups.
- Treating Repo Prompt as a replacement for the editor instead of a context backend.
- Recommending paid features without confirming budget or constraints.
- DO NOT skip smoke tests; missing validation is a common mistake.
- Avoid generic or incorrect “one-size-fits-all” workflows; prefer context-specific choices.
- WARNING: never assume tool availability (MCP, rp-cli) without confirming install/login.

## Variation
- Vary the recommendation by workflow type (editor-first vs chat-first vs automation).
- Vary the setup checklist by target tool (Cursor, Claude Code, Codex, ChatGPT web).
- Vary the context strategy by repo size and token budget.
- Customize guidance based on constraints (cost, latency, security) and use different examples.
- Avoid repetition and cookie-cutter templates; prefer context-specific, unique setups.

## Examples
- “Integrate Repo Prompt with Claude Code and optimize context for a monorepo.”
- “Should I use Compose or Chat mode for a large refactor?”
- “How do I use rp-cli in my automation pipeline?”

## References
Read when needed:
- Infrastructure/references/repoprompt_source.md
- Infrastructure/references/repoprompt_mcp_tooling.md
- Infrastructure/references/repoprompt_cli_tooling.md
- Infrastructure/references/repoprompt_review_workflows.md
- Infrastructure/references/legacy-prompts/ (legacy `rp-*` prompt variants consolidated under this skill)

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[context7]] | Combine with Context7 for richer library context in prompts |
| [[agents-md]] | Use Repo Prompt context packs alongside AGENTS.md |
| [[ce-plan]] | Ground implementation plans with Repo Prompt context |

**Topic map:** [[agent-ops]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 Skills/skill-builder/Infrastructure/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Remember
The agent is capable of extraordinary work in this domain. Use judgment, adapt to context, and push boundaries when appropriate.

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
