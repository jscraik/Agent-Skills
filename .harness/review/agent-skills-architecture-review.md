# Agent Skills Architecture Review

Repository: `agent-skills`

Review date: 2026-05-07

Review artifact: `.harness/review/agent-skills-architecture-review.md`

Reference lenses applied:

- *The Pragmatic Programmer*: DRY ownership, orthogonality, tracer bullets, automation, reversibility, entropy control, broken windows.
- *A Philosophy of Software Design*: deep modules, cognitive load, change amplification, information hiding, shallow abstractions, tactical complexity.
- *Extreme Programming Explained*: feedback loops, humane iteration, testability, continuous integration, small reversible change, communication density.
- *Domain-Driven Design*: ubiquitous language, bounded contexts, model integrity, anti-corruption boundaries, strategic design.
- *Five Lines of Code*: structural refactoring pressure, small methods, branching complexity, mutation control, mechanical simplification, refactor seams.

This review does not summarize those books. It uses them as pressure systems against the repository's implementation reality.

Evidence basis:

- Repository instructions and domain language: `AGENTS.md`, `UBIQUITOUS_LANGUAGE.md`, `Docs/agents/**`, `.harness/features/agent-skills-intent.md`.
- Runtime and command surfaces: `Infrastructure/bin/ask`, `Infrastructure/scripts/lib/ask/commands/**`, `Infrastructure/scripts/lifecycle-and-sync/**`.
- Validation and governance: `Infrastructure/scripts/validate_all.sh`, `Infrastructure/scripts/verify-work.sh`, `.github/workflows/**`, `.circleci/config.yml`, `harness.contract.json`, `.harness/quality/criteria.md`.
- Skill and plugin trees: `Skills/**/SKILL.md`, `Plugins/**/skills/**`, `.agents/skills/**` where relevant as runtime projection evidence.
- Repository surface and debt signals from live commands:
  - `./bin/ask repo doctor --json --robot` returned a blocking catalog parity signal with `catalog_parity.count_mismatch`, while repo status, projection sync, runtime budget, and command handles passed.
  - `python3 Infrastructure/scripts/docs_lint.py --mode warn --config Infrastructure/docs-policy.json` passed with 177 scanned files, 0 errors, 0 warnings.
  - `wc -l` found major orchestrator sizes: `Infrastructure/scripts/lib/ask/commands/skills.py` at 3001 lines, `Infrastructure/bin/ask` at 1900 lines, `repo.py` at 1029 lines, `command_surface.py` at 726 lines, `validate_all.sh` at 636 lines, and `check_repo_surface_inventory.py` at 746 lines.
  - TODO-like scan across `Infrastructure`, `Skills`, `Plugins`, `Docs`, and `.harness` found 172 hits in `Infrastructure`, 35 in `Plugins`, 8 in `Docs`, 4 in `.harness`, and 1 in `Skills`.

Confidence labels:

- High: directly supported by source/config/docs/runtime output.
- Medium: supported by multiple surfaces but still interpretive.
- Low: strategic or market inference with limited repo-only proof.

## 1. Executive Summary

This project is coherent, but not yet clean.

The repository is trying to be a local-first, agent-native control plane for authoring, validating, discovering, routing, syncing, and governing Codex skills and plugin workflows. That intent is real in the implementation, not just README language. The strongest proof is the repeated source/projection/runtime separation encoded in `UBIQUITOUS_LANGUAGE.md`, `Docs/agents/14-path-ownership-boundaries.md`, the generated command-handle system in `Infrastructure/scripts/lifecycle-and-sync/command_surface.py`, runtime budget checks, catalog parity checks, and the `./bin/ask` CLI as an agent-operable front door.

The architecture has a genuine thesis:

- Keep canonical skill sources separate from runtime projections.
- Give agents short handles and machine-readable command outputs.
- Enforce path ownership, runtime budgets, catalog parity, and docs policy.
- Treat local workflows, skills, plugins, and harness governance as one operating system rather than scattered prompt files.

That is differentiated. Most repositories claiming to be "agent-native" stop at markdown prompts. This one has runtime projection, generated handles, policy hashes, validation scripts, CI gates, root skill sets, command discovery, repo-surface inventory, and memory/learning surfaces.

The main problem is that the control plane is becoming harder to reason about than the skills it governs.

The largest risk is not lack of ambition. It is accumulated orchestration mass:

- `Infrastructure/scripts/lib/ask/commands/skills.py` is a 3001-line multi-context module that mixes skill discovery, plugin cache handling, runtime projection, command-surface behavior, proofs, analytics, and dynamic module loading.
- `Infrastructure/bin/ask` is a 1900-line CLI front controller with command registration, fuzzy error handling, argument parsing, imports, and dispatch responsibilities.
- `repo doctor` already reports a blocking catalog parity mismatch while other core signals pass.
- `repo_surface` reports 4543 blocking findings, most from tracked historical artifacts, plus unresolved ownership decisions and generated work areas.
- The CI surface is serious but split across GitHub Actions and a very thin CircleCI job, creating a governance story that is plausible but easy to misunderstand.

The project is agent-native in a real sense, but its agent-native model is under strain. Agents can operate it through `./bin/ask`, generated handles, JSON modes, docs maps, validation gates, and repo doctor outputs. However, agents also face a lot of cognition tax: many docs, many skills, many policy surfaces, multiple validation lanes, historical artifact noise, generated/runtime/source boundaries, and large orchestrator files where local reasoning is weak.

The moat is not the skill catalog by itself. The catalog can be copied. The moat is the operational discipline around skills: source/projection separation, runtime-surface budgeting, command handles, validation loops, repo cognition, learned-fix memory, and proof of real agent outcomes. The strategic posture should be hybrid: a broad skill/plugin workbench can be the distribution surface, but the proof-driven control plane must be the trust layer underneath it. If the project becomes a company-level asset, the defensible core is not breadth alone; it is breadth constrained by outcome proof.

Blunt assessment:

- Coherence: yes.
- Pragmatism: mixed. The source/projection model is pragmatic; some governance layers are heavier than the current proof warrants.
- Abstraction quality: high in the policy/command-handle modules, low in the giant CLI/skills orchestrators.
- Agent-native reality: real, not performative, but still too expensive for a fresh agent to load mentally.
- Moat: real only if broad skill/plugin ambition is governed by measured workflow outcomes and aggressive simplification around the proof loop.
- Biggest failure mode: becoming an impressive local governance machine that fewer humans and agents can confidently operate.

## 2. Architectural Risk Assessment

### Risk 1: Control-plane concentration

Fact:

- `Infrastructure/scripts/lib/ask/commands/skills.py` is 3001 lines.
- `Infrastructure/bin/ask` is 1900 lines.
- `Infrastructure/scripts/lib/ask/commands/repo.py` is 1029 lines.

Interpretation:

These are not automatically bad because control planes naturally centralize routing. The risk is that these files mix domain concerns that should be separately evolvable: skill catalog management, plugin cache refresh, projection sync, proof/eval flows, runtime budget, CLI help, fuzzy error guidance, and repo health.

Architectural impact:

- Change amplification rises: a change to skill installation can require understanding projection, plugin cache state, runtime handles, and `ask` registration.
- Local reasoning weakens: agents must inspect large files to answer small questions.
- Review quality degrades: reviewers will skim because the diff context is too large.

Confidence: High.

Recommendation:

Split by domain responsibility before adding new workflow modes:

- `ask/commands/skills.py` should become a thin command shell.
- Move catalog parity, projection sync, proof/eval, plugin cache, and installer/builder resolution into separate command service modules with explicit inputs and JSON outputs.
- Preserve current command names as compatibility wrappers while shifting logic behind deeper modules.

### Risk 2: Governance becoming ceremony

Fact:

- The repo has `harness.contract.json`, `.harness/quality/criteria.md`, `.github/workflows/pr-pipeline.yml`, `.circleci/config.yml`, docs lint, repo doctor, runtime budget, command handle validation, repo-surface inventory, memory learnings, and path ownership policy.
- `./bin/ask repo doctor --json --robot` currently blocks on catalog parity even while several other core signals pass.
- `repo_surface` reports thousands of blocking findings, mostly tracked historical artifacts.

Interpretation:

Governance is real and unusually mature, but it is at risk of outpacing the smallest reliable product loop. If checks block on surfaces that humans and agents cannot quickly interpret or fix, governance becomes drag instead of trust.

Architectural impact:

- Slower iteration.
- More time spent satisfying meta-workflows than improving skill outcomes.
- Higher chance agents bypass or cargo-cult gates.

Confidence: High.

Recommendation:

Make governance prove one thing first: "Can an agent safely find, run, modify, validate, and close out a skill change?" Treat every gate as either required for that proof or optional/advisory until it earns its place.

### Risk 3: Repository cognition debt

Fact:

- The repo intentionally tracks many docs, artifacts, generated areas, memory surfaces, and historical evidence.
- `repo doctor` reports `repo_surface` warnings with 4543 blocking findings, including tracked historical artifacts, generated work areas, ownership decisions, runtime database, and duplicated infrastructure paths.
- `Docs/agents/15-repo-surface-ownership.md` explicitly says every tracked file must have an ownership classification.

Interpretation:

The repo is trying to turn cognition into infrastructure, which is strategically interesting. But unclassified cognitive material becomes the opposite: a fog layer. The current system has the right classifier concept but too much unresolved inventory.

Architectural impact:

- Future agents over-read stale artifacts.
- Maintainers lose confidence in whether a file is source, projection, archive, fixture, or accidental debris.
- Strategic docs can drift into competing truths.

Confidence: High.

Recommendation:

Make repo-surface cleanup a first-class architecture milestone. Do not treat it as housekeeping. In this repository, file ownership is part of the product.

### Risk 4: Skill proliferation without outcome proof

Fact:

- Root skill sets include broad domains such as `agent-ops`, `frontend-ui`, `backend-platform`, `product-strategy`, `security-ops`, `content-publishing`, `mobile-native`, `skill-factory`, `plugin-factory`, and `harness-engineering`.
- `selection_policy.py` caps the visible runtime surface and defines hidden bridge/system skills.
- The current visible runtime budget passes.

Interpretation:

The repo has learned the right lesson about context budget: not every skill should be visible by default. But the next risk is hidden proliferation. A large latent catalog is still operational debt if skills overlap, route ambiguously, or lack outcome telemetry.

Architectural impact:

- Agents choose the wrong skill.
- Skill authors optimize prose instead of operational results.
- Duplicate workflows accumulate under different names.

Confidence: Medium-High.

Recommendation:

Require every skill family to earn visibility through one or more concrete outcome proofs: successful closeout examples, eval scenarios, command compatibility, ownership boundaries, and deprecation strategy for overlaps.

### Risk 5: Dual-provider CI ambiguity

Fact:

- GitHub Actions has substantial workflows including PR pipeline, security scan, skill quality, docs governance, recursive shadow checks, and graph diff.
- `.circleci/config.yml` is very small and runs `diagnose_skill.py --all`.
- `pr-pipeline.yml` includes commentary indicating some package-backed enforcement belongs to CircleCI.

Interpretation:

The split can be valid, especially if CircleCI owns heavier runtime/package checks and GitHub owns governance/security gates. But the contract needs to be extremely explicit because the current visible implementation makes GitHub look like the real system and CircleCI like a token gate.

Architectural impact:

- Required-check confusion.
- False confidence if one provider is green while the other does not exercise meaningful behavior.
- Agents may update the wrong workflow.

Confidence: Medium.

Recommendation:

Document and enforce CI ownership by capability, not provider name. Every required check should answer: what behavior does it prove, where is the source contract, and what failure should block merges?

## 3. Repository Cognition Review

This repository has unusually strong cognition surfaces:

- `AGENTS.md` provides a terse operating contract.
- `UBIQUITOUS_LANGUAGE.md` gives stable domain terms.
- `Docs/agents/README.md` and linked docs provide progressive guidance.
- `Docs/agents/14-path-ownership-boundaries.md` defines source/runtime/projection ownership.
- `Docs/agents/15-repo-surface-ownership.md` defines tracked file ownership categories.
- `.harness/memory/LEARNINGS.md` preserves learned fixes.
- `.harness/features/agent-skills-intent.md` now captures strategic intent.
- `./bin/ask repo doctor --json --robot` provides machine-readable repo health.

That is ahead of normal 2026 repository practice. Most codebases still treat agent cognition as incidental markdown. This one treats it as a governed runtime surface.

The problem is density and competing authority.

The repo has many maps, contracts, validators, reports, artifacts, and docs. The architecture is discoverable if the reader already knows to use `./bin/ask`, `UBIQUITOUS_LANGUAGE.md`, and `Docs/agents/README.md`. It is much less discoverable if the reader starts from arbitrary files or generated projections.

From a Pragmatic Programmer lens, the repo has excellent automation intent but visible broken windows:

- unresolved catalog parity;
- repo-surface findings;
- stale/legacy references;
- large orchestrators;
- generated/runtime artifacts that must be classified rather than ignored.

From a Philosophy of Software Design lens, the cognition system is deep in concept but shallow in some access paths. A great cognition system lets agents know less. Here, agents still need to know a lot: which plane owns which path, which docs are binding, which skill tree is canonical, which generated handle is just a pointer, and which CI provider owns which check.

Operational recommendation:

Create one "fresh agent golden path" document or command output that answers five questions in under two minutes:

1. What is canonical source?
2. What is generated/runtime projection?
3. How do I find the right skill?
4. How do I validate a change?
5. What must never be edited directly?

`AGENTS.md` and `./bin/ask repo doctor` are close. The missing part is a human-and-agent readable synthesis that is automatically checked against live command outputs.

## 4. Complexity Audit

### Intentional complexity

The following complexity appears justified:

- Source/projection/runtime separation. This prevents agents from editing generated runtime surfaces and makes local runtime synchronization possible.
- Runtime surface budgeting. Without it, visible skill count and prompt token cost would grow until agents degrade.
- Generated command handles. These reduce invocation friction while preserving canonical ownership elsewhere.
- Catalog parity and path ownership checks. These protect the central promise that skill sources and runtime projections remain aligned.
- Docs lint and instruction routing. This repo is instruction-heavy by design; docs are operational code.
- Plugin cache and runtime mirror concepts. Plugin ecosystems need anti-corruption boundaries between bundled/cache state and editable source.

### Accidental complexity

The following complexity appears accidental or at least insufficiently compressed:

- `skills.py` doing too many jobs.
- `Infrastructure/bin/ask` combining front controller, command table, error correction, imports, dispatch, and some UX logic.
- Multiple legacy/compatibility references without a visible expiry policy.
- CI split that is more complicated than the visible check responsibility explains.
- Historical artifact retention that appears to exceed current repo-cognition value.
- Overlapping skill families whose boundaries are partly policy-defined and partly name-driven.

### Complexity that may be strategic but is not yet proven

- Multi-agent/harness workflow governance.
- Deep plugin lifecycle machinery.
- Large-scale skill family benchmarks.
- Repo-level memory and Project Brain integration.
- Review swarm and artifact-first governance.

These are plausible leverage, but the proof standard should be stricter: show that these systems reduce regression rate, reduce time to correct skill selection, or increase successful autonomous closeout.

## 5. Deep vs Shallow Module Analysis

### Deep modules

#### `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`

Fact:

- Defines root skill sets, default visible skills, policy version, projection modes, plugin root glob, hidden bridge skills, and policy identity hashing.

Interpretation:

This is a genuinely deep module. It compresses context-selection policy into a small, inspectable boundary. Callers do not need to rediscover the default visible surface or root skill families.

Risk:

Policy constants can become a dumping ground if every exception is added here.

Preserve:

- explicit versioning;
- small public surface;
- deterministic identity hash;
- visible/hidden distinction.

#### `Infrastructure/scripts/lifecycle-and-sync/command_surface.py`

Fact:

- Defines `CommandHandle`, handle validation, mention resolution, generated handle rendering, folded aliases, runtime handle reports, and handle budget validation.
- Generated handle bodies explicitly say the real workflow is elsewhere and point to canonical source paths plus `./bin/ask skills resolve`.

Interpretation:

This is one of the repo's best architectural modules. It makes generated handles intentionally shallow while preserving a deep ownership boundary. It is an anti-corruption layer between human/agent invocation syntax and canonical skill sources.

Risk:

The module is already 726 lines. If it starts owning skill discovery or projection sync, it will lose its depth.

Preserve:

- handles as pointers, not logic;
- deterministic validation;
- generated text that discourages editing runtime projections.

#### `repo doctor` signal composition in `Infrastructure/scripts/lib/ask/commands/repo.py`

Fact:

- Builds signals from repo status, projection sync, catalog parity, runtime budget, command handles, and repo surface, then emits a golden-path payload.

Interpretation:

This is a tracer-bullet architecture: a single command proves the major operating assumptions. It is valuable because it is machine-readable and maps scattered governance into one operational health check.

Risk:

The file also contains many other repo command responsibilities. The `doctor` concept should be preserved even if the module is split.

Preserve:

- signal names;
- JSON output;
- next-action guidance;
- pass/warn/block classification.

### Shallow or overloaded modules

#### `Infrastructure/scripts/lib/ask/commands/skills.py`

Fact:

- 3001 lines.
- Imports skill discovery, plugin cache state, projection sync, command surface, root skill sets, manifests, rooted runtime, catalog parity, analytics, benchmarks, dynamic module loading, installer/builder paths, and more.

Interpretation:

This is the most important complexity hotspot. It is not one module. It is several bounded contexts sharing one file.

Architectural smell:

- God command module.
- Mixed abstraction levels.
- Hidden temporal coupling between discovery, projection, cache, proof, and runtime handle behavior.
- High change amplification.

Refactor seam:

Extract around stable nouns:

- `skill_catalog_service`;
- `skill_projection_service`;
- `plugin_cache_service`;
- `skill_proof_service`;
- `skill_audit_service`;
- `skill_command_rendering`;
- `skill_resolution_service`.

Do not start by changing behavior. Start by moving pure or near-pure helper clusters behind explicit functions and test them.

#### `Infrastructure/bin/ask`

Fact:

- 1900 lines.
- Extends `sys.path`, imports many command functions, defines fuzzy correction helpers, error mapping, and CLI behavior.

Interpretation:

The CLI is valuable as a single front door. But the implementation is larger and more coupled than the interface needs to be. This is a shallow shell becoming a central nervous system.

Refactor seam:

Keep `./bin/ask` as the stable executable. Move command registry, correction UX, parser construction, and command invocation into importable modules.

#### `.circleci/config.yml`

Fact:

- 26 lines.
- Runs one diagnose command.

Interpretation:

As a module in the CI architecture, this is shallow relative to the apparent dual-provider governance story. It may be acceptable if CircleCI is intentionally a narrow smoke gate. If it is supposed to own package-backed enforcement, it is underbuilt.

Decision needed:

Either document it as a narrow smoke/provenance check or move meaningful CircleCI-owned validation into it.

## 6. Domain Integrity Review

The repo has a coherent domain model, but several bounded contexts are bleeding together.

### Strong domain language

Verified terms:

- Agent Skills Kit.
- `ask` CLI.
- Canonical Skill Source.
- Runtime Projection.
- Generated Command Handle.
- User Runtime Links.
- Plugin Runtime Mirror.
- Workspace/User Sync.
- Visible Runtime Surface.
- Strict Skill Audit.

These are good DDD terms because they describe stable responsibilities, not implementation accidents.

### Likely bounded contexts

#### Skill Authoring Context

Primary surfaces:

- `Skills/**/SKILL.md`;
- `Skills/agent-ops/**`;
- `Plugins/skill-factory/**`;
- skill audit commands;
- line-budget and strict audit docs.

Core model:

- a skill is a bounded operational instruction package with triggers, progressive disclosure, and validation expectations.

Risk:

Skill authoring and runtime projection leak into each other when agents inspect generated `.agents/skills/**` surfaces as if they were editable source.

#### Runtime Projection Context

Primary surfaces:

- `.agents/skills/**`;
- command handles;
- `Infrastructure/scripts/lifecycle-and-sync/**`;
- projection sync commands.

Core model:

- runtime surfaces are generated views optimized for agent discovery and context budget, not source of truth.

Risk:

If runtime projections are tracked or edited without ownership clarity, the model collapses.

#### Governance and Validation Context

Primary surfaces:

- `harness.contract.json`;
- `.github/workflows/**`;
- `.circleci/config.yml`;
- `Infrastructure/scripts/validate_all.sh`;
- `Infrastructure/scripts/verify-work.sh`;
- docs lint;
- repo doctor.

Core model:

- gates protect source/projection parity, docs truth, runtime budget, and workflow safety.

Risk:

Governance terms become overloaded: "validate", "doctor", "audit", "check", "proof", and "diagnose" need crisp differences.

#### Plugin Lifecycle Context

Primary surfaces:

- `Plugins/plugin-factory/**`;
- `Plugins/skill-factory/**`;
- `Plugins/cache/**`;
- plugin runtime mirror docs and commands.

Core model:

- plugins bring packaged capability sets into a local skill runtime while preserving source/cache/mirror boundaries.

Risk:

Plugin cache handling and skill command handling currently appear inside large shared orchestration modules, weakening the bounded context.

#### Evidence and Proof Context

Primary surfaces:

- `Workouts/**` where present;
- skill eval tooling;
- `.harness/quality/criteria.md`;
- benchmark policy refresh;
- docs/governance checks;
- memory learnings.

Core model:

- capabilities become trusted when they have operational proof, not just author intent.

Risk:

This is the most strategically important context, but it is not yet the most obvious product surface.

### Domain fractures

The following language areas need tightening:

- `proof`, `prove`, `audit`, `diagnose`, and `doctor`.
- `skill`, `plugin`, `command handle`, `root skill set`, and `runtime projection`.
- `generated`, `cache`, `mirror`, `projection`, and `runtime`.
- `legacy`, `compat`, `archive`, and `fixture`.

Recommendation:

Add a domain glossary check to docs lint for overloaded terms. This does not need to be sophisticated. Even a curated term map with "allowed meanings" would reduce drift.

## 7. Skill/Plugin Architecture Review

### What works

The skill architecture has a real agent-native shape:

- root skill sets keep default context small;
- individual skills use `SKILL.md` as the entrypoint;
- skills reference scripts and examples rather than embedding everything in prompt text;
- command handles reduce invocation friction;
- runtime projections separate discovery from canonical editing;
- plugins provide bundled skills without forcing all plugin content into root context.

The selection policy is especially strong. It encodes the idea that agent capability must be discoverable but not always loaded. That is a 2026-standard agent architecture principle, and this repo is ahead of most peers here.

### What is fragile

Skill/plugin composability is still partly dependent on naming and discipline rather than hard interfaces.

Fragility signals:

- broad `agent-ops` surface contains many operational, language, validation, workflow, and governance skills;
- plugin-factory and skill-factory are conceptually adjacent and easy to confuse;
- hidden bridge/system skills are policy-defined rather than discoverable as a separate typed domain;
- generated handles can point well, but overlapping skills can still make initial choice ambiguous;
- plugin cache refresh and skill handling appear coupled in `skills.py`.

### Strategic read

The skill system's defensible value is not "we have many skills." Many skills are easy to write and easy to copy badly.

The defensible value is:

- skill selection discipline;
- runtime budget discipline;
- source/projection anti-drift;
- proof-backed skill promotion;
- operational learnings attached to skill evolution;
- command and validation surfaces that agents can execute deterministically.

The architecture should keep the broad workbench ambition, but it should promote fewer, sharper, better-proven skills into the trusted core. Breadth is useful as exploration and distribution; proof is what makes the platform trustworthy.

## 8. Agent-Native Capability Review

### Ahead of current standards

The repo is ahead of normal May 2026 practice in these areas:

- machine-readable repo health via `./bin/ask repo doctor --json --robot`;
- generated command handles;
- visible runtime budget;
- path ownership boundaries;
- source/projection separation;
- docs-as-operational-contract;
- memory/learned-fix surfaces;
- skill discoverability with progressive disclosure;
- validation command contracts;
- command-line front door designed for agents.

### Aligned with current standards

The repo is aligned with good current practice in:

- CI-based docs and governance checks;
- pinned GitHub Actions;
- security-oriented workflow surfaces;
- root wrapper command instead of scattered package scripts;
- JSON/robot modes;
- warning/blocker classification.

### Lagging or strained

The repo lags or strains in:

- typed boundaries inside the Python command modules;
- small local reasoning units;
- proof/eval outcome visibility;
- repo-surface noise;
- CI ownership clarity;
- onboarding path for a fresh agent;
- structural tests around command services;
- deprecation and compatibility expiry policy.

### Real or performative?

The agent-native model is real.

Evidence:

- Agents are expected to operate through `./bin/ask`.
- Commands expose JSON/robot outputs.
- Runtime surfaces are budgeted.
- Generated handles are explicitly designed to point to canonical skill sources.
- Docs and AGENTS instructions tell agents what is source versus projection.
- Validation gates are built around drift and agent-facing surfaces.

But the model is not yet ergonomic enough.

A genuinely mature agent-native repo should let a competent fresh agent make a safe small change after loading only a few small surfaces. This repo is close conceptually, but the actual path still asks the agent to navigate a lot of policy, docs, skill families, and large command modules.

## 9. Governance & Workflow Review

### Strengths

The governance model is serious:

- `AGENTS.md` defines root command expectations.
- `harness.contract.json` encodes branch protection, memory policy, observability, and CI provider policy.
- `.harness/quality/criteria.md` defines quality criteria.
- docs lint passes across 177 files.
- repo doctor composes multiple health signals.
- GitHub Actions includes PR template, risk policy, dependency review, actions pinning, consistency drift, docs governance, skill quality, security, and graph checks.
- `Docs/agents/04-validation.md` documents validation scope.

### Weaknesses

Governance is not fully self-explaining:

- The difference between GitHub Actions and CircleCI responsibilities is not obvious from the workflow sizes.
- Some gates defer or warn in ways that may be valid but need careful expectation-setting.
- Catalog parity currently blocks.
- Repo surface ownership is conceptually excellent but operationally noisy.

### XP lens

The project has feedback loops, but some are too heavy:

- Tight loop: `./bin/ask repo doctor --json --robot`.
- Tight loop: docs lint.
- Medium loop: `verify-work --fast`.
- Heavy loop: full `validate_all.sh`.
- Noisy loop: repo-surface inventory until backlog is classified.

XP would push the architecture toward smaller, more frequent, safer feedback. The repo should treat full validation as a release confidence layer, not the only meaningful signal. `repo doctor` should become the daily loop and should recommend the smallest next fix.

## 10. Refactor Recommendations

### 1. Split `skills.py` by bounded context

Priority: Critical.

First extraction:

- Move plugin cache refresh/report/error code into `ask/services/plugin_cache.py`.
- Move dynamic skill-builder/installer path lookup into `ask/services/skill_tool_resolution.py`.
- Move catalog parity logic behind `ask/services/skill_catalog.py`.
- Keep CLI functions in `ask/commands/skills.py` as thin adapters.

Why:

This reduces change amplification and gives agents smaller files to inspect.

Validation:

- existing skill list/resolve/audit commands;
- catalog parity doctor signal;
- runtime budget command;
- command handle validation.

### 2. Shrink `Infrastructure/bin/ask`

Priority: High.

First extraction:

- command registry module;
- parser construction module;
- fuzzy error/correction module;
- invocation wrapper module.

Keep:

- the `./bin/ask` executable path;
- current CLI behavior;
- current `--json`/`--robot` contracts.

Why:

The front door should stay stable while its implementation becomes boring.

### 3. Promote repo doctor to the canonical agent entrypoint

Priority: High.

Add:

- `./bin/ask repo doctor --next` or equivalent that prints only the highest-priority corrective action;
- docs link from `AGENTS.md`;
- CI artifact that preserves doctor output.

Why:

Agents need one command that tells them what is true now.

### 4. Make repo-surface cleanup architectural, not janitorial

Priority: High.

Create tracked categories:

- canonical source;
- generated but owned;
- fixture;
- historical archive;
- runtime state;
- deletion candidate;
- migration pending.

Then enforce thresholds:

- 0 tracked runtime databases;
- 0 duplicated infrastructure paths unless explicitly classified;
- generated work areas must be ignored, owned, or regenerated from source;
- historical artifacts require an index and retention reason.

### 5. Add deprecation budgets

Priority: Medium.

For each `legacy`, `compat`, or fallback path:

- owner;
- reason;
- removal condition;
- max age;
- validation coverage.

Why:

Without expiry, compatibility code becomes permanent architecture.

### 6. Make skill promotion outcome-based

Priority: Medium-High.

Require for core/default-visible skills:

- command handle;
- validation command;
- one successful closeout example;
- one failure-mode note;
- one eval or deterministic proof where possible;
- overlap check against neighboring skills.

Why:

This turns the catalog into a quality system rather than a library of promising prompts.

## 11. Anti-Patterns Identified

### God command module

Location:

- `Infrastructure/scripts/lib/ask/commands/skills.py`.

Impact:

- high cognitive load;
- risky edits;
- unclear bounded contexts.

### Front-controller accretion

Location:

- `Infrastructure/bin/ask`.

Impact:

- central file becomes harder to test and reason about.

### Governance without proportional proof

Location:

- `.github/workflows/**`;
- `harness.contract.json`;
- `.harness/quality/criteria.md`;
- repo-surface inventory.

Impact:

- risk of ceremony exceeding reliable product behavior.

### Artifact hoarding

Location:

- repo-surface findings;
- `.harness/**`;
- `Infrastructure/artifacts/**` where tracked or referenced;
- historical generated reports.

Impact:

- stale evidence competes with live truth.

### Compatibility permanence

Location:

- legacy/compat/fallback references in scripts and docs.

Impact:

- old architecture never dies, it just gains new adapters.

### Domain overload

Terms:

- proof/prove/audit/doctor/diagnose;
- skill/plugin/handle/projection;
- cache/mirror/runtime/generated.

Impact:

- future agents will make plausible but wrong edits.

## 12. Drift Risks

### Drift Signal 1: Increasing command-module size

Why it matters:

Large command modules undermine local reasoning and invite tactical patches.

Likely root cause:

Adding new workflows directly to `ask/commands/*.py` because it is convenient.

Operational impact:

Agents need more context, reviews become weaker, tests become broader and slower.

Severity:

High.

Threshold:

- Any command module above 1200 lines requires an extraction plan.
- Any module above 2000 lines blocks new feature logic except extraction work.

Corrective action:

Extract services by bounded context.

Should block merges:

Yes for new feature logic added to `skills.py` without extraction.

### Drift Signal 2: Catalog parity remains blocking

Why it matters:

The repo's source/projection thesis depends on parity.

Likely root cause:

Generated/runtime updates not synchronized with canonical sources or manifest changes.

Operational impact:

Agents cannot trust discovery surfaces.

Severity:

High.

Threshold:

- Any `catalog_parity` block should block release.
- More than 24 hours of main-branch parity drift should trigger owner review.

Corrective action:

Run the specific doctor-catalog next action, fix source/projection mismatch, document root cause if recurrent.

Should block merges:

Yes.

### Drift Signal 3: Repo-surface findings keep rising

Why it matters:

Repository cognition is part of the product.

Likely root cause:

Artifacts and generated outputs are committed without ownership classification.

Operational impact:

Fresh agents cannot distinguish live source from stale evidence.

Severity:

High.

Threshold:

- 0 tracked runtime databases.
- 0 duplicated infrastructure paths unless classified.
- Historical artifacts above 500 tracked paths require an archive/index decision.
- Any increase in unclassified generated work areas blocks release.

Corrective action:

Classify, ignore, archive, or delete. Do not leave "temporary" tracked outputs.

Should block merges:

Yes for new unclassified artifacts.

### Drift Signal 4: Prompt growth replaces harness improvement

Why it matters:

This repo's value is operational execution, not longer instructions.

Likely root cause:

Fixing agent failures by adding prose instead of changing tools, validators, or command outputs.

Operational impact:

Token cost rises while reliability may not improve.

Severity:

Medium-High.

Threshold:

- Any skill grows beyond budget without a new command, script, eval, or proof artifact.
- Default visible runtime token estimate grows without measured routing improvement.

Corrective action:

Move repeated instruction into scripts, validators, command output, or examples.

Should block merges:

Usually warn; block if default visible runtime budget regresses.

### Drift Signal 5: Skills overlap without routing proof

Why it matters:

Ambiguous skills waste context and cause wrong workflows.

Likely root cause:

Creating new skills for every task type without consolidation.

Operational impact:

Agents choose by keyword rather than domain boundary.

Severity:

Medium-High.

Threshold:

- More than three skills with the same trigger noun require consolidation review.
- Any default-visible skill must have an overlap note.

Corrective action:

Consolidate, fold, or add routing boundaries and examples.

Should block merges:

Block for new default-visible skills; warn for latent skills.

### Drift Signal 6: CI ownership becomes unclear

Why it matters:

Governance only works if failures map to responsibility.

Likely root cause:

Adding checks wherever convenient.

Operational impact:

Agents update the wrong workflow or treat advisory checks as blocking.

Severity:

Medium.

Threshold:

- Every required check must map to one source contract and one owning workflow.
- Provider split must be documented when both GitHub Actions and CircleCI cover the same domain.

Corrective action:

Use CI check-name parity and update provider ownership docs.

Should block merges:

Yes when required checks change.

### Drift Signal 7: Compatibility layers lack expiry

Why it matters:

Permanent compatibility code multiplies paths.

Likely root cause:

Avoiding breaking changes without scheduling deletion.

Operational impact:

More hidden branches and unknown unknowns.

Severity:

Medium.

Threshold:

- Every legacy/compat path needs owner, removal condition, and validation coverage.

Corrective action:

Add deprecation manifest and enforce stale entries.

Should block merges:

Warn initially; block after policy adoption.

## 13. Technical Debt Hotspots

### Technical debt hotspot: `Infrastructure/scripts/lib/ask/commands/skills.py`

Debt type:

- orchestration sprawl;
- hidden coupling;
- mixed bounded contexts.

Why it matters:

This file is central to the product. If it remains the place where every skill-related concept lands, the repo will become less agent-operable over time.

### Technical debt hotspot: `Infrastructure/bin/ask`

Debt type:

- front-controller accretion.

Why it matters:

`./bin/ask` is the golden path. Its implementation should be small enough that command behavior can be changed safely.

### Repo-surface inventory backlog

Debt type:

- cognition debt;
- ownership ambiguity.

Why it matters:

Unclassified files create hallucination fuel for future agents.

### CI provider split

Debt type:

- governance ambiguity.

Why it matters:

If required checks are not obviously owned, workflow edits become risky.

### Legacy/compat references

Debt type:

- temporal coupling;
- stale architecture.

Why it matters:

They keep old models alive after the domain has moved on.

### `validate_all.sh`

Debt type:

- large shell gate.

Why it matters:

It is probably useful, but at 636 lines it should be treated as a critical system with modular subchecks, clear failure classes, and fast focused equivalents.

## 14. Strategic Review

Here is the direct answer.

The project is coherent. It is not a pile of random skills. It is a serious attempt to build an agent-operable capability control plane.

The complexity is partly justified. Source/projection separation, command handles, runtime budgets, path ownership, and repo doctor are all real leverage. They solve problems that appear once agents start operating a repo repeatedly.

The complexity is also partly self-inflicted. The giant command modules, artifact backlog, legacy compatibility, and broad governance matrix are not moat by themselves. They are carrying cost. Some of them are necessary scaffolding. Some of them are just accumulated motion.

The architecture is pragmatic at the boundaries and tactical in the internals. The boundary ideas are good: one CLI, canonical source, generated runtime projection, validation contracts, visible budgets, docs as control surfaces. The internal implementation needs more deep modules and fewer command files that know everything.

The abstraction quality is uneven:

- High: selection policy, command surface, path ownership language, repo doctor signal model.
- Medium: validation wrappers and docs governance.
- Low: large command modules and compatibility clusters.

The project is solving a real problem. Agent workflows do need capability discovery, routing, validation, context budgeting, and anti-drift. This is not imaginary.

The governance is helping, but it is close to slowing things down. It becomes leverage only when each gate has a clear proof target and a quick fix path. It becomes drag when it produces red lights that require archaeology.

What creates leverage:

- deterministic `ask` commands;
- generated handles;
- runtime budget;
- source/projection separation;
- path ownership;
- repo doctor;
- learned-fix memory;
- proof/eval loops;
- skill promotion discipline.

What creates drag:

- giant orchestrators;
- unclassified artifacts;
- overlapping skills;
- ambiguous legacy compatibility;
- dual CI ownership that is not self-evident;
- too many docs that are accurate individually but expensive collectively.

What should be deleted:

- tracked runtime databases;
- unclassified generated work areas;
- historical artifacts without indexed retrieval value;
- compatibility paths with no owner or removal condition;
- duplicate infrastructure paths after source ownership is proven;
- low-use skills that cannot produce outcome proof.

What should become core:

- `repo doctor` as the agent entrypoint;
- skill outcome proof;
- command-handle resolution;
- source/projection parity;
- runtime-surface budget;
- repo-surface ownership;
- fresh-agent onboarding path.

The smallest compelling version inside the hybrid strategy:

1. Ten high-value skills.
2. One `./bin/ask` front door.
3. Generated handles for those skills.
4. Source/projection sync.
5. Runtime budget.
6. `repo doctor`.
7. One proof artifact per skill showing it improves agent closeout.

Everything else should justify itself against that loop. The broader workbench can exist around it, but it should be treated as an exploration layer until individual workflows earn core status.

Will developers adopt this?

Not in its current full complexity as a first experience. Expert agent builders will respect it. Normal developers will bounce unless the golden path is much smaller and the value appears in minutes. Adoption depends on presenting the control plane as a small reliable workflow, not as a whole civilization of governance.

Does this improve cognition or worsen it?

Both. The underlying concepts improve cognition. The current surface area can worsen it. The next phase should be cognition compression.

Is it anti-fragile or brittle?

The architecture has anti-fragile ingredients: validation, memory, proofs, command handles, drift detection. The implementation still has brittle concentration points. It becomes anti-fragile only if failures produce smaller, clearer modules and better proof loops instead of more prose.

If the project fails, it will fail because it becomes an expert-only governance system that cannot prove it makes agents faster, safer, or more reliable.

If it succeeds, it will succeed because it becomes both a productive skill/plugin workbench and the best local control plane for turning messy human/agent workflows into discoverable, validated, outcome-proven skills. The workbench creates reach; the control plane creates trust.

## 15. Recommended Simplifications

1. Make `repo doctor` the front door for all repo health questions.

2. Split command modules before adding major new workflows.

3. Reduce docs entrypoints to a small live chain:

- `AGENTS.md`;
- `UBIQUITOUS_LANGUAGE.md`;
- `Docs/agents/README.md`;
- `Docs/agents/14-path-ownership-boundaries.md`;
- validation guide.

4. Move repeated prose into command output or validators.

5. Collapse overlapping skill triggers.

6. Treat generated handle text as intentionally boring.

7. Add an expiry manifest for compatibility paths.

8. Turn repo-surface inventory into a visible burn-down with thresholds.

9. Define CI ownership by proven behavior.

10. Promote only outcome-proven skills into default visibility.

## 16. Recommended Deletions

Deletion candidates must be verified before removal. Do not bulk-delete from this review alone.

Recommended deletion classes:

- tracked runtime database files;
- unclassified generated work areas;
- duplicate infrastructure paths after ownership mapping;
- historical artifacts that are neither indexed nor used by a current validator;
- compatibility scripts with no current caller;
- stale docs that duplicate a canonical instruction map;
- low-signal benchmark/report artifacts that cannot influence a decision;
- skill aliases that no longer resolve to distinct workflows;
- redundant workflow files that prove the same behavior with weaker signal.

Deletion policy:

- classify first;
- prove no current caller;
- remove or archive;
- update doctor/repo-surface inventory;
- record the decision in `.harness/decisions/**` or the repo's chosen decision surface.

## 17. Recommended Core Investments

### Outcome proof system

Make outcome proof the center of the project.

Metrics:

- skill chosen correctly;
- task completed;
- validation passed;
- time/context cost;
- failure mode captured;
- regression avoided.

### Fresh-agent onboarding

Build an executable onboarding path:

- `./bin/ask repo orient --json --robot`;
- top commands;
- source/projection warning;
- current blockers;
- safest next action.

### Command service extraction

Invest in deep modules under `ask/services/**` before expanding features.

### Skill overlap analytics

Detect overlapping triggers and route ambiguity.

### CI ownership map

Generate a required-check map from source contracts.

### Repository surface burn-down

Make file ownership classification part of release readiness.

## 18. Long-Term Scalability Risks

### Human scalability

Risk:

Only Jamie or a small set of expert agents can safely operate the full system.

Mitigation:

Executable orientation, fewer entrypoints, better service boundaries, and deletion of stale artifacts.

### Agent scalability

Risk:

Agents load too much context, choose ambiguous skills, or patch generated surfaces.

Mitigation:

Runtime budget enforcement, generated-handle warnings, skill overlap checks, source/projection guards.

### Governance scalability

Risk:

Checks multiply until the system is slower than the work.

Mitigation:

Every check must declare proof target, owner, failure action, and merge-blocking status.

### Plugin ecosystem scalability

Risk:

Plugin cache/mirror/source boundaries become unclear as external plugin count grows.

Mitigation:

Plugin anti-corruption layer, cache ownership docs, plugin proof contract.

### Strategic scalability

Risk:

The project scales breadth without making proof the promotion mechanism.

Mitigation:

Keep catalog expansion, but separate experimental breadth from trusted core. Core promotion should require proof.

## 19. Moat Analysis

### What is the actual moat?

The actual moat is operational, not merely technical:

- local-first agent workflow discipline;
- source/projection/runtime separation;
- generated command handles;
- context-budget control;
- validation and anti-drift loops;
- accumulated learned fixes;
- outcome-proven skill workflows;
- a broad workbench whose breadth is filtered through proof, validation, and runtime budget discipline;
- repository cognition quality;
- developer habit formation around `./bin/ask`.

The moat is not:

- having many skills without proof;
- having many docs;
- having complex CI;
- using AI terminology;
- having plugin folders;
- having a big CLI.

### Is the moat durable?

Medium, but only if outcome proof becomes the promotion mechanism for the broad platform.

The architecture can become durable because workflow memory, validation habits, a broad workbench surface, and trusted local control planes compound over time. But without measurable outcome proof, competitors can copy the visible structure and present a cleaner developer experience.

### Is the moat measurable?

It can be, but the repo should measure it more directly.

Useful moat metrics:

- percentage of tasks where agents select the correct skill on first attempt;
- skill-run closeout success rate;
- validation pass rate after agent edits;
- context tokens loaded per successful task;
- number of regressions caught by repo doctor before CI;
- time for a fresh agent to make a safe skill edit;
- number of core skills with proof artifacts;
- catalog parity drift duration;
- repo-surface unclassified count;
- deprecation backlog age.

### Is the moat merely complexity?

Partly, today.

The architecture contains real leverage, but some of the moat currently looks like complexity because the proof loop is not visible enough. Complexity becomes moat only when it produces reliability competitors cannot easily match. Otherwise it is just adoption friction.

### Could a smaller competitor rebuild this quickly?

A smaller competitor could rebuild the visible shell quickly:

- skill folders;
- generated command handles;
- a CLI;
- docs lint;
- basic sync;
- a few CI checks.

They could not quickly rebuild the lived operational memory, governance lessons, workflow taxonomy, and proof corpus if this repo curates those aggressively.

If this repo stays noisy, a smaller competitor can beat it with less machinery and a sharper golden path.

### Strategically defensible parts

- Outcome-proven skill workflows.
- Source/projection/runtime boundary discipline.
- Runtime context budget and selection policy.
- Repo doctor as an agent health protocol.
- Learned-fix memory connected to validation.
- Skill/plugin anti-corruption boundaries.
- Developer trust in `./bin/ask`.

### Parts that only feel sophisticated

- Large command modules.
- Extensive docs that are not attached to checks.
- CI breadth without clear ownership.
- Skill catalog breadth without usage/proof.
- Legacy compatibility layers without expiry.
- Historical artifacts without retrieval value.

### What should be aggressively protected?

- `./bin/ask` command contract.
- Source/projection separation.
- Command handle determinism.
- Visible runtime budget.
- Catalog parity.
- Path ownership classification.
- Outcome proof artifacts.
- Ubiquitous language.

### What should be simplified because it weakens the moat?

- Giant command modules.
- Unclassified historical artifacts.
- Overlapping skills.
- Ambiguous CI provider split.
- Redundant docs.
- Compatibility paths with no expiry.

### Likely false moat assumptions

- "More skills means more value."
- "More governance means more trust."
- "Technical sophistication is defensibility."
- "A local-first control plane will be adopted just because it is powerful."
- "Agents can navigate the same complexity the author can."

### If this succeeds massively

Competitors will struggle because the project will have accumulated a trusted corpus of agent workflows, validation rules, failure memories, and local runtime contracts that reliably improve developer outcomes. The hard part will be social and operational: trust, habit, proof, and continual simplification.

### If competitors catch up quickly

They will catch up because they choose the smaller compelling version, make it easy to adopt, and avoid carrying historical complexity. They will copy the concepts and beat the experience.

## 20. Competitive Replication Risk

Replication risk is high for the visible architecture and medium for the operational system.

Easy to copy:

- markdown skill format;
- root skill categories;
- generated command handles;
- basic CLI;
- docs lints;
- source/projection naming;
- GitHub workflow gates.

Harder to copy:

- lived taxonomy of agent failure modes;
- mature path ownership rules;
- robust runtime budget policy;
- reliable skill selection data;
- closeout proof history;
- developer trust in the local command surface;
- governance that catches real drift without slowing every change.

The repo should assume any visible mechanism can be cloned. The durable advantage must be data and discipline: proof that the mechanism works, and a lower-friction path for future agents to use it.

## 21. Evidence & Traceability Matrix

| Conclusion | Evidence category | File paths / surfaces | Symbols, interfaces, components | Runtime behavior observed | Confidence | Why it matters |
|---|---|---|---|---|---|---|
| The repo is a local-first agent skill control plane, not just a skill library. | docs, source-code, runtime flow | `AGENTS.md`, `UBIQUITOUS_LANGUAGE.md`, `Docs/agents/14-path-ownership-boundaries.md`, `Infrastructure/bin/ask` | `./bin/ask`, Canonical Skill Source, Runtime Projection, Generated Command Handle | `./bin/ask repo doctor --json --robot` emits multi-signal health payload | High | Establishes the actual domain and prevents treating this as generic documentation. |
| Source/projection/runtime separation is intentional architecture. | docs, source-code, naming patterns | `UBIQUITOUS_LANGUAGE.md`, `Docs/agents/14-path-ownership-boundaries.md`, `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` | generated handles, runtime projections, canonical source paths | projection sync signal passed in repo doctor | High | This is one of the repository's most important stability boundaries. |
| Command handles are a deep anti-corruption layer when kept as pointers. | source-code, runtime paths | `Infrastructure/scripts/lifecycle-and-sync/command_surface.py` | `CommandHandle`, handle regex, generated handle rendering, handle validation | command handle signal passed with 93 handles and 0 violations | High | Handles reduce agent friction while preserving canonical ownership. |
| Selection policy is a strong deep module. | source-code, dependency graph | `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py` | root skill sets, visible skill names, `policy_identity()` | runtime budget passed with 10 visible defaults and estimated 3172 description tokens | High | It compresses context-budget and visibility policy into one small boundary. |
| `skills.py` is a high-risk god command module. | source-code, architectural coupling | `Infrastructure/scripts/lib/ask/commands/skills.py` | skill discovery, plugin cache, projection sync, analytics, dynamic loading | `wc -l` reports 3001 lines | High | It concentrates too many bounded contexts and raises change amplification. |
| `Infrastructure/bin/ask` should stay stable but shrink internally. | source-code, developer workflow | `Infrastructure/bin/ask` | CLI front door, imports, parser/dispatch, fuzzy errors | `wc -l` reports 1900 lines | High | The repo's main agent interface should be easier to reason about and test. |
| Repo doctor is a valuable tracer-bullet architecture. | source-code, runtime flow | `Infrastructure/scripts/lib/ask/commands/repo.py` | `repo_doctor`, signal builders, golden-path payload | doctor produced pass/warn/block signals and next action | High | It gives agents one machine-readable truth surface for repo health. |
| Catalog parity drift currently undermines the central thesis. | runtime flow, validation | `./bin/ask repo doctor --json --robot`, catalog parity command path | `catalog_parity.count_mismatch`, `doctor-catalog` next action | doctor exited 2 with catalog parity block | High | Source/projection trust depends on parity being green or quickly fixable. |
| Repo-surface debt is a strategic risk, not ordinary cleanup. | runtime flow, docs, governance | `Docs/agents/15-repo-surface-ownership.md`, repo doctor output | repo surface ownership categories | doctor reported 4543 blocking findings, including historical artifacts and ownership decisions | High | File ownership is part of the agent cognition product. |
| Docs governance is relatively mature. | docs, validation | `Infrastructure/scripts/docs_lint.py`, `Infrastructure/docs-policy.json`, `Docs/**` | docs lint policy | docs lint scanned 177 files with 0 errors and 0 warnings | High | Accurate docs are operational code in this repo. |
| CI is serious but ownership is not obvious enough. | CI/CD, governance | `.github/workflows/pr-pipeline.yml`, `.circleci/config.yml`, `harness.contract.json` | PR pipeline gates, CircleCI diagnose job | GitHub workflow is 552 lines; CircleCI config is 26 lines | Medium | Provider split can confuse agents unless mapped by proven behavior. |
| The skill/plugin architecture is genuinely agent-native. | skills, plugins, runtime paths | `Skills/**/SKILL.md`, `Plugins/**/skills/**`, `selection_policy.py`, `command_surface.py` | root skills, plugin skills, hidden bridge skills, generated handles | runtime budget and handles pass | High | Distinguishes real operational design from AI-themed prompt storage. |
| The system still has discoverability risk. | docs, naming patterns, source-code | `Docs/agents/**`, `Skills/**`, `Plugins/**`, `ask` modules | many skill families, many routing docs, generated/runtime/source distinctions | large docs and command surfaces observed | Medium-High | Fresh agents may need too much context before safe action. |
| The real moat is broad skill/plugin capability constrained by operational proof, not catalog breadth alone. | interpretation, strategic analysis | `.harness/quality/criteria.md`, `repo doctor`, skill/proof/eval surfaces, `selection_policy.py` | quality criteria, runtime budget, learned fixes, skill validation, visible skill policy | proof/eval machinery exists but is not yet the obvious center | Medium | Preserves the hybrid platform ambition while preventing investment in visible complexity instead of compounding reliability. |
| Legacy/compatibility paths need expiry. | source-code, docs, naming patterns | `Infrastructure/**`, `Docs/**`, `.harness/restore-manifest.json` | legacy/compat/fallback references | TODO/legacy scan found many references, especially in Infrastructure | Medium-High | Permanent compatibility layers create hidden branching and tactical design. |
| Governance is close to becoming heavy. | CI/CD, validation, docs | `.github/workflows/**`, `.circleci/config.yml`, `harness.contract.json`, `Infrastructure/scripts/validate_all.sh` | full validation, docs lint, doctor, repo surface, policy gates | several layers observed; catalog parity currently blocks | Medium | Checks must prove real behavior and have fast remediation paths. |
| The smallest compelling product is much smaller than the repo. | interpretation, strategic analysis | `AGENTS.md`, `selection_policy.py`, `command_surface.py`, `repo.py` | ask CLI, handles, runtime budget, doctor | existing primitives support a smaller golden path | Medium | Adoption requires a crisp initial value loop. |
| Future scaling risk is cognitive, not just technical. | docs, source-code, runtime flow | `Docs/agents/**`, `Infrastructure/bin/ask`, `skills.py`, `.harness/**` | instruction maps, command surfaces, memory/evidence surfaces | high surface area and current repo-surface backlog observed | High | Agent-native systems fail when cognition costs exceed reliability gains. |

## Review Closeout Notes

This review is intentionally blunt because the repository is strong enough to deserve sharper criticism.

The architectural north star is good: make agent workflows discoverable, deterministic, validated, and durable. The immediate work is to reduce the amount of machinery an agent must understand to participate safely.

The next strategic decision should be:

Do you want Agent Skills Kit to be primarily a broad skill/plugin workbench, or the narrowest reliable local control plane for outcome-proven agent workflows?

The final recommendation is hybrid, but with hierarchy: keep the broad skill/plugin workbench as the exploration and distribution surface, and make the proof-driven control plane the promotion and trust mechanism. Breadth should exist; trusted breadth should be earned.
