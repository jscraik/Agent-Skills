# Agents Md Guidance

Read when an AGENTS refactor needs Codex discovery rules, Context Pointer design, or Harness Engineering plan-routing context that would bloat the entrypoint.

## Codex Instruction Discovery

- Codex loads discovered `AGENTS.md` files before work and merges applicable global, root, and nested guidance by scope.
- A closer instruction file overrides broader guidance inside its subtree.
- Codex discovers at most one instruction file per directory by default. Linked docs are references, not automatically loaded instructions, unless repo configuration or a discovered instruction explicitly makes them part of the route.
- Keep root AGENTS content focused on rules relevant to every task in that scope: project purpose, non-default toolchain, non-standard commands, command boundaries, and critical validation expectations.

## Context Pointer Use

Use Context Pointers for task-specific detail that does not need to be always loaded: linked docs, nested AGENTS files, skill handles, command names, headings, scripts, schemas, hooks, and code anchors.

Context ledger routing categories:

- root: relevant to every task in the active scope;
- nested AGENTS scope: narrower rule that should auto-load only below a directory;
- linked reference: durable detail, examples, or procedures needed only on demand;
- Context Pointer: a stable link, heading, command, function, module, or skill handle that helps future agents find relocated context;
- supplemental: useful context that is not binding instruction; and
- deletion candidate: redundant, vague, obsolete, or already replaced by a verified canonical source.

A pointer is acceptable only when:

- the target path, heading, handle, command, or code anchor exists;
- the owning instruction surface tells future agents when to follow it;
- the moved rule remains binding where it must be binding; and
- the context ledger records why the move did not lose required behavior.

## Harness Engineering Plan Pointer

For Harness Engineering work, AGENTS should point to the `@harness-engineering` or `he-plan` contract instead of defining a competing plan format. The durable plan artifact should carry source traceability, stable acceptance IDs, repo-relative paths, risks, validation, and tracker or PR traceability.

Keep plan instructions concise in AGENTS. Use unresolved questions only when planning is the requested output or evidence is insufficient to choose safely.

## Validation Checklist

- Active instruction scope and discovery order identified.
- All moved pointers resolve.
- Contradictions are resolved or explicitly blocked for user choice.
- Binding memory, handoff, validation, approval, and security contracts are preserved.
- Exact validation commands are reported with `pass`, `fail`, or `blocked`.
