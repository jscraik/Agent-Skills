# WARP.md

This file provides guidance to Warp (warp.dev) when working with code in this repository.

## Project Overview

Claudeception is an **OpenAI Codex agent skill** for continuous learning—it enables Codex to autonomously extract and preserve learned knowledge into reusable skills.

It is not an application codebase; it is a skill definition plus documentation and examples.

## Key Files

- `SKILL.md` — The main skill definition (YAML front matter + instructions). This is what Codex loads.
- `assets/skill-template.md` — Template for creating new skills
- `examples/` — Sample extracted skills demonstrating proper format

## Skill File Format

Skills use YAML front matter followed by optional Markdown instructions:

```yaml
---
name: kebab-case-name
# Required in Codex: single-line, <= 500 characters.
description: Fix XYZ when you see ABC. Use when: ...
metadata:
  author: Codex
  version: "1.0.0"
  date: "2026-01-19"
---
```

The `description` field is critical—it determines when Codex will surface the skill via implicit invocation.

## Installation Paths

- **User-level**: `~/.codex/skills/<skill-name>/`
- **Repo-level**: `.codex/skills/<skill-name>/` (checked into a repository)

## Quality Criteria for Skills

When modifying or creating skills, ensure:

- **Reusable**: Helps with future tasks, not just one instance
- **Non-trivial**: Requires discovery, not just documentation lookup
- **Specific**: Clear trigger conditions (exact error messages, symptoms)
- **Verified**: Solution has actually been tested and works

## Research Foundation

The approach is based on academic work on skill libraries (Voyager, CASCADE, SEAgent, Reflexion). See `references/research-references.md` for details.
