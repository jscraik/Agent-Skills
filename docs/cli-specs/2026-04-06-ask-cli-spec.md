---
title: ask (Agent Skills Kit) CLI Specification
status: active
date: 2026-04-06
deepened: 2026-04-06
spec_depth: full
agent_compatible: true
schema_version: 1
---

# ask (Agent Skills Kit) CLI Specification

## Enhancement Summary
This specification has been deepened to include:
- **Full Signature Set:** All commands now have explicit type-safe parameter definitions.
- **Unified Error Registry:** Formal mapping of exit codes to `ERR_*` string constants.
- **Distributed Tracing:** Support for external `trace_id` injection via flags/env.
- **Telemetry Support:** New optional `telemetry` field in `CallResult` for performance tracking.
- **Context Awareness:** Formalized `.git` discovery for repository root detection.
- **Atomic Promotion:** Hardened state model to prevent partial filesystem states.

## Strategic Alignment
- **Problem Statement:** The `agent-skills` repository currently relies on a fragmented collection of shell scripts and Python utilities with inconsistent interfaces, making it difficult for both humans and agents to manage the skill lifecycle reliably.
- **Audience:** Dual-mode. Optimized for human developers at a TUI and autonomous agents (Gemini, Codex, Claude) using JSON.
- **Context Discovery:** The CLI automatically identifies its environment by searching for the nearest `.git` directory to establish the `<REPO_ROOT>`.

## Command Hierarchy
```mermaid
graph TD
    ask[ask] --> skills[skills]
    ask --> repo[repo]
    ask --> mcp[mcp]
    
    skills --> sync[sync]
    skills --> list[list]
    skills --> audit[audit]
    skills --> install[install]
    skills --> fold[fold]
    
    repo --> validate[validate]
    repo --> status[status]
    repo --> graph[graph]
    
    mcp --> mcp_sync[sync]
    mcp --> mcp_verify[verify]
```

## Interface Contract

### Type-Safe Signatures
```typescript
ask skills sync(scope?: "user" | "workspace", dry_run?: boolean)
/** @param scope - Discovery tier to target. Defaults to "workspace". */

ask skills list(category?: string, status?: "active"|"incubating", json?: boolean)
/** @param category - Filter by directory (e.g. github, product). */

ask skills audit(path: string, level?: "compat" | "strict")
/** @param level - "strict" runs full PI and security gates. */

ask skills install(url: string, remediate?: boolean, dest?: string)
/** @param remediate - Scaffolds missing contract/eval files if true. */

ask skills fold(source: string, target: string, sensitivity?: float)
/** @param sensitivity - Overlap threshold (default 0.2). */

ask repo status(verbose?: boolean)
/** Returns overall health, sync status, and lint issues. */

ask repo graph(format?: "mermaid" | "json", focus?: string)
/** Generates or queries the dependency/skill graph. */
```

### Response Envelope (`CallResult`)
```json
{
  "status": "success" | "error" | "partial",
  "trace_id": "string (uuid-v4)",
  "metadata": {
    "version": "0.1.0",
    "command": "string",
    "latency_ms": "integer",
    "next_steps": ["string"]
  },
  "data": {
    "plan": {
      "writes": ["string"],
      "deletes": ["string"],
      "symlinks": [{"from": "string", "to": "string"}]
    },
    "results": { "type": "object" }
  },
  "telemetry": {
    "tokens_estimated": "integer",
    "cache_hit": "boolean"
  },
  "errors": [
    {
      "code": "string (See Error Registry)",
      "message": "string",
      "fix_suggestion": "string",
      "help_url": "string"
    }
  ]
}
```

## Operation Lifecycle

### State Model: Skill Installation (`skills install`)
1.  **RESOLVING:** Parse URL and verify repository provenance.
2.  **QUARANTINE:** Download artifacts to `.quarantine/<run-id>/`.
3.  **REMEDIATING:** (Optional) Scaffold `contract.yaml` and `evals.yaml`.
4.  **VALIDATING:** Run `skill_gate.py` and `openclaw_skill_guard.py`.
5.  **ATOMIC PROMOTION:** Move from quarantine to destination; update symlinks. **MUST NOT** update any symlinks until all file moves are verified.
6.  **COMPLETED:** Emit `CallResult` and update skill index.

### Error Registry (Exit Codes)
| Code | String Code | Description |
| :--- | :--- | :--- |
| **0** | `SUCCESS` | Operation completed normally. |
| **1** | `ERR_RUNTIME` | Network timeout, filesystem permission, etc. |
| **2** | `ERR_VALIDATION` | `ERR_PI_GUARD`, `ERR_SCHEMA_INVALID`, `ERR_PATH_TRAVERSAL`. |
| **3** | `ERR_DEPENDENCY` | Missing binary (e.g. `gh`, `mermaid-cli`). |
| **4** | `ERR_CONFLICT` | `ERR_REDUNDANCY` (Overlap >= threshold). |
| **5** | `ERR_AUTH` | Authentication required to access source/repo. |

## Security & Safety

### Adversarial Validation
- **Path Sanitization:** All file arguments are resolved against the repository root discovered via `.git`. Any path resolving outside the root is rejected with `ERR_PATH_TRAVERSAL`.
- **Signal Handling:** On `SIGINT` or `SIGTERM`, the CLI must halt and remove active `.quarantine/` directories. Promotion steps must be idempotent to allow safe retry.

### Redaction Policy
Apply fail-closed redaction to all outputs:
- **Secrets:** Redact patterns matching `sk-...`, `ghp_...`, `AIza...`, and `Bearer ...`.
- **Absolute Paths:** Replace home directory and local paths with `<REPO_ROOT>` or `<USER_HOME>`.

## Acceptance and Test Matrix

| ID | Description | Command | Expected Outcome |
| :--- | :--- | :--- | :--- |
| **CA1** | Context Discovery | `cd subfolder && ask repo status` | Correctly identifies root via `.git`. |
| **CA2** | Distributed Tracing | `ASK_TRACE_ID=foo ask skills list --json` | Returned `trace_id` equals `foo`. |
| **CA3** | Atomic Failure | `ask skills install` + Network Cut | No partial skill folder in destination. |
| **CA4** | Error Mapping | `ask skills audit /etc/passwd` | Exit 2; JSON error `ERR_PATH_TRAVERSAL`. |
| **CA5** | Redundancy Catch | `ask skills install <overlap>` | Exit 4; Confidence score in JSON `data`. |
| **CA6** | Telemetry Output | `ask skills list --json` | Includes `telemetry` object in envelope. |

## Definition of Done
- [ ] CLI handles `SIGINT` (Ctrl+C) gracefully with clean exit.
- [ ] Non-interactive mode (non-TTY) disables all spinners and prompts.
- [ ] Redaction filter passes all 8+ standard project secret patterns.
- [ ] `ask --help` provides TS-style signatures for all commands.
- [ ] Automated tests cover all `CA1` through `CA6` scenarios.
