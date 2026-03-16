---
name: remotion
description: Best-practice guidance for Remotion (React video). Use when building or reviewing Remotion compositions, timing, assets, audio, captions, or rendering.
---

# Remotion Best Practices

Use the Remotion ruleset as a focused advisor for composition design, timing, assets, captions, and render reliability.

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Workflow](#workflow)
- [Validation](#validation)
- [References](#references)

## Standards snapshot
- Keep guidance rule-backed and topic-specific rather than generic React advice.
- Favor deterministic timing, asset loading, and caption workflows over visual guesswork.
- Prefer Remotion-native primitives and official utilities before custom abstractions.
- Treat render reliability and decode support as first-class constraints, not cleanup work.

## When to use
- You are building or reviewing a Remotion composition.
- You need help with timing, sequencing, transitions, assets, captions, audio, or render setup.
- You want the fastest route to the right topic-specific rule file instead of broad video guidance.

## Required inputs
- The question, code path, or failing behavior.
- Optional topic focus:
  - compositions;
  - timing;
  - assets;
  - audio;
  - captions;
  - transitions;
  - rendering;
  - Mediabunny utilities.
- Any constraints such as target render environment, deadline, or performance limits.

## Deliverables
- A concise answer grounded in the most relevant rule file or files.
- Implementation guidance or review findings scoped to the user’s issue.
- Specific validation steps for the affected composition or media workflow.

## Philosophy
- Use the smallest rule set that fully explains the issue.
- Prioritize render reliability and timing correctness over stylistic novelty.
- Keep advice tied to real Remotion capabilities rather than generic React patterns.

## Failure mode
- If the request is about general frontend video UI rather than Remotion itself, route to a broader frontend skill.
- If the task is about shipping a full app rather than Remotion implementation details, use a build-focused skill instead.
- If the user wants speculative advice without project context, keep recommendations bounded and note assumptions.

## Constraints
- Redact secrets, private asset URLs, and internal file paths by default when summarizing media workflows.
- Keep recommendations scoped to Remotion and closely related utilities.
- Do not recommend speculative dependency churn when an existing Remotion-native path already fits.

## Workflow
1. Identify the dominant topic.
2. Open the matching rule file in `rules/` first.
3. Add neighboring rules only if the issue crosses boundaries:
   - timing plus transitions;
   - captions plus fonts;
   - assets plus can-decode checks.
4. Answer from the smallest relevant rule set.
5. End with the concrete validation commands or checks the user should run next.

## Anti-patterns
- Dumping the full ruleset when only one or two rule files matter.
- Giving animation advice without checking timing, duration, and asset constraints.
- Treating decode support or caption sync as optional cleanup.

## Validation
- Fail fast: stop at the first broken media assumption and validate that before broadening the recommendation.
- Verify the advice maps to a real Remotion capability or utility already covered by the ruleset.
- Prefer composition-level verification over broad app-level claims.
- When render issues are involved, include the exact preflight check:
  - asset existence;
  - decode support;
  - duration and timing assumptions;
  - caption synchronization.

## Examples
- "Which Remotion rule files should I use to fix choppy transitions and timing drift?"
- "Review this composition for caption sync and asset loading risks."
- "What is the safest way to measure dynamic text before rendering this scene?"

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Task profile: `references/task-profile.json`
- Rules directory: `rules/`
- Asset preview: `assets/remotion.png`

## See Also

| Skill | When to use together |
|---|---|
| [[sora]] | Compare Remotion (code-driven) with Sora (AI-driven) video |
| [[stitch-remotion]] | Generate Remotion compositions from Stitch screen assets |
| [[imagegen]] | Generate still images to use as Remotion assets |
| [[slides]] | Convert slide decks into Remotion video compositions |
| [[video-transcript-downloader]] | Download reference transcripts before scripting Remotion narration |

**Topic map:** [[frontend-ui]]

<!-- decision-feedback-protocol:v2 -->
**Decision feedback protocol (required):**
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture: `decision` (`accepted|partial|rejected|deferred`), `outcome` (`good|neutral|bad|unknown`), and `confidence` (`high|medium|low`).
- Persist with: `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
- The recorder tags `subject` (for example `ui`, `code_review`, `backend`, `security`) for cross-domain quality analytics.
<!-- /decision-feedback-protocol -->
