---
title: ask (Agent Skills Kit) CLI Specification
status: active
date: 2026-04-06
deepened: 2026-04-06
spec_depth: full
agent_compatible: true
schema_version: 1
---

## Table of Contents

- [Enhancement Summary](#enhancement-summary)
- [Strategic Alignment](#strategic-alignment)
- [Command Hierarchy](#command-hierarchy)
- [Interface Contract](#interface-contract)
  - [Type-Safe Signatures](#type-safe-signatures)
  - [Response Envelope (`CallResult`)](#response-envelope-callresult)
- [Operation Lifecycle](#operation-lifecycle)
  - [State Model: Skill Installation (`skills install`)](#state-model-skill-installation-skills-install)
  - [Error Registry (Exit Codes)](#error-registry-exit-codes)
- [Security & Safety](#security--safety)
  - [Adversarial Validation](#adversarial-validation)
  - [Redaction Policy](#redaction-policy)
- [Acceptance and Test Matrix](#acceptance-and-test-matrix)
- [Robot Mode (AI Agent Interface)](#robot-mode-ai-agent-interface)
- [Definition of Done](#definition-of-done)

# ask (Agent Skills Kit) CLI Specification

## 2026-05-13 Refresh

This document remains the implementation-grade baseline for the original
`ask` envelope, error, telemetry, and lifecycle contracts. The live command
surface has since expanded beyond the 2026-04-06 tree. Validate the current
surface with `./bin/ask --help`; as of the 2026-05-13 documentation refresh it
exposes these top-level topics:

- `repo`: `status`, `validate`, `check-stability`, `doctor`,
  `closeout`, `doctor-catalog`, `provider-audit`, `surface`
- `skills`: `list`, `budget`, `handles`, `resolve`, `parse`,
  `proof`, `prove`, `explain`, `route`, `goal`, `improve`,
  `starter`, `sync`, `audit`, validation helpers, `install`, `fold`,
  `init`
- `runtime`: `surface`, `budget`
- `reviewers`: `resolve`
- `workouts`: `list`, `run`, `score`, `promote`
- `plugins`, `evals`, `graph`, `mcp`, and `wiki`

The product golden path is now documented separately in
[ask Product Golden Path Command Contracts](/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md):
`repo doctor` -> `skills improve` -> `skills explain` -> `skills prove`
-> `repo closeout --changed`.

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
- **Audience:** Dual-mode. Optimized for human developers at a TUI and autonomous agents (OpenAI, Codex, Codex) using JSON.
- **Context Discovery:** The CLI automatically identifies its environment by searching for the nearest `.git` directory to establish the `<REPO_ROOT>`.

## Command Hierarchy
```mermaid
graph TD
    ask[ask] --> skills[skills]
    ask --> repo[repo]
    ask --> reviewers[reviewers]
    ask --> runtime[runtime]
    ask --> plugins[plugins]
    ask --> evals[evals]
    ask --> workouts[workouts]
    ask --> graph[graph]
    ask --> mcp[mcp]
    ask --> wiki[wiki]

    skills --> sync[sync]
    skills --> list[list]
    skills --> budget[budget]
    skills --> handles[handles]
    skills --> resolve[resolve]
    skills --> parse[parse]
    skills --> proof[proof]
    skills --> prove[prove]
    skills --> explain[explain]
    skills --> route[route]
    skills --> goal[goal]
    skills --> improve[improve]
    skills --> starter[starter]
    skills --> audit[audit]
    skills --> install[install]
    skills --> fold[fold]
    skills --> init[init]

    repo --> validate[validate]
    repo --> status[status]
    repo --> check_stability[check-stability]
    repo --> doctor[doctor]
    repo --> closeout[closeout]
    repo --> doctor_catalog[doctor-catalog]
    repo --> provider_audit[provider-audit]
    repo --> surface[surface]

    runtime --> runtime_surface[surface]
    runtime --> runtime_budget[budget]

    reviewers --> reviewers_resolve[resolve]

    workouts --> workouts_list[list]
    workouts --> workouts_run[run]
    workouts --> workouts_score[score]
    workouts --> workouts_promote[promote]

    plugins --> plugins_init[init]

    evals --> evals_run[run]
    evals --> benchmark[benchmark]
    evals --> dashboard[dashboard]

    graph --> graph_related[related]
    graph --> graph_find[find]
    graph --> graph_info[info]
    graph --> graph_chain[chain]
    graph --> graph_list[list]
    graph --> graph_topics[topics]
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

ask skills fold(source: string, target: string, sensitivity?: number)
/** @param sensitivity - Overlap threshold (default 0.2). */

ask repo status(verbose?: boolean)
/** Returns overall health, sync status, and lint issues. */

ask graph related(skill: string, depth?: int, reverse?: boolean, topicFilter?: string, tier?: string)
/** Finds related skills in the graph. Depth controls BFS traversal (default 1). */

ask graph find(query: string, topicFilter?: string, tier?: string)
/** Full-text search across skill names and topics. */

ask graph info(skill: string)
/** Returns full node details: topic, tier, degree, stability, all links. */

ask graph chain(from: string, to: string)
/** Finds shortest path between two skills via BFS. */

ask graph list(topicFilter?: string, tier?: string)
/** Lists all skills with optional topic/tier filtering. */

ask graph topics()
/** Lists all topic clusters in the skill graph. */

# Global Options (all commands)
ask [...] --json
/** Output machine-parseable JSON with CallResult envelope. */

ask [...] --robot | --agent-mode | -r
/** Enable AI-friendly mode: fuzzy matching, helpful corrections, verbose guidance. */

ask [...] --trace-id <id>
/** Inject trace ID for distributed log correlation. */
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
| **CA7** | Graph Navigation | `ask graph related skill-builder --json` | Returns related skills with weights and topics. |
| **CA8** | Graph Search | `ask graph find security --tier stable` | Returns matching stable-tier security skills. |
| **CA9** | Graph Pathfinding | `ask graph chain skill-creator skill-installer` | Returns shortest path between skills. |
| **CA10** | Agent Next Steps | `ask graph info <skill> --json` | `metadata.next_steps` includes related commands. |
| **CA11** | Robot Mode Fuzzy | `ask skill list --robot` | Corrects to `ask skills list` with guidance. |
| **CA12** | Robot Mode Correction | `ask skills ls --robot --json` | `metadata.correction_note` explains the fix. |
| **CA13** | Helpful Errors | `ask invalid-command` | Error includes similar valid commands + examples. |

## Robot Mode (AI Agent Interface)

The CLI includes a dedicated **Robot Mode** (`--robot`, `--agent-mode`, `-r`) designed for AI coding agents.

### Philosophy

- **Honor clear intent:** When the agent's intent is legible but syntax is off, honor the command and provide guidance.
- **Educational errors:** When intent is unclear, provide detailed error messages with examples.
- **Structured output:** All responses include machine-parseable guidance via `metadata` fields.

### Fuzzy Matching

Robot mode enables fuzzy command matching:

| Typo | Correction | Guidance |
|------|------------|----------|
| `ask skill list` | `ask skills list` | "Use 'skills' for exact matching next time" |
| `ask skills ls` | `ask skills list` | "Use 'list' for exact matching next time" |
| `ask graph search X` | `ask graph find X` | "Use 'find' for exact matching next time" |
| `ask eval benchmark` | `ask evals benchmark` | "Use 'evals' for exact matching next time" |

### Error Message Format

When a command cannot be parsed (even with fuzzy matching):

```
❌ Unknown topic: 'invalid-topic'

💡 Did you mean 'ask skills'?
   Valid topics: repo, skills, plugins, evals, graph

📚 Examples:
   • ask skills list
   • ask skills audit backend/cli-spec --level strict
   • ask graph find security
```

### JSON Output with Corrections

```json
{
  "status": "success",
  "metadata": {
    "correction_note": "🤖 Robot mode: Interpreting 'skill' as 'skills' 💡 Tip: Use 'skills' for exact matching next time.",
    "next_steps": ["ask skills audit backend/cli-spec --level strict"]
  },
  "data": { ... }
}
```

## Definition of Done
- [ ] CLI handles `SIGINT` (Ctrl+C) gracefully with clean exit.
- [ ] Non-interactive mode (non-TTY) disables all spinners and prompts.
- [ ] Redaction filter passes all 8+ standard project secret patterns.
- [ ] `ask --help` provides TS-style signatures for all commands.
- [ ] Automated tests cover all `CA1` through `CA6` scenarios.
