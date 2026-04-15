# Skill Creator Foundations

## Table of Contents

- [Why Skills Exist](#why-skills-exist)
- [Core Principles](#core-principles)
- [Skill Anatomy](#skill-anatomy)
- [Progressive Disclosure Model](#progressive-disclosure-model)
- [Reference Design Patterns](#reference-design-patterns)

## Why Skills Exist

Skills are modular, self-contained folders that give Codex reliable domain behavior through reusable instructions and resources.

High-value capabilities a skill can provide:

1. Specialized workflows for recurring task classes.
2. Tool integration guidance for specific APIs, file formats, and operational constraints.
3. Domain context that is not obvious from generic model knowledge.
4. Bundled reusable artifacts in scripts, references, and assets.

## Core Principles

### Keep context economical

Treat context as a limited shared resource. Put only essential routing and execution guidance in `SKILL.md`, then move depth to `Infrastructure/references/`.

### Match instruction strictness to task fragility

- High freedom: use for judgment-heavy domains with many valid paths.
- Medium freedom: use when patterns exist but configuration varies.
- Low freedom: use for fragile workflows requiring deterministic sequencing.

### Preserve validation integrity

When forward-testing, evaluate real task behavior rather than whether another agent can infer hidden intended answers.

## Skill Anatomy

A skill package should be organized like this:

```text
skill-name/
├── SKILL.md
├── agents/
│   └── openai.yaml
├── Infrastructure/references/
├── Infrastructure/scripts/
└── assets/
```

Notes:

- `SKILL.md` is required and should stay concise.
- `agents/openai.yaml` is recommended for UI metadata.
- Add `Infrastructure/scripts/`, `Infrastructure/references/`, and `assets/` only when they materially improve repeatability.

## Progressive Disclosure Model

Use a three-layer context model:

1. Frontmatter metadata (`name`, `description`) for routing.
2. `SKILL.md` for workflow summary and navigation.
3. `Infrastructure/references/` and scripts for deep detail and deterministic execution.

Rule of thumb:

- Keep SKILL-level instructions short and direct.
- Move examples, edge-case guides, and domain depth to reference docs.
- Keep references discoverable from `SKILL.md` with explicit links and usage conditions.

## Reference Design Patterns

Use these patterns when organizing detailed guidance:

1. High-level guide plus topic-specific references.
2. Domain partitioning where each domain gets its own reference file.
3. Conditional detail where advanced topics are linked from baseline flow.

Reference hygiene rules:

- Keep references one hop from `SKILL.md`.
- Avoid duplicating the same instruction across multiple files.
- Add a table of contents for docs so scope is visible at a glance.
