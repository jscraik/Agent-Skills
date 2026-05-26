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

## Subagent Lifecycle Skeleton

Use lifecycle hooks when a coordinator requested task envelopes, artifact-first
reviewer output, or blocked-agent classification.

```json
{
  "SubagentStart": [
    {
      "type": "command",
      "command": "${PLUGIN_ROOT}/hooks/subagent-start-context.sh"
    }
  ],
  "SubagentStop": [
    {
      "type": "command",
      "command": "${PLUGIN_ROOT}/hooks/subagent-stop-verify.sh"
    }
  ]
}
```

Start with a shared recorder and verifier. The start hook should pass the
runtime card path, expected artifacts, validation commands, and authority
boundary. The stop hook should check that required artifacts exist, are
non-empty, and have a receipt before coordinator synthesis.

## Runtime Card Fields

Runtime cards should be snapshots, not permanent truth. Include `generated_at`,
`expires_at`, source timestamps, and `freshness: fresh|stale|unknown` along
with repo, cwd, branch, head SHA, dirty state, session, turn, trace, goal,
permission profile, approval reviewer, active hooks hash, active agents,
expected artifacts, known external refs, and last validation.

## Stop Claim Check

A Stop hook should block only high-confidence contradictions, such as claiming a
test passed without a matching command outcome, claiming an artifact exists when
it is missing, or claiming PR readiness without refreshed check/review evidence.
Uncertain matches should warn and write telemetry rather than trapping the
assistant.

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
