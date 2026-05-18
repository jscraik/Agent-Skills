---
schema_version: 1
title: Agent Skills Kit Repository Intent
status: reviewed
date: 2026-05-07
repo: agent-skills
evidence_mode: live-repository-analysis
review_decisions:
  product_posture: local-control-plane-first
  proof_standard: outcome-proof-before-core-default-visible
  artifact_debt: quarantine-aggressively
---

# Agent Skills Kit Repository Intent

## Reading Contract

This is an intent document, not a generic architecture overview.

Use it to understand what this repository is trying to become, what future
agents should preserve, and where the system is already drifting. Every major
claim is separated into:

- **Hard evidence**: observed in code, config, docs, tests, or command output.
- **Interpretation**: a strong inference from multiple repo facts.
- **Speculation**: plausible strategic direction that still needs an explicit
  decision or operational proof.

The repo name used for this artifact is `agent-skills`.

# Review Decisions

The review loop on 2026-05-07 resolved the highest-impact strategic ambiguity:

- **Product posture**: local control plane first. Optimize around Jamie's
  Codex/harness reliability before broad portability or public packaging.
- **Proof standard**: outcome proof before a skill becomes core or
  default-visible. Reachability and structural audits are necessary but not
  sufficient.
- **Artifact debt**: quarantine aggressively. Historical/generated artifacts
  should be moved, untracked, or archived behind explicit indexes unless they
  are stable fixtures or intentionally retained references.

These are not cosmetic preferences. They should shape future scope decisions,
review severity, and merge blockers.

# Project Intent

Agent Skills Kit is trying to become a governed capability control plane for AI
coding agents. Its job is not merely to store prompts or skill files. Its job is
to make agent workflows authorable, discoverable, synchronizable, auditable, and
provable across canonical source, generated command surfaces, and runtime
installations.

**Hard evidence**

- `AGENTS.md` defines the repository as the canonical control plane for
  authoring, validating, discovering, and syncing Codex skills, operator docs,
  and agent workflows.
- `README.md` describes the product promise as teaching coding agents how work
  actually works, then proving they remembered.
- `UBIQUITOUS_LANGUAGE.md` defines canonical skill sources, runtime
  projections, generated command handles, user runtime links, plugin mirrors,
  and sync operations.
- `Docs/product/agent-capability-control-plane.md` names four outcomes:
  remember workflows, keep context small, prevent drift, and prove quality.
- `./bin/ask repo doctor --json --robot` exists and composes repo status,
  catalog parity, runtime budget, command-handle health, and repo surface
  diagnostics into one agent-facing decision.

**Interpretation**

The repository is strongest when it behaves like an operating layer for agents:
small command contracts up front, deeper evidence behind them, and generated
runtime surfaces that agents can invoke without loading the entire catalog.

The project is weakest when it behaves like a large archive of every useful
artifact the agent ecosystem has ever produced. That archive impulse shows up
as tracked historical artifacts, generated state, duplicated paths, and a
surface inventory with thousands of warnings or violations.

# Core Thesis

The core thesis is:

> Agent reliability improves when local operational knowledge is captured as
> small, invokable capabilities with deterministic routing, explicit ownership,
> validation gates, and proof loops.

This is a real thesis, and the repo has built machinery around it.

**Hard evidence**

- `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py` defines
  projection modes, root skill sets, default visible skill names, plugin skill
  scan roots, hidden system bridge names, and a policy identity hash.
- `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` generates thin
  `$handle` command surfaces that point back to canonical source paths and
  state that the real workflow is not inside the generated handle.
- `Docs/architecture/context-budgeted-skill-trees.md` defines the source,
  manifest, and runtime projection layers, plus hard context-budget rules for
  rooted skill trees.
- `Docs/architecture/runtime-projection-modes.md` separates resolver,
  projection, runtime handle, workspace sync, user sync, and live invocation as
  different acceptance gates.
- Live command output from `./bin/ask runtime budget --json --robot` reported
  `projection_mode: rooted`, `root_skill_set_count: 10`, no policy violations,
  and `generated_command_handle_count: 93`.

**Interpretation**

This is not performative agent-native architecture. Generated handles, rooted
projection, runtime budgets, canonical source boundaries, and robot-mode JSON
are all implementation-level attempts to control agent context and execution.

The problem is not that the project lacks architecture. The problem is that the
architecture has outgrown its own product compression. A future agent can
discover the truth, but it still has to cross too many documents, command
surfaces, and debt reports to understand what matters first.

# Strategic Direction

The repo should narrow around one product line:

> A local, repo-governed Agent Skills Kit that lets an AI coding agent inspect
> repo health, find the right capability for a goal, understand the capability,
> prove it is safe and useful, and close work with evidence.

This is explicitly **local-control-plane-first**. Portability, public packaging,
and team-platform features should be built only after the local Codex/harness
loop proves it reduces avoidable agent mistakes.

The golden path is already documented:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask skills explain <handle> --json --robot
./bin/ask skills prove <handle> --json --robot
./bin/ask repo closeout --changed --json --robot
```

**Hard evidence**

- `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md`
  states the product problem as compression and names the desired flow:
  `doctor -> improve -> explain/prove -> closeout`.
- `Docs/plans/2026-05-06-feat-agent-first-golden-path-product-compression-plan.md`
  scopes the first executable slice to `ask repo doctor`.
- `Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md` defines
  namespace-first product command contracts and a shared JSON envelope.
- `Infrastructure/scripts/lib/ask/envelope.py` implements a structured result
  envelope with trace IDs, metadata, errors, and exit codes.

**Interpretation**

The golden path should become the repo's first screen and operating contract.
Everything else should support it. If a doc, skill, plugin, artifact, or
validation check does not make this loop more reliable, it is either a
secondary reference or a cleanup candidate.

# Intended Users

Primary users:

- AI coding agents operating inside this repo or downstream repos.
- Jamie as the repo owner and operator who needs repeatable agent behavior.
- Future maintainers building, reviewing, or pruning skill surfaces.
- Governance reviewers checking that generated and runtime surfaces did not
  become hidden sources of truth.

Secondary users:

- Technical co-founders or staff engineers evaluating whether this can become
  a reusable agent-control-plane product.
- Plugin and skill authors who need source ownership, audit, and packaging
  rules.

**Hard evidence**

- `README.md` positions `./bin/ask` as the main operator interface.
- `Docs/agents/16-agent-operating-contract.md` defines agent-first commands,
  robot mode, result envelopes, and next-command behavior.
- `harness.contract.json` requires memory, branch protection, issue-tracking,
  risk gates, observability, and CI-provider policy.

# Non-Goals

This repo should not become:

- A generic prompt library.
- A general-purpose knowledge base.
- A dumping ground for runtime logs, generated reports, or historic artifacts.
- A broad plugin marketplace implementation.
- A replacement for each downstream repo's own product, validation, or runtime
  contracts.
- A dashboard-first governance product before the CLI loop is stable.

**Hard evidence**

- `Docs/agents/14-path-ownership-boundaries.md` says runtime projections and
  mirrors are non-canonical and should not be hand-edited.
- `Docs/agents/15-repo-surface-ownership.md` says every tracked file must be
  source, fixture, policy, reference, intentional archive, or explicitly owned
  generated/vendored surface.
- `./bin/ask repo surface --json --robot` currently reports thousands of
  tracked historical artifacts and ownership findings, which is the clearest
  evidence that the repo has already drifted toward archive behavior.

# System Philosophy

The system philosophy is canonical-only at the source layer and generated-only
at the runtime layer.

Stable mental model:

1. **Product plane**: authored skills, plugin capability content, operator docs.
2. **Factory plane**: sync, projection, graph, validation, and install logic.
3. **Runtime plane**: generated handles, mirrors, runtime links, caches.

Humans edit the product and factory planes. Agents invoke the runtime plane but
should trace decisions back to canonical source.

**Hard evidence**

- `Docs/agents/14-path-ownership-boundaries.md` explicitly defines the
  three-plane model.
- `UBIQUITOUS_LANGUAGE.md` says `.agents/skills/**` is generated and
  `.skillsets/**` is a generated rooted skill manifest.
- `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` renders
  generated handle files that point back to canonical source.
- `Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`
  classifies runtime state, generated surfaces, source, policy, references,
  fixtures, unknown ownership, and historical artifacts.

**Interpretation**

This plane separation is the architectural spine. If it collapses, the repo
becomes a confusing prompt repository with extra machinery.

# Architectural Patterns

## Canonical Source With Generated Runtime Handles

Canonical skill bodies live under `Skills/**` or plugin-owned
`Plugins/*/skills/**`. Runtime command handles under `.agents/skills/**` are
generated pointers.

This pattern is intentional leverage. It allows short `$handle` invocation
without making the handle the source of truth.

## Rooted Skill Trees And Context Budgets

The default runtime shape is rooted projection: ten root skill sets expose
small front doors, while deeper module skills remain latent until selected.

This pattern is ahead of most 2026 agent repos because it treats context as a
governed budget, not an infinite prompt window.

## Namespace-First CLI Contracts

The public command surface is `./bin/ask`. It favors namespaces like `repo`,
`skills`, `runtime`, `plugins`, `evals`, and `workouts` rather than random
top-level scripts.

This is pragmatic. It gives agents one place to start and a consistent JSON
mode.

## Validation-As-Governance

Validation is not only linting. It enforces projection integrity, path
ownership, runtime budgets, plugin shadowing, provider policy, skill catalogs,
skill authoring-family gates, and runtime separation.

This is strong but expensive. It is useful only if the golden path summarizes
the result into a next action.

# Agent-Native Design Assumptions

The repo assumes agents need:

- A stable command entrypoint.
- JSON and robot-friendly output.
- One primary next command.
- Generated command handles for easy invocation.
- Source-traceable skills.
- Runtime-budget protection.
- Explicit blockers and warning-level diagnostic debt.
- Validation evidence before completion.

**Hard evidence**

- `Infrastructure/bin/ask` supports robot/fuzzy parsing behavior.
- `Docs/agents/16-agent-operating-contract.md` defines `--robot` mode and
  agent-first command behavior.
- `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md`
  requires `agent_summary`, `blocking`, `blockers`, `next_command`, and signal
  states for golden-path commands.
- `./bin/ask repo doctor --json --robot` already returns these concepts.

**Interpretation**

The agent-native model is real. It is not just markdown telling agents what to
do. The remaining gap is product clarity and proof maturity.

# Harness/Governance Model

The repo uses a harness-style governance model where repository rules are made
machine-checkable and agent-facing.

Key governance surfaces:

- `harness.contract.json`
- `.harness/ci-required-checks.json`
- `.harness/quality/criteria.md`
- `.harness/memory/LEARNINGS.md`
- `Docs/agents/**`
- `Infrastructure/scripts/validate_all.sh`
- `Infrastructure/scripts/validation-and-linting/verify-work.sh`
- `Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`

**Hard evidence**

- `harness.contract.json` defines branch protection checks, diff budgets,
  memory policy, observability policy, CI-provider policy, issue tracking, and
  loop-stage contracts.
- `.harness/quality/criteria.md` defines release-grade quality metrics for the
  skill-authoring family.
- `.harness/memory/LEARNINGS.md` stores append-only repo-specific gotchas and
  drift learnings.
- `Docs/agents/04-validation.md` maps PR validation jobs to `./bin/ask repo
  validate --scope=<name>`.

**Interpretation**

The governance model is unusually serious for an agent-skill repository. It is
also at risk of becoming too ceremonial unless every gate can be traced to a
failure class agents actually hit.

# Critical Constraints

Preserve these constraints unless an explicit migration replaces them:

- `./bin/ask` is the public repo-operation entrypoint.
- Root package-manager installs are not the default; use repo wrappers.
- Canonical sources live in `Skills/**`, plugin-owned `Plugins/*/skills/**`,
  and `Infrastructure/**` tooling, not generated runtime surfaces.
- `.agents/skills/**` is generated command-handle/runtime projection.
- `Plugins/cache/**` is runtime/plugin cache and should not be newly tracked.
- `.skillsets/**` must be resolved as generated tracked, generated ignored,
  fixture, or source; current policy still marks ownership decision required.
- Skill invocation analytics are attribution evidence, not outcome proof.
- Structural audit is not outcome proof.
- Repo surface warnings must stay visible even when non-blocking.

# Stable Interfaces

Stable or intentionally stabilizing interfaces:

- `./bin/ask repo doctor --json --robot`
- `./bin/ask repo doctor-catalog --json --robot`
- `./bin/ask repo surface --json --robot`
- `./bin/ask runtime budget --json --robot`
- `./bin/ask skills handles --json --no-handles`
- `./bin/ask skills resolve <handle> --json`
- `bash Infrastructure/scripts/validate_all.sh`
- `bash Infrastructure/scripts/validation-and-linting/verify-work.sh`
- Generated command handles under `.agents/skills/<handle>/SKILL.md`
- Rooted manifests under `.skillsets/**`, subject to ownership-policy cleanup
- `harness.contract.json` governance contract

Future agents should prefer these interfaces over ad hoc shell exploration once
they understand the current task.

# Sources of Complexity

## Intentional Complexity

- Source/projection/runtime separation.
- Rooted skill trees and context-budget enforcement.
- Generated command handles.
- Skill audit, proof, eval, workout, and validation loops.
- Plugin-owned skill source versus plugin runtime cache.
- Repo surface inventory and path ownership policies.

These are justified when they reduce agent ambiguity or prevent generated
state from becoming accidental source.

## Accidental Complexity

- Tracked historical artifacts and generated evidence under `Infrastructure`,
  `artifacts`, and `.harness`.
- Duplicated path shapes such as `Infrastructure/Infrastructure/**`.
- Mixed docs that describe implemented commands and planned commands close
  together.
- Multiple counts for visible/default skills depending on which surface is
  queried.
- `.skillsets/**` being operationally used while repo-surface policy still
  classifies it as ownership-decision-required.
- A very large tracked-file count for a skill/control-plane repo.

**Hard evidence**

- `git ls-files | wc -l` returned `7729`.
- `fd -a "SKILL.md$" Skills Plugins .agents/skills | wc -l` returned `153`.
- `./bin/ask repo surface --json --robot` reported `total_paths: 7729`,
  `blocking_findings: 4543`, and thousands of tracked historical artifacts.
- `./bin/ask repo doctor --json --robot` currently reports catalog parity drift
  as a blocker while other runtime and handle checks pass.

# Sources of Leverage

The repo creates leverage when it turns tacit operator knowledge into reusable
agent behavior.

High-leverage surfaces:

- `UBIQUITOUS_LANGUAGE.md`: stabilizes vocabulary so agents do not invent
  inconsistent meanings for sync, projection, handles, and source.
- `./bin/ask`: gives agents a command-first operating loop.
- Generated handles: make capabilities invokable without loading full sources.
- Runtime budget checks: prevent capability discovery from becoming context
  overload.
- Repo doctor: compresses low-level diagnostics into one decision.
- Path ownership and repo surface inventory: prevent hidden source-of-truth
  drift.
- Skill authoring-family gates: turn skill quality into a repeatable release
  bar.
- Memory learnings: retain failure patterns across runs.

# Probable Moat

The moat is not the skill catalog. A determined team can copy a list of skill
files.

The moat is the operational loop:

1. Capture local expertise as canonical capabilities.
2. Generate small invocation surfaces.
3. Route agents to the right capability at the right time.
4. Enforce context budgets and path ownership.
5. Prove reachability, structural quality, and outcome usefulness separately.
6. Feed failures back into memory, docs, validators, and command contracts.

**Interpretation**

This becomes hard to copy only if the proof loop is real. If the repo stops at
"lots of skills with nice descriptions," it has no moat. If it can demonstrate
that agents using these capabilities make fewer mistakes, close work more
reliably, and preserve project-specific rules across repos, it becomes
commercially interesting.

# Modern Standards Assessment (May 2026)

This assessment uses live repo evidence plus a light check against current
primary references:

- OpenAI agent guidance emphasizes tools, handoffs, guardrails, tracing, evals,
  and agent optimization:
  <https://platform.openai.com/docs/guides/agents-sdk>,
  <https://openai.github.io/openai-agents-python/tracing/>,
  <https://platform.openai.com/docs/guides/trace-grading>, and
  <https://openai.github.io/openai-agents-python/guardrails/>.
- MCP's current specification emphasizes lifecycle management, capability
  negotiation, resources, prompts, tools, authorization, logging, and explicit
  user consent/control for data and tool use:
  <https://modelcontextprotocol.io/specification/2025-11-25/basic>,
  <https://modelcontextprotocol.io/specification/2025-03-26/basic/lifecycle>,
  <https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization>,
  and <https://modelcontextprotocol.io/docs/concepts/prompts>.
- GitHub Actions security guidance emphasizes least-privilege token
  permissions, secret handling, OIDC, dependency review, and code scanning:
  <https://docs.github.com/actions/learn-github-actions/security-hardening-for-github-actions>
  and
  <https://docs.github.com/en/code-security/concepts/secret-security/about-secret-scanning>.

| Area | Assessment | Evidence | Recommendation |
| --- | --- | --- | --- |
| Agent-native architecture | Ahead | `./bin/ask`, robot JSON, generated handles, rooted projection, runtime budgets | Keep compressing into golden-path commands. |
| AI workflow ergonomics | Aligned but noisy | `repo doctor` exists; docs and specs still expose many lower-level surfaces | Make doctor/improve/explain/prove/closeout the first screen. |
| Repository cognition | Lagging | `repo surface` reports 4543 blocking findings and 7729 tracked paths | Quarantine or reclassify historical/generated debt. |
| Governance systems | Ahead | Harness contract, validation scopes, path ownership, quality criteria | Keep gates, but tie each to agent-facing blocker classes. |
| Deterministic execution | Ahead | Policy identity, generated command surface checks, structured envelopes | Preserve deterministic next-command selection. |
| Validation loops | Ahead but heavy | `validate_all.sh`, `verify-work.sh`, authoring-family gate, repo doctor | Add changed-file closeout so agents do not overrun full gates. |
| Observability | Aligned but under-integrated | Harness observability config and skill telemetry exist; proof analytics still planned | Treat analytics as attribution, not outcome proof. |
| Typed boundaries | Mixed | Python dataclasses/envelopes exist; JSON schemas are uneven across commands | Promote command payload schemas for golden-path outputs. |
| Context management | Ahead | Rooted skill trees, context budgets, hidden system bridges | Enforce budgets through CI and runtime doctor. |
| Multi-agent coordination | Aligned | Skills, reviewers, artifacts, harness contracts | Require artifact-first reviewer output for swarms. |
| Memory architecture | Aligned | `.harness/memory/LEARNINGS.md`, Project Brain references, local memory policy | Make memory freshness and duplication measurable. |
| DX/UX quality | Underbuilt | Many powerful commands, but too much discovery burden | Build concise command help and examples around the golden path. |
| Infra pragmatism | Mixed | Wrappers are strong; many generated/artifact surfaces are tracked | Stop treating every artifact as repo material. |
| Scalability | Mixed | Rooted projection scales; repo surface debt does not | Cap visible skills and tracked generated surfaces. |
| Maintainability | At risk | Many docs/specs/plans with overlapping claims | Establish source-of-truth docs per product stage. |
| Security posture | Aligned | CodeQL, Semgrep, secret scan, security workflows, provider policy | Verify least-privilege permissions and MCP approval paths regularly. |
| CI/CD maturity | Aligned | GitHub Actions plus CircleCI dual-provider policy and required check manifest | Reduce duplicated check-name drift. |
| Testing realism | Mixed | Strong structural tests; outcome proof still developing | Invest in workouts/evals that prove agent behavior, not only file shape. |
| Prompt/skill composability | Ahead | Root skills, command handles, plugin skill scan roots | Remove overlapping skills or fold them behind routers. |
| Operational resilience | Mixed | Doctor detects blockers; surface debt remains huge | Turn known debt into bounded remediation lanes. |
| Portability | Underbuilt | Local paths, Codex-specific contracts, harness dependencies | Decide whether this is local-first product or portable toolkit. |
| Dependency discipline | Aligned | Root no-install policy, wrappers, `.mise.toml`, tool contracts | Keep package commands inside verified package roots. |

# Drift Detection Signals

These signals should be reviewed in PRs, release gates, and periodic repo
health runs.

| Signal | Why It Matters | Likely Root Cause | Operational Impact | Severity | Measurable Indicator | Corrective Action | Blocks Merge/Release |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Catalog parity drift | Agents cannot trust docs or routing counts | Manual README or catalog edits | Goal routing blocks or misroutes | High | `./bin/ask repo doctor` signal `catalog_parity.state=block` | Regenerate or repair canonical count surfaces | Yes |
| Runtime budget inflation | Context cost rises without reliability gain | More visible skills, weak routing discipline | Agents load too much and behave inconsistently | Medium | `advanced_visible_count > 60` or description token warnings | Fold skills behind roots or hide low-use handles | No by default, yes in strict release |
| Generated surface hand edits | Runtime projection becomes hidden source | Agents or humans editing `.agents/**` directly | Sync overwrites work or creates false truth | High | Path ownership diff touches generated runtime without allowed sync | Revert direct edit and regenerate from source | Yes |
| `.skillsets/**` ownership remains unresolved | Core projection is operational but policy-ambiguous | Generated snapshots used as both runtime and evidence | Cleanup and CI decisions stay unclear | High | Repo surface reports `.skillsets` ownership decision required | Decide generated tracked vs ignored vs fixture and encode allowlist | Yes for strict cleanup lanes |
| Repo surface blocking findings increase | Archive behavior overtakes source clarity | Retaining logs, artifacts, generated reports | Onboarding and validation become noisy | High | `repo surface blocking_findings` rises release-over-release | Quarantine historical artifacts and allowlist intentional archives | Yes if changed files add debt |
| Duplicated orchestration logic | `ask`, scripts, docs, and workflows diverge | Copy-pasted wrappers or one-off fixes | Agents receive contradictory commands | High | Same behavior implemented in more than one script without shared helper | Extract helper under `Infrastructure/scripts/lib/ask/**` or canonical script | Yes when behavior changes |
| Prompt growth replaces harness improvement | Instructions become longer instead of safer | Fixing behavior with prose only | Agents forget or misapply rules | Medium | AGENTS/docs line count grows while validators unchanged | Convert repeated instruction into command/check/test | No, but should block governance PRs |
| Skills become undiscoverable | Capability catalog loses utility | Hidden routers, stale manifests, missing handles | Agents improvise instead of invoking skills | High | `skills handles --check` failures or missing command handles | Regenerate projections and repair source metadata | Yes |
| Structural audit treated as outcome proof | The repo claims quality without user-task evidence | Conflating lint with agent success | False confidence and weak moat | High | `skills prove` marks audit as outcome success | Split reachability, structural, and outcome evidence | Yes for proof features |
| Skill invocation analytics treated as outcome proof | Telemetry shows use, not usefulness | Metric overreach | Wrong capabilities get promoted | High | Analytics-only records marked as outcome proof | Classify analytics as attribution evidence only | Yes |
| Tool proliferation without consolidation | Every integration becomes a new surface | Plugin enthusiasm without product pruning | Agents face too many equivalent options | Medium | More than 3 overlapping skills for same operator goal | Fold behind router or delete low-use duplicate | No unless default-visible |
| CI/governance check-name drift | Required checks stop matching actual workflows | Dual CI providers and manual manifests | Protected branches enforce stale checks | High | Required-check manifest differs from workflow job names | Run CI name parity and update canonical manifest | Yes |
| Memory systems become non-deterministic | Agents cite stale or duplicate facts | Multiple memory roots without freshness policy | Future runs inherit wrong guidance | Medium | Same learning appears in multiple places with conflicting wording | Consolidate into `.harness/memory/LEARNINGS.md` or Project Brain | No by default |
| MCP/tool approval bypass | External tool execution becomes unsafe | Convenience shortcuts around approval | Data or write operations happen without consent | High | MCP-dependent workflow lacks auth/approval preflight | Run MCP startup/security triage and require approval checks | Yes |
| Historical artifacts remain active | Old evidence competes with current truth | No retention boundary | Agents follow stale plans or reports | Medium | Dated artifacts referenced from front-door docs | Move behind indexed archive or delete after reference scan | No, yes if front-door linked |
| Onboarding time rises | Product compression is failing | Too many docs and commands before first safe action | New agents waste context and make mistakes | Medium | Cold-agent first safe command takes more than 5 minutes | Front-load `repo doctor` and one next action | No |
| Validation runtime exceeds usefulness | Gates become avoided | Full suite used for every small doc edit | Agents skip validation or time out | Medium | Fast doc-only closeout exceeds 5 minutes | Add changed-file closeout scopes and clear blocked outcomes | No |
| Repeated TODO clusters remain unresolved | Strategic debt becomes background noise | Planning without cleanup lanes | Maintainers stop trusting TODOs | Low to medium | More than 25 unresolved TODO/FIXME markers in one area | Convert to issues or delete stale comments | No unless in touched area |
| UX wording becomes marketing-first | Product loses operational clarity | Trying to sell before proving behavior | Agents and humans misunderstand what exists | Medium | README promises commands not implemented | Gate docs against live `ask --help` output | Yes for public docs |

# Technical Debt Signals

Current debt worth naming plainly:

- `repo doctor` is useful but currently blocked by catalog parity drift in the
  live tree.
- `repo surface` reports thousands of blocking findings, dominated by
  historical artifacts and tracked generated/runtime-like surfaces.
- `.skillsets/**` has operational importance but unresolved repo-surface
  ownership classification.
- The product language still sometimes conflates implemented commands,
  planned commands, and future analytics proof.
- The repo tracks enough artifacts that future agents may mistake old evidence
  for current architecture.

# UX Philosophy

The UX should be command-first and evidence-backed:

- One entry command.
- One current decision.
- One primary next command.
- Detailed evidence available, but not shoved into the first screen.
- Generated handles for invocation, canonical source for truth.
- No landing-page language in operational docs unless it maps to a command.

The target UX is not "beautiful docs." It is "a cold agent can safely start
work in under five minutes and know what would block completion."

# What Future Agents Should Preserve

- The `./bin/ask` public command surface.
- The distinction between canonical source and runtime projection.
- Generated command handles as pointers, not source.
- Rooted skill trees and context budgets.
- `UBIQUITOUS_LANGUAGE.md` as vocabulary authority.
- Path ownership boundaries.
- Repo surface inventory policy.
- Skill proof semantics: reachability, structural quality, and outcome proof
  are separate.
- Golden-path command compression.
- Exact command outcomes in closeout evidence.
- Append-only memory learnings for repo-specific failure modes.

# What Future Agents Should Challenge

- Any new skill that duplicates an existing capability without measurable
  routing or outcome benefit.
- Any generated artifact added to git without an owner, generator, and
  retention boundary.
- Any doc that advertises planned commands as implemented.
- Any validation gate whose failure class is not understandable to agents.
- Any plugin cache or runtime mirror treated as source.
- Any attempt to grow the visible catalog instead of improving selection.
- Any "temporary" compatibility path that lacks an expiration or review date.

# Open Questions

1. Should `.skillsets/**` be officially tracked generated distribution output,
   ignored generated output, or a fixture subset?
2. What is the canonical outcome-proof artifact for a skill: workout, eval,
   trace grade, session evidence, or a combined proof index?
3. Which plugin and skill families are core, and which are experiments?
4. What retention index should govern `Infrastructure/artifacts/**`,
   `artifacts/**`, and historical evidence bundles after aggressive
   quarantine?
5. What portability boundary is acceptable after the local-control-plane loop
   proves adoption value?

# Recommended Decisions

## Decision 1: Make The Golden Path The Product

Recommendation: make `repo doctor -> skills improve -> skills explain -> skills
prove -> repo closeout` the canonical public loop and demote everything else to
advanced reference.

Tradeoff: this hides some advanced power from first-contact users, but that is
the point. The repo already has enough machinery. The product needs fewer
front doors.

## Decision 2: Classify `.skillsets/**` Explicitly

Recommendation: classify `.skillsets/**` as generated tracked distribution
output only if CI proves it is current, has a generator, and is required for
runtime or review. Otherwise stop tracking it or move stable fixture subsets
under explicit fixtures.

Tradeoff: tracking generated manifests can help review and runtime parity; it
also creates drift unless regenerated deterministically.

## Decision 3: Treat Outcome Proof As The Moat

Recommendation: do not promote a skill to core/default-visible unless it has
reachability proof, structural audit proof, and at least one realistic outcome
proof artifact.

Tradeoff: this slows catalog growth. That is good. Catalog growth is not the
moat.

## Decision 4: Quarantine Historical Artifacts

Recommendation: quarantine aggressively. Move historical artifacts behind an
indexed archive or remove them after reference scans. Keep summaries, fixtures,
and evidence indexes; do not keep raw event streams by default.

Tradeoff: some archaeology becomes harder. The repo becomes much easier for
current agents to reason about.

## Decision 5: Stay Local-First Until Proof Is Strong

Recommendation: keep the product local-first and Codex/harness-native until the
golden path proves real adoption value. Avoid building a broad portable
platform before the loop is sharp.

Tradeoff: portability is delayed. But premature portability would multiply
abstractions before the core proof model is stable.

# Strategic Contradictions

- The repo says it prevents drift, but live repo-surface inventory shows
  substantial tracked drift.
- The repo says it keeps context small, but advanced visible skill count is far
  above the advisory threshold even though policy still passes.
- The repo says generated surfaces are not source, but `.skillsets/**` remains
  unresolved in surface ownership while being operationally important.
- The repo wants to prove capability quality, but much of the current machinery
  still proves structure and reachability more strongly than outcomes.
- The repo wants to be agent-first, but the first-contact path still requires
  reading many docs to understand which warnings are acceptable.

# Suggested Simplifications

- Collapse first-contact documentation around five commands.
- Hide raw catalog size from the README; emphasize proof and golden-path
  behavior instead.
- Delete or archive historical run outputs unless they are fixtures or indexed
  references.
- Fold overlapping skills behind root routers.
- Convert repeated prose warnings into validators or `ask` doctor signals.
- Give every generated tracked surface a `generator`, `source inputs`,
  `review_after`, and `strict validation` rule.
- Make `repo doctor` the canonical answer to "what should an agent do first?"

# Missing Capabilities

- A fully implemented `skills improve` command that maps goals to capabilities
  with one next action.
- A concise `skills explain` command for canonical source, handle, visibility,
  and limitations.
- A canonical `skills prove` command that separates reachability, structural
  proof, analytics attribution, and outcome proof.
- `repo closeout --changed` as a completion-readiness gate.
- A normalized skill invocation evidence projection that is privacy-safe and
  clearly non-canonical.
- A generated docs check that prevents README/product docs from advertising
  commands not exposed by `./bin/ask --help`.
- A retention mechanism for historical artifacts.

# Long-Term Scalability Concerns

- Skill count can scale only if routing quality scales faster than catalog
  size.
- Validation can scale only if changed-file closeout and golden-path summaries
  prevent agents from running full suites blindly.
- Memory can scale only if learnings are indexed, deduplicated, and freshness
  tagged.
- Plugin support can scale only if plugin cache/mirror/source boundaries stay
  strict.
- Multi-agent review can scale only if artifacts, not mailbox text, are the
  completion evidence.
- Commercial portability can scale only if local Jamie-specific assumptions are
  isolated behind adapters.

# Strategic Review

## Is This Project Coherent?

Yes at the core, no at the edges.

The coherent core is a capability control plane: source ownership, generated
runtime surfaces, context budgets, command contracts, validation, and proof.
The incoherent edge is the amount of historical/generated material tracked
alongside source and policy.

## Is The Architecture Pragmatic?

Mostly yes. The source/projection/runtime split is practical because agents
need small invokable handles without losing source traceability. The rooted
skill-tree model is also practical because context is a real constraint.

The least pragmatic part is the repo-surface sprawl. A control plane with
thousands of tracked historical artifacts is fighting itself.

## Is The Complexity Justified?

The core complexity is justified. The archive complexity is not.

Keep the machinery that reduces agent ambiguity. Remove or quarantine the
material that increases it.

## Is The Agent-Native Model Real Or Performative?

Real. Generated command handles, robot JSON, trace IDs, next commands, runtime
budgets, and path ownership checks are implementation facts.

It becomes performative only if the proof layer stops at structural audits and
never demonstrates better agent outcomes.

## What Is Genuinely Differentiated?

- Treating skills as governed capabilities rather than prompt snippets.
- Separating canonical source from runtime invocation surfaces.
- Budgeting context at the skill-tree level.
- Using repo doctor and closeout-style commands to give agents deterministic
  next actions.
- Encoding repo-specific learned failures into memory and validation.

## What Feels Trend-Driven?

- Broad plugin and skill surface expansion without enough outcome proof.
- Large AI governance vocabulary where a smaller command loop would do.
- Any analytics story that treats invocation as success.

## What Should Be Deleted Immediately?

Do not blindly delete unknown files. But the deletion/quarantine queue should
start with:

- tracked runtime databases unless documented as fixtures;
- unindexed historical artifacts and run logs;
- duplicated `Infrastructure/Infrastructure/**` material after reference scan;
- stale generated reports reproducible from source;
- dead compatibility paths with no owner or review date.

## What Should Become Core?

- `./bin/ask repo doctor`
- `./bin/ask skills improve`
- `./bin/ask skills explain`
- `./bin/ask skills prove`
- `./bin/ask repo closeout --changed`
- rooted projection and command handles;
- path ownership;
- repo surface inventory;
- outcome proof artifacts.

## What Creates Leverage?

Leverage comes from converting repeated agent failure modes into small
capabilities, validators, proof artifacts, and memory learnings.

## What Creates Drag?

Drag comes from tracked artifacts, duplicated docs, overlapping skills, command
surfaces that are planned but not implemented, and validation failures whose
meaning is not compressed into a next action.

## What Would Make This Hard To Copy?

Real proof data: before/after agent outcomes, trace grades, workouts, closeout
success rates, and evidence that skill use reduces failures across repos.

The file layout is copyable. The operational history plus proof loop is not.

## What Would Make This Commercially Valuable?

A team product that can answer:

- Which agent capability should be used for this repo task?
- Did the agent load the right capability?
- Did it follow the repo's rules?
- Did validation prove the outcome?
- What drift is accumulating?
- What should be fixed next?

That is commercially valuable if it reduces review burden, failed agent runs,
onboarding time, and policy drift.

## What Would Make Developers Adopt It?

Developers will adopt the smallest useful loop:

```bash
./bin/ask repo doctor --json --robot
./bin/ask skills improve "<goal>" --json --robot
./bin/ask repo closeout --changed --json --robot
```

They will not adopt a giant skill catalog first. They will adopt a command that
makes their agents stop making avoidable mistakes.

## Biggest Risks

- The repo keeps adding capability surfaces faster than it proves outcomes.
- Governance becomes ceremony.
- Historical artifacts bury current truth.
- Local-first assumptions make portability too expensive later.
- Multiple docs disagree about what is implemented.
- Runtime/generated surfaces become de facto source.

## Assumptions Likely Wrong

- More skills automatically improve agent performance.
- Structural audit is close enough to outcome proof.
- Agents will read enough docs to infer the safe path.
- Local telemetry can be used as proof without careful privacy and evidence
  classification.
- A repo this large can remain understandable without aggressive surface
  pruning.

## Smallest Compelling Version

The smallest compelling version is:

- five golden-path commands;
- ten or fewer default root skill sets;
- a handful of high-value proven skills;
- generated handles;
- path ownership;
- repo doctor;
- closeout;
- one proof index that distinguishes reachability, structure, and outcome.

Everything else is secondary until that loop is excellent.

## If This Became The Company Moat

Aggressively protect:

- proof semantics;
- command contracts;
- source/projection/runtime separation;
- privacy-safe telemetry;
- memory learnings;
- routing quality;
- context-budget discipline;
- drift detection.

Do not protect catalog size. It is the least defensible asset.

## If This Fails

It will fail because it becomes too big to trust: too many skills, too many
artifacts, too much governance language, too little outcome proof, and no single
command path that makes agents better immediately.

# Evidence & Traceability Matrix

| Conclusion | Evidence Type | File Paths | Symbols / Interfaces / Components | Runtime Behaviour Observed | Confidence | Why The Evidence Matters |
| --- | --- | --- | --- | --- | --- | --- |
| The repo is a governed agent capability control plane, not a prompt dump. | docs, source-code, CLI | `AGENTS.md`, `README.md`, `Docs/product/agent-capability-control-plane.md`, `Infrastructure/bin/ask` | `./bin/ask`, `repo doctor`, `skills`, result envelopes | `repo doctor` composes multiple repo-health signals | High | The control-plane claim is present in docs and implemented as command machinery. |
| Canonical source and runtime projection separation is the architectural spine. | docs, source-code, naming patterns | `UBIQUITOUS_LANGUAGE.md`, `Docs/agents/14-path-ownership-boundaries.md`, `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` | `CommandHandle`, generated `.agents/skills/**`, `source_path` | Generated handles point back to canonical source and state the real workflow is elsewhere | High | This prevents generated runtime surfaces from becoming hidden source. |
| Rooted skill trees are intentional context management. | docs, source-code, config | `Docs/architecture/context-budgeted-skill-trees.md`, `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py` | `ROOT_SKILL_SET_NAMES`, `PROJECTION_MODE_CHOICES`, `policy_identity()` | Runtime budget reports rooted projection, 10 root skill sets, no violations | High | The repo treats context size as a governed resource. |
| The agent-native model is real. | source-code, CLI, docs | `Infrastructure/bin/ask`, `Infrastructure/scripts/lib/ask/envelope.py`, `Docs/agents/16-agent-operating-contract.md` | `--json`, `--robot`, `trace_id`, `next_command`, `agent_summary` | `repo doctor` returns machine-readable blocking state and next command | High | Agent behavior is supported by executable contracts, not only instructions. |
| The product direction is golden-path compression. | specs, plans, CLI | `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md`, `Docs/plans/2026-05-06-feat-agent-first-golden-path-product-compression-plan.md` | `repo doctor`, `skills improve`, `skills explain`, `skills prove`, `repo closeout` | `repo doctor` first slice exists; other commands are partly planned/incomplete | High | The repo has a clear strategic direction: fewer first-contact decisions. |
| Current repo state has serious surface debt. | runtime flow, source-code, docs | `Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`, `Docs/agents/15-repo-surface-ownership.md` | `repo surface`, classifications, allowlist policy | `repo surface` reports 7729 paths and 4543 blocking findings | High | The project claims drift prevention while carrying large tracked-surface drift. |
| Catalog parity drift is a live blocker class. | runtime flow, CLI | `./bin/ask repo doctor --json --robot`, `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md` | `catalog_parity`, `repo doctor-catalog` | `repo doctor` reports catalog parity as blocking in the live tree | High | This proves the repo can identify a real docs/catalog mismatch before agents proceed. |
| `.skillsets/**` needs an explicit ownership decision. | docs, source-code, runtime flow | `Docs/agents/15-repo-surface-ownership.md`, `Infrastructure/scripts/validation-and-linting/check_repo_surface_inventory.py`, `.skillsets/**` | `ownership_decision_required`, rooted manifests | `repo surface` reports `.skillsets` ownership decision findings | High | Operational manifests cannot remain policy-ambiguous forever. |
| The moat depends on outcome proof, not catalog size. | docs, tests, interpretation | `Docs/product/agent-capability-control-plane.md`, `.harness/quality/criteria.md`, `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md` | `skills prove`, workouts/evals, quality metrics | Current docs distinguish reachability, structural proof, and outcome proof; full proof is still developing | Medium-high | Skill catalogs are copyable; validated agent behavior is harder to copy. |
| Validation is mature but risks becoming too heavy without closeout compression. | source-code, docs, CI/CD | `Infrastructure/scripts/validate_all.sh`, `Infrastructure/scripts/validation-and-linting/verify-work.sh`, `.github/workflows/**`, `.circleci/config.yml` | validation scopes, required checks, fast mode, changed files | Validation suite includes many required governance gates | High | Strong gates help only if agents can select the right subset and understand blockers. |
| Security posture is aligned but should stay approval- and least-privilege-oriented. | CI/CD, config, external standards | `.github/workflows/codeql.yml`, `.github/workflows/secret-scan.yml`, `.github/workflows/semgrep.yml`, `harness.contract.json`, `Docs/agents/06-security-and-governance.md` | CodeQL, Semgrep, secret scan, provider policy, MCP preflight | Security workflows are present; MCP-dependent work requires auth checks | Medium-high | Current 2026 standards emphasize tool approval, least privilege, and code scanning. |
| Plugin support is useful but at risk of surface proliferation. | source-code, docs, naming patterns | `Plugins/**`, `Plugins/cache/**`, `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`, `Docs/agents/14-path-ownership-boundaries.md` | `PLUGIN_SKILL_ROOT_GLOB`, plugin cache, plugin-owned sources | Plugin-owned sources and runtime caches are distinct | Medium-high | Plugin growth is leverage only if source/cache boundaries and routing remain strict. |
| Memory is part of the operating model, not optional decoration. | docs, memory, config | `.harness/memory/LEARNINGS.md`, `harness.contract.json`, `AGENTS.md` | memory policy, learnings surface, Project Brain linkage | Learnings file records concrete repo-specific failure patterns | High | Durable failure memory is how future agents avoid repeated mistakes. |
| The project is commercially interesting only if it reduces agent failures. | interpretation, docs, runtime flow | `README.md`, `Docs/product/agent-capability-control-plane.md`, `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md` | doctor/improve/explain/prove/closeout loop | First slice can already block unsafe work; full loop is not complete | Medium | The strongest market claim is reliability, not skill count. |
| The repo is currently more overbuilt in archive/governance surfaces than in core agent architecture. | architecture coupling, runtime flow, docs | `Docs/agents/15-repo-surface-ownership.md`, `Infrastructure/artifacts/**`, `artifacts/**`, `.harness/**` | tracked artifacts, historical classifications, repo surface warnings | Surface inventory shows large historical artifact burden | High | This identifies what to delete or quarantine without weakening the core. |
| Future portability is underbuilt. | docs, config, interpretation | `harness.contract.json`, `.mise.toml`, `Docs/specs/2026-05-06-feat-agent-first-golden-path-product-compression-spec.md`, local path references | local collector paths, Codex sessions, Linear, harness | Specs reference `$HOME/.agents/session-collector`, `$HOME/.agents/otel-collector`, and `~/.codex/sessions` | Medium | Local-first is currently a strength, but commercial portability will require adapters. |
| Current best-practice alignment is strongest around evals/traces/proof intent, weakest around repo discoverability. | external standards, docs, runtime flow | OpenAI Agents/Evals/Trace guidance, MCP spec, GitHub security docs, repo docs | evals, trace grading, tool approvals, capability negotiation, code scanning | Repo has validation/proof plans and security workflows, but surface inventory remains noisy | Medium-high | This grounds the May 2026 assessment in current agent and CI expectations. |
