low
- file: Infrastructure/scripts/lifecycle-and-sync/command_surface.py:42-58,180-186
- finding: Folded-alias policy is duplicated across two hardcoded sets (FOLDED_SKILL_HANDLE_ALIASES and HIDDEN_COMPATIBILITY_COMMAND_HANDLES), and the hidden list repeats nearly all folded keys manually.
- risk: This increases drift risk and maintenance noise for future alias updates (easy to add/remove in one set but forget the other), which is avoidable complexity in a config-heavy control surface.
- remediation: Derive HIDDEN_COMPATIBILITY_COMMAND_HANDLES from FOLDED_SKILL_HANDLE_ALIASES keys plus explicit one-offs (currently he-goal-governor-archive), for example:
  HIDDEN_COMPATIBILITY_COMMAND_HANDLES = {"he-goal-governor-archive", *FOLDED_SKILL_HANDLE_ALIASES.keys()}
  This keeps behavior identical while removing duplicated policy declarations.

WROTE: artifacts/reviews/jsc-351-pu011/simplicity-unslopify.md
