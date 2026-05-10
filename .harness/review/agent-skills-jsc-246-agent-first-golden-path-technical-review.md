---
schema_version: 1
artifact_id: agent-skills-jsc-246-agent-first-golden-path-technical-review
artifact_type: he-code-review
type: he-code-review
canonical_slug: agent-skills-jsc-246-agent-first-golden-path
title: Agent Skills JSC-246 Agent First Golden Path Technical Review
harness_stage: he-code-review
status: complete
date: 2026-05-09
origin: .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
reviewed_artifact: .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
traceability_required: true
linear_status: existing
linear_issue: JSC-246
linear_issue_url: https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden
linear_team: JSC
linear_workspace: Jscraik
linear_project: agent-skills
linear_milestone: Command surface and ask reliability
linear_parent_issue_title: "Build repo surface contract and agent capability control-plane golden paths"
review_result: approved_for_plan_with_residual_risks
---

# Agent Skills JSC-246 Agent First Golden Path Technical Review

## Review Verdict

Approved for `he-plan`.

The deepened spec is now strong enough to plan from. It keeps JSC-246 bounded to
the agent-first `ask` command loop and adds the missing pressure checks that
matter before implementation: a specific HE Gate Profile, a first-principles
check, live Linear delta classification, live evidence drift handling, negative
proof requirements, and an artifact naming/search rule that prevents duplicate
specs for the same active Linear slice.

No blocking review finding is open against the spec artifact.

## Scope Reviewed

Reviewed artifact:

- `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`

Source context:

- `.harness/linear/agent-skills-linear-plan.md`
- `.harness/refactors/agent-first-golden-path.md`
- `Docs/specs/2026-05-01-feat-agent-capability-control-plane-and-repo-surface-contract-spec.md`
- `Plugins/harness-engineering/skills/he-spec/SKILL.md`
- `Plugins/harness-engineering/references/gate-selection-contract.md`
- `Plugins/harness-engineering/references/first-principles-contract.md`
- `Plugins/harness-engineering/references/agent-native-compression-contract.md`
- `Plugins/harness-engineering/skills/he-spec/references/spec-artifact-contract.md`
- `Plugins/harness-engineering/references/linear-delta-capture-gate.md`

Live command evidence:

- `./bin/ask skills resolve he-spec --json --robot`
- `./bin/ask repo doctor --json --robot`
- `./bin/ask skills explain he-spec --json --robot`
- `./bin/ask skills prove he-spec --json --robot`
- `./bin/ask repo closeout --changed --json --robot`

## Linear Work Item Contract

`linear_status: existing`

| Field | Value |
| --- | --- |
| Linear issue | `JSC-246` |
| URL | https://linear.app/jscraik/issue/JSC-246/build-repo-surface-contract-and-agent-capability-control-plane-golden |
| Team | `JSC` |
| Workspace | `Jscraik` |
| Project | `agent-skills` |
| Project ID | `791c2f12-5ffb-4644-8421-f4216ac6d805` |
| Milestone | `Command surface and ask reliability` |
| Selected slice | `Agent First Golden Path` |
| Priority | `High` |
| Status at review refresh | `Todo` / unstarted |
| Required labels | `Roadmap: Next`, `Agent`, `Infra`, `Improvement` |
| Review route | Technical review of the HE spec artifact only |
| Linear mutation | None; this review did not create, update, close, or relabel Linear objects |

The review applies to the current spec artifact:

```text
.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md
```

It does not approve implementation of `JSC-174`, `JSC-230`, `JSC-231`,
`JSC-232`, `JSC-233`, `JSC-234`, `JSC-235`, `JSC-236`, `JSC-167`,
`JSC-169`, `JSC-171`, `JSC-172`, `JSC-173`, or `JSC-175`.

## Findings

No open blocking findings remain.

### Finding 0: Linear Delta Refresh Is Now Covered

Severity: High
Status: Fixed in spec

The spec now records the live Linear delta capture performed on `2026-05-09`.
This was necessary because the active `agent-skills` project contains tempting
adjacent work, especially `JSC-174` / `ask start` and active `JSC-230`
command-handle children, that could otherwise slip into JSC-246 under the
general banner of "agent-first golden path."

Evidence:

- `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`
  includes `## Linear Delta Capture Refresh`.
- The refresh confirms `JSC-246` remains `Todo`, high priority, in project
  `agent-skills`, milestone `Command surface and ask reliability`, with labels
  `Roadmap: Next`, `Agent`, `Infra`, and `Improvement`.
- The spec classifies `JSC-230` through `JSC-236` as out of scope for this
  spec, and classifies `JSC-167`, `JSC-169`, `JSC-171`, `JSC-172`, `JSC-173`,
  `JSC-174`, and `JSC-175` as candidate or adjacent slices that are not
  admitted.
- It explicitly calls out `JSC-174` / `ask start` as blocked inside JSC-246
  unless ablation proof and a later Linear Delta Capture Gate admit it.

Impact:

This closes the main scope loophole. `he-plan` can now use the existing
`repo doctor` first-truth path without silently expanding into a new public
first-contact command, commandable-skill-tree implementation, or output-profile
lane.

### Finding 1: Gate Profile Is Now Specific Enough

Severity: High
Status: Fixed in spec

The spec now records an architecture-sensitive gate profile instead of allowing
the work to drift into a broad `mixed` lifecycle review. The selected contracts
match the actual risk: command routing, proof language, diagnostic continuation,
docs compression, and closeout evidence.

Evidence:

- `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`
  includes `## HE Gate Profile`.
- The profile requires gate selection, first principles, agent-native
  compression, spec artifact, and Linear delta contracts.
- It explicitly skips plugin hooks, domain-model production, and security scan
  because the slice does not admit hook-enforced behavior, domain semantics,
  permissions, auth, secrets, sandboxing, dependencies, or external mutation.

Impact:

This prevents `he-plan` from loading every adjacent governance surface just
because the slice mentions agents, routing, proof, and Linear. The correct
planning posture is narrow architecture-sensitive proof, not maximal process.

### Finding 2: First-Principles Check Blocks Catalog/Cockpit Drift

Severity: High
Status: Fixed in spec

The spec now names the verified failure: agents can see many useful `ask`
surfaces but still need repo archaeology to know the first safe command, the
next command, and closure readiness. It rejects the assumption that a broader
command catalog, more docs, or a new cockpit command is automatically better.

Evidence:

- `## First-Principles Check` names the verified failure, fundamental
  constraint, challenged assumption, smallest mechanism, rejected analogy, and
  proof requirement.
- The selected mechanism is to harden the existing five-command loop:
  `repo doctor`, `skills improve`, `skills explain`, `skills prove`, and
  `repo closeout --changed`.

Impact:

This keeps JSC-246 aligned with the harness engineering philosophy: preserve
intent through execution with the smallest proof-producing mechanism. It also
prevents the plan from treating dashboards, catalogs, aliases, or docs as the
default answer.

### Finding 3: Negative Proof Requirements Close The False-Confidence Gap

Severity: High
Status: Fixed in spec

The spec now requires failure and refusal cases, not just happy-path command
examples. This is important because the risk in JSC-246 is false confidence:
commands exist, but their next-action, proof, fallback, or closeout semantics
could still be ambiguous.

Evidence:

- `## Negative Proof Requirements` requires cases for blocking sync vs advisory
  surface debt, fallback routing, ambiguous routing, missing handles,
  reachability-only proof, unrelated closeout churn, docs-only completion, and
  new command admission before ablation proof.
- The acceptance matrix already maps the same behavior through `SA3` through
  `SA18`.

Impact:

The next plan has to prove restraint and failure handling. That makes the
eventual implementation more production-grade because it verifies what the
control plane must not claim.

### Finding 4: Artifact Naming Rule Prevents Duplicate Active Specs

Severity: Medium  
Status: Fixed in spec

The spec now explains why it keeps the existing stable path rather than creating
a second dated spec for the same active JSC-246 slice. It also states the chain
keys future agents should search by.

Evidence:

- `## Agentic Search And Artifact Naming` records the current path,
  `canonical_slug`, `linear_issue`, and `date`.
- It forbids duplicate dated specs for the same active slice unless the Linear
  Delta Capture Gate admits a new execution slice or the artifact is
  intentionally superseded.
- It requires backlink preservation if a later dated rename is approved.

Impact:

This handles the dated Linear-style concern without creating artifact
duplication today. Future agent search remains grounded in frontmatter and
canonical slug rather than path naming alone.

### Finding 5: Live Evidence Drift Is No Longer A Hidden Acceptance Risk

Severity: Medium
Status: Fixed in spec

The live command evidence changed slightly between spec passes: repo-surface
diagnostic counts increased, the `he-spec` source revision moved to
`17b151a25`, and `repo closeout --changed` now reports a much larger unrelated
dirty worktree. The spec now explains which evidence is stable behavior and
which values are volatile snapshots.

Evidence:

- `## Deepening Refresh: Live Evidence Drift` records the latest command
  outcomes.
- The latest `repo doctor` result is still `blocking: false` with
  `./bin/ask repo surface --json --robot` selected as a diagnostic advisory.
- The latest `skills prove he-spec` result is still
  `reachable_without_outcome_proof`, with reachability and structural quality
  passing but outcome proof not run.
- The latest `repo closeout --changed` remains blocked by `sync_required` from
  unrelated dirty worktree state.
- The spec now states that numeric repo-surface counts are diagnostic snapshots,
  not acceptance thresholds.

Impact:

This prevents a brittle plan. The implementation should test command semantics:
blocking state, next-command class, fallback visibility, proof-level honesty,
and closeout isolation. It should not test incidental counts from a shared
worktree.

## Residual Risks

### Residual Risk 1: Live Closeout Is Still Noisy

`./bin/ask repo closeout --changed --json --robot` still blocks on
`sync_required` in the current worktree because unrelated HE/factory,
generated-artifact, media, and session-evidence files are dirty.

This is not a spec blocker. It is a planning constraint. `he-plan` must prove
closeout with controlled changed-file evidence, a temporary branch, or
helper-level fixtures.

### Residual Risk 2: Exact Routing Fixtures Need Live Registry Grounding

The spec correctly requires route-family assertions before exact-handle
assertions. `he-plan` must still decide the exact representative route fixture
set and resolve every exact expected handle through the live registry before
using it as acceptance evidence.

### Residual Risk 3: Docs Compression Can Still Be Over-Optimized

The spec requires docs compression plus fresh-agent metrics, but the plan must
avoid optimizing only for line count. The useful metric is whether an agent can
start from `repo doctor`, follow emitted commands, and reach ready-or-blocked
without docs archaeology.

## Validation Evidence

| Command | Result | Notes |
| --- | --- | --- |
| `./bin/ask skills resolve he-spec --json --robot` | pass | Resolved generated handle to canonical HE Spec source at source revision `17b151a25`. |
| `./bin/ask repo doctor --json --robot` | pass | Repo usable with non-blocking diagnostic debt; runtime budget and command handles pass; selected `repo surface` as diagnostic advisory. |
| `./bin/ask skills explain he-spec --json --robot` | pass | Shows canonical source, generated handle, rooted runtime projection, latent visibility, validation, and `skills proof` reachability command. |
| `./bin/ask skills prove he-spec --json --robot` | pass | Reachability and structural quality pass; `proof_status: reachable_without_outcome_proof`; outcome proof available but not run. |
| `./bin/ask repo closeout --changed --json --robot` | blocked | `sync_required` from unrelated dirty HE/factory/generated/session-evidence work; valid blocker evidence, not clean JSC-246 success proof. |
| `python3 Infrastructure/scripts/validation-and-linting/he_artifact_identity_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md` | pass | Spec artifact identity remains valid after deepening. |
| `python3 Infrastructure/scripts/validation-and-linting/he_frontmatter_safety_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md` | pass | Spec frontmatter remains parser-safe after deepening. |
| `python3 Infrastructure/scripts/validation-and-linting/he_linear_traceability_lint.py .harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md` | pass | Spec Linear traceability remains valid after deepening. |

## Review Decision

Proceed to `he-plan`.

The next plan must preserve these constraints:

- Keep `JSC-246` bounded to the agent-first golden path.
- Start with behavior characterization and fixtures, not docs rewrites.
- Treat the HE Gate Profile as architecture-sensitive, not broad `mixed`.
- Carry the first-principles check into sequencing and acceptance.
- Preserve the Linear Delta Capture Refresh: do not implement `JSC-174`,
  `JSC-230`, or related children through this slice without a later admitting
  gate.
- Treat live repo-surface counts as snapshots, not pass/fail thresholds.
- Include the negative proof cases as tests, fixtures, or blocked fixture gaps.
- Do not add a new command, alias, proof schema, promotion state, or lifecycle
  gate without ablation proof and explicit scope admission.
- Keep repo-surface debt advisory unless the relevant command reports a true
  blocker.
- Use controlled closeout evidence before closure.

## Evidence & Traceability Matrix

| Conclusion | Evidence type | Files / commands | Confidence | Why it matters |
| --- | --- | --- | --- | --- |
| The spec is ready for `he-plan`. | spec, review, validation | `.harness/specs/agent-skills-jsc-246-agent-first-golden-path-spec.md`; post-deepening artifact identity, frontmatter, and Linear traceability lints | High | The artifact is traceable, bounded, and now carries the risk and negative-proof detail needed for planning. |
| Live Linear deltas are classified and do not block planning. | Linear, spec | `## Linear Delta Capture Refresh`; live Linear issue and milestone fetches | High | Prevents adjacent `ask start`, command handles, bootstrap, and docs-test work from entering this slice by implication. |
| The correct risk profile is architecture-sensitive, not mixed. | spec, contract review | `## HE Gate Profile`; gate selection contract | High | Prevents broad lifecycle governance from expanding the slice. |
| First-principles discipline is now explicit. | spec, contract review | `## First-Principles Check`; first-principles contract | High | Blocks docs/catalog/cockpit additions that do not prevent the verified failure. |
| Volatile command counts are not acceptance thresholds. | command evidence, spec | `## Deepening Refresh: Live Evidence Drift`; `./bin/ask repo doctor --json --robot`; `./bin/ask repo closeout --changed --json --robot` | High | Keeps the plan focused on behavior semantics rather than stale snapshot values. |
| Negative proof is now part of acceptance. | spec | `## Negative Proof Requirements`; acceptance matrix `SA3`-`SA18` | High | Forces the plan to prove failure handling and non-claims, not only happy paths. |
| Artifact search is protected without creating a duplicate dated spec. | spec, artifact contract | `## Agentic Search And Artifact Naming`; spec artifact contract | Medium-high | Preserves traceability and avoids two active specs for the same JSC-246 slice. |
| Live closeout evidence remains a blocker scenario only. | command evidence | `./bin/ask repo closeout --changed --json --robot` | High | Prevents noisy worktree state from being mistaken for clean completion proof. |

## Linear Acceptance Traceability

| Linear issue | Acceptance IDs | Review coverage | Scope |
| --- | --- | --- | --- |
| `JSC-246` | SA1, SA2, SA16, SA18, SA20 | Gate profile, first-principles check, Linear delta refresh, live evidence drift, negative proof, artifact naming, validation evidence | Approved for `he-plan` with residual planning risks. |
| `JSC-246` | SA3-SA15, SA19, SA20 | Technical review readiness checklist | Ensures `he-plan` starts with behavior characterization, fixtures, and compression proof instead of docs-first or command-expansion work. |
| `JSC-246` | SA1, SA2, SA18 | Validation evidence | Confirms spec artifact identity, frontmatter safety, and Linear traceability pass after deepening. |
| `JSC-174` | SA14, SA16 | Scope guard only | Not admitted; `ask start` requires ablation proof and a later Linear Delta Capture Gate. |
| `JSC-230` and children | SA10, SA16 | Scope guard only | Not admitted; commandable skill-tree and handle-proof work remains outside this review. |
