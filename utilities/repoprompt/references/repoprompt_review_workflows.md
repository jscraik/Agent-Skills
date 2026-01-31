# RepoPrompt review workflows (2026-01)

Purpose: fast, token-efficient diff review and review follow-up using RepoPrompt tools.

## Diff review (MCP or rp-cli)
- Do **not** run `git diff` to read full patch content.
- Use name-only diffs to select files; pass diffs to RepoPrompt review mode.

### Scope inference (no diff reading)
- If user specifies staged/unstaged/range, follow it.
- Else default: staged if staged changes exist; otherwise unstaged.

### Build selection (name-only)
- staged: `git diff --staged --name-only`
- unstaged: `git diff --name-only`
- range: `git diff <range> --name-only`
- both: union staged + unstaged lists

### Send review
- MCP: `chat_send mode="review" include_diffs=true selected_paths=[...]`
- CLI: `review "Review the diffs for the selected files..."`
- Do not paste diffs into the message.

## Follow-up from review
- Read all review feedback files referenced by the user.
- Address every item, using RepoPrompt context tools as needed.
- Append an Appendix section to the plan/log/todos/tasks file to capture the follow-up work.
