# Hook Examples

Use these examples when authoring or reviewing Codex hooks. Keep project hooks
repo-local when they depend on repo files, and keep global hooks small and
portable.

## Minimal Command Hook

~~~json
{
  "SessionStart": [
    {
      "type": "command",
      "command": "${PLUGIN_ROOT}/hooks/session-start.sh"
    }
  ]
}
~~~

For plugin-bundled hooks, prefer PLUGIN_ROOT and PLUGIN_DATA for plugin-owned
paths. For repo-local hooks, prefer paths discovered from the repo contract
instead of hardcoded home-directory paths.

## Script Skeleton

~~~bash
#!/usr/bin/env bash
set -euo pipefail

repo_root="${CODEX_WORKSPACE_ROOT:-${PWD}}"

if [[ -f "${repo_root}/scripts/verify-work.sh" ]]; then
  bash "${repo_root}/scripts/verify-work.sh" --fast
fi
~~~

## Validation Evidence

Run the owner repo hook validator first, then any focused projection checks:

~~~bash
bash scripts/validate-codex-hooks.sh
bash scripts/audit-codex-symlinks.sh
~~~

If the hook is plugin-bundled, also validate the plugin manifest and bundled
hook path so the command is executable from the plugin root after install.
