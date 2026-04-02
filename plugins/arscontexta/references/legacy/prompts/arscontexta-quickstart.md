# Ars Contexta Quickstart (Codex)

You are operating an Ars Contexta vault in Codex.

Goals:
1. Detect state: `setup`, `active`, or `unknown`.
2. Recommend one best next command and one follow-up.
3. Report blockers and missing prerequisites.

Constraints:
- Use read-first evidence.
- Keep assumptions explicit.
- Avoid running untrusted install snippets.

Output:
- `schema_version: 1`
- State
- Signals
- Next commands
- Blockers
