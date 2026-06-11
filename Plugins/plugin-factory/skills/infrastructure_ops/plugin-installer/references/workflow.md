# Plugin Installer Workflow

Use this file for staged install behavior after loading `SKILL.md`.

## Procedure

1. Resolve source, destination, trust policy, and pinned ref.
2. Stage plugin payload in quarantine.
3. Validate staged payload before promotion.
4. Promote atomically to destination.
5. Write provenance manifest and rollback journal.
6. Return install summary and explicit blockers.

## Command Matrix

```bash
bin/ask plugins install <url> --path Plugins/<plugin-name>
uv run python Skills/plugin-installer/Infrastructure/scripts/install-plugin-from-github.py --url <url> --path Plugins/<plugin-name> --validation-level strict
uv run python Skills/plugin-builder/Infrastructure/scripts/plugin_builder.py validate <installed-plugin-path>
```

## Required Artifacts

- provenance manifest
- rollback journal
- validation command output

## Blockers

- untrusted source without explicit override
- unpinned ref when pinning is required
- path traversal or symlink escape outside plugin root
- failed validation in quarantine stage
