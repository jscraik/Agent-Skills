# Description optimization

## Table of Contents
- [When to use this reference](#when-to-use-this-reference)
- [Core idea](#core-idea)
- [Build a realistic trigger eval set](#build-a-realistic-trigger-eval-set)
- [Use near-miss negatives](#use-near-miss-negatives)
- [What good trigger queries look like](#what-good-trigger-queries-look-like)
- [How to interpret trigger misses](#how-to-interpret-trigger-misses)
- [Round requirement](#round-requirement)
- [Improvement heuristics during optimization](#improvement-heuristics-during-optimization)
- [Blind comparison for subjective improvements](#blind-comparison-for-subjective-improvements)

## When to use this reference

Use this when:
- the skill triggers inconsistently;
- the `description` feels too vague or too broad;
- you are choosing between multiple trigger phrasings;
- the skill passes content evals but still routes poorly in realistic prompts.

## Core idea

The `description` is routing logic, not marketing copy.

Optimize it with realistic trigger evals:
- enough **should-trigger** prompts to cover the intended surface area;
- enough **should-not-trigger** prompts to catch near-misses;
- phrasing that looks like something a real user would actually type.

Do not rely on toy prompts. “Read this PDF” or “format this data” is usually too thin to reveal whether the routing boundary is correct.

## Build a realistic trigger eval set

Default target:
- **8–10 should-trigger queries**
- **8–10 should-not-trigger queries**

Each query should feel concrete:
- include filenames, paths, tools, URLs, teams, or domain details when appropriate;
- mix formal and casual phrasing;
- vary length;
- include a few messy prompts with abbreviations, typos, or partial context.

Coverage goals for should-trigger queries:
1. direct asks that clearly match the skill;
2. indirect asks where the user never names the skill but obviously needs it;
3. uncommon but valid edge cases;
4. prompts where a nearby competing skill exists, but this skill should win.

Coverage goals for should-not-trigger queries:
1. adjacent tasks that share vocabulary but need a different skill;
2. prompts that mention the same file types but require a different outcome;
3. ambiguous phrasing where a naive keyword match would over-trigger;
4. simple one-step tasks that the base model can handle without consulting the skill.

## Use near-miss negatives

The most valuable negative tests are **near-misses**, not obviously irrelevant prompts.

Weak negative:
- “Write a fibonacci function” for a document-processing skill

Strong negative:
- a prompt that mentions PDFs, extraction, or formatting, but is actually asking for legal review, OCR troubleshooting, or UI work outside the skill boundary

If the negative set is too easy, the skill will look more precise than it actually is.

## What good trigger queries look like

Good queries usually include:
- the user’s actual goal;
- enough context to make routing non-trivial;
- some messiness from real life;
- a reason the skill would materially help.

Examples of realistic patterns:
- “my PM dropped a CSV in `/tmp/customer-export.csv` and wants the duplicates removed plus a JSON summary grouped by region”
- “I’ve got a half-finished AGENTS file and need it split into linked docs without losing repo-specific rules”
- “can you turn this repeated triage workflow into a reusable skill and make sure it does not trigger for ordinary bugfix work”

## How to interpret trigger misses

A trigger miss does not always mean the description is wrong.

Check whether the query was:
- too simple to justify loading a skill;
- too underspecified to disambiguate from competing skills;
- outside the intended artifact/output contract;
- missing the operational detail that would make the skill clearly valuable.

Likewise, an over-trigger does not always mean the keywords are wrong. Sometimes the skill boundary is underspecified because the description does not say what **not** to use it for.

## Round requirement

In non-trivial builder rounds, route and description assessment is mandatory.

- Record that assessment even when you do not change wording.
- If evidence shows ambiguity, weak triggering, or misleading boundaries, edits are mandatory before marking the round ready.
- If no edits are needed, state why in the round evidence so downstream handoff is auditable.

## Improvement heuristics during optimization

When improving a skill after evals or human feedback:

1. **Generalize from feedback rather than overfitting**
   - Fix the underlying pattern, not just the one prompt that failed.

2. **Keep the prompt lean**
   - Remove instructions that are not pulling their weight.
   - If transcripts show repeated unproductive work, simplify the guidance.

3. **Explain the why**
   - Prefer reasoning and tradeoffs over rigid all-caps rules when possible.
   - Models usually respond better to justified constraints than unexplained commands.

4. **Promote repeated helper logic into `scripts/`**
   - If multiple eval runs independently recreate the same helper script, parser, converter, or formatter, bundle it once and tell the skill to reuse it.

5. **Review transcripts, not just final outputs**
   - Final artifacts can look fine while the workflow is wasteful, fragile, or dependent on lucky exploration.

## Blind comparison for subjective improvements

When the main question is “is the new version actually better?”, run a blind comparison when practical.

Pattern:
1. generate outputs from baseline and candidate variants;
2. present the outputs without revealing which variant produced which result;
3. collect the judgment first;
4. only then reveal the winner and inspect why it won.

Use this for:
- writing quality;
- UX/design guidance;
- style-sensitive docs work;
- any skill where pass/fail assertions alone miss the real quality bar.

Do not use blind comparison as a substitute for hard validation. Keep validators and safety gates in place, then use blind review to resolve subjective tie-breaks.
