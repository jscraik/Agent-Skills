---
schema_version: 1
---

# agent-skills Agent Guide

This repository is the canonical source of Codex skills, linked operator docs, and agent workflow instructions. It is managed using the **Agent Skills Kit (`ask`)** CLI.

> 🤖 **AI Agent Mode (Robot Mode):** This CLI is designed for AI coding agents like yourself. It accepts `--robot` (or `--agent-mode`) to enable maximum flexibility: fuzzy command matching, helpful error corrections, and detailed guidance when things go wrong. When the intent is clear but syntax is off, we'll honor your intent and show you the correct syntax for next time.

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

## 🤖 Robot Mode: AI Agent Flexibility Contract

The `ask` CLI is designed to be maximally helpful to AI coding agents. We understand that:
- You might use slightly different syntax than documented
- Your intent is usually clear even if your command isn't perfect
- You need detailed, actionable error messages with examples

### Robot Mode Flags

| Flag | Purpose |
|------|---------|
| `--robot` | Enable AI-friendly mode: flexible parsing, helpful corrections, verbose guidance |
| `--agent-mode` | Alias for `--robot` |
| `--json` | Always use this for structured output parsing |

### Flexibility Guarantees

When `--robot` is enabled (or when we detect AI agent usage patterns):

**1. Fuzzy Command Matching**
```bash
# These will all work and be corrected:
ask skill list                    # → ask skills list
ask graph search security         # → ask graph find security
ask validate skill backend/ce-spec # → ask skills audit backend/ce-spec --level strict
```

**2. Smart Argument Recovery**
```bash
# Wrong order? We'll figure it out:
ask skills audit --level strict backend/ce-spec  # ✓ Works
ask skills audit backend/ce-spec strict          # → Corrected to --level strict
```

**3. Helpful Error Messages**
When we can't figure out your intent, you'll get:
```
❌ Error: I couldn't find a skill at 'backend/ce-specs'

💡 Did you mean one of these?
   • backend/ce-spec
   • backend/cli-spec
   • backend/backend-engineer

📚 Examples of correct usage:
   ask skills audit backend/ce-spec --level strict
   ask skills audit backend/cli-spec --level compat
   ask graph info ce-spec

🔍 Try searching: ask graph find "ce-spec"
```

### Agent Best Practices

1. **Always use `--json` for programmatic parsing**
   ```bash
   ask skills list --json | jq '.data.skills[].name'
   ```

2. **Check `metadata.next_steps` in responses**
   ```json
   {
     "status": "success",
     "metadata": {
       "next_steps": [
         "ask skills audit backend/cli-spec --level strict",
         "ask graph related cli-spec"
       ]
     }
   }
   ```

3. **Use the graph for discovery**
   ```bash
   ask graph find "security" --tier stable --json
   ask graph chain skill-creator skill-installer --json
   ask graph related skill-builder --depth 2 --json
   ```

4. **When in doubt, the CLI will guide you**
   Every error includes:
   - What went wrong
   - What you probably meant
   - 2-3 correct examples
   - A suggested next command

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
