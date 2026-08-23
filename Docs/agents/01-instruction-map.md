# Instruction Map Compatibility Pointer

The canonical instruction map is [Docs/agents/README.md](/Docs/agents/README.md). This file
preserves existing links only; do not maintain a second category list here.

Discovery order:

1. Read the active global and repository `AGENTS.md` files.
2. Open [Docs/agents/README.md](/Docs/agents/README.md).
3. Load only the task-specific instruction file named by that router.
4. Stop for a decision only when two applicable live instructions still
   conflict after scope and precedence are resolved.
