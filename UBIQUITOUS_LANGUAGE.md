# Ubiquitous Language

## Scope and Sources

- Scope: `agent-skills` repository operations, Skills SDK product direction, skill authoring, skill sync, and runtime visibility.
- Sources: `AGENTS.md`, `README.md`, `Docs/reference/skills-sdk-platform-atlas.html`, `.harness/specs/2026-06-03-skills-sdk-v1-product-spec.md`, `.harness/plan/2026-06-04-skills-sdk-v1-0-product-implementation-plan.md`, `Docs/goals/skills-sdk-v1-0-product-implementation/goal.md`, `Docs/agents/14-path-ownership-boundaries.md`, `Docs/agents/13-workflow-and-safety-guidance.md`, `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`, `Infrastructure/references/skill-validation-reporting-contract.md`, `skills-system/skill-installer/SKILL.md`, `skills-system/skill-installer/references/skill-factory/install-flows.md`, `Skills/agent-ops/ubiquitous-language/SKILL.md`, and `.harness/quality/steering-uptake.md`.
- Last updated: 2026-09-27

## Separation-first direction

The earlier permanent-Agent-Skills ownership guidance is incorrect and retired.
The approved route is Foundry holding -> SDK checking and preparation -> private
Tessl registry -> Codex home installation, with verified OpenAI-provider exemptions.
SDK owns the agent-facing workflow and required integration adapters as well as
reusable tooling. Foundry is not mandatory permanent post-processing storage.
Agent-Skills is a temporary migration source, not a third permanent owner.
Complete that lifecycle, required consumer cutovers and authorised retirement
before product refinement. Local work does not grant live-action authority.
See the [six rules](/Docs/agents/14-path-ownership-boundaries.md#approved-lifecycle).
Legacy model-specific stage terms below describe existing selected proof lanes,
not mandatory calls for every local task or substitutes for registry/runtime proof.
Historical plans in Scope and Sources are provenance, not current scope authority.
The [platform atlas](/Docs/reference/skills-sdk-platform-atlas.html) is explicitly
retired as of 2026-09-27. Its preserved diagrams, status labels and next actions
are historical evidence, not active product direction or implementation proof.
See [PM Thread Coordination](/Docs/agents/26-pm-thread-coordination.md) for the
master controller and completion-driven owner workflow.

## Canonical Terms

| Term | Definition | Aliases to avoid | Confidence |
| --- | --- | --- | --- |
| **Agent Skills Kit** | The transitional `agent-skills` repository and its existing CLI. Retain only migration responsibilities until required tooling and package consumers use Skills SDK and Skills Foundry independently. | skills repo, agent-skills stuff | High |
| **Skills Foundry** | The holding repository at `/Users/jamiecraik/dev/skills-foundry` for permitted skills and plugins awaiting SDK processing, including complete contents, provenance and licences. Blocked or rejected candidates may remain held with reasons. Holding or catalog admission is not SDK clearance; permanent post-processing source ownership is not implied. | approved registry, runtime cache, permanent package owner | High |
| **Active SDK Candidate** | An exact complete package version selected for SDK inspection or transformation. The recorded owner governs editable source; holding, checking and scratch copies do not transfer ownership. | all held packages, runtime copy, approved package | High |
| **Skills SDK** | The project at `/Users/jamiecraik/dev/skills-sdk` owning the agent-facing SKILL.md, references and eval workflow plus reusable tooling for create, update, external intake, checks and installation of checked versions via Tessl. SDK owns supported registry/runtime adapters while keeping its Python core portable. | handoff-only tooling, marketplace, Tessl registry | High |
| **SDK Clearance** | Candidate-bound successful checks required before private registry delivery and managed installation. A holding record, static shape pass or stale approval alone is not clearance. | Foundry admission, file exists, installed already | High |
| **OpenAI Provider Exemption** | Verified OpenAI-provided plugins and OpenAI system skills use their intended provider-managed routes without SDK processing. Name, path and compatible format do not establish origin; migration must preserve these surfaces. | all Codex plugins, OpenAI-compatible, unchecked exception | High |
| **Professional Lifecycle Contract** | The Skills SDK promise that a skill can move through source shape, package identity, guardrails, eval/proof, distribution handoff, and runtime verification with receipts. | platform vision, dashboard, lifecycle vibes | High |
| **Professional Output** | A skill package or receipt-backed handoff whose thin surface, guardrails, durable memory, improvement loop, proof, and runtime boundaries are clear enough for another agent or operator to trust and replay. | polished prose, nice docs, pretty atlas | High |
| **Thin Surface** | The product posture that keeps the default SDK interface small and author-facing while moving heavy detail into receipts, references, schemas, and progressive-disclosure docs. | minimal product, less functionality | High |
| **Strong Guardrails** | The SDK boundary work that blocks or labels unsafe adoption, weak evidence, permission drift, unresolved review, package ambiguity, and runtime overclaiming before a skill is treated as ready. | security section, generic safety, warnings | High |
| **Durable Memory** | First-party routed knowledge, glossary, provenance, references, and learned steering that move with the package or repo instead of living only in chat or local cache. | notes, memories, arbitrary docs | High |
| **Operational Reference** | A package-local `references/*.md` file that carries either structured knowledge (claim cards plus at least one principle, heuristic, checklist, rubric, lens, or eval scenario) or the complete KnowledgeOS operational playbook. Skills SDK rechecks this shape at ingest; prose or source lineage alone is insufficient. | useful prose, reading notes, source summary | High |
| **Citation Record** | Traceability metadata for a source and exact locator. It does not grant quotation or redistribution rights; protected-source access and reuse policy remain producer-owned, while the SDK consumes portable paraphrased claims and stable identifiers. | reuse permission, public-safe proof, local source path | High |
| **Selected System Improvement** | An improvement of an existing source, test, instruction, wrapper, or contract selected because Jamie explicitly requested system improvement, a consequential boundary was crossed, a failure recurred across three independent tasks, two named active consumers require a contract that no existing surface can provide, or executable contracts contradict one another. | automatic ratchet, feedback ceremony, process reflex | High |
| **Self Improving** | The product posture that uses a Selected System Improvement to turn qualifying eval, runtime, review, observability, or operator evidence into a bounded source improvement with fresh proof. | auto-magic, self-healing, vague learning loop | High |
| **Upstream Feedback Loop** | A selected improvement that moves a qualifying downstream failure into an existing source fixture, adapter, validator, route checklist, or package before the next relevant pipeline run. | post-run patching, live Tessl tweak, after-the-fact fix | High |
| **Pipeline Ratchet** | A deterministic existing contract strengthened by a Selected System Improvement when its named consumer and proof justify the carrying cost. | reminder, convention, automatic response to feedback | High |
| **Package-Scored Generated Fixture** | A reviewed generated eval case whose Tessl task scores installed package instructions and references rather than a freshly generated chat response. | response eval, final.json case, transcript case | High |
| **Response-Producing Scenario** | An eval case whose runner explicitly creates `raw_response`, `final.json`, transcript, or another observable output artifact for scoring. | package fixture, static package review | High |
| **Canonical Skills SDK Pipeline** | The approved managed flow: permitted Foundry holding/intake -> SDK checking and preparation -> checked private Tessl version -> selected Codex home installation. New authoring and external intake enter SDK processing. Specific security/model/eval lanes follow the applicable candidate contract and action authority; they do not change these ownership boundaries. | optional registry, handoff-only separation, mandatory public release | High |
| **Foundry Stage** | Permitted holding of complete unprocessed packages and provenance, including blocked candidates. Catalog validation does not grant SDK clearance, source transfer or installation. | approved library, permanent source destination | High |
| **SDK Lifecycle Stage** | The recurring control cycle at entry, early, middle, and pre-release. It parses source, builds SkillIR/package identity, applies security and proof findings, updates evals and guardrails, and reconciles each evidence lane before escalation. | compiler pass, package build only, one early SDK box | High |
| **Guardrails Stage** | The sandboxed `oss-security` review stage for risk modes, intake, package hardening, permissions, semantic review, trust, adoption decisions, and human-review blockers. | security backlog, compliance, warnings | High |
| **Evals/Proof Stage** | Two ordered proof stages over one declared release scenario set: `oss-local` authors and repairs 5 to 10 scenarios, targeting 8; bounded qwen shards count only after one aggregate receipt proves matching package, dataset, rubric, profile, and exact case coverage; `oss-cloud` then checks those same case ids before pre-release. Both require deterministic checks, scorer quality, calibration, receipts, and evidence boundaries. | tests only, evals only, one proof box, different local/cloud sets | High |
| **Tessl Distribution Stage** | Retention and readback of exact SDK-checked versions in the private `jscraik` workspace, with identity and private visibility verified. These versions are the managed installation source. External scoring is separate proof; public release is optional and only Jamie decides it. | dry run delivered, eventual public release | High |
| **Skills SDK Tessl Workspace** | The operator-visible Tessl workspace `jscraik` used for every Skills SDK project, scenario preparation, local Tessl proof, live-private dry-run staging, private registry retention, and later publication decisions. Plugin manifests start `private: true`; public visibility requires a separate explicit publish lane. Older examples that say `skills-sdk`, `skills-sdk-lab`, or `jscraik-private` are stale aliases and should be replaced with, or blocked until changed to, `jscraik`. | skills-sdk workspace, skills-sdk-lab workspace, jscraik-private workspace | High |
| **Local Runtime Truth Stage** | Verify selected checked Tessl versions installed under `~/.codex/skills` and `~/.codex/plugins`: identity, discovery, required behaviour, update, rejection and recovery, preserving OpenAI exemptions. Project-local skill proof alone does not prove home-level native plugins. | source sync, dry-run install, project proof equals home proof | High |
| **Entry Lifecycle Cycle** | The cycle from Foundry intent through SDK parsing, SkillIR, package identity, and initial receipts before sandboxed security review. | author loop, source loop | High |
| **Early Lifecycle Cycle** | The cycle after `oss-security` that turns findings into source fixes, package-contract updates, eval creation, and upstream pipeline ratchets before `oss-local`. | security cleanup, early SDK loop | High |
| **Middle Lifecycle Cycle** | The cycle after `oss-local` that reconciles local proof, repairs scenarios and scorers, and decides whether the value of `oss-cloud` justifies escalation. | proof loop, cloud handoff | High |
| **Pre-release Lifecycle Cycle** | The cycle after `oss-cloud` that reconciles package, trust, review, and proof evidence and stages the exact candidate through a Tessl dry run before external Tessl evaluation. | release loop, publish preparation | High |
| **Runtime Loop** | Feedback from installed behaviour to the recorded editable-source owner and SDK workflow. Corrections require fresh candidate checks and a new private registry version before managed installation; do not silently edit installed copies. | runtime authoring, permanent Foundry loop | High |
| **Evidence Inventory** | The non-executing classification of capability evidence references as file, schema, receipt, command, external, pass, blocked, or not-run. It can pass while still requiring command replay for behavior proof. | evidence proof, replay, CI pass | High |
| **Evidence Replay** | A separate receipt lane that runs or plans command evidence and binds current command outputs to capability claims. | evidence verify, inventory, not-run refs | High |
| **Reader-State Map** | A documentation planning artifact that records what the target reader already knows, what each section or block introduces, what citations support the claim, and what missing information must be gathered from the writer before the doc can safely proceed. | audience assumptions, reader model, undocumented prerequisites | High |
| **Grounding Map** | The concept-tracking part of a Reader-State Map: concept -> prerequisite, introduced here, cited evidence, or missing foundation, used to prevent docs from leaning on terms or ideas before the reader can understand them. | concept list, glossary notes, jargon list | High |
| **`ask` CLI** | The public command interface at `./bin/ask` that agents must use for repository operations. | helper script, ask wrapper | High |
| **Canonical Skill Source** | The editable source path named by the package's explicit owner decision. Foundry holding does not establish permanent source ownership. Old Agent-Skills paths remain source only until recorded transfer and cutover. Checked Tessl versions are distribution sources; runtime and scratch copies are not editable authority. | runtime skill, always Foundry, always Agent-Skills | High |
| **Canonical Source Inspection** | Directly reading a skill's `SKILL.md` or package files for repair, audit, source review, or authoring when runtime skill use is not being claimed. | using the skill, running the skill | High |
| **Runtime Projection** | The generated skill view under `.agents/skills/**` that Codex and agent runtimes consume. | canonical skill, source skill | High |
| **Tracked Policy Source** | The reviewed repository file that declares policy for a runtime system; for Codex configuration this is the tracked `codex/config.toml`, distinct from the mutable home runtime copy. | canonical config, live config, global config | High |
| **Runtime Config Copy** | The regular mutable `~/.codex/config.toml` file materialized from the tracked policy source so Codex Desktop may persist runtime-owned settings without rewriting reviewed repository policy. | global config symlink, standalone policy source, copied config drift | High |
| **Projection Reconciler** | The repository-owned `codex/scripts/reconcile-config-projection.sh` path, normally invoked by `com.jamiecraik.config-projection-reconciler`, that applies `codex/projection-map.json` to home targets on a bounded schedule. | symlink fixer, config watcher, auto-repair daemon | High |
| **Runtime Projection Strategy** | The explicit map contract for a projected target: `symlink`, `copy`, or `copy-runtime`; `copy-runtime` preserves a regular runtime config while rejecting symlink replacement. | projection mode, link type, repair behavior | High |
| **Approval Routing** | The Codex configuration path selected by `approvals_reviewer = "auto_review"` for eligible interactive tool or sandbox approvals. It evaluates an approval request; it does not create user authority for a new commit, publication, or review-state mutation. | auto-approve everything, commit permission, user authorization | High |
| **Commit Authorization Boundary** | The user-approved repository, action, and file scope that permits staging and committing; once explicitly named, it should not be requested again unless ownership, risk, destination, or scope expands. | create-commits confirmation, broad staging permission, portfolio prompt | High |
| **Duplicate Commit Authorization Prompt** | A redundant request to reconfirm a commit or PR scope already explicitly authorized by Jamie. It is a workflow defect; preserve unrelated or unknown-owned files and ask only for the unresolved boundary. | “Please explicitly confirm Create the portfolio commits”, approval loop | High |
| **Runtime Skill Activation** | Using a skill through the active runtime-visible route/projection after proof gates pass. | reading source, source fallback | High |
| **Agent Skills Standard** | The cross-client package format defined by agentskills.io: a skill directory with one `SKILL.md` manifest and optional `scripts/`, `references/`, `assets/`, and eval files. It defines package contents, not a mandatory filesystem root. | OpenAI-only skill format, Codex-only skill format | High |
| **Interoperable Skill Root** | A `.agents/skills/` directory scanned by compatible clients for cross-client project or user skills. It is a convention for discovery; ownership still depends on the current repository contract. | always-canonical `.agents`, generated source | High |
| **Codex-Native Skill Root** | A `.codex/skills/` directory used as a Codex/client-specific skill root. It can be project-local source only when that owner repo explicitly declares it. | Agent Skills standard path, generic skill root | Medium |
| **Manifest-Declared Project Skill Source** | A project-local skill root such as `.agents/skills/` or `.codex/skills/` that the owner repo's `skills-sdk.json` classifies as `canonical_project_source`. | copied local skill, generated projection | High |
| **Project Skill Lifecycle Gate** | The Skills SDK create/install/update gate that writes a project-local skill to the owner repo, runs the configured eval suite there, and records a promote, rollback, or blocked decision. | file write, sync, manual install | High |
| **Owner Repo Skill Evidence** | Eval outputs, lifecycle events, traces, and promotion decisions saved under the owner repo's `.harness/` evidence paths for a project-local skill. | central SDK evidence, copied proof | High |
| **Command Surface Handle** | A skill name resolved by the current flat skill registry; the CLI retains `command_surface` as a compatibility response alias, not a source of ownership. Historical `.skillsets/command-surface.json` rows are obsolete routing metadata, not active runtime inputs. | command stub, runtime stub, generated skill | High |
| **User Runtime Links** | The home-directory skills and plugin links or directories under `~/.agents/**` and `~/.codex/**` that expose accepted or curated runtime availability. They are never source ownership or package-admission evidence. | user sync, installed skills, source of truth | High |
| **Plugin Runtime Mirror** | An existing transitional copied plugin tree that resolves marketplace paths without aliasing repo source. Preserve consumers until authorised cutover. The target managed route installs complete checked Tessl versions, except verified provider exemptions. | canonical plugin root, target distribution source | High |
| **Workspace Sync** | The operation `./bin/ask skills sync --scope workspace` that refreshes repo-local runtime projections and the generated root `SKILL.md` index. | sync the repo, update links | High |
| **User Sync** | The transitional operation `./bin/ask skills sync --scope user` that points user-level runtime skill directories at the current workspace projection. It requires explicit runtime authority and is not the target checked-Tessl installation route. | install checked versions, make Codex see it | High |
| **Visible Runtime Surface** | The default picker-readable projection emitted from typed canonical skill and plugin sources, with hidden, system bridge, and plugin collision policies applied. | skill list, visible skills | High |
| **Advanced Repo Discovery** | Repository scan mode that includes hidden/internal or non-default plugin/system lanes for diagnostics without changing picker eligibility. | hidden skill, missing skill | Medium |
| **Feature Worktree** | A separate checkout and branch used for isolated feature work without disturbing dirty changes in the primary checkout. | worktree, clean checkout | High |
| **Runtime-Link Worktree Hazard** | A cleanup hazard where a user runtime link such as `~/.agents/skills`, `~/.codex/skills`, or a plugin marketplace path still points into a worktree that is about to be removed. | stale worktree link, dangling skills | High |
| **Projection Refresh Lane** | A bounded change path where generated projections are refreshed from canonical sources instead of hand-edited. | sync pass, generated update | Medium |
| **Strict Skill Audit** | The `./bin/ask skills audit <path> --level strict` check that validates skill structure, runtime links, security gates, family benchmarks, and readiness. | check the skill, make sure it works | High |
| **External Skill Intake** | The staged decision process for evaluating an outside skill as a source proposal before writing it into canonical repo source. | install external skill, copy skill in | High |
| **Intake Decision** | The machine-readable `data.intake_decision` result that classifies an external skill as `install_new`, `blend_into_existing`, `keep_separate`, `reject_duplicate`, or `needs_human_choice` before canonical writes. | install result, precheck, vibes check | High |
| **Manifest-Backed Candidate** | A skill or plugin candidate containing supported dependency manifests such as `package.json`, `pyproject.toml`, `requirements.txt`, `Gemfile`, `go.mod`, or lockfiles. | package skill, dependency skill | High |
| **Release-Readiness Claim** | A statement or promotion action that treats a skill as ready for canonical routing, command-surface exposure, blending into an owner skill, or production use. | gold-ready, done, production-ish | High |
| **Second-Review Lane** | The local `ask skills external-review` path that combines strict audit evidence with Plugin Eval, Tessl local review, and optional Snyk dependency screening. | external review, plugin eval pass | Medium |
| **Mise Trust Blocker** | A local runtime state where `mise` refuses to load the worktree config until the specific `.mise.toml` is trusted. | mise broken, toolchain issue | High |
| **Policy Identity** | The deterministic hash representing the active selection and discovery policy. | policy hash, sync hash | Medium |
| **High-Signal Steering Candidate** | Jamie steering or review feedback that informs a local repair first and may justify a Selected System Improvement after its threshold is met. | feedback, comment, preference | High |
| **High-Signal Steering Feedback** | Jamie guidance deliberately admitted to the Selected System Improvement route with a named consumer, carrying cost, and proof. | feedback, comment, preference | High |
| **Workflow Papercut Log** | An optional temporary scratch file for a selected complex system-improvement lane; it is never a routine-delivery prerequisite or durable proof. | notes, memory, final proof | High |
| **Feedback Intent Radius** | The scope at which feedback should be applied: `line`, `function`, `file`, `package`, `repository`, `architecture_rule`, or `durable_memory`. | scope guess, local fix | High |
| **Pattern Sweep** | A bounded search for similar cases after feedback implies a transferable rule, with each match classified as fixed, left, deferred, or not applicable. | grep and fix all, one-off search | High |
| **Generalized Feedback Rule** | The transferable principle implied by a local feedback example, stated without the incidental function, command, test, doc section, line, error, or file name. | local fix, review nit | High |
| **Similar-Case Disposition** | The classification of equivalent cases found during a pattern sweep: fixed now, different semantics, deferred with reason, or not applicable. | sweep done, grep result | High |
| **Repeated Error Research Gate** | After two equivalent failures, stop unchanged retries, preserve the error and command, and change one diagnostic, input, environment condition, or implementation hypothesis. Consult repository evidence first and research alternatives when the cause remains uncertain. No fixed option count or new steering artifact is required. | keep trying, fight the error | High |
| **Repo-Local Prek Home** | The hook cache selected by the repository installer: `PREK_HOME="${CODEX_HOOK_CACHE_ROOT}/prek"`, using a writable temporary root by default, not repository `.cache/prek` or `~/.cache/prek`. The installer validates the selected paths before wiring generated hooks. | home prek cache, local workaround | High |
| **Durable Surface** | The canonical repo file or generated-source owner that should carry a steering rule so future agents inherit it. | note, reminder, chat context | High |
| **Horizontal OODA Context** | Awareness of adjacent organizational activity that may change how an agent should orient before acting. | background noise, extra context | Medium |
| **Vertical OODA Context** | Awareness that an agent is acting across stacked trajectories, not only the current turn or current patch. | thread memory, task history | Medium |
| **Misuse-Resistant Interface Design** | API design that carries authority, ownership, and invariants in the shape of the interface so correct use is natural and unsafe use is hard to express. | safer helper, secure API, process rule | High |
| **Zero-Setup Agent Workspace** | Product posture where an agent can land in a workspace, discover the contract, bootstrap itself, validate readiness, and report blockers without the customer integrating the product manually. | setup docs, customer integration, manual wiring | High |
| **Systems Thinking Product Rule** | Product posture that spots blockers, designs systematic ways for people and agents to overcome them, and explains how code carries the repeatable mechanism. | systems thinking, unblocker mindset, empowerment design | High |
| **Environment Refinement** | A meta-change to instructions, validators, tests, ledgers, or workflow contracts that makes a repeated agent failure harder to repeat. | doc rewrite, reminder, preference note | High |
| **Diagnostic Debt Classification** | A structured explanation for repo warnings or diagnostic counts that names the dominant category, owner or decision boundary, and next action before closeout claims the debt is nonblocking. | diagnostic debt, warnings, repo doctor noise | High |
| **CTF Workflow Eval** | High-level workflow eval where a planted UI or app-state flag is the win condition; repeated runs refine skills for reliability, wall-clock time, and codebase drift. | coding RL, UI smoke test, manual QA | High |

## Prompt Translations

| User phrase | Canonical intent | Better Codex wording |
| --- | --- | --- |
| "sync my skills" | Identify whether the requested action is transitional projection maintenance or checked-version installation. | "Resolve the package, current route and runtime authority first. Use the SDK/Tessl route for target managed installs; never relink home runtimes to this worktree by default." |
| "find the ubiquitous-language skill" | Locate the canonical skill source and determine whether the runtime projection exposes it. | "Search `Skills/**`, `Plugins/**`, `.agents/skills/**`, and `./bin/ask skills list --json` for `ubiquitous-language`, then report source path and runtime visibility separately." |
| "so you will not be able to use it?" | Distinguish manual filesystem access from formal runtime skill availability. | "Check whether the skill is available through the active runtime projection; if not, state whether the canonical source can only be inspected for repair/review, not used as a runtime skill." |
| "proceed" | Continue the previously selected action within its existing authority and current canonical ownership. | "Resolve the current owner, carry out the authorized next step, and run its focused proof. Do not infer source copying, installation, or runtime mutation from this confirmation alone." |
| "run the skill" | Execute the skill workflow through runtime-visible skill activation in the current repo scope and produce its expected artifact. | "Prove `ubiquitous-language` is runtime-visible, then use it to create or update repo-root `UBIQUITOUS_LANGUAGE.md`, citing source files and validating the output file exists." |
| "make it available" | Prove installed identity and Codex discovery, not merely source existence. | "Select the checked Tessl version and authorised installation route, or verified OpenAI-provider route. Report actual discovery separately from source inventory." |
| "check it works" | Produce fresh evidence for the changed surface. | "Run the smallest relevant validation command for the changed skill or sync policy and report exact pass/fail/blocker output." |
| "update the plugin" | Change the recorded editable source within scope, then recheck the candidate. | "Use SDK validation and a newly checked private Tessl version before managed installation. A holding copy does not transfer source ownership; live actions require matching authority." |
| "install this external skill" | Use SDK **External Skill Intake** and checks before managed installation. | "Check the complete candidate through SDK, then install its checked private Tessl version with matching authority. If that route is unavailable, report the gap. Legacy direct-source installation is limited to [explicitly authorised existing-consumer recovery](/Docs/agents/17-skill-management.md#transitional-install-failure-recovery)." |
| "is this skill ready?" | Verify the **Release-Readiness Claim** with required gates. | "Run strict audit, second-review lane, smoke evals when cases exist, and release evals before command-surface exposure or canonical routing; include Snyk only for manifest-backed candidates." |
| "don't make me say this again" | Treat the correction as a **High-Signal Steering Candidate**. | "Fix the named outcome locally, then select a system improvement only when its threshold and existing-surface need are established." |
| "every bit of steering I give is high signal" | Treat each steering item as diagnostic evidence. | "Use the local repair path by default; record a selected system improvement only when it is materially justified." |
| "you are failing to operate effectively" | Diagnose the active lane and apply the smallest safe correction. | "Stop only where a direct safety or evidence boundary requires it; otherwise repair and prove the named behavior." |
| "do not proceed until you prove it" | Require proof appropriate to the named boundary. | "Use focused existing proof for local work; use the selected system-improvement route only when the stated threshold is met." |
| "this is how I think about the problem generally" | Treat the named issue as a transferable rule until proven local. | "Run a bounded pattern sweep, classify similar cases, and preserve the rule in the owning doc, glossary, skill, or validator." |
| "agents need to OODA across the stack" | Expand orientation beyond the current turn. | "Check horizontal organizational context and vertical stacked trajectories before deciding the action radius." |
| "make the unsafe use hard to express" | Apply **Misuse-Resistant Interface Design**. | "Shape the API around narrow authority, owned schemas, typed invariants, contextual errors, and policy-like tests." |
| "drop agents into the workspace with zero setup" | Apply **Zero-Setup Agent Workspace**. | "Design agent-facing setup as discoverable, idempotent, validated workspace self-setup with explicit blocker classification." |
| "keep systems thinking sharp" | Apply **Systems Thinking Product Rule**. | "Name the blocker, encode the repeatable unblocking mechanism in code or contract, validate it, and explain the before and after." |
| "prove you can operate this way" | Make an **Environment Refinement** before ordinary task work continues. | "Change the repo contract or validator so the repeated failure is harder to reproduce, then run evidence that proves the new mechanism." |
| "capturing the flag is the win condition" | Apply **CTF Workflow Eval**. | "Use a planted flag as the success criterion, then iterate the skill from evidence until reliability and wall-clock targets are met." |
| "agent-skills becomes obsolete" | Complete the six-rule lifecycle and required consumer cutover, then authorise retirement. | "Prove SDK workflow, checked private Tessl delivery and installed home-runtime behaviour without Agent-Skills. Preserve provider exemptions and every required consumer; defer unrelated product refinement." |
| "professional output" | Apply the mantra as **Thin Surface**, **Strong Guardrails**, **Durable Memory**, **Self Improving**, and **Professional Output**. | "Place the change on the canonical pipeline and prove the package has shape, guardrails, durable memory, a bounded improvement loop, and replayable evidence before calling it professional output." |
| "pass with not_run refs" | Distinguish **Evidence Inventory** from **Evidence Replay**. | "Treat `sdk evidence verify` as inventory/classification; run or plan replay receipts before claiming command behavior is proven." |
| "make the atlas clearer" | Use the **Canonical Skills SDK Pipeline**, distinguishing target from observed capability. | "Show holding, SDK checks, private Tessl versions and home runtime, with provider exemptions. Place specific model proof under its selected candidate contract; do not invent working integrations." |
| "feed it in at the start of the pipeline" | Use the **Upstream Feedback Loop** and **Pipeline Ratchet**. | "Classify the recurring failure, patch the source fixture, adapter, validator, route checklist, or package before `oss-local`, and prove scenario-quality blocks the old shape before widening to `oss-cloud` or Tessl." |
| "auto-review should approve this for me" | Distinguish **Approval Routing** from the **Commit Authorization Boundary**. | "Use `auto_review` for the eligible tool or sandbox approval; treat an explicit repository/action/scope request as the commit authority, do not ask for a **Duplicate Commit Authorization Prompt**, and stop only for unknown ownership or a real scope expansion." |
| "Please explicitly confirm: Create the portfolio commits" | Classify whether the user already named and authorized the repository and commit scope before asking again. | "Triage the portfolio files and ownership first. If Jamie already authorized that exact repository and scope, continue without a second confirmation; preserve unrelated or unknown-owned files and ask only about the unresolved boundary." |
| "who keeps changing my config.toml?" | Trace the **Projection Reconciler** and inspect the **Runtime Projection Strategy** before blaming the desktop runtime. | "Check the launchd reconciler command, interval, recent log, map strategy, and live target type; use **Runtime Config Copy** for the mutable main config and keep profiles or other targets on their declared strategies." |

## Relationships

Projection and marketplace relationships below describe the existing transitional
implementation unless explicitly identified as the target lifecycle. They do not
authorise new direct-source installs or turn historical model lanes into a new
programme requirement. Preserve current consumers until authorised cutover.

- A **Canonical Skill Source** may produce one **Runtime Projection** entry after **Workspace Sync**.
- A tracked policy source may produce a **Runtime Config Copy** when the **Runtime Projection Strategy** is `copy-runtime`; the **Projection Reconciler** must preserve that regular file rather than restore a symlink.
- **Approval Routing** may auto-review an eligible tool request, but only the **Commit Authorization Boundary** authorizes a new commit scope; a **Duplicate Commit Authorization Prompt** signals that the agent has confused those concepts.
- **Skills Foundry** holds permitted candidates; **Skills SDK** checks complete versions and owns the workflow and adapters; private **Tessl Distribution** supplies managed installations. Editable source follows its recorded owner. **agent-skills** is transitional until required consumers cut over; ownership claims alone do not prove registry or runtime state.
- **Skills SDK** professionalizes an explicitly selected source from the current owner through the **Professional Lifecycle Contract** before any **Tessl Distribution Stage** or **Local Runtime Truth Stage** claim is made.
- The **Canonical Skills SDK Pipeline** governs roadmap, atlas, route-map and capability language. Implementation slices name their required consumer and lifecycle outcome; legacy ten-stage model diagrams do not override the six approved rules.
- A qualifying downstream signal may enter an **Upstream Feedback Loop** through a **Selected System Improvement**; it is not complete if the change only patches the current live Tessl result.
- A behavioral release candidate carries one 5-to-10-case scenario set, targets 8 high-value cases, and preserves exact case-id parity through `oss-local`, `oss-cloud`, Tessl dry-run, and external Tessl evaluation. Changing the set returns it to `oss-local`.
- A **Package-Scored Generated Fixture** must not require **Response-Producing Scenario** artifacts such as `raw_response`, `final.json`, transcripts, or chat output unless the selected runner actually produces them.
- **Evidence Inventory** can prove that evidence references are present and classified; **Evidence Replay** is required before command refs or external lanes prove current behavior.
- KnowledgeOS produces a **Knowledge Capsule** and proves its operational shape; Skills SDK admits it as an **Operational Reference** only after independently checking the same section contract. A **Citation Record** proves traceability, while reuse rights remain a separate producer-side policy.
- A **Runtime Projection** entry becomes available to user-level Codex sessions through **User Runtime Links** after **User Sync**.
- In this repository, `.agents/skills/**` is a **Runtime Projection** for generated root skill sets and system bridges. In another owner repo, `.agents/skills/**` or `.codex/skills/**` is editable source only when a project-local `skills-sdk.json` declares that root as **Manifest-Declared Project Skill Source**.
- Project-local skill source is saved in the owner repo at `<declared-root>/<skill-handle>/`. Its portable eval suite lives with the skill at `<declared-root>/<skill-handle>/evals/evals.json`; SDK evidence and lifecycle events live under the owner repo's `.harness/` paths.
- **Agent Skills Standard** compatibility means preserving `SKILL.md` package shape, progressive disclosure, optional `scripts/`/`references/`/`assets/`, and portable evals. It does not by itself decide whether a local path is canonical or generated.
- Historical command-surface projections are obsolete routing metadata, not active inputs to the flat registry. The current resolver must not pretend a deleted package is available. Directly loading canonical SKILL.md source can support source inspection, repair, audit, or authoring; it does not prove runtime installation or activation.
- **Runtime Skill Activation** requires the active runtime projection and user runtime links to pass their proof gates. If proof is blocked, stop and repair/sync the runtime surface or explicitly reframe the work as source inspection with no skill-use claim.
- `~/.agents/plugins` is the user-facing **Personal Plugin Marketplace Root** and must be a real directory on each macOS host, not a symlink to a repo or worktree. The marketplace may contain per-plugin aliases to the active profile mirror, while **Plugin Runtime Mirrors** such as `~/.codex/plugins` are real copied directories and must be refreshed after plugin source or marketplace changes.
- First-party canonical skills under `Skills/**` are part of the **Visible Runtime Surface** unless they are explicitly hidden by selection policy.
- Plugin-owned skills under `Plugins/**/skills/**` remain plugin-scoped. They become picker-readable through plugin runtime roots and collision policy, not by being flattened into first-party skill projection.
- The **Visible Runtime Surface** is controlled by typed source ownership, hidden-skill policy, system bridge policy, plugin collision policy, and generated projection freshness. Do not maintain a separate hand-written first-party allowlist.
- A **Feature Worktree** can intentionally diverge from the primary checkout; uncommitted skills in the primary checkout are not automatically present in the feature worktree.
- A **Runtime-Link Worktree Hazard** must be cleared before worktree removal is
  complete. Git branch ancestry and clean worktree status do not prove that
  user runtime links, plugin marketplaces, or visible skill projections are
  still valid.
- **Strict Skill Audit** depends on local runtime health; a **Mise Trust Blocker** must be fixed before treating audit failure as a skill defect.
- **External Skill Intake** produces an **Intake Decision** before canonical writes; `reject_duplicate` and `needs_human_choice` stop the install path.
- A **Manifest-Backed Candidate** needs Snyk dependency screening before a **Release-Readiness Claim**; pure `SKILL.md`-first candidates without supported manifests report Snyk as not applicable.
- The **Second-Review Lane** does not replace local evals; it supplies static quality, package-shape, and optional dependency-security evidence.
- `SKILL.md` at the repo root is a generated index surface and should be refreshed by sync, not hand-edited.

## Example Dialogue

> **Dev:** "When I say `sync my skills`, do I mean just update `SKILL.md`?"
>
> **Domain expert:** "No. First distinguish legacy projection maintenance from installing a checked Tessl version. Do not relink your home runtime to this checkout by default."
>
> **Dev:** "If a skill is on disk, is Codex able to use it?"
>
> **Domain expert:** "Only if the active runtime projection exposes it. Source existence and runtime visibility are related but not the same."
>
> **Dev:** "Why did `prek-pro` not appear even though `ask skills list` found it?"
>
> **Domain expert:** "Source discovery and runtime discovery are different. Diagnose the active route first. `./bin/ask skills load-preview --json` inspects the transitional projection; it does not prove the target Tessl install."

> **Dev:** "Why did the agent ask me to confirm portfolio commits again when I already said to commit the repository changes?"
>
> **Domain expert:** "That was a **Duplicate Commit Authorization Prompt**. **Approval Routing** is for eligible tool or sandbox requests; your explicit repository and file scope already established the **Commit Authorization Boundary**. The agent should triage ownership, preserve unrelated files, and continue unless the scope actually expands."

## Flagged Ambiguities

- "Skill" can mean **Canonical Skill Source**, **Runtime Projection**, or a skill advertised in the session prompt. Recommendation: use **Canonical Skill Source** for editable files, **Runtime Projection** for `.agents/skills/**`, and **available skill** for what the active Codex session can invoke.
- "agent-skills" means the transitional repository, not the permanent SDK home. Name **Skills SDK** for the workflow/tooling/adapters and **Skills Foundry** for permitted candidates awaiting processing.
- "Skills SDK" names the standalone tooling project. Name a specific executable when distinguishing its public CLI from the transitional Agent-Skills `ask sdk` commands.
- "Proof" can mean inventory, replay, eval score, hosted CI, Tessl run, or installed runtime behavior. Recommendation: use **Evidence Inventory**, **Evidence Replay**, **Evals/Proof Stage**, **Tessl Distribution Stage**, or **Local Runtime Truth Stage** to avoid overclaiming.
- "Feedback loop" can mean a conversational reminder, a post-run patch, or a true **Upstream Feedback Loop**. Recommendation: reserve **Upstream Feedback Loop** for a selected, thresholded change that lands before the relevant pipeline lane and uses an existing deterministic contract where one is justified.
- "Professional output" can mean polished docs or the actual package-readiness target. Recommendation: reserve it for the combination of **Thin Surface**, **Strong Guardrails**, **Durable Memory**, **Self Improving**, and receipt-backed package/runtime boundaries.
- ".agents/skills" can mean an interoperable source root in another project or the generated runtime projection in this repository. Recommendation: check the owner repo's `skills-sdk.json` before editing.
- "Sync" can mean **Workspace Sync**, **User Sync**, or checked-version installation. Resolve the intended target and authority; never default to home-runtime relinking from the current checkout.
- "Use it" can mean **Canonical Source Inspection** or **Runtime Skill Activation**. Recommendation: keep them separate; source inspection is allowed for repair/review, but a blocked runtime proof means the skill was not used.
- "Worktree" can mean the original dirty checkout or the new feature checkout. Recommendation: name the absolute path when reporting where commands ran.
- "Make it visible" can mean adding files to source control, refreshing runtime projection, or enabling the plugin runtime root. Recommendation: verify with `./bin/ask skills list --json` and `./bin/ask skills load-preview --json`, not only `find`.
- "Stub" is overloaded. Recommendation: say **Command Surface Handle** for `$`-mentionable flat-registry skill-name handles and reserve "stub" for test doubles or temporary executable placeholders.
- "Auto-review" is overloaded. Recommendation: use **Approval Routing** for the configured reviewer and **Commit Authorization Boundary** for the user's explicit mutation authority; never use `auto_review` as a synonym for “approve every commit or publication.”
- "Config" is overloaded. Recommendation: use **Tracked Policy Source** for the reviewed repo file, **Runtime Config Copy** for the mutable home file, and **Projection Reconciler** for the scheduled mechanism that materializes the map.

## Agent Integration

- Instruction surface updated: `AGENTS.md`
- Integration summary: future agents are told to read this glossary before changing skills, sync policy, runtime projections, agent-facing docs, Skills SDK plans/specs/atlas visuals, capability claims, or product-direction docs, and to use Prompt Translations for terse or ambiguous user phrases.
- Validation/enforcement: manual glossary validation in this run; no new validator added yet.

## Decisions

- This glossary is maintained repository guidance linked from `AGENTS.md`.
- First-party skill picker eligibility is deterministic from canonical source ownership and hidden policy. `prek-pro`, `ubiquitous-language`, and other first-party `Skills/**` entries must not need per-skill allowlist edits.

## Open Questions

- Should the repo add a dedicated validation check that flags a canonical skill copied into `Skills/**` but absent from the generated runtime projection after sync?
