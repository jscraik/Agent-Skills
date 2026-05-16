# Repo-Local Audit Boundaries

Use this note when hardening a skill whose canonical source is outside the
`agent-skills` repository, such as repo-local Codex skills under another repo's
`.codex/skills/` tree.

## Boundary Cue

If `./bin/ask skills audit <absolute-path> --level strict --json --robot`
returns `ERR_PATH_TRAVERSAL`, classify the failure as a repository-boundary
blocker. It means the agent-skills audit runner refused to traverse outside its
allowed repository boundary; it does not by itself prove the target skill
content is invalid.

## Safe Handling

1. Confirm the target is canonical in its owning repository.
2. Run that repository's documented validators or focused gates.
3. Run `git diff --check` on the edited skill paths when available.
4. Report the agent-skills audit as `blocked`, including the exact
   `ERR_PATH_TRAVERSAL` text and the substitute validation evidence.

Do not copy repo-local skills into `.agents/**`, `Plugins/cache/**`, temporary
mirrors, or generated projection paths to satisfy the audit runner. That turns a
boundary guard into source drift.

## Output Shape

```yaml
validation:
  - command: ./bin/ask skills audit /owner/repo/.codex/skills/name --level strict --json --robot
    status: blocked
    reason: ERR_PATH_TRAVERSAL; target is outside agent-skills audit boundary
  - command: git diff --check -- .codex/skills/name
    status: pass
blocked_by:
  class: repository_boundary
  next_step: use owner repo validators or add an explicit owner-repo audit lane
```
