# Greptile Setup and Governance

## Table of Contents
- [Purpose](#purpose)
- [Prerequisites](#prerequisites)
- [MCP setup](#mcp-setup)
- [Repository governance setup (.greptile)](#repository-governance-setup-greptile)
- [Runtime policy gate (required every run)](#runtime-policy-gate-required-every-run)
- [Confidence and strictness policy defaults](#confidence-and-strictness-policy-defaults)
- [Training loop defaults](#training-loop-defaults)
- [Troubleshooting](#troubleshooting)

## Purpose
This document defines required setup and runtime governance for Greptile-powered workflows (`check-pr` and `greploop`) under the organizational review policy umbrella.

## Prerequisites
- `gh` CLI installed and authenticated (`gh auth status`).
- Greptile API key available as `GREPTILE_API_KEY` (never print token values).
- Repository indexed in Greptile.
- Separation of concerns: the coding agent must not approve its own PR output.

## MCP setup
1. Add Greptile MCP server:
   - URL: `https://api.greptile.com/mcp`
   - Header: `Authorization: Bearer <GREPTILE_API_KEY>`
2. Verify connectivity:
   - Run `list_custom_context`.
3. Validate PR visibility:
   - Run `list_merge_requests` for the target repository.

## Repository governance setup (.greptile)
Create directory-scoped governance files in each important repo segment:

```text
.greptile/
  config.json
  rules.md
  files.json
```

- `config.json`: strictness, comment types, structured rule IDs.
- `rules.md`: prose guidance and architecture examples.
- `files.json` (mandatory): schema/API pointers for graph-based cross-file validation.

Configuration precedence:
1. Org-enforced dashboard rules
2. Directory-scoped `.greptile/`
3. Legacy `greptile.json` (ignored if `.greptile/` exists in same directory)
4. Dashboard defaults

Multi-directory merge logic:
- strictness: MAX
- fileChangeLimit: MIN
- comment types: union
- booleans: OR

## Runtime policy gate (required every run)
Every `check-pr` and `greploop` run must evaluate and report:
- independent validation (reviewer role must be independent from coding role),
- auth + MCP availability,
- required `.greptile/` files,
- precedence + merge-logic application,
- branch strictness requirements,
- confidence-based decision mapping.

Full policy text and checklist:
- [Organizational review policy](organizational-review-policy.md)

## Confidence and strictness policy defaults
- Strictness 1: security-critical or fresh calibration scopes.
- Strictness 2: required default for `main`/production targets.
- Strictness 3: stable, non-critical internal infrastructure.

Confidence action defaults:
- 5/5: merge-ready
- 4/5: merge after minor polish
- 3/5 or below: rework and re-review required

## Training loop defaults
- React to comments with 👍 / 👎 (include reason with 👎).
- Use commit-to-commit deltas to validate addressed feedback.
- Apply 3-ignore suppression only for intentional patterns.
- Expect a 2–3 week calibration period for new repositories.

## Troubleshooting
- Reviews not running: verify repository indexing completion.
- MCP failures: verify API key wiring and bearer header format.
- Shallow context: ensure `.greptile/files.json` points to schema/API artifacts.
- Noisy comments: tighten scoped rules and provide explicit 👎 rationale.
