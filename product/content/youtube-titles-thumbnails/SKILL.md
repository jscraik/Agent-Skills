---
name: youtube-titles-thumbnails
description: Generate SEO/CTR-oriented YouTube title options and thumbnail copy variants with rationale. Use when the user wants video packaging ideas, not a full script or production plan.
metadata:
  skill-type: team_automation

---

# YouTube Titles & Thumbnails

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

Deliver strong YouTube title and thumbnail-copy options with clear positioning tradeoffs. The deeper craft guidance lives in `references/full-guide.md`.

## When to use
- Use when asked for high-performing YouTube titles, packaging angles, or thumbnail text.
- Use it when the user wants differentiated options they can test, not a full script.
- Route broader product or PRD work to `product-spec`.

## Required inputs
- topic
- audience
- any transcript, notes, or positioning constraints
- whether thumbnail text is also needed

## Deliverables
- multiple title options with meaningful variation
- paired thumbnail text ideas when requested
- concise rationale explaining angle, audience fit, and risk of overclaim

## Failure mode
If the topic or audience is too vague to create differentiated packaging, ask for the smallest missing detail rather than generating interchangeable options.

## Standards snapshot (March 2026)
- Optimize for click-through without damaging trust or misrepresenting the content.
- Generate meaningfully different packaging angles rather than shallow word swaps.
- Keep technical specificity when it improves audience targeting.
- Avoid invented metrics, fake controversy, and generic growth-hack language.

## Constraints
- Redact secrets, tokens, credentials, and sensitive data by default.
- Do not invent metrics, outcomes, or controversy hooks the content cannot support.
- Keep options concise enough to be usable as real packaging candidates.

## Workflow
1. Identify the audience, promise, and core novelty of the video.
2. Generate multiple packaging angles such as speed, surprise, transformation, or hard-earned lesson.
3. Pair each title with thumbnail text only when that improves the package.
4. Call out which options are safest, boldest, and most technically targeted.

## Validation
- Confirm tone, audience fit, and length constraints.
- Fail fast if key inputs are missing.
- Confirm each option is distinct enough to test.
- Confirm the packaging does not promise something the video cannot substantiate.

## Anti-patterns
- Overlong outputs that ignore format limits.
- Generic suggestions not tied to the topic.
- Producing a dozen near-duplicate titles with no real angle change.
- Packaging that reads like bait instead of a credible technical promise.

## Examples
- "Give me 10 title options for this developer tooling video."
- "Pair thumbnail text with three strong title angles."
- "Create safer and bolder packaging options for this technical tutorial."

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
| [[youtube-hooks-scripts]] | Pair with a hook and script for complete video packaging |
| [[video-transcript-downloader]] | Research competitor videos before writing titles |
| [[imagegen]] | Generate thumbnail concept images |
| [[visual-explainer]] | Present A/B thumbnail options in a visual comparison page |

**Topic map:** [[content-publishing]]

<!-- decision-feedback-protocol:v3 -->
**Decision feedback protocol (always run):**
After delivering results, ask the user directly:
> "Quick feedback — decision: accepted/partial/rejected/deferred? outcome: good/neutral/bad? confidence: high/medium/low?"
Then record it immediately:
`python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <decision> --outcome <outcome> --confidence <confidence> --notes "<optional notes>"`
Do not skip this step. Record even if the outcome is good.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
