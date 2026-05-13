# Repo Surface Ownership

## Table of Contents

- [Purpose](#purpose)
- [Scope](#scope)
- [Classifications](#classifications)
- [Path Policy](#path-policy)
- [Unknown Ownership](#unknown-ownership)
- [Decision Tests](#decision-tests)
- [Allowlist Contract](#allowlist-contract)
- [Cleanup Rules](#cleanup-rules)
- [Validation](#validation)

## Purpose

Define how tracked repository surfaces are classified before cleanup, projection
changes, or runtime ownership decisions. This policy keeps source, generated
state, runtime output, fixtures, and historical evidence from competing as if
they had the same authority.

The governing rule:

```text
Every tracked file must be source, fixture, policy, reference, intentional
archive, or an explicitly owned generated/vendored surface. Everything else is
generated output, runtime state, historical artifact, unknown ownership, or a
cleanup candidate that needs evidence before action.
```

## Scope

First-slice inventory classification is tracked-files-only through `git
ls-files`. Untracked and runtime-state discovery is report-only future work until
policy rules and validation cover those paths.

This policy complements [Path Ownership Boundaries](/Docs/agents/14-path-ownership-boundaries.md):

- path ownership says where humans may edit;
- repo surface ownership says how the repository classifies tracked surfaces
  before cleanup, allowlisting, or retention decisions.

## Classifications

| Classification        | Meaning                                                                                         | Default Action                                              |
| --------------------- | ----------------------------------------------------------------------------------------------- | ----------------------------------------------------------- |
| `source`              | Authored product, plugin, workflow, tooling, or docs content.                                   | Track and edit in canonical source paths.                   |
| `fixture`             | Stable test or validation input intentionally checked in.                                       | Track only with a clear consumer and reason.                |
| `policy`              | Governance, routing, validation, or ownership rule.                                             | Track and keep linked from the relevant front door.         |
| `reference`           | Supporting context loaded through progressive disclosure.                                       | Track when indexed and intentionally reachable.             |
| `intentional_archive` | Historical material retained with an index, reason, and retention boundary.                     | Track only with explicit retention reason.                  |
| `vendored_snapshot`   | Third-party, OpenAI, plugin, or runtime mirror retained as a snapshot.                          | Track only with owner and update command.                   |
| `generated_tracked`   | Reproducible generated output intentionally tracked as a distribution or compatibility surface. | Track only with generator, source inputs, and verification. |
| `generated_ignored`   | Reproducible generated output that should not be tracked.                                       | Ignore or remove from git after verification.               |
| `runtime_state`       | Local state written by tools, runtimes, harnesses, or automations.                              | Do not track unless converted into a documented fixture.    |
| `historical_artifact` | Run output, dated evidence, logs, event streams, or generated reports.                          | Ignore by default; preserve summaries or fixtures only.     |
| `unknown`             | Ownership cannot be proven from policy, references, or live readers.                            | Block cleanup and strict validation until resolved.         |

## Path Policy

| Path Pattern                                          | Default Classification      | Required Behavior                                                                |
| ----------------------------------------------------- | --------------------------- | -------------------------------------------------------------------------------- |
| `Skills/**`                                           | `source`                    | Canonical first-party skill source. Track and edit here.                         |
| `Plugins/*/skills/**`                                 | `source`                    | Canonical plugin-owned skill source when authored by this repo.                  |
| `Plugins/*/.codex-plugin/**`                          | `source` or `policy`        | Track plugin metadata and package policy.                                        |
| `.agents/skills/**`                                   | `generated_tracked`         | Generated command handles. Do not hand-edit; regenerate through sync.            |
| `.skillsets/**`                                       | `generated_tracked`         | Generated rooted manifests and command-surface projections. Do not hand-edit; regenerate through skills sync. |
| `Plugins/cache/**`                                    | `generated_ignored`         | Runtime/plugin cache. Never newly track.                                         |
| `Infrastructure/scripts/**`                           | `source`                    | Tooling source. Track and validate with the relevant focused tests.              |
| `Infrastructure/references/**`                        | `reference`                 | Preserve when indexed and intentionally referenced.                              |
| `Infrastructure/references/deferred-skill-context/**` | `reference`                 | Preserve behind indexes; do not load by default.                                 |
| `Infrastructure/artifacts/**`                         | `historical_artifact`       | Ignore by default; track only allowlisted fixtures, summaries, or indexes.       |
| `artifacts/**`                                        | `historical_artifact`       | Generated evidence. Ignore by default; keep summaries rather than event streams. |
| `.harness/*.db`                                       | `runtime_state` by default  | Do not track unless moved under fixtures and documented.                         |
| `.harness/backups/**`                                 | `runtime_state`             | Do not track.                                                                    |
| `.harness/ci-migrate-snapshots/**`                    | `historical_artifact`       | Ignore by default; track only an allowlisted fixture or retained summary.        |
| `.harness/core/**`                                    | `policy`                    | Track repo invariants and operating rules.                                       |
| `.harness/knowledge/**`                               | `reference` or `policy`     | Preserve Project Brain linkage when intentionally indexed.                       |
| `.harness/decisions/**`                               | `policy`                    | Preserve decision records as primary execution authority when intentionally indexed. |
| `.harness/linear/**`                                  | `policy`                    | Track approved execution routing and Linear destination decisions.               |
| `.harness/reframes/**`                                | `policy`                    | Track selected reframe routes, rollback rules, and anti-regression constraints. |
| `.harness/refactors/**`                               | `policy`                    | Legacy name for selected reframe routes; preserve existing artifacts but prefer `.harness/reframes/**` for new work. |
| `.harness/ideate/**`                                  | `reference`                 | Track durable folded HE ideation artifacts.                                      |
| `.harness/brainstorm/**`                              | `policy`                    | Track durable HE brainstorm artifacts as primary execution authority.            |
| `.harness/specs/**`                                   | `reference`                 | Track durable HE spec artifacts.                                                 |
| `.harness/plan/**`                                    | `reference`                 | Track durable HE plan artifacts.                                                 |
| `.harness/solutions/**`                               | `policy`                    | Track verified reusable solved-pattern captures owned by HE lifecycle policy.    |
| `.harness/features/**`                                | `reference`                 | Track curated repo intent and feature guardrails as secondary context.           |
| `.harness/strategy/**`                                | `reference`                 | Track strategy and moat rationale as secondary context.                          |
| `.harness/triage/**`                                  | `reference`                 | Track prioritization and discarded paths as secondary context.                   |
| `.harness/review/**`                                  | `reference`                 | Track curated review evidence as secondary context.                              |
| `.harness/memory/**`                                  | `reference`                 | Track repo-local learned fixes and recurring operational context.                |
| `.harness/quality/**`                                 | `policy`                    | Track governance scorecards and quality criteria.                                |
| `.harness/*.json`                                     | `policy` or `generated_tracked` | Track only when consumed by validators or Harness setup/restore flows.       |
| `.workouts/**`                                        | `fixture` or `source`       | Track workout harness source and stable fixtures.                                |
| `.skill-telemetry/**`                                 | `runtime_state`             | Do not track.                                                                    |
| `skills-system/**`                                    | ownership decision required | Decide vendored snapshot, generated mirror, or legacy cleanup candidate.         |
| `Infrastructure/Infrastructure/**`                    | `unknown` violation         | Treat duplicated path shape as suspicious until allowlisted with reason.         |

## Unknown Ownership

Unknown ownership is a blocker, not a delete signal.

When a path is `unknown`:

1. Do not delete, move, or rewrite it.
2. Check active source, tests, docs, generated handles, runtime readers, and
   deferred context indexes.
3. Record the owner, retention reason, fixture role, generator, or cleanup
   blocker.
4. Reclassify only after evidence exists.

Strict inventory mode must fail when non-allowlisted unknown ownership exists.

## Decision Tests

Use these tests before resolving known ambiguous surfaces.

| Surface                            | Candidate Classifications                                                  | Required Evidence                                                                                                                                                                                                                                                                                                       |
| ---------------------------------- | -------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.skillsets/**`                    | `generated_tracked`                                                        | Generated from `Skills/**`, `Plugins/**`, and generator code by rooted skills sync. Treat checked-in files as compatibility projections, not canonical source; validate freshness with handle/projection checks. |
| `.harness/*.db`                    | `runtime_state`, `fixture`, `unknown`                                      | If local harness or runtime commands write it, classify as runtime state. If tests read a stable DB, move or document it under fixtures. If no reader or fixture role is proven, keep it unknown.                                                                                                                       |
| `.harness/**/*.md`                 | `policy`, `reference`, `source`, `fixture`, `intentional_archive`, `unknown` | Track curated Markdown under documented roots only. Primary execution authority belongs to roots classified as policy above, especially `.harness/linear/**`, `.harness/reframes/**`, legacy `.harness/refactors/**`, `.harness/decisions/**`, `.harness/core/**`, `.harness/brainstorm/**`, and `.harness/solutions/**`; `.harness/specs/**`, `.harness/plan/**`, `.harness/ideate/**`, and `.harness/memory/**` remain reference unless an active workflow explicitly admits a selected document as authority. Strategy, triage, review, and feature docs remain secondary context unless admitted by the selected slice. Every tracked `.harness/**/*.md` file must have an explicit owner and classification before it is treated as source, fixture, policy, reference, or intentional archive. |
| `skills-system/**`                 | `vendored_snapshot`, `generated_tracked`, `historical_artifact`, `unknown` | If reproducible from an upstream or plugin update command, document the command. If active runtime readers consume it, document owner and reader. If only stale references remain, keep it as a cleanup candidate until reference scans pass.                                                                           |
| `Infrastructure/Infrastructure/**` | `historical_artifact`, `intentional_archive`, `unknown`                    | If no active source, runtime reader, or fixture depends on it, classify as historical artifact or cleanup candidate. If retained, require an allowlist reason explaining the duplicated path shape.                                                                                                                     |

## Allowlist Contract

Use allowlists to explain intentional exceptions, not to hide policy debt.

Canonical allowlist path:

```text
Infrastructure/policy/repo_surface_allowlist.json
```

The first-slice schema is:

```json
{
  "schema_version": 1,
  "entries": [
    {
      "id": "stable-exception-id",
      "match_type": "exact",
      "pattern": "path/or/prefix",
      "classification": "fixture",
      "reason": "why this exception is intentionally tracked",
      "owner": "owning area or person",
      "review_after": "YYYY-MM-DD"
    }
  ]
}
```

Rules:

- `match_type` must be `exact`, `glob`, or `prefix`.
- Regex matching is excluded from the first slice.
- `reason` must be non-empty.
- Each entry must include `expires` or `review_after`.
- Entries can downgrade a strict blocking finding to a warning only when the
  entry classification matches the classifier result.
- Matching precedence is deterministic: `exact`, then longest `prefix`, then
  longest `glob`, with ties sorted by `id`.
- The finding payload should report `allowlist_entry: null` or the matching
  allowlist entry `id`.

## Cleanup Rules

Cleanup is classification-first, never deletion-first.

Before a path can be marked `safe_to_delete`, evidence must show:

- zero active source references;
- zero runtime readers or projection dependencies;
- zero deferred-context references unless the material is moved behind an indexed
  reference;
- an explicit owner, allowlist, or retention decision.

Historical artifact cleanup should preserve:

- current summary reports;
- stable fixtures consumed by tests;
- indexed deferred context;
- intentional archives with a retention reason.

Historical artifact cleanup should reject:

- timestamped run logs with no fixture role;
- JSONL event streams with no retained summary;
- generated reports that can be reproduced;
- nested accidental copies with no owner.

## Validation

P0 policy verification:

```bash
rg 'source|fixture|historical_artifact|runtime_state|unknown' Docs/agents/15-repo-surface-ownership.md
rg '.skillsets|.harness|skills-system|Plugins/cache|Infrastructure/Infrastructure' Docs/agents/15-repo-surface-ownership.md
```

Later implementation slices should route machine validation through:

```bash
./bin/ask repo surface --json
./bin/ask repo surface --strict --json
```
