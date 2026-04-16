# OpenAI-Inspired Documentation Writing Principles

Use this reference as the writing-quality source of truth for docs-expert.

Source inspiration: [What makes documentation good](https://developers.openai.com/cookbook/articles/what_makes_documentation_good/)

## Table of Contents
- [Purpose](#purpose)
- [1) Make docs easy to skim](#1-make-docs-easy-to-skim)
- [2) Write well](#2-write-well)
- [3) Be broadly helpful](#3-be-broadly-helpful)
- [4) Break rules when context requires it](#4-break-rules-when-context-requires-it)
- [Quick self-review rubric](#quick-self-review-rubric)

## Purpose

Documentation succeeds when it puts useful information into a reader's head quickly and reliably.

This guide prioritizes reader comprehension over author preference.

## 1) Make docs easy to skim

- Split content into clear sections with explicit titles.
- Prefer informative sentence-like headings over abstract labels.
  - Better: "Streaming reduced time to first token by 50%"
  - Worse: "Results"
- Include a table of contents for long or sectioned docs.
- Keep paragraphs short.
- Start sections and paragraphs with standalone topic sentences.
- Put topic words early in topic sentences.
  - Better: "Vector databases speed up embeddings search."
  - Worse: "Embeddings search can be sped up by vector databases."
- Put takeaways before step-by-step procedures.
- Use bullets and tables where they reduce scan effort.
- Bold high-value text intentionally; do not overuse bolding.

## 2) Write well

- Keep sentences simple.
- Split long sentences into shorter ones.
- Remove filler words and unnecessary adverbs.
- Prefer imperative voice when giving instructions.
- Prefer unambiguous phrasing over clever phrasing.
- Minimize left-branching sentence structures when a right-branching rewrite is clearer.
- Avoid demonstrative pronouns across sentences when they reduce clarity.
  - Instead of "this/that", repeat the explicit noun when needed.
- Be consistent:
  - heading style,
  - punctuation style,
  - terminology and casing,
  - naming patterns.
- Avoid telling readers what they think or feel.
  - Avoid: "You probably want..."
  - Prefer: "To do X, run..."

## 3) Be broadly helpful

- Write for mixed audiences, including non-native English readers.
- Avoid abbreviations unless expanded on first use.
  - Example: write "retrieval-augmented generation (RAG)" once, then use RAG.
- Proactively include solutions for common failure points.
  - environment variables,
  - path issues,
  - permissions,
  - dependency setup.
- Prefer specific, accurate terminology over insider jargon.
- Keep examples general, exportable, and self-contained.
- Prioritize high-value/common tasks before rare edge cases.
- Never teach bad habits.
  - Example: never hardcode API keys in examples.
- When useful, open with a broad frame before a narrow implementation detail.

## 4) Break rules when context requires it

These principles are defaults, not rigid law.

Break a rule when repository constraints, user needs, or safety requirements justify it.

When breaking a rule:
- state the reason,
- explain the tradeoff,
- record the decision in the deliverable.

## Quick self-review rubric

- Is the doc skimmable from headings and topic sentences alone?
- Can a reader find the main takeaway in under 30 seconds?
- Are examples runnable, self-contained, and safe?
- Is wording concrete, unambiguous, and consistent?
- Does the doc help both experienced and newer readers?
- If a rule was broken, is the reason documented?
