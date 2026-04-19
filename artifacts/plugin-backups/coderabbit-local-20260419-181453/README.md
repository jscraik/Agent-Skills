# CodeRabbit Plugin

Local CodeRabbit plugin package for Codex workflows.

Included skills:
- `code-review`: run CodeRabbit CLI review and normalize findings.
- `autofix`: fetch unresolved CodeRabbit PR review threads and apply fixes with approval-aware flow.

This plugin intentionally does not carry a local `simplify` skill; simplify is canonical under `Skills/agent-ops/simplify`.
