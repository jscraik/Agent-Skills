---
name: agents-md
description: "Refactor or create AGENTS.md using progressive disclosure: keep root guidance minimal, split detailed instructions into linked docs, and flag contradictions or redundancy. Use this skill when the user asks to create, update, or refactor AGENTS.md."
---

# Agents Md

Create and maintain concise, high-signal AGENTS guidance with progressive disclosure.

## When to use
- Use this skill when the user asks to create or update `AGENTS.md`.
- Use this skill when AGENTS docs are too large, duplicated, or contradictory.
- Use this skill when instruction routing needs to be split into linked files.

## Inputs
- Target repository root path.
- Existing `AGENTS.md` and related instruction docs.
- Verified commands/paths from repository sources.
- Preferred instruction tree (`instructions/agents` or `docs/agents`) based on repo convention.

## Outputs
- Updated minimal root `AGENTS.md`.
- Linked category docs for deeper instructions.
- Contradiction list and deletion candidates.
- Evidence-backed command map and validation notes.

## Philosophy
- Prefer concise, verifiable guidance over comprehensive prose.
- Keep root AGENTS as an operator map, with depth in linked docs.
- Optimize for reader success in under two minutes.
- Why keep this instruction in root instead of a linked doc?
- What evidence confirms this command/path is real?
- Which tradeoff is best here: brevity or explicitness?

## Constraints
- Redact secrets, tokens, credentials, and PII by default.
- Do not invent commands, scripts, or paths.
- Keep ASCII by default unless repository conventions require otherwise.
- Avoid adding dependencies, legacy shims, or compatibility layers unless explicitly requested.

## Procedure
1. Discover repo facts and instruction hierarchy.
2. Detect command/style conventions from actual repo evidence.
3. Identify contradictions and duplicate guidance.
4. Write minimal root AGENTS and link deeper docs.
5. Add table of contents for generated docs.
6. Validate links, commands, and instruction consistency.

## Validation
- Confirm commands exist in repo scripts/docs.
- Confirm file paths exist and links resolve.
- Confirm no contradictory instructions remain unresolved.
- Fail fast: stop at first critical contradiction and request decision.

## Anti-patterns
- Do not dump full policy documents into root AGENTS.
- Never duplicate the same instruction across many files without need.
- Do not keep vague guidance that cannot be executed.
- Avoid repetitive, generic, cookie-cutter templates that ignore repo context.
- Warn on conflicting package manager instructions and unresolved hierarchy conflicts.

## Variation
- Adapt structure for small repos versus multi-package monorepos.
- Use different category splits based on repo domains (frontend, backend, ops, docs).
- Customize guidance depth to team maturity and operational risk.

## Mandatory workflow snippet
1. Explore project first, then invoke skill.
2. IMPORTANT: Prefer retrieval-led reasoning over pre-training-led reasoning for any React, Tauri, Apps-SDK-ui, Tailwind, Vite, Storybook + Chat Widget tasks.
3. Add a Table of Contents for docs.

## Examples
- Refactor an overloaded AGENTS file into root plus `instructions/agents/*` docs.
- Merge AGENTS/CLAUDE/GEMINI shared rules to canonical AGENTS links.
- Audit contradictions and return an explicit conflict-decision list.

## Resource map
- References: `references/contract.yaml`, `references/evals.yaml`, `references/folded-legacy-modes-core60.md`, `references/task-profile.json`

<!-- decision-feedback-protocol:v2 -->
## Decision Quality Feedback
- If post-run feedback capture is enabled, emit non-blocking `post_run_feedback` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist with `python3 utilities/skill-builder/scripts/record_skill_feedback.py`.
<!-- /decision-feedback-protocol -->

## Quality Uplift
- Philosophy and approach: apply a clear framework, explain why, consider tradeoff decisions, and use a practical mental model for execution.
- Guiding question: Why is this the right context-specific path?
- Guiding question: What tradeoff is being made and how is risk reduced?
- Guiding question: How do we verify behavior end-to-end before completion?
- Anti-pattern warning: avoid generic or repetitive output; DO NOT hide failures; NEVER skip validation; avoid common pitfall and mistake patterns.
- Anti-pattern warning: treat incorrect or wrong assumptions as blockers, and call out anti-pattern risks explicitly.
- Variation: vary recommendations by context-specific constraints; adapt, customize, and use different approaches when constraints differ.
- Variation: prefer diverse, unique alternatives and avoid repetition or cookie-cutter template convergence.
- Empowerment: enable users to explore options confidently, be capable and creative, unlock safe choices, and empower execution.
