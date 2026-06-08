# Ubiquitous Language

## Scope and Sources

- Scope: `agent-skills` repository operations, skill authoring, skill sync, and runtime visibility.
- Sources: current conversation, `AGENTS.md`, `README.md`, `Docs/agents/14-path-ownership-boundaries.md`, `Docs/agents/13-workflow-and-safety-guidance.md`, `Infrastructure/scripts/lifecycle-and-sync/selection_policy.py`, `Infrastructure/references/skill-validation-reporting-contract.md`, `skills-system/skill-installer/SKILL.md`, `skills-system/skill-installer/references/skill-factory/install-flows.md`, and `Skills/agent-ops/ubiquitous-language/SKILL.md`.
- Last updated: 2026-05-16

## Canonical Terms

| Term | Definition | Aliases to avoid | Confidence |
| --- | --- | --- | --- |
| **Agent Skills Kit** | The governed repository and CLI system for authoring, validating, discovering, and syncing Codex skills. | skills repo, agent-skills stuff | High |
| **`ask` CLI** | The public command interface at `./bin/ask` that agents must use for repository operations. | helper script, ask wrapper | High |
| **Canonical Skill Source** | The editable source of a skill under `Skills/<topic-cluster>/<skill-name>/` or a plugin-owned skill path. | runtime skill, synced copy | High |
| **Runtime Projection** | The generated skill view under `.agents/skills/**` that Codex and agent runtimes consume. | canonical skill, source skill | High |
| **Agent Skills Standard** | The cross-client package format defined by agentskills.io: a skill directory with one `SKILL.md` manifest and optional `scripts/`, `references/`, `assets/`, and eval files. It defines package contents, not a mandatory filesystem root. | OpenAI-only skill format, Codex-only skill format | High |
| **Interoperable Skill Root** | A `.agents/skills/` directory scanned by compatible clients for cross-client project or user skills. It is a convention for discovery; ownership still depends on the current repository contract. | always-canonical `.agents`, generated source | High |
| **Codex-Native Skill Root** | A `.codex/skills/` directory used as a Codex/client-specific skill root. It can be project-local source only when that owner repo explicitly declares it. | Agent Skills standard path, generic skill root | Medium |
| **Manifest-Declared Project Skill Source** | A project-local skill root such as `.agents/skills/` or `.codex/skills/` that the owner repo's `skills-sdk.json` classifies as `canonical_project_source`. | copied local skill, generated projection | High |
| **Project Skill Lifecycle Gate** | The Skills SDK create/install/update gate that writes a project-local skill to the owner repo, runs the configured eval suite there, and records a promote, rollback, or blocked decision. | file write, sync, manual install | High |
| **Owner Repo Skill Evidence** | Eval outputs, lifecycle events, traces, and promotion decisions saved under the owner repo's `.harness/` evidence paths for a project-local skill. | central SDK evidence, copied proof | High |
| **Command Surface Handle** | A metadata row in `.skillsets/command-surface.json` that makes a skill addressable by a stable `$<handle>` and resolves to a canonical `SKILL.md` source. It is not a generated wrapper file and must not be treated as canonical source. | command stub, runtime stub, generated skill | High |
| **User Runtime Links** | The home-directory links `~/.agents/skills` and `~/.codex/skills` that point to the active runtime projection. | user sync, installed skills | High |
| **Plugin Runtime Mirror** | A real copied plugin tree, such as `~/plugins` or a Codex profile `Plugins/`, refreshed from canonical `~/dev/agent-skills/Plugins` so marketplace paths resolve without aliasing repo source. | plugin symlink, canonical plugin root | High |
| **Workspace Sync** | The operation `./bin/ask skills sync --scope workspace` that refreshes repo-local runtime projections and the generated root `SKILL.md` index. | sync the repo, update links | High |
| **User Sync** | The operation `./bin/ask skills sync --scope user` that points user-level runtime skill directories at the current workspace projection. | install skills, make Codex see it | High |
| **Visible Runtime Surface** | The bounded default skill list exposed by `DEFAULT_VISIBLE_FLAT_SKILL_NAMES` to control always-loaded skill context. | skill list, visible skills | High |
| **Advanced Repo Discovery** | Repository scan mode that can find skills not promoted into the default visible runtime surface. | hidden skill, missing skill | Medium |
| **Feature Worktree** | A separate checkout and branch used for isolated feature work without disturbing dirty changes in the primary checkout. | worktree, clean checkout | High |
| **Projection Refresh Lane** | A bounded change path where generated projections are refreshed from canonical sources instead of hand-edited. | sync pass, generated update | Medium |
| **Strict Skill Audit** | The `./bin/ask skills audit <path> --level strict` check that validates skill structure, runtime links, security gates, family benchmarks, and readiness. | check the skill, make sure it works | High |
| **External Skill Intake** | The staged decision process for evaluating an outside skill as a source proposal before writing it into canonical repo source. | install external skill, copy skill in | High |
| **Intake Decision** | The machine-readable `data.intake_decision` result that classifies an external skill as `install_new`, `blend_into_existing`, `keep_separate`, `reject_duplicate`, or `needs_human_choice` before canonical writes. | install result, precheck, vibes check | High |
| **Manifest-Backed Candidate** | A skill or plugin candidate containing supported dependency manifests such as `package.json`, `pyproject.toml`, `requirements.txt`, `Gemfile`, `go.mod`, or lockfiles. | package skill, dependency skill | High |
| **Release-Readiness Claim** | A statement or promotion action that treats a skill as ready for canonical routing, command-surface exposure, blending into an owner skill, or production use. | gold-ready, done, production-ish | High |
| **Second-Review Lane** | The local `ask skills external-review` path that combines strict audit evidence with Plugin Eval, Tessl local review, and optional Snyk dependency screening. | external review, plugin eval pass | Medium |
| **Mise Trust Blocker** | A local runtime state where `mise` refuses to load the worktree config until the specific `.mise.toml` is trusted. | mise broken, toolchain issue | High |
| **Policy Identity** | The deterministic hash representing the active selection and discovery policy. | policy hash, sync hash | Medium |
| **High-Signal Steering Candidate** | Any Jamie steering or review feedback item before classification; default to treating it as potentially durable until a specific non-durable reason is recorded. | feedback, comment, preference | High |
| **High-Signal Steering Feedback** | Jamie guidance classified as a repeated agent behavior failure or transferable operating rule; it must be persisted before ordinary work continues. | feedback, comment, preference | High |
| **Feedback Intent Radius** | The scope at which feedback should be applied: `line`, `function`, `file`, `package`, `repository`, `architecture_rule`, or `durable_memory`. | scope guess, local fix | High |
| **Pattern Sweep** | A bounded search for similar cases after feedback implies a transferable rule, with each match classified as fixed, left, deferred, or not applicable. | grep and fix all, one-off search | High |
| **Generalized Feedback Rule** | The transferable principle implied by a local feedback example, stated without the incidental function, command, test, doc section, line, error, or file name. | local fix, review nit | High |
| **Similar-Case Disposition** | The classification of equivalent cases found during a pattern sweep: fixed now, different semantics, deferred with reason, or not applicable. | sweep done, grep result | High |
| **Repeated Error Research Gate** | The troubleshooting rule that the same error twice stops retries and triggers research of 3-5 plausible fixes, selection of the efficient safe option, implementation, and evidence. | keep trying, fight the error | High |
| **Repo-Local Prek Home** | The repository-owned `.cache/prek` directory used by generated git hook shims through `PREK_HOME`, preventing Codex sandboxed commit/push hooks from writing `~/.cache/prek/prek.log`. | home prek cache, local workaround | High |
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
| "sync my skills" | Refresh the active workspace projection and point user runtime links at it. | "Run `./bin/ask skills sync --scope workspace --json`, then `./bin/ask skills sync --scope user --json`, and verify `~/.codex/skills` points at this worktree." |
| "find the ubiquitous-language skill" | Locate the canonical skill source and determine whether the runtime projection exposes it. | "Search `Skills/**`, `Plugins/**`, `.agents/skills/**`, and `./bin/ask skills list --json` for `ubiquitous-language`, then report source path and runtime visibility separately." |
| "so you will not be able to use it?" | Distinguish manual filesystem access from formal runtime skill availability. | "Check whether the skill is available through the active `~/.codex/skills` projection; if not, state whether it can still be read manually from disk." |
| "proceed" | Carry out the previously described corrective path. | "Copy the missing canonical skill into this feature worktree, promote it to the visible runtime surface if needed, sync workspace and user scopes, then validate discoverability." |
| "run the skill" | Execute the skill workflow in the current repo scope and produce its expected artifact. | "Use `$ubiquitous-language` to create or update repo-root `UBIQUITOUS_LANGUAGE.md`, citing source files and validating the output file exists." |
| "make it available" | Ensure Codex runtime discovery can see a skill, not just that source files exist. | "Add the skill to the default visible runtime surface when appropriate, run workspace and user sync, and verify `./bin/ask skills list --json` includes it." |
| "check it works" | Produce fresh evidence for the changed surface. | "Run the smallest relevant validation command for the changed skill or sync policy and report exact pass/fail/blocker output." |
| "update the plugin" | Change the canonical plugin source and refresh materialized runtime mirrors. | "Patch `Plugins/<plugin>`, run the relevant plugin validation, then run `./bin/ask skills sync --scope user --projection rooted` or `./bin/ask plugins sync-local-runtime` so copied plugin mirrors are replaced." |
| "install this external skill" | Run **External Skill Intake** before writing canonical source. | "Run `./bin/ask skills install <github-url> --dry-run --json --robot`, inspect `data.intake_decision`, then install, blend, keep separate, reject, or stop for a human ownership choice." |
| "is this skill ready?" | Verify the **Release-Readiness Claim** with required gates. | "Run strict audit, second-review lane, smoke evals when cases exist, and release evals before command-surface exposure or canonical routing; include Snyk only for manifest-backed candidates." |
| "don't make me say this again" | Treat the correction as **High-Signal Steering Feedback**. | "Classify the feedback type and intent radius, update the closest durable surface, validate it, and report the new rule." |
| "every bit of steering I give is high signal" | Treat each steering item as a **High-Signal Steering Candidate** before ordinary work. | "Classify the steering, choose durable or non-durable disposition, update the closest mechanism when durable, validate it, and report why the same feedback should not recur." |
| "you are failing to operate effectively" | Trigger the steering override halt. | "Stop the active lane, close stale child agents, classify the blocker, make a durable environment refinement, validate the mechanism, and prove it before resuming ordinary work." |
| "do not proceed until you prove it" | Require validated environment-refinement evidence before task continuation. | "Run the steering uptake protocol, update docs/tests/validators/ledger as needed, and report blocker, mechanism, proof, and remaining limit before returning to the implementation lane." |
| "this is how I think about the problem generally" | Treat the named issue as a transferable rule until proven local. | "Run a bounded pattern sweep, classify similar cases, and preserve the rule in the owning doc, glossary, skill, or validator." |
| "agents need to OODA across the stack" | Expand orientation beyond the current turn. | "Check horizontal organizational context and vertical stacked trajectories before deciding the action radius." |
| "make the unsafe use hard to express" | Apply **Misuse-Resistant Interface Design**. | "Shape the API around narrow authority, owned schemas, typed invariants, contextual errors, and policy-like tests." |
| "drop agents into the workspace with zero setup" | Apply **Zero-Setup Agent Workspace**. | "Design agent-facing setup as discoverable, idempotent, validated workspace self-setup with explicit blocker classification." |
| "keep systems thinking sharp" | Apply **Systems Thinking Product Rule**. | "Name the blocker, encode the repeatable unblocking mechanism in code or contract, validate it, and explain the before and after." |
| "prove you can operate this way" | Make an **Environment Refinement** before ordinary task work continues. | "Change the repo contract or validator so the repeated failure is harder to reproduce, then run evidence that proves the new mechanism." |
| "capturing the flag is the win condition" | Apply **CTF Workflow Eval**. | "Use a planted flag as the success criterion, then iterate the skill from evidence until reliability and wall-clock targets are met." |

## Relationships

- A **Canonical Skill Source** may produce one **Runtime Projection** entry after **Workspace Sync**.
- A **Runtime Projection** entry becomes available to user-level Codex sessions through **User Runtime Links** after **User Sync**.
- In this repository, `.agents/skills/**` is a **Runtime Projection** for generated root skill sets and system bridges. In another owner repo, `.agents/skills/**` or `.codex/skills/**` is editable source only when a project-local `skills-sdk.json` declares that root as **Manifest-Declared Project Skill Source**.
- Project-local skill source is saved in the owner repo at `<declared-root>/<skill-handle>/`. Its portable eval suite lives with the skill at `<declared-root>/<skill-handle>/evals/evals.json`; SDK evidence and lifecycle events live under the owner repo's `.harness/` paths.
- **Agent Skills Standard** compatibility means preserving `SKILL.md` package shape, progressive disclosure, optional `scripts/`/`references/`/`assets/`, and portable evals. It does not by itself decide whether a local path is canonical or generated.
- A **Command Surface Handle** exists only to make a routed skill mentionable, for example `$he-heartbeat`; the real workflow remains in the resolved **Canonical Skill Source**. If `./bin/ask` is unavailable outside this repository, search the owner skill tree for the exact handle and load the canonical `SKILL.md` source.
- `~/.agents/plugins` is a live symlink to canonical `Plugins/`, while **Plugin Runtime Mirrors** such as `~/plugins` are real copied directories and must be refreshed after plugin source or marketplace changes.
- A skill can exist in **Advanced Repo Discovery** while remaining absent from the **Visible Runtime Surface**.
- The **Visible Runtime Surface** is controlled by `DEFAULT_VISIBLE_FLAT_SKILL_NAMES`, not by the mere presence of a `SKILL.md` file.
- A **Feature Worktree** can intentionally diverge from the primary checkout; uncommitted skills in the primary checkout are not automatically present in the feature worktree.
- **Strict Skill Audit** depends on local runtime health; a **Mise Trust Blocker** must be fixed before treating audit failure as a skill defect.
- **External Skill Intake** produces an **Intake Decision** before canonical writes; `reject_duplicate` and `needs_human_choice` stop the install path.
- A **Manifest-Backed Candidate** needs Snyk dependency screening before a **Release-Readiness Claim**; pure `SKILL.md`-first candidates without supported manifests report Snyk as not applicable.
- The **Second-Review Lane** does not replace local evals; it supplies static quality, package-shape, and optional dependency-security evidence.
- `SKILL.md` at the repo root is a generated index surface and should be refreshed by sync, not hand-edited.

## Example Dialogue

> **Dev:** "When I say `sync my skills`, do I mean just update `SKILL.md`?"
>
> **Domain expert:** "No. In this repo, translate that into workspace sync plus user sync, then verify the home-directory runtime links."
>
> **Dev:** "If a skill is on disk, is Codex able to use it?"
>
> **Domain expert:** "Only if the active runtime projection exposes it. Source existence and runtime visibility are related but not the same."
>
> **Dev:** "Why did `ubiquitous-language` not appear after copying it?"
>
> **Domain expert:** "Because it existed in the canonical source tree but was not yet part of the visible runtime surface. Add it to the selection policy, sync, and verify with `./bin/ask skills list --json`."

## Flagged Ambiguities

- "Skill" can mean **Canonical Skill Source**, **Runtime Projection**, or a skill advertised in the session prompt. Recommendation: use **Canonical Skill Source** for editable files, **Runtime Projection** for `.agents/skills/**`, and **available skill** for what the active Codex session can invoke.
- ".agents/skills" can mean an interoperable source root in another project or the generated runtime projection in this repository. Recommendation: check the owner repo's `skills-sdk.json` before editing.
- "Sync" can mean **Workspace Sync**, **User Sync**, or a lower-level projection refresh script. Recommendation: default to both `./bin/ask skills sync --scope workspace` and `./bin/ask skills sync --scope user` when the user says "sync my skills."
- "Use it" can mean manually reading a skill's instructions or invoking it through runtime skill discovery. Recommendation: answer both availability paths when a skill was just added.
- "Worktree" can mean the original dirty checkout or the new feature checkout. Recommendation: name the absolute path when reporting where commands ran.
- "Make it visible" can mean adding files to source control or adding a skill to **Visible Runtime Surface**. Recommendation: verify with `./bin/ask skills list --json`, not only `find`.
- "Stub" is overloaded. Recommendation: say **Command Surface Handle** for `$`-mentionable metadata routes and reserve "stub" for test doubles or temporary executable placeholders.

## Agent Integration

- Instruction surface updated: `AGENTS.md`
- Integration summary: future agents are told to read this glossary before changing skills, sync policy, runtime projections, or agent-facing docs, and to use Prompt Translations for terse or ambiguous user phrases.
- Validation/enforcement: manual glossary validation in this run; no new validator added yet.

## Decisions

- `ubiquitous-language` is intentionally included in `DEFAULT_VISIBLE_FLAT_SKILL_NAMES` because it governs how terse user language maps to repo-native agent actions; revisit only if default skill-context pressure becomes a measured problem.

## Open Questions

- Should this glossary become a maintained repository contract linked from `AGENTS.md`, or remain an operator aid until the vocabulary stabilizes?
- Should the repo add a dedicated validation check that flags a canonical skill copied into `Skills/**` but absent from both the visible runtime surface and documented advanced discovery paths?
