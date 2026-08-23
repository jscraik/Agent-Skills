# Contradictions and Cleanup

Use `Docs/agents/05-contradictions-and-cleanup.md` for current maintenance
invariants. Historical cleanup events belong in version control, not in an
instruction file that agents may interpret as present-tense repository truth.

## Current Invariants

- The repository root has no package-manager install step. Package commands run
  only inside verified package roots.
- Run preflight scripts as CLIs; do not source them as shell-function libraries.
- Keep detailed `ask` behavior in
  [Agent Operating Contract](/Docs/agents/16-agent-operating-contract.md), skill
  lifecycle rules in [Skill Management](/Docs/agents/17-skill-management.md),
  and preview commands in
  [Browser and Local Preview](/Docs/agents/18-browser-and-local-preview.md).
- Resolve the checkout with `git rev-parse --show-toplevel` and `pwd -P`; do not
  encode a personal absolute path or path casing as repository identity.
- When current instructions conflict, resolve canonical ownership, executable
  behavior, and scope precedence before editing prose. If two applicable live
  rules still cannot both be satisfied, stop with `Decision required:`.

## Cleanup Rule

Remove duplicated or obsolete detail only after its current owner and replacement
pointer are verified. Preserve memory, handoff, validation, approval, security,
and release boundaries unless an executable replacement exists.
