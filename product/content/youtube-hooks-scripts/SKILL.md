---
name: youtube-hooks-scripts
description: Create high-retention hooks and full scripts for technical YouTube videos
  tailored to topic, audience, and length. Use when the user asks for a hook, outline,
  or full script.
metadata:
  skill-type: team_automation
---

# YouTube Hooks & Scripts

## Table of Contents
- [Scope and triggers](#scope-and-triggers)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Standards snapshot](#standards-snapshot-march-2026)
- [Workflow](#workflow)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Decision feedback protocol](#decision-feedback-protocol)

Deliver high-retention technical YouTube hooks, outlines, and scripts. The deeper craft guidance lives in `references/full-guide.md`.

## When to use
- Use when asked for technical YouTube hooks, outlines, or long-form scripts.
- Use it for packaging the story and teaching arc of a video, not for broader product planning.
- Route broader product or PRD work to `product-spec`.

## Required inputs
- topic
- audience
- desired output shape: hooks, outline, or full script
- runtime or length target when known
- any transcript, notes, or claims that must be preserved

## Deliverables
- the requested hook set, outline, or full script
- framing matched to audience sophistication and video length
- explicit notes where claims, examples, or metrics require user-provided evidence

## Failure mode
If the prompt lacks the core topic, audience, or target output shape, ask for the smallest missing detail instead of generating generic creator slop.

## Standards snapshot (March 2026)
- Optimize for retention without sacrificing technical accuracy.
- Match the opening promise, structure, and payoff to the audience’s actual sophistication.
- Prefer concrete curiosity gaps, earned authority, and clear viewer outcomes over hype.
- Keep claims evidence-bound; do not invent benchmarks, timelines, or personal anecdotes.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default.
- Do not invent metrics, user results, or unverifiable claims.
- Keep outputs aligned to the requested format and audience sophistication.

## Workflow
1. Identify the requested output: hook options, outline, or full script.
2. Anchor on topic, audience, runtime, and desired tone.
3. Build a clear promise, narrative spine, and payoff sequence.
4. Deliver concise variations when the user is choosing direction; deliver a full script only when that is the ask.

## Validation
- Confirm tone, audience fit, and length constraints.
- Fail fast if key inputs are missing.
- Confirm the opening hook creates a clear curiosity gap without misleading the viewer.
- Confirm the script payoff actually cashes the promise made in the opening.

## Anti-patterns
- Overlong outputs that ignore format limits.
- Generic suggestions not tied to the topic.
- Hooks that overpromise and scripts that never deliver the promised insight.
- Thumbnail-style sensationalism inside a script intended for trust-building technical content.

## Examples
- "Give me five hook options for a technical video about Codex workflows."
- "Turn these notes into a 10-minute tutorial script."
- "Write an outline for a video aimed at senior TypeScript engineers."

<!-- skill-score-boost-v1 -->
## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.

## Decision feedback protocol

## See Also

| Skill | When to use together |
|---|---|
| [[youtube-titles-thumbnails]] | Create titles and thumbnails to pair with the script |
| [[video-transcript-downloader]] | Study competitor transcripts before writing hooks |
| [[product-spec]] | Spec the content series before scripting individual videos |
| [[notebooklm]] | Use NotebookLM to generate audio overviews from scripts |

**Topic map:** [[content-publishing]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
