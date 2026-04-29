# Concepts

Concept docs explain how the system works and why it is shaped this way.

Write concepts for readers who can run commands, but need help understanding the "why" and the tradeoffs.

When you describe a workflow, link to the exact script or folder and show a small example.

## What Is A Skill?

A **skill** is a reusable Markdown workflow that guides AI agent behavior. In
this repo, the editable source lives in one of two canonical places:

- `Skills/<topic>/<skill>/SKILL.md` for first-party skills.
- `Plugins/<plugin>/skills/**/SKILL.md` for plugin-owned skills.

Generated runtime copies under `.agents/skills/**` are projections, not source
of truth.

Each canonical skill folder contains a `SKILL.md` file with frontmatter such as:

```yaml
---
name: skill-name
description: What this skill does
triggers:
  - "when to use"
---
# Skill content in Markdown
```

**Canonical skill folder structure:**

```
Skills/<topic>/<skill-name>/
|-- SKILL.md           # Required: skill definition
|-- Infrastructure/references/        # Optional: supporting docs
|-- Infrastructure/scripts/           # Optional: helper scripts
`-- Infrastructure/templates/         # Optional: file templates
```

## Runtime Projection

The `.agents/skills/` directory is a generated runtime projection consumed by
Codex and other agent runtimes. In rooted mode it contains root router skills
plus generated command handles such as `$he-heartbeat`.

This design:

1. Keeps full workflow bodies in canonical source paths.
2. Makes important routed skills mentionable through thin `$handle` pointers.
3. Keeps generated runtime and command-surface metadata reproducible.
4. Separates resolver proof, projection proof, user sync, and live picker proof.

Use these commands to inspect the live surfaces:

```bash
python3 bin/ask skills list --json
python3 bin/ask skills handles --check --json
python3 bin/ask skills resolve he-heartbeat --json
python3 bin/ask reviewers resolve skillinspector --json
```

`python3 bin/ask skills sync --scope workspace --projection rooted` refreshes
repo-local projection files. `python3 bin/ask skills sync --scope user
--projection rooted` refreshes user runtime links and profile-local plugin
mirrors.

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

**See also:** [Skill Genome Loop Runbook](/Docs/skill-graphs/runbooks/skill-genome-loop.md)

- Back to [Docs index](/Docs)
