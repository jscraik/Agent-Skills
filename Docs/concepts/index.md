# Concepts

Concept docs explain how the system works and why it is shaped this way.

Write concepts for readers who can run commands, but need help understanding the “why” and the tradeoffs.

When you describe a workflow, link to the exact script or folder and show a small example.

## What is a Skill?

A **skill** is a reusable prompt template that guides AI agent behavior. Each skill lives in a folder with a `SKILL.md` file containing:

```yaml
---
name: skill-name
description: What this skill does
triggers:
  - “when to use”
---

# Skill content in Markdown
```

**Skill folder structure:**
```
<category>/<skill-name>/
├── SKILL.md           # Required: skill definition
├── Infrastructure/references/        # Optional: supporting docs
├── Infrastructure/scripts/           # Optional: helper scripts
└── Infrastructure/templates/         # Optional: file templates
```

## Why Symlinks?

The `/.agents/skills/` directory contains symlinks to all skills. This design:

1. **Avoids duplication** — One canonical copy of each skill
2. **Enables multi-tool support** — Codex, Claude Code, Gemini all read from the same location
3. **Simplifies updates** — Edit once, all tools see the change

The sync script (`Infrastructure/scripts/sync_skills.sh`) creates symlinks in:
- `~/.agents/skills`
- `~/.agents/agent-skills` (repo root)
- `~/.codex/skills`
- `~/.claude/skills`
- `~/.gemini/antigravity/skills` (projection)

## Deprecations and Aliases

When a skill is deprecated:

1. Add `deprecated: true` to the frontmatter
2. Add `replacement: new-skill-name` if a successor exists
3. The skill remains loadable but agents are warned

Alias skills redirect to canonical skills:

```yaml
---
name: old-name
alias: canonical-name
---
```

## Skill Genome Loop

The Skill Genome Loop is a nightly process that:

1. **Analyzes** skill usage patterns from session logs
2. **Scores** skills on routing confusion and outcome quality
3. **Emits** improvement candidates for human review
4. **Gates** all changes behind human approval

**Controls:**
- `rollout-mode.txt`: `off | observe_only | active`
- `kill-switch.txt`: Emergency stop (file exists = stop)

**See also:** [Skill Genome Loop Runbook](/docs/skill-graphs/runbooks/skill-genome-loop.md)

- Back to [Docs index](/docs)
