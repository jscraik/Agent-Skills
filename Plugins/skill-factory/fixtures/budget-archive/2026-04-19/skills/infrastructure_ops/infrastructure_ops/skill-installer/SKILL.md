---
name: skill-installer
description: Install Codex skills into the canonical git source tree from a curated list or a GitHub repo path. Use when a user asks to list installable skills, install a curated skill, or install a skill from another repo (including private repos).
metadata:
  short-description: Install curated skills from openai/skills or other repos
  skill-type: infrastructure_ops
---

# Skill Installer

Use this skill for listing and installing skills from trusted sources.

## When to use
- List available installable skills.
- Install from curated catalog or explicit GitHub repo/path.
- Verify install destination and runtime visibility.

## Do not use
- Skill creation or refactor design work: route to `[[skill-creator]]`.
- Release-hardening/eval work: route to `[[skill-builder]]`.

## Core Philosophy
- Verify source and destination before writing anything.
- Prefer explicit user intent over inferred replacement behavior.
- Preserve required operational context in `references/` with clear signposts.

## Core workflow
1. Classify request: `list` or `install`.
2. Resolve source and destination with explicit user intent.
3. Run minimal installer helper command.
4. Verify resulting filesystem state.
5. Report exact paths and restart requirement.

## Required output contract
Provide:
- `schema_version`
- `mode`
- `source`
- `destination`
- `validation_evidence`
- `restart_required`

## Progressive disclosure policy
Required operational context is never removed. Preserve context by relocating details into `references/`.

Read when:
- handling source and install safety caveats: [install flows](./references/install-flows.md)
- handling failures: [troubleshooting](./references/troubleshooting.md)
- verifying policy boundaries: [contract](./references/contract.yaml)

## Anti-Patterns to Avoid
- Overwriting existing installs without explicit confirmation.
- Treating untrusted URLs or paths as safe inputs.
- Reporting success without filesystem verification evidence.

## Constraints
- Do not overwrite existing installs without explicit confirmation.
- Treat URLs and paths as untrusted input.
- Redact tokens, credentials, and secret values.
