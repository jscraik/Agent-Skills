# Governance and style appendix

## Table of Contents
- [Deck-aligned upgrade checklist](#deck-aligned-upgrade-checklist)
- [Skill-graph contract gap report](#skill-graph-contract-gap-report)
- [Philosophy and tradeoffs](#philosophy-and-tradeoffs)
- [Anti-patterns and caveats](#anti-patterns-and-caveats)
- [Variation and adaptation](#variation-and-adaptation)
- [Empowering execution style](#empowering-execution-style)

## Deck-aligned upgrade checklist

Use this checklist before drafting or revising a recursive skill runbook.

### 1) Cockpit modes and delegation metadata

- [x] Keep `mode` explicit in delegation metadata for each task profile.
- [x] Align vocabulary to deck terms (**autopilot / co-pilot / manual override**) and document compatibility aliases where downstream enums still use `collaboration`.
- [x] Add a one-line migration note in skill-graph docs when a profile still emits `collaboration`.
- [ ] Require each profile to state `delegation` rationale and cost-benefit assumptions (`HBT`, `APT`, `Ps`) at run start.

### 2) Recipe/runner/tool architecture in SKILL.md

- [x] Keep `SKILL.md` as SOP + routing instructions and move helpers to `references/` and `scripts/`.
- [x] Add an explicit “architecture” block: **LLM processor (reasoning) + skill recipe (logic) + MCP/tools (actions)**.
- [ ] Document when `tools`/scripts are optional vs required, with exact argument names.

### 3) Structure and progressive disclosure

- [x] Preserve metadata -> SKILL body -> `references/` -> `scripts/` loading order.
- [x] Add a brief section in this file that states the minimum fields to keep in `SKILL.md` vs `references/`.
- [x] Add a short "load contract" for any dynamic injection inputs used by recursive runs.

### 4) Routing-by-description and boundaries

- [x] Keep description as WHAT + WHEN + non-goals (selection boundary).
- [ ] Add one mandatory negative-trigger case for each major boundary.
- [ ] Require acceptance assertions for trigger and non-trigger prompts in `references/evals.yaml`.

### 5) Sandbox boundary and invocation gating

- [x] Split process guidance into:
  - **Decision model** (pure text/metadata selection in SKILL/description)
  - **Script execution model** (explicit command allowlist, `--dry-run`, `--confirm`, approvals)
- [ ] Before any recursive run, require pre-checks for:
  - controls existence (`kill-switch`, `rollback-required`, rollout mode),
  - invocation envelope fields,
  - sub-agent isolation and network allowlist.
- [ ] Require gate checks before approval:
  - `run`, `iteration_journal`, `promotion_decision` completeness
  - reviewer signatures + provenance fields.

### 6) Workflow archetypes

- [x] Add explicit mapping in this skill to deck patterns:
  - **sequential**: strict step order,
  - **router**: multiple skill/branch paths,
  - **orchestrator**: coordinator + bounded child workers.
- [x] Keep SKILL execution defaulted to sequential, with optional router/orchestrator paths.

### 7) Evaluation + two-agent hardening loop

- [x] Use RED → GREEN → REFACTOR sequence.
- [ ] Keep a two-agent pattern for upgrades: one author + one verification pass before merge.
- [ ] Add explicit pressure-tests for rationalization and policy bypass attempts.

## Skill-graph contract gap report

| Contract/doc | What the deck emphasizes | Current state | Gap / action |
| --- | --- | --- | --- |
| `docs/skill-graphs/schemas/task-profile.schema.md` | Cockpit mode vocabulary: `autopilot/co-pilot/manual` | Updated to canonical wording with compatibility note (`collaboration` -> `co-pilot`). | ✅ Updated plus legacy alias note. |
| `docs/skill-graphs/question-lifecycle.md` | Question timing, ownership, and post-run feedback boundaries | New canonical contract | ✅ Added runtime-owned question lifecycle contract. |
| `docs/skill-graphs/knowledge-graph-operating-model.md` | Explicit architecture + invocation delegation framing | Mentions skills/tools/chef and optional delegation; no explicit deck-language terms | ✅ Added explicit architecture split + mode map + archetype mapping. |
| `docs/skill-graphs/index.md` | Workflow archetypes (sequential/router/orchestrator) | Shows phase pipeline only | ✅ Added explicit mapping to deck archetypes. |
| `docs/skill-graphs/workflows/promotion-gate.md` | Control gates + security + human gate before promotion | Has checks and reviewer gate but no explicit invocation-boundary section | ✅ Added explicit Invocation boundary checks section. |
| `docs/skill-graphs/runbooks/kill-switch-and-escalation.md` | Invocation gating hierarchy + safe rollback | Has control hierarchy; no direct link from SKILL to mandatory pre-run checks | ✅ Added mandatory pre-run invocation check section and cross-reference. |
| `utilities/skill-creator/SKILL.md` | Dynamic injection and boundary-safe loading | Moved details to this appendix for compaction safety. | ✅ Appendix now carries extended governance details. |

## Philosophy and tradeoffs
- Use this skill when consistent decision-making matters more than one-off execution because project context should drive the approach.
- Principle and mindset: prioritize tradeoffs and constraints over rigid checklists; understand why each step exists.
- Ask this to keep outcomes robust: Why is this the right default, and what could change this outcome?
- How do we adapt if constraints shift?
- What evidence is needed before choosing one path over another?

## Anti-patterns and caveats
- Avoid applying this playbook generically without checking repository-specific context.
- **NEVER** skip required validation gates when behavior changes.
- **DO NOT** use this skill as a rigid replacement for engineering judgment.
- **DON'T** ignore warnings or assume one pattern fits all repos.
- **DON'T** introduce legacy-preservation code paths unless the user explicitly asks for compatibility.
- Common pitfall: treating anti-patterns as optional.
- Incorrect assumptions here can lead to fragile guidance.
- Warning: wrong sequencing can create avoidable regressions.

## Variation and adaptation
- Vary the workflow by team size, risk, and deployment target.
- Use different strategies for small, medium, and large changes.
- Adapt recommendations to the specific environment and avoid repetitive templates.
- Avoid generic or cookie-cutter responses; craft context-specific alternatives.
- Keep outputs diverse and not repetitive.
- Converge on a custom path only after evidence review.
- Different constraints should produce different, non-generic recommendations.

## Empowering execution style
- Be capable of exploring multiple options and enabling the team to make safe decisions.
- Unlock confidence by explaining options and tradeoffs clearly.
- Feel free to be creative while staying rigorous and precise.
- Push boundaries with practical alternatives when simple recipes fail.
- Enable outcomes-oriented problem solving.
