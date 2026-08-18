---
title: Codex sandbox live PR sweep permissions
asset_family: agent operations automation
owner: Agent Skills Team
source_artifact: Skills/agent-ops/pr-green-sweep/SKILL.md
freshness_reviewed_on: 2026-08-18
review_after_days: 90
---

# Codex Sandbox Live PR Sweep Permissions

## Table of Contents

- [Problem](#problem)
- [Resolution](#resolution)
- [Evidence](#evidence)
- [Follow-up](#follow-up)

## Problem

PR green sweep heartbeats repeatedly reported `error connecting to
api.github.com` and treated the failure like GitHub connectivity was down. The
same run later proved GitHub auth, DNS, TLS, and API access were healthy when
the command was executed with explicit Codex sandbox network permission.

The real failure class was an environment-contract gap: networked PR commands
were being run without the required sandbox network permission, while unrelated
`mise` home-cache write warnings added noise. Retrying the same command without
changing the permission profile repeated the failure and forced Jamie to give
the same operational steering again.

## Resolution

For live PR sweep work in Codex sandboxed sessions:

1. Treat `gh`, CircleCI, CodeRabbit, Snyk, package registry, and equivalent
   live-state commands as networked operations.
2. Run them with explicit network permission before classifying failures as
   service outages, bad credentials, or repo defects.
3. Before the shell starts, export approved writable paths for the stateful
   tools in scope: `XDG_CACHE_HOME`, `XDG_STATE_HOME`, `MISE_CACHE_DIR`,
   `MISE_STATE_DIR`, and `UV_CACHE_DIR`. Set `npm_config_cache` only when npm
   is in scope. Retain the operator-authenticated `gh` configuration; set
   `GH_CONFIG_DIR` only when an explicitly supplied configuration is already
   authenticated. Resolve the repository root with
   `git rev-parse --show-toplevel`, then set `MISE_TRUSTED_CONFIG_PATHS` to its
   explicitly approved `.mise.toml` file, not the current subdirectory or the
   whole worktree. Verify each resolved state path is inside the approved
   scratch directory and writable, and the trusted-config path is that approved
   config file, before invoking `gh`, `mise`, `uv`, or npm.
4. Keep live-state probes short and non-watch unless actively waiting for one
   known check.
5. After two equivalent command, approval, or permission failures, stop the
   active PR lane and refine the environment contract before retrying.

The repeat-prevention rule is stronger than a local workaround: a PR sweep is
not allowed to continue from stale GitHub state when the live-state environment
contract has not been proven.

## Evidence

- `gh auth status` reported the active `jscraik` account with `repo` and
  `workflow` scopes.
- `gh api rate_limit` returned the authenticated rate-limit record when run
  with explicit network permission.
- `curl -I https://api.github.com` returned HTTP `200`.
- `gh pr list --state open --limit 20 --json number,title,headRefName,headRefOid,baseRefName,mergeable,isDraft,statusCheckRollup,reviewDecision,url` returned the current open PR
  inventory when run with explicit network permission.
- The same command without the network permission profile previously returned
  `error connecting to api.github.com`.
- `mise` warnings targeted `/Users/jamiecraik/Library/Caches/mise/...` and were
  filesystem cache writes, not GitHub network evidence.

## Follow-up

- Keep `$pr-green-sweep` and root agent guidance aligned with this solution.
- If a future live PR command reports a network-looking error, prove the
  sandbox permission profile before changing repo code or asking Jamie to debug
  connectivity.
