# Live Deferred Context

Skill Factory keeps runtime context small through handles, compact `SKILL.md`
files, and deferred `references/`, `scripts/`, `assets/`, and `evals/`
content. Deferred does not mean archived.

## Rules

- Active plugin entrypoints, references, scripts, assets, and evals must live in
  canonical plugin paths.
- Alias symlinks are allowed when they point within the active plugin tree, such
  as `skills/skill-builder -> code_quality_review/skill-builder`.
- `skill-creator` and `skill-installer` are Codex `.system` skills. Skill
  Factory attaches local contracts under
  `skills-system/<skill>/references/skill-factory/` rather than maintaining
  standalone plugin-owned `SKILL.md` forks.
- Active files must not resolve through `fixtures/budget-archive/**`.
- `fixtures/budget-archive/**` is historical input only. It must not satisfy
  live helper, reference, or runtime visibility checks.
- When slimming a hot path, move still-valid detail to a live reference and add
  a clear "read when" condition.

## Validation

Run the active archive-link check after changing plugin handles, references, or
script layout:

```bash
python3 Infrastructure/scripts/validation-and-linting/check_plugin_active_archive_links.py --plugin skill-factory
python3 Infrastructure/scripts/validation-and-linting/check_skill_factory_system_overlays.py
```
