# Gold Standard CLI Design (April 2026)

## Table of Contents

- [1. The Dual-Mode Pattern](#1-the-dual-mode-pattern)
- [2. Core Functional Requirements](#2-core-functional-requirements)
  - [Structured Data First](#structured-data-first)
  - [Predictive Execution (Dry-Run)](#predictive-execution-dry-run)
  - [Observability & Traceability](#observability--traceability)
  - [Safety Gates](#safety-gates)
- [3. UX Patterns from Industry Leaders](#3-ux-patterns-from-industry-leaders)
- [4. Agentic Interaction Metrics](#4-agentic-interaction-metrics)
- [5. Environment Standards](#5-environment-standards)

The 2026 Gold Standard for command-line interfaces has evolved from being purely human-centric to **Agent-Native**. A modern CLI must be equally efficient for a human at a terminal and an autonomous agent operating in a loop.

## 1. The Dual-Mode Pattern
Every Gold-tier CLI must support two distinct interaction modes:

- **Human Mode (Default):**
  - Rich TUI (Text User Interface) with colors and spinners.
  - Interactive prompts for missing arguments.
  - "Forgiving" input parsing (e.g., case-insensitivity).
  - High-signal progress indicators.
- **Agent Mode (Machine-Readable):**
  - Enabled via `--json`, `--output json`, or environment variables.
  - Silent/Quiet by default (no spinners or ASCII art).
  - Deterministic structured output.
  - Non-interactive (fails if a prompt would have been shown, unless `--yes` or `--force` is present).

## 2. Core Functional Requirements

### Structured Data First
- **`--json` on every command:** Every command that returns data must have a JSON representation.
- **Schema Discovery:** Support `--schema` or `--describe` to output the JSON schema for the command's results.
- **Field Masking:** Support `--fields` or `--select` to limit output size, preserving context tokens for agents.

### Predictive Execution (Dry-Run)
- **`--dry-run` for all mutations:** Any command that changes state (create, update, delete, deploy) MUST support a dry-run mode.
- **Plan Output:** Dry-run should output a "Plan" object in JSON format describing exactly what *would* happen.

### Observability & Traceability
- **Request IDs:** Every command execution should generate or accept a `trace-id` for correlation across logs.
- **Semantic Exit Codes:**
  - `0`: Success
  - `1`: General Error
  - `2`: Validation Error (Agent should fix input)
  - `3`: Missing Dependency (Agent should install/setup)
  - `4`: Rate Limited (Agent should back off)
  - `5`: Authentication Required (Agent should prompt user)

### Safety Gates
- **Gated Destructive Actions:** Commands like `delete` or `drop` must require `--force` or `--confirm` in non-interactive mode.
- **Adversarial Validation:** Input must be hardened against path traversal (`../`), shell injection, and control character injection.

## 3. UX Patterns from Industry Leaders

| Feature | Reference | Implementation Note |
| :--- | :--- | :--- |
| **Context Awareness** | `gh` | Automatically detect repo/org from the local environment. |
| **Simulation** | `stripe` | Provide `trigger` or `simulate` commands for testing state. |
| **Manifest-First** | `flyctl` | Prefer modifying a `config.yaml` or `toml` over 20+ command flags. |
| **Interactive Help** | `vercel` | Help text should be contextual and include example "Next Steps". |

## 4. Agentic Interaction Metrics
- **Token Efficiency:** Does the CLI provide a `minified` or `compact` JSON mode?
- **Workflow Guidance:** Does the success output include a `next_steps` field?
- **Error Recoverability:** Do error messages include a `help_url` or a `fix_suggestion`?

## 5. Environment Standards
- **`NO_COLOR` / `CLICOLOR` Support:** Respect the industry-standard environment variables for color control.
- **Configuration Precedence:** 
  1. Flags
  2. Environment Variables
  3. Local Config File (`.mytool.yaml`)
  4. Global User Config (`~/.config/mytool/config.yaml`)
  5. Defaults
