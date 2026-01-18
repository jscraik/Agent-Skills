# Agent Skills

This repository is the source of truth for Codex/agent skills. Canonical skills live in the categorized folders below, while the `skills/` directory provides a flat symlink view used by tooling.

## Repository Layout

```
~/dev/agent-skills/
├── github/       # GitHub/DevOps workflows
├── frontend/     # Frontend/UI patterns
├── apple/        # Apple/Swift/SwiftUI skills
├── backend/      # Backend/Architecture/CLI
├── product/      # Product specs, docs, planning
├── utilities/    # Utilities and helpers
├── skills/       # Flat symlink directory (tooling entrypoint)
├── skills-system/ # Bundled/system skills (kept out of flat view)
└── SKILL.md      # Human-readable skills index
```

## How It Works

- Each skill lives in a category folder and includes its own `SKILL.md`.
- The `skills/` directory contains symlinks to the canonical folders so tools can load a flat list.
- `skills-system/` stores bundled/system skills and is excluded from the flat view to avoid duplicates.
- Use `scripts/sync_skills.sh` to update symlinks and regenerate `SKILL.md` after adding or moving skills.

## Categories and Skills

See `SKILL.md` for the full index with descriptions.
