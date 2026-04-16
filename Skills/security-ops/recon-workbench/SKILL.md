---
name: recon-workbench
description: Run authorized, evidence-backed Recon Workbench (rwb) workflows (doctor/authorize/plan/run/summarize/manifest/validate/reconcile) and produce evidence-cited findings. Use when interrogating macOS/iOS, web/React, or OSS targets under explicit scope/permission.
metadata:
  skill-type: runbook
---

# Recon Workbench (rwb)

Recon Workbench is a CLI-first interrogation platform. It is designed to produce
**evidence-backed** findings under explicit authorization, with deterministic
artifacts and validation.

When you respond while this skill is active, answer with sections titled exactly:
**Outputs** and **Procedure** (and include authorization notes).

## Table of Contents
- [Standards snapshot](#standards-snapshot-march-2026)
- [Scope and triggers](#scope-and-triggers)
- [Philosophy](#philosophy)
- [Constraints](#constraints-non-negotiable)
- [Compliance](#compliance-recon-workbench-repo)
- [Entrypoints](#entrypoints-recon-workbench-repo)
- [Target kinds](#target-kinds)
- [Probe Sets](#probe-sets)
- [Escalation Levels](#escalation-levels)
- [Scope Configuration](#scope-configuration)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Procedure](#procedure)
- [Validation](#validation)
- [Escalation Ladder](#escalation-ladder-worst-case-path)
- [Evidence Discipline](#evidence-discipline)
- [Build Mode](#build-mode-tooling-design)
- [Inspect Mode](#inspect-mode-evidence-collection)
- [Variation Rules](#variation-rules)
- [Empowerment Principles](#empowerment-principles)
- [Anti-Patterns to Avoid](#anti-patterns-to-avoid)
- [Examples](#examples)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Remember](#remember)

## Standards snapshot (March 2026)
- Authorization and scope evidence are mandatory before any target-specific interrogation.
- Treat run artifacts and evidence paths as the source of truth; uncited claims are hypotheses.
- Start read-only, escalate only with explicit justification, and stop on circumvention pressure.
- Keep outputs deterministic, redact sensitive material by default, and validate findings before summarizing them.

## When to use
- Running rwb CLI flows (`doctor`, `authorize`, `plan`, `run`, `summarize`, `manifest`, `validate`, `reconcile`).
- Designing/updating probe catalogs, schemas, or validation scripts.
- Producing evidence-backed findings/reports with artifact citations (no speculation).
- If the target is a web app and source is unavailable/minified, use `web-app-interrogate`.

## Philosophy
- **Evidence over inference**: if you can’t cite an artifact, label it a hypothesis.
- **Least privilege**: start static/read-only, escalate only when justified and allowed.
- **Safety first**: stop on unclear authorization, scope violations, or circumvention pressure.

## Constraints (non-negotiable)
- **Authorization required** before any target-specific interrogation.
- **Evidence-only claims**: every claim must cite an artifact path under `runs/...`.
- **No circumvention**: no DRM bypass, no cracking, no private user data access.
- **Least privilege**: start read-only; escalate only when justified and permitted.
- **Redact by default**: scrub secrets from logs, HARs, screenshots, and reports.

## Compliance (Recon Workbench repo)
When operating inside `~/dev/recon-workbench`, follow:
- `Docs/agents/*` (start at `Docs/agents/cli.md`)
- `docs/reference/GOLD_STANDARD.md`
- `docs/reference/AUTHORIZATION_CHECKLIST.md`
- `docs/reference/DATA_HANDLING.md`

## Entrypoints (Recon Workbench repo)
Prefer running inside the repo via `mise` to ensure `uv`, Python, and Node are correct:

```bash
mise exec -- uv run --python 3.12 python -m rwb <command> [args...]
```

If `uv` is already on PATH, `uv run --python 3.12 python -m rwb ...` is equivalent.

Secondary/legacy wrapper:
- `./recon <command>` (shell wrapper around `Infrastructure/scripts/recon_cli.py`)

## Target kinds

| Kind | Description | Example Locator |
|------|-------------|-----------------|
| `macos-app` | macOS applications | `/Applications/MyApp.app` |
| `ios-sim` | iOS Simulator apps | `com.example.MyApp` |
| `ios-device` | iOS device apps | `com.example.MyApp` |
| `web-app` | Web applications | `https://example.com` |
| `oss-repo` | Open source repositories | `owner/repo` or git URL |

## Probe Sets

Predefined probe sets live in `probes/catalog.json`.
Common sets (not exhaustive):

- `macos-baseline`, `macos-objc-static`, `macos-debug`, `macos-accessibility`
- `ios-baseline`, `ios-objc-static`, `ios-debug`, `ios-smoke`
- `ios-diagnose`, `ios-device-diagnose`, `ios-sim-diagnose-pack`, `ios-device-diagnose-pack`, `diagnose-pack`
- `web-baseline`, `web-stimulus`
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

# Limit escalation level
max_escalation_level: "instrumentation"  # read_only < instrumentation < escalation

# Require authorization
require_authorization: true
```

## Required inputs
## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.


- `target_id`: Unique identifier for the target
- `target_kind`: One of macos-app, ios-sim, ios-device, web-app, oss-repo
- `target_locator`: Path, URL, bundle ID, or repo identifier
- `probe_set` or `probes`: Predefined probe set or custom probe list
- `authorization`: Authorization artifact (required when scope enforces authorization)
- `run_dir`: Output directory for artifacts (use `runs/<target_id>/...`)

## Deliverables
**Structure**: `runs/<target>/<session>/<run>/`
- `raw/` - Probe artifacts (logs, dumps, traces, HARs)
- `manifest.json` - SHA256 hashes for integrity verification
- `derived/findings.json` - Schema-valid findings with evidence citations; include `schema_version`
- `derived/report.md` - Human-readable summary with artifact paths
- `derived/report.json` - Machine-readable report (when generated); include `schema_version` when schema-bound

Schema source of truth in the repo: `Infrastructure/config/schemas/` (e.g. `Infrastructure/config/schemas/findings.v2.schema.json`).

## Failure mode
If authorization is missing, scope is unclear, evidence validation fails, or the requested workflow would require circumvention or out-of-scope escalation, stop immediately, report the exact blocker, and refuse to manufacture findings.

## Procedure

### 1) Check Toolchain

```bash
mise exec -- uv run --python 3.12 python -m rwb doctor --json
```

### 2) Create Authorization (required by scope)

```bash
mise exec -- uv run --python 3.12 python -m rwb authorize \
  --target-id myapp \
  --target-kind macos-app \
  --target-locator "/Applications/MyApp.app" \
  --output authorization.json
```

### 3) Generate Probe Plan

```bash
mise exec -- uv run --python 3.12 python -m rwb plan \
  --target-id myapp \
  --target-kind macos-app \
  --target-locator "/Applications/MyApp.app" \
  --probe-set macos-baseline \
  --authorization authorization.json
```

### 4) Execute Probes

```bash
mise exec -- uv run --python 3.12 python -m rwb run \
  --plan-file probe-plan.json \
  --run-dir runs/myapp/
```

### 5) Generate Findings + Report

```bash
mise exec -- uv run --python 3.12 python -m rwb summarize \
  --run-dir runs/myapp/
```

### 6) Validate Artifacts (CLI-first)

```bash
mise exec -- uv run --python 3.12 python -m rwb validate \
  --catalog probes/catalog.json \
  --plan probe-plan.json

mise exec -- uv run --python 3.12 python -m rwb validate \
  --evidence runs/myapp/derived/findings.json \
  --run-dir runs/myapp
```

## Validation

Fail fast: stop at the first failed validation gate, fix it, then re-run the same gate.

```bash
# Validate probe catalog
python Infrastructure/scripts/validate_catalog.py --catalog probes/catalog.json

# Validate a manifest
python Infrastructure/scripts/validate_manifest.py runs/myapp/manifest.json

# Validate evidence paths in findings
python Infrastructure/scripts/validate_evidence.py runs/myapp/derived/findings.json runs/myapp/
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
- Redact HAR files before sharing and record redaction in the report
- Use `manifest.json` to verify artifact integrity in `data/runs/...` (or legacy `runs/...`)

## Build Mode (Tooling Design)

When creating or evolving the workbench:

- Design schemas in `Infrastructure/config/schemas/` with JSON Schema validation
- Add probes to `probes/catalog.json` (alias to `Infrastructure/config/probes/catalog.json`) with target kinds and timeouts
- Implement probe scripts in `Infrastructure/scripts/probes/`
- Define probe sets for common workflows
- Update `AGENTS.md` with agent instructions
- Add validation scripts to `Infrastructure/scripts/validate_*.py`

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

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.

## See Also
| Skill | When to use |
|---|---|
| [[security-best-practices]] | Turn recon findings into concrete secure-by-default implementation guidance |
| [[security-threat-model]] | Map recon evidence into trust boundaries, abuse paths, and mitigations |
| [[security-ownership-map]] | Connect the findings to code ownership and bus-factor risk |
| [[systematic-debugging]] | Debug confirmed runtime behavior after recon narrows the target surface |

**Topic map:** [[security-ops]]
