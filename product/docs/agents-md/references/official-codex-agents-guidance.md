# Official Codex AGENTS Guidance

Use this reference when updating `AGENTS.md` skills or auditing repo instruction trees.

## Table of Contents
- [Canonical Discovery Order](#canonical-discovery-order)
- [Key Limits And Knobs](#key-limits-and-knobs)
- [Verification Commands](#verification-commands)
- [Troubleshooting Notes](#troubleshooting-notes)
- [Progressive Disclosure Implications](#progressive-disclosure-implications)
- [Sources](#sources)

## Canonical Discovery Order
- Global scope: Codex checks `~/.codex/AGENTS.override.md` first, then `~/.codex/AGENTS.md`, and uses the first non-empty file.
- Project scope: starting at the project root and walking down to the current working directory, Codex checks `AGENTS.override.md`, then `AGENTS.md`, then any names listed in `project_doc_fallback_filenames`.
- Codex includes at most one auto-discovered instruction file per directory.
- Files closer to the current working directory override broader guidance because they are appended later in the merged prompt.
- Empty instruction files are ignored.

## Key Limits And Knobs
- `project_doc_fallback_filenames`: additional filenames that Codex should treat as project instructions when `AGENTS.md` is absent.
- `project_doc_max_bytes`: maximum combined byte budget for discovered project docs. The default is 32 KiB.
- `CODEX_HOME`: swaps the home directory Codex uses for global config and global `AGENTS` files.
- If OpenAI doc pages phrase `project_doc_max_bytes` differently, prefer the `agents-md` guide plus live Codex source behavior for operator guidance. As of March 2026, the guide and `codex-rs/core/src/project_doc.rs` both reflect an effective combined discovery budget across the loaded instruction chain.

## Verification Commands
- Root scope:
  - `codex --ask-for-approval never "Summarize the current instructions."`
- Nested scope:
  - `codex --cd <subdir> --ask-for-approval never "Show which instruction files are active."`
- Audit/logging:
  - inspect `~/.codex/log/codex-tui.log`
  - inspect recent `session-*.jsonl` if session logging is enabled

## Troubleshooting Notes
- If the wrong instructions appear, look for a higher-priority `AGENTS.override.md`.
- If fallback names are ignored, confirm they are listed in `project_doc_fallback_filenames` and restart Codex or start a new run.
- If instructions look stale, restart Codex in the target directory; there is no manual cache-clear step.
- If guidance is truncated, raise `project_doc_max_bytes` or split instructions into narrower nested scopes.

## Progressive Disclosure Implications
- Keep root `AGENTS.md` short and high signal.
- Use nested scoped `AGENTS.override.md` or `AGENTS.md` for true local rule changes.
- Use linked docs for depth, examples, and policy detail, but do not present them as automatically loaded unless they are themselves discovered instruction files.
- A concise, accurate root file is better than a large catch-all document.

## Sources
- OpenAI docs: `https://developers.openai.com/codex/guides/agents-md/`
- OpenAI docs config reference: `https://developers.openai.com/codex/config-reference/`
- Codex repo implementation: `codex-rs/core/src/project_doc.rs`
