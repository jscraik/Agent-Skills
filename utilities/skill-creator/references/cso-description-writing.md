# CSO: Description writing for reliable skill selection

This reference formalizes how to write **high-performing `description:` frontmatter** for skills in this repo.

## Why this matters (selection model constraint)

- **Only `name` and `description` are loaded for skill selection.**
- The SKILL.md body and `references/` content are loaded **only after** the skill is invoked.

So: **if the description doesn’t match the user’s request, the skill won’t load.**

## Required shape (WHAT + WHEN, without workflow)

In this repo, gold-gated skills are expected to encode:

- **WHAT** the skill does (action + deliverable/domain)
- **WHEN** to use it (trigger contexts: files, symptoms, keywords, situations)

This is enforced by `skill_gate.py` (see finding `FM_DESC_WHAT_WHEN`).

### Pattern A (recommended default)

> `"<what>. Use when <triggers>."`

Example:

```yaml
description: Create and validate Codex skills (SKILL.md + references + scripts). Use when creating or upgrading a skill, or when a skill fails validation gates.
```

### Pattern B (deliverable/domain-forward)

> `"<what> for <deliverable/domain>. Use when <files/symptoms/keywords>."`

Example:

```yaml
description: Draft a migration plan for schema or data changes. Use when the user mentions migrations, backfills, rollouts, or rollback/verification requirements.
```

## Trigger-only vs WHAT+WHEN (tradeoff, formalized)

### Trigger-only is tempting…

Example (trigger-only):

```yaml
description: Use when creating or editing skills.
```

This is tempting because it’s short, but it usually underperforms because:

- It is hard to distinguish from nearby “docs / templates / prompts” skills.
- It lacks the **WHAT** clause that anchors the skill’s intent.
- It is easier for the model to mis-select.

In practice, trigger-only descriptions are an **anti-pattern** for gold-gated skills here (and may fail `FM_DESC_WHAT_WHEN`).

### If you want trigger-heavy, keep WHAT ultra-short

Use a **single verb phrase** for WHAT, and push richness into WHEN keywords.

Example:

```yaml
description: Audit and upgrade skills. Use when skill selection is flaky, triggers are ambiguous, validation gates fail, or the skill needs progressive-disclosure refactors.
```

## Keyword coverage checklist (copy/paste)

When editing a description, explicitly cover the keywords the model is likely to match.

### Deliverables / artifacts (nouns)

- plan, report, spec, PRD, ADR, checklist, rubric, contract, evals, schema

### Filetypes / extensions

- SKILL.md, contract.yaml, evals.yaml
- .md, .yaml/.yml, .json, .toml
- language-specific extensions only if relevant (.ts, .py, .rs, etc.)

### Domains (nouns)

- auth, billing, CI, deployment, security, accessibility, performance, data, migrations

### Symptoms / failure modes

- flaky, inconsistent, hanging, drifting, ambiguous, brittle, failing gate, failing validation
- rationalizing, skipping steps, shortcutting

### Errors (only when the skill is tied to specific errors)

- include a few canonical error strings users paste verbatim (e.g. “Missing YAML frontmatter”, “description too long”)

### Synonyms (make matching robust)

- timeout / hang / freeze
- redact / sanitize
- validate / verify / gate

### Negative triggers (non-goals)

- translate poem, write fiction, generic “help me code”
- anything your skill should **not** be selected for

## Anti-workflow-in-description examples (GOOD / BAD)

The description is for **selection**, not procedure. Keep workflow details in SKILL.md body / references.

### BAD (workflowy: sequencing terms)

```yaml
description: Use when creating skills; first collect prompts, then write the skill, then run validators, then package it.
```

Why it’s bad:

- It contains multiple workflow terms (“first”, “then”, “then”).
- `skill_gate.py` may warn with `FM_DESC_WORKFLOWY`.
- Models can treat this as the *entire procedure* and skip the skill body.

### BAD (checklist leakage)

```yaml
description: Use when creating skills; follow the checklist and validation steps to finish.
```

### GOOD (outcome + triggers, no sequencing)

```yaml
description: Create and upgrade skills with required validation gates. Use when creating a new skill, revising triggers, adding eval cases, or fixing skill_gate/quick_validate failures.
```

### Mapping to `skill_gate.py` heuristics

- `FM_DESC_WHAT_WHEN`: description must include both **WHAT** and **WHEN**.
- `FM_DESC_WORKFLOWY`: avoid multiple workflow terms in description (keep procedures in the body).

## Mini rubric (quick self-check)

- Single-line YAML scalar (no newlines).
- **Third person** (never “I” / “you”).
- 120–250 characters is a good target (shorter can be ambiguous; longer risks limits).
- No angle brackets (`<` or `>`).
- Avoid workflow terms (“step”, “first”, “then”, “next”, “finally”, “checklist”).

