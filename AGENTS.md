---
schema_version: 1
---

# agent-skills Agent Guide

This repository is the canonical source of Codex skills, linked operator docs, and agent workflow instructions. It is managed using the **Agent Skills Kit (`ask`)** CLI.

## Unified Agent Interface: `ask`

All agents (Gemini, Codex, Claude) MUST use the `bin/ask` CLI for repository operations.

- **Primary Commands:**
  - `ask repo status`: Check overall repository health and sync state.
  - `ask repo validate`: Run the full validation suite.
  - `ask skills list`: Discover active skills and their categories.
  - `ask skills sync`: Rebuild runtime projections (symlinks).
  - `ask skills audit <path> --level strict`: Perform a second-pass quality and security check.

## Mandatory workflow snippet

1. **Grounding:** `ask repo status --json`
2. **Investigation:** `ask skills list --category <topic>`
3. **Validation:** `ask skills audit <path> --level strict`
4. **Synchronization:** `ask skills sync`

## Skill Management Protocol

- **Fail-Fast Recovery:** If `ask skills install` fails due to missing files (e.g., `contract.yaml`), you should re-run with the `--remediate` flag to automatically scaffold the missing boilerplate.
- **Mandatory Hardening:** Whether you use `--remediate` or pivot to a manual import, it is **never** the end of the task. You MUST immediately invoke `ask skills audit <path> --level strict` to identify gaps, then harden the skill until it passes the "Gold Standard" validation.
- **Folding Strategy:** If `ask skills fold source target` returns a confidence score >= 0.2, prioritize folding the functionality into the existing skill instead of creating a duplicate.

## Skill line-budget policy

To maintain rapid context loading, follow these constraints:
- `SKILL.md` body (prose) should be <= 300 lines.
- Move bulk content (complex examples, detailed procedures, compatibility lists) to `references/<topic>.md` under the skill directory and replace with a one-line link.
- Preserve high-value nuance during relocation; do not summarize away technical depth.

## Browser/Playwright

- When browser tooling cannot access local files directly, start `python3 -m http.server` in the relevant directory.

## Testing Standards

- Run `ask repo validate` before committing any changes to core logic or multiple skills.
- Ensure all tests pass (`pytest` or repo-native equivalent) after multi-file changes.

<!-- AGENT-FIRST-SCAFFOLD:START -->
## Technical context

- Entry point: `bin/ask`
- Implementation logic: `scripts/lib/ask/`
- Spec artifacts: `docs/cli-specs/`
- Execution Ledger: `docs/plans/`

State model: `S0 -> S1 -> S2 -> S3 -> S4 -> S5` with rollback to `Sx` on critical governance events.
<!-- AGENT-FIRST-SCAFFOLD:END -->
