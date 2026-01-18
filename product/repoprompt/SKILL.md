---
name: repoprompt
description: "Plan and guide Repo Prompt integration and usage in AI coding workflows. Use when integrating Repo Prompt with editors/agents."
---

# Repo Prompt Integration

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md

## Overview
Guide the user to the most effective Repo Prompt integration path for their workflow, with minimal setup friction and maximal context efficiency.

## When to Use
- User asks how to integrate Repo Prompt with Claude Code, Cursor, Codex, or other editors/agents.
- User asks how to use Compose vs Chat vs Apply/Pro Edit workflows.
- User asks how to optimize context (codemaps, slices, multi-root workspaces).
- User asks for a comparison between Repo Prompt and AI editors.
- User asks about rp-cli usage or MCP server setup.

## Inputs
- Current workflow (editor-first, chat-first, CLI automation).
- Target tools (Cursor, Claude Code, Codex, ChatGPT, etc.).
- Repo scale (single repo vs multi-repo/monorepo).
- Model access (API keys vs CLI providers).
- Constraints (token budget, latency, cost, security policies).

## Outputs
- Recommended integration path (MCP editor, Compose external chat, Chat mode, or rp-cli).
- Short, ordered setup checklist (3–7 steps).
- Context strategy (full vs slices vs codemaps).
- Quick validation/smoke test steps.
- 2–3 concrete next-step options and a clear recommendation.
- If proposing /interview-me, still provide a minimal recommendation + checklist first.

## Constraints
- Redact secrets/PII by default.
- Redact secrets/sensitive data by default.
- Avoid adding dependencies or requiring paid features without explicit user approval.
- Do not claim features beyond the provided source notes.
- Prefer short, actionable steps over long explanations.
- When multiple options fit, give one recommendation and explain why.

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
- references/repoprompt_source.md

## When to use
- Use this skill when the task matches its description and triggers.
- If the request is outside scope, route to the referenced skill.
## Procedure
1) Clarify scope and inputs.
2) Execute the core workflow.
3) Summarize outputs and next steps.

## Antipatterns
- Do not add features outside the agreed scope.
