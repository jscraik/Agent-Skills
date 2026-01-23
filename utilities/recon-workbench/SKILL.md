---
name: recon-workbench
description: "Analyze and report authorized evidence using Recon Workbench workflows. Use when running recon/rwb CLI commands, planning probe runs, or summarizing evidence-backed findings for macOS, iOS, web apps, or OSS repos."
---

# Recon Workbench (rwb)

**Recon Workbench** is a production-grade forensic evidence collection platform with policy-driven authorization, comprehensive validation, and supply chain integrity.

Answer with sections titled exactly: **Outputs** and **Procedure** (include authorization notes).

## When to use
- Running Recon Workbench CLI flows (`recon` or `uv run python -m rwb`)
- Planning or executing probe sets for authorized targets
- Summarizing evidence-backed findings and reports with artifact citations

## Compliance
- Follow `docs/agents/scope-safety.md`, `docs/agents/cli.md`, `docs/agents/dev-workflow.md`, and `docs/agents/ai-governance.md`
- Follow `AGENTS.md` and linked agent docs under `docs/agents/`
- Use `docs/reference/GOLD_STANDARD.md` for compliance gates
- Apply `docs/reference/AUTHORIZATION_CHECKLIST.md` before any run
- Apply `docs/reference/DATA_HANDLING.md` for redaction/retention
- Evidence-only claims: every finding must cite an artifact path under `data/runs/...`

## Purpose

Create or evolve a unified, controlled interrogation workflow that: (1) authorizes targets, (2) plans probes, (3) collects deterministic artifacts, (4) generates evidence-backed findings, and (5) validates integrity with SHA256 manifests.

## Philosophy

- **Evidence over inference**: If you cannot cite an artifact, mark it as a hypothesis
- **Least privilege**: Start with static inventory, escalate only when justified
- **Safety first**: No circumvention, no DRM bypass, no private user data access
- **Decision-ready outputs**: Minimize noise, maximize traceability
- **Explain escalations**: Document the why behind each escalation step

## Pre-action Questions

Before building or inspecting, clarify:

1. **Authorization**: Do we have explicit permission to analyze the target?
2. **Target type**: macOS app, iOS Simulator/device, web app, or OSS repo?
3. **Goal**: Inventory, behavior map, API surface, regression diff, or patch plan?
4. **Evidence outputs**: What artifacts are required (JSON schemas, reports, traces)?
5. **Escalation limit**: Maximum allowed level (read_only < instrumentation < escalation)?

## Core Constraints (Non-Negotiable)

- **No circumvention**: No DRM bypass, no cracking, no private data access
- **Evidence-only**: Every finding must cite an artifact path under `data/runs/...`
- **Observation-first**: Prefer static analysis; use dynamic only when authorized
- **Authorized tools only**: For deeper visibility, request debug builds and use LLDB/Instruments/logs
- **Web/React caution**: Component inspection only on authorized apps with documented permission
- **Redact by default**: Scrub secrets from logs, snapshots, and reports

## CLI Commands (recon/rwb)

Primary entrypoint from repo root: `uv run python -m rwb <command>`.
Secondary wrapper: `./recon <command>` (same subcommands).
Command names below use `recon` for brevity; substitute the primary entrypoint when running.

Core commands (see `docs/reference/CLI_REFERENCE.md` for flags):

| Command | Purpose |
|---------|---------|
| `recon doctor` | Check toolchain readiness (use `--json` for machine output) |
| `recon setup` | Validate required tooling presence |
| `recon init` | Register a target and locator |
| `recon plan` | Dry-run planner (requires `--probes` or `--probe-set`) |
| `recon run` | Execute probes (requires `--write --exec --confirm-run`; optional `--parallel N`) |
| `recon diff` | Compare baseline vs stimulus runs |
| `recon summarize` | Generate findings.json from artifacts |
| `recon report` | Compile report.md and report.json |
| `recon prune` | Delete old sessions (requires `--write --confirm-prune`) |
| `recon export` | Export a run as a portable evidence bundle |
| `recon import` | Import evidence bundle from ZIP |
| `recon mcp-serve` | Start MCP server for AI agent integration |

## Target Kinds

| Kind | Description | Example Locator |
|------|-------------|-----------------|
| `macos-app` | macOS applications (.app bundles) | `/Applications/MyApp.app` |
| `ios-sim` | iOS Simulator apps | `com.example.MyApp` (bundle ID) |
| `ios-device` | Physical iOS devices | `UDID` or device serial |
| `web-app` | Web applications | `https://example.com` |
| `oss-repo` | Open source repositories | `owner/repo` or git URL |

## Probe Sets

Predefined probe sets live in `probes/catalog.json`.
Common sets (not exhaustive):

- `macos-baseline`, `macos-objc-static`, `macos-debug`, `macos-accessibility`
- `ios-baseline`, `ios-objc-static`, `ios-debug`, `ios-smoke`
- `ios-diagnose`, `ios-device-diagnose`, `ios-sim-diagnose-pack`, `ios-device-diagnose-pack`
- `web-baseline`
- `oss-baseline`, `oss-full`

## Escalation Levels

- **read_only**: Static analysis, no code execution
- **instrumentation**: Log capture, tracing, non-invasive monitoring
- **escalation**: Debug builds, LLDB, dynamic analysis (requires explicit authorization)

## Scope Configuration

Create `scope.yaml` to set organizational defaults:

```yaml
# Disallow dangerous probes
disallowed_probes:
  - "debug.lldb_backtrace"
  - "ios.device_diagnose"

# Limit escalation level
max_escalation_level: "instrumentation"  # read_only < instrumentation < escalation

# Require authorization
require_authorization: true
```

## Inputs

- `target_id`: Unique identifier for the target
- `target_kind`: One of macos-app, ios-sim, ios-device, web-app, oss-repo
- `target_locator`: Path, URL, bundle ID, or repo identifier
- `probe_set`: Predefined probe set or custom probe list
- `run_dir`: Output directory for artifacts

## Outputs

**Structure**: `data/runs/<target>/<session>/<run>/`
- `raw/` - Probe artifacts (logs, dumps, traces, HARs)
- `manifest.json` - SHA256 hashes for integrity verification
- `derived/findings.json` - Schema-valid findings with evidence citations; include `schema_version`
- `derived/report.md` - Human-readable summary with artifact paths
- `derived/report.json` - Machine-readable report (when generated); include `schema_version` when schema-bound

## Procedure

### 1) Check Toolchain

```bash
uv run python -m rwb doctor --json
```

### 2) Initialize Target

```bash
uv run python -m rwb init myapp --kind macos-app --locator "/Applications/MyApp.app"
```

### 3) Generate Probe Plan

```bash
uv run python -m rwb plan myapp --type baseline --probe-set macos-baseline --json
```

### 4) Execute Probes (explicit consent required)

```bash
uv run python -m rwb run myapp --type baseline --probe-set macos-baseline --write --exec --confirm-run
```

### 5) Generate Findings

```bash
uv run python -m rwb summarize myapp --run baseline_123456 --json
```

### 6) Compile Report

```bash
uv run python -m rwb report myapp --json
```

## Validation

Fail fast: stop at the first failed validation gate, fix the issue, and re-run the failed check before proceeding.

```bash
# Validate probe catalog
python scripts/validate_catalog.py --catalog probes/catalog.json

# Validate a manifest
python scripts/validate_manifest.py data/runs/myapp/manifest.json

# Validate evidence paths in findings
python scripts/validate_evidence.py data/runs/myapp/derived/findings.json data/runs/myapp/
```

## Escalation Ladder (Worst-Case Path)

1. **Static inventory** (safe, read-only)
2. **Baseline run** (minimal interaction)
3. **Stimulus run** (targeted action)
4. **Diff** (baseline vs stimulus)
5. **Advanced observation** (approved tools only; stop if protections block)

**Stop conditions**:
- Goals are met with evidence
- Further steps require circumvention or exceed authorization
- Signals flatten (no new findings across two successive probes)

## Evidence Discipline

- Every finding must cite one or more evidence paths
- Summaries must list commands used + artifact locations
- If evidence is insufficient, request additional probes rather than speculating
- Use `manifest.json` to verify artifact integrity in `data/runs/...`

## Build Mode (Tooling Design)

When creating or evolving the workbench:

- Design schemas in `schemas/` with JSON Schema validation
- Add probes to `probes/catalog.json` with target kinds and timeouts
- Implement probe scripts in `scripts/probes/`
- Define probe sets for common workflows
- Update `AGENTS.md` with agent instructions
- Add validation scripts to `scripts/validate_*.py`

## Inspect Mode (Evidence Collection)

When analyzing a target:

1. Confirm authorization and target type
2. Select appropriate probe set
3. Execute probes and collect artifacts
4. Generate findings with evidence citations
5. Validate all artifacts and evidence paths
6. Produce report with artifact links

## Variation Rules

- Vary probe depth by authorization level and target risk profile
- Vary artifact collection based on target type (Apple, web, OSS) and goal
- Avoid repeating the same probe sequence across unrelated targets
- Prefer different variations when signals flatten

## Empowerment Principles

- **Operators**: Explicit stop conditions and safe rollback options
- **Teams**: Multiple probe paths when trade-offs exist
- **Stakeholders**: Clear evidence links and decision-ready summaries
- **Reviewers**: Direct artifact pointers for verification

## Anti-Patterns to Avoid

- Acting without explicit authorization or documented scope
- Skipping evidence capture while reporting conclusions
- Using intrusive probes when static inventory suffices
- Escalating by default instead of justifying each step
- Treating unknowns as confirmed facts
- Relying on inferred behavior without artifacts

## Example Prompts

- "Run a baseline reconnaissance on this macOS app and generate findings"
- "Design a probe set for React web app component inspection"
- "Validate the evidence paths in this findings.json"
- "Create an authorization artifact for this iOS Simulator target"
- "Generate a SHA256 manifest for this run directory"

## Remember

The agent is capable of extraordinary work in this domain. These guidelines unlock that potential—they don't constrain it.
Use judgment, adapt to context, and push boundaries when appropriate.

## Resources

### Documentation

- `README.md` - Project overview and quickstart
- `docs/reference/GOLD_STANDARD.md` - Gold Industry Standard compliance
- `AGENTS.md` - Agent instructions and workflows
- `docs/guides/SECURITY.md` - Security policy and vulnerability reporting
- `config/scope.example.yaml` - Scope configuration template

### Schemas

- `schemas/authorization.schema.json` - Authorization artifact structure
- `schemas/probe-plan.v2.schema.json` - Probe plan validation
- `schemas/findings.v2.schema.json` - Findings structure
- `schemas/manifest.v2.schema.json` - Integrity manifest structure

### Probe Catalog

- `probes/catalog.json` - All available probes and probe sets

### Validation Scripts

- `scripts/validate_catalog.py` - Validate probe catalog
- `scripts/validate_manifest.py` - Validate integrity manifest
- `scripts/validate_evidence.py` - Validate evidence paths in findings

### MCP Integration

- `scripts/mcp_server.py` - MCP server for AI agent integration

## Constraints
- Redact secrets/PII by default.
- Avoid destructive operations without explicit user direction.

## Anti-patterns
- Avoid vague guidance without concrete steps.
- Do not invent results or commands.
- Do not add features outside the agreed scope.
