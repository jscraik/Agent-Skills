---
name: every-style-editor
description: Edit prose to conform to Every's editorial house style, including grammar, punctuation, mechanics, and naming conventions. Use when the user wants articles, newsletters, social copy, or other branded editorial writing polished, not repo docs QA.
metadata:
  skill-type: code_quality_review
---

# Every Style Editor

## Table of Contents
- [Standards snapshot](#standards-snapshot)
- [When to use](#when-to-use)
- [When not to use](#when-not-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Output contract](#output-contract)
- [Workflow](#workflow)
- [Validation](#validation)
- [Constraints](#constraints)
- [Anti-patterns](#anti-patterns)
- [Examples](#examples)
- [References](#references)
- [Gotchas](#gotchas)

## Standards snapshot
- Use this skill for Every-specific editorial review, not generic repo docs QA.
- Preserve the author's meaning and voice while tightening copy to Every's house style.
- Quote exact problem text when giving feedback so edits are actionable.
- Route rule-heavy edge cases to the preserved style guide instead of guessing from memory.
- Keep the full upstream style guide intact in references instead of collapsing it into vague writing advice.

## When to use
- The user wants line editing or proofreading against Every's style guide.
- The content is an article, newsletter, social post, memo, or other prose intended to match Every's editorial conventions.
- The user wants grammar, punctuation, mechanics, capitalization, number style, link style, or tone issues flagged with concrete fixes.
- A human editor needs a clean, structured review before publication or internal review.

## When not to use
- The main task is repository docs QA or README rewriting; use `docs-expert`.
- The task is ideation, headline generation, or content strategy rather than line editing.
- The copy does not need Every's brand/style conventions and only needs a generic rewrite.
- The request is primarily about code, product design, or implementation rather than prose editing.

## Required inputs
- The text to review or rewrite.
- Optional content context:
  - document type
  - audience
  - target channel such as article, newsletter, or social
  - whether the user wants a review report, inline rewrite, or both
- Any explicit constraints such as word count, preserved phrasing, or sections not to touch.

## Deliverables
- A concise editorial assessment.
- Exact line edits or issue-by-issue corrections.
- Specific Every style-guide references for non-obvious changes.
- Recurring pattern notes when the same issue appears multiple times.
- Optional rewritten copy when the user wants a clean pass instead of a review memo.

## Failure mode
- If the user does not provide text, stop and ask for the copy to review.
- If the requested style authority is not Every's style guide, stop and say this skill is the wrong editorial standard.
- If the user wants generic docs QA or brand-agnostic cleanup, route to the narrower appropriate skill instead of forcing Every style rules onto unrelated text.

## Output contract
Use this shape when the user asks for structured output:

```json
{
  "schema_version": 1,
  "document_type": "string|null",
  "overall_assessment": "string",
  "issues": [
    {
      "location": "string",
      "issue_type": "grammar|punctuation|mechanics|style-guide|clarity",
      "original": "string",
      "correction": "string",
      "rule_reference": "string",
      "explanation": "string"
    }
  ],
  "recurring_issues": ["string"],
  "final_recommendations": ["string"]
}
```

Contract rules:
- Always include `schema_version`.
- Quote exact source text for corrections when possible.
- Use `document_type: null` only when the format cannot be inferred safely.

## Workflow
1. Read the full piece once for context:
   - document type
   - audience
   - tone
   - purpose
2. Decide the review mode:
   - review memo only
   - inline rewrite
   - review plus clean rewrite
3. Review the text line by line for:
   - grammar and sentence structure
   - punctuation and mechanics
   - capitalization and headline casing
   - Every-specific usage rules
   - clarity, specificity, and unnecessary filler
4. Open `references/EVERY_WRITE_STYLE.md` whenever a rule depends on Every's specific house style, especially for numbers, punctuation, capitalization, links, titles, pronouns, and usage conventions.
5. Group repeated issues into pattern notes so the user can improve the draft systematically, not just patch isolated sentences.
6. Present exact corrections with rule references, then provide the cleanest next step:
   - accept the edits
   - request a clean rewrite
   - review only selected sections again

## Validation
- Verify every correction points to real source text.
- Verify style-guide claims are backed by the preserved Every guide rather than generic writing intuition.
- Verify the author's meaning is preserved even when the sentence is tightened.
- Verify the output distinguishes single-instance fixes from recurring issues.

## Constraints
- Do not silently rewrite the author's argument or point of view.
- Do not claim Every style requires something unless the rule is actually supported by the preserved guide.
- Do not turn this into generic brand strategy or repository docs auditing.
- Redact sensitive, private, or unpublished information only when necessary for safety; otherwise preserve editorial context.

## Anti-patterns
- Giving vague advice like "tighten this up" without concrete edits.
- Applying generic copywriting taste as if it were Every house style.
- Overwriting the author's voice instead of editing for clarity and compliance.
- Summarizing the style guide so aggressively that important edge-case rules disappear.

## Examples
- "Edit this essay against Every's style guide and flag the exact lines that break house style."
- "Proofread this newsletter draft for punctuation, capitalization, and Every-specific usage."
- "Give me a review memo for this article, then produce a clean rewrite that follows Every style."
- "Check this social copy for Every voice and mechanics, but preserve the original intent."

## References
- `references/EVERY_WRITE_STYLE.md`
- `references/contract.yaml`
- `references/evals.yaml`

## Gotchas
- Symptom: Feedback sounds like generic writing advice instead of Every editorial review.
  Cause: The review skipped the Every-specific rule reference.
  Do instead: Check the preserved style guide for rule-backed corrections.
  Check: Non-obvious edits cite a concrete Every rule.
- Symptom: The author's voice disappears in the rewrite.
  Cause: The edit optimized for polish instead of preserving intent.
  Do instead: Keep the original meaning and cadence where possible while fixing compliance issues.
  Check: The revised copy still sounds like the same piece, just cleaner.

## See Also

| Skill | When to use together |
|---|---|
| [[docs-expert]] | Improve repository documentation instead of brand-editorial prose |
| [[changelog]] | Edit engineering summaries for a clearer external or community audience |
| [[youtube-hooks-scripts]] | Shape the longer-form video script before applying Every-style edits |
| [[youtube-titles-thumbnails]] | Tighten packaging copy once the tone and messaging are set |

**Topic map:** [[content-publishing]]
