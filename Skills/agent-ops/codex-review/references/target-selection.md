# Codex Review Target Selection

## Decision Table

| Git state | Review target | Preferred command |
|---|---|---|
| Staged, unstaged, or untracked patch | local dirty work | `codex review --uncommitted` |
| Branch with committed work | branch/base diff | `codex review --base <base>` |
| Open PR | PR base diff | `codex review --base origin/<pr-base>` |
| Landed or already-pushed single change | commit diff | `codex review --commit <ref>` |

## Rules

- Do not force local review after the work has been committed. A clean `--uncommitted` run only proves there is no dirty patch.
- For clean `main` after landing, review the commit with `--commit <ref>` or review the branch before merging.
- Resolve PR base with `gh pr view --json baseRefName --jq .baseRefName` when available.
- If no PR base is available for a non-main branch, use `origin/main` unless repo instructions name a different base.
- Run `git fetch origin` before branch/base review when remote freshness matters and network permission is available.
- Current Codex CLI versions may reject `--base` plus an inline prompt. Run plain `codex review --base <ref>` first, then handle custom instructions separately.
