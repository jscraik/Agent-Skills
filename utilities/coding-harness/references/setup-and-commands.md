# Coding Harness setup and command reference

## Table of Contents
- [Prerequisites](#prerequisites)
- [Command truth source](#command-truth-source)
- [Install modes](#install-modes)
- [Bootstrap workflow](#bootstrap-workflow)
- [Abbreviations](#abbreviations)
- [Metadata](#metadata)
- [Invariants](#invariants)
- [States](#states)
- [Transition Table (Canonical)](#transition-table-canonical)
- [Update workflow for existing repos](#update-workflow-for-existing-repos)
- [Error Handling](#error-handling)
- [Idempotency](#idempotency)
- [Execution Modes](#execution-modes)
- [Dry-Run Simulation](#dry-run-simulation)
- [Observability Logs](#observability-logs)
- [Validation Checklist](#validation-checklist)
- [Executor pseudocode](#executor-pseudocode)
- [Validation ladder](#validation-ladder)
- [environment.toml action sync behavior](#environmenttoml-action-sync-behavior)
- [Command map](#command-map)
- [Capability boundaries](#capability-boundaries)

## Prerequisites

- Node.js `>=24.0.0`
- `pnpm` (repo package manager)
- Repository write access for `harness init` template changes
- For remote GitHub checks, a valid token (GitHub App JWT is preferred when verifying App installation state)

## Command truth source

Prefer runtime command help over stale prose snapshots:

```bash
harness --help
```

If harness is not installed globally in the current shell, use:

```bash
pnpm exec tsx src/cli.ts --help
```

## Install modes

### Global npm install (required for generated preflight)

```bash
npm install -g @brainwav/coding-harness
harness --help
```

Recommended managed install:

```bash
mise install -g npm:@brainwav/coding-harness
```

Required private package auth wiring:

```bash
export NPM_TOKEN=<token>
# CircleCI project settings -> Environment Variables:
#   NPM_TOKEN
```

### Project-local source CLI (only for coding-harness development)

Use this only when developing inside the `coding-harness` source repository itself.
Generated `scripts/check-environment.sh` in consumer repositories does not fall back
to `pnpm exec tsx src/cli.ts ...`; it requires the global `harness` binary from npm.

## Bootstrap workflow

1. Install dependencies:

## Abbreviations
| Abbr | Meaning |
| --- | --- |
| `S` | state |
| `E` | event |
| `G` | guard |
| `A` | action |
| `N` | next state |

## Metadata
| Field | Value |
| --- | --- |
| `owner` | `repo-maintainers` |
| `max_duration` | `30m` |
| `escalation` | `open blocker issue + page on-call maintainer` |

## Invariants
- Every transition table row preserves canonical `S | E | G | A | N` semantics.
- Terminal states emit deterministic machine-readable outcomes (`DONE`, `FAIL`, or `BLOCKED`).

## States
```txt
S0 (non-terminal)
DONE (terminal)
FAIL (terminal)
BLOCKED (terminal)
```

## Transition Table (Canonical)
`S | E | G | A | N`

### State machine

```txt
B0 PREFLIGHT -> B1 DEPS -> B2 INIT_PREVIEW -> B3 INIT_APPLY -> B4 VALIDATE -> B5 READY
     |             |            |              |
     +-----------> BX FAIL <----+--------------+
```

### Transition table (`S | E | G | A | N`)

| S | E | G | A | N |
| --- | --- | --- | --- | --- |
| `B0 PREFLIGHT` | `preflight_ok` | preflight script passes | `bash scripts/codex-preflight.sh --stack auto --mode required` | `B1 DEPS` |
| `B1 DEPS` | `deps_installed` | `pnpm` available | `pnpm install` | `B2 INIT_PREVIEW` |
| `B2 INIT_PREVIEW` | `preview_ok` | dry-run exits clean | `harness init --dry-run` | `B3 INIT_APPLY` |
| `B3 INIT_APPLY` | `init_applied` | templates generated | `harness init` | `B4 VALIDATE` |
| `B4 VALIDATE` | `checks_pass` | baseline gate passes | `pnpm check` and optional `harness verify-coderabbit` | `B5 READY` |
| `B*` | `error` | any guard fails | capture blocker + stop | `BX FAIL` |

Expected scaffold lane in `B3`:
- `.coderabbit.yaml`
- `.github/workflows/pr-pipeline.yml`

## Update workflow for existing repos

Routine existing-install upgrades now use `harness upgrade`, not `harness init --update`.
Reserve `harness init --update` for re-scaffolding missing tracked baseline files.

### State machine

```txt
U0 CHECK -> U1 PREVIEW -> U2 APPLY -> U3 VALIDATE -> U4 DONE
   |          |           |             |
   |          +-------> U1R RESCAFFOLD -+
   +-----------------> UX FAIL <--------+
```

### Transition table (`S | E | G | A | N`)

| S | E | G | A | N |
| --- | --- | --- | --- | --- |
| `U0 CHECK` | `updates_found` | update check runs | `harness init --check-updates` | `U1 PREVIEW` |
| `U0 CHECK` | `legacy_manifest` | old restore manifest is missing `ciProvider` but provider can be inferred | auto-repair during `harness init --check-updates` | `U1 PREVIEW` |
| `U1 PREVIEW` | `preview_ok` | dry-run output reviewed for routine upgrade | `harness upgrade --dry-run` | `U2 APPLY` |
| `U1 PREVIEW` | `tracked_baseline_missing` | tracked scaffold files are missing and need re-scaffold | `harness init --dry-run --update` | `U1R RESCAFFOLD` |
| `U1R RESCAFFOLD` | `re_scaffold_ok` | re-scaffold preview accepted | `harness init --update` (or `--interactive`) | `U3 VALIDATE` |
| `U2 APPLY` | `apply_ok` | selected routine upgrade strategy confirmed | `harness upgrade` | `U3 VALIDATE` |
| `U3 VALIDATE` | `checks_pass` | validation ladder passes | run `pnpm check` (+ deep gate if needed) | `U4 DONE` |
| `U*` | `migration_or_rollback` | contract transition needed | `harness init --migrate` or `harness init --rollback` | `U0 CHECK` |
| `U*` | `error` | any guard fails | capture blocker + stop | `UX FAIL` |

## Error Handling
- `VALIDATION_ERROR`: invalid command invocation or malformed workflow input.
- `BLOCKED_DEPENDENCY`: missing binaries/auth/dependencies required by guards.
- `POLICY_FAIL`: required validation/policy gates fail.
- `SYSTEM_ERROR`: runtime/process failures.

## Idempotency
- Key: `<lane>|<repo>|<event>|<target_state>`.
- Re-running preview and validate steps must be side-effect free.
- Apply steps should be replay-safe with guard checks.

## Execution Modes
- `STRICT`: stop on first violation/failure.
- `ADVISORY`: collect warnings and continue where safe.

## Dry-Run Simulation
- No file mutations or external writes; no side effects.
- Deterministic transition trace output based on guard evaluation.

## Observability Logs
`workflow_id, transition_code, from_state, to_state, correlation_id, result`

## Validation Checklist
- every non-terminal state has >=1 outbound transition
- deterministic `(S,E)` handling
- failure paths route to `FAIL`/`BLOCKED`
- terminal states (`B5 READY`, `U4 DONE`) have no outbound transitions

## Executor pseudocode

```txt
run bootstrap or update lane
for each transition row, execute action when guard is true
stop on first error transition and emit unblock guidance
```

## Validation ladder

Baseline gate:

```bash
pnpm check
```

Deep gate (when runtime behavior, contract behavior, or artifact handling changed):

```bash
pnpm test:deep
```

Situational governance checks:

```bash
harness check-authz --contract harness.contract.json --repo <owner/repo> --branch <branch>
harness check-environment --contract harness.contract.json --attestation artifacts/check-environment-attestation.json
harness docs-gate --mode advisory --json
harness tooling-audit --path <directory> --format table
```

## environment.toml action sync behavior

`harness init` generates `.codex/environments/environment.toml` with:

- Setup script block using the detected package manager.
- Four canonical actions: `Tools`, `Run`, `Debug`, `Test`.
- Dynamic per-script action blocks (for each `package.json` script), with icon inference:
  - `tool`
  - `run`
  - `debug`
  - `test`

Important constraints:

- Auto-update is safe by default only for harness-autogenerated files.
- Existing custom/non-autogenerated environment files should be treated as user-owned and not silently overwritten.
- Missing `run` / `debug` / `test` scripts get explicit failing commands to prevent false success.

## Command map

### Setup and governance

- `harness init`
- `harness init --check-updates`
- `harness upgrade --dry-run`
- `harness upgrade`
- `harness init --update`
- `harness init --migrate`
- `harness init --rollback`
- `harness branch-protect`
- `harness verify-coderabbit`
- `harness check-authz`
- `harness check-environment`
- `harness docs-gate`
- `harness org-audit`
- `harness tooling-audit`
- `harness preset`
- `harness ci-migrate`

### Risk and policy gates

- `harness risk-tier`
- `harness policy-gate` (alias: `harness risk-policy-gate`)
- `harness preflight-gate`
- `harness diff-budget`
- `harness review-gate`
- `harness evidence-verify`
- `harness silent-error`
- `harness observability-gate`
- `harness drift-gate`
- `harness pr-template-gate`
- `harness license-gate`

### Documentation and planning hygiene

- `harness gardener`
- `harness brainstorm-gate`
- `harness plan-gate`
- `harness prompt-gate`
- `harness blast-radius`
- `harness memory-gate`

### Context and remediation loops

- `harness context`
- `harness search`
- `harness index-context`
- `harness context-health`
- `harness remediate`
- `harness replay`

### Pilot and operations

- `harness gap-case`
- `harness pilot-evaluate`
- `harness pilot-rollback`
- `harness automation-run`
- `harness simulate`
- `harness ui:fast`
- `harness ui:verify`
- `harness ui:explore`

### Intake and workflow governance

- `harness linear`
- `harness linear-gate`
- `harness workflow-generate`

## Capability boundaries

Harness can:

- Scaffold governance templates and maintain them over time.
- Enforce policy checks and report structured pass/fail outcomes.
- Verify expected repository setup (including CodeRabbit config, ruleset checks, and npmrc guidance).
- Generate Codex environment action blocks from live project scripts.

Harness cannot:

- Create or rotate GitHub credentials/tokens for you.
- Replace repository-specific engineering judgment or business logic testing.
- Bypass required checks, rulesets, or review independence policies.
- Safely overwrite user-customized non-autogenerated environment templates without explicit direction.
