# Skill Routing

Keep skill entrypoints compact, prove routing by content shape, and put durable leverage in shared references and repo context.

Pack id: pack.harness-engineering
Facet id: skill_routing
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.

## Claim Cards

### claim.harness.small-skill-set: Shared Skills Should Stay Few And Dense

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Harness behavior should be concentrated into a small shared set of high-density skills before creating many fragmented workflow artifacts.

### claim.harness.content-shape-beats-path: Content Shape Beats Path

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Artifact classification should be based on frontmatter, H1, sections, source links, identifiers, and evidence shape before directory path.

### claim.harness.progressive-disclosure-routing: Progressive Disclosure Needs Routing Proof

- Type: claim-card
- Status: reviewed
- Claim strength: inferred

Short skill descriptions and front matter should be tested as routing surfaces, because detailed instructions only help when the agent loads them at the right time.

### claim.harness.few-general-skills-deep-references: Few General Skills Need Deep References

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Keep only a handful of general workflow skills, then put additional leverage in references, scripts, docs, and tests attached to those workflows.

### claim.harness.shared-instructions-in-codebase: Shared Instructions Belong In The Codebase

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Team agent instructions should live in the codebase so the leverage applies to every agent working on the team's behalf.

### claim.harness.source-prompt-coverage: Source Prompt Coverage Limits Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Sampled or partial artifacts may support local work, but they should not become repo-wide authority without equivalent source-prompt coverage evidence.

### claim.harness.stage-arc-boundary: Stages Need Arc Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Every lifecycle stage should name what came before it, what it owns now, and what proof or artifact it hands off next.

### claim.harness.lifecycle-exit-proof: Exit Needs Status And Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct

A lifecycle stage should not claim done without validation evidence or a concrete reason validation is not applicable.

### claim.harness.knowledge-out-of-heads: Knowledge Must Leave Individual Heads

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Harness engineering should move repeated team knowledge out of individual heads into repo surfaces that every agent can use.

### claim.harness.context-budget-discipline: Context Budget Needs Discipline

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Harnesses should load the smallest relevant context slice and compile repeated rules into durable controls where feasible.

### claim.harness.spec-source-toolchain: Specifications Need A Toolchain

- Type: claim-card
- Status: reviewed
- Claim strength: direct

Specifications should be treated as versioned source artifacts with linting, examples, tests, graders, changelogs, and release gates.

## Principles

### principle.harness.stage-owns-one-arc: A Stage Owns One Arc

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.stage-arc-boundary, claim.harness.lifecycle-exit-proof

Treat each lifecycle stage as owning a bounded arc, not the whole program.

Rationale: Downstream agents need to know the entry evidence, active authority, exit proof, handoff target, and closure boundary before trusting a stage output.

### principle.harness.skill-surface-stays-small: Skill Surface Stays Small

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.small-skill-set, claim.harness.few-general-skills-deep-references

Keep skills few, workflow-shaped, and backed by deeper local references.

Rationale: A small high-quality skill surface is easier for agents to route to, while references, scripts, docs, and tests can hold detail without fragmenting triggers.

### principle.harness.shared-repo-context-over-personal-context: Shared Repo Context Over Personal Context

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.shared-instructions-in-codebase, claim.harness.knowledge-out-of-heads

Put recurring agent context where the team and every agent can inherit it.

Rationale: Personal instructions help one operator, but repo-owned docs, skills, scripts, tests, and errors compound across the whole team.

## Heuristics

### heuristic.harness.classify-by-content-shape: Classify By Content Shape

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.content-shape-beats-path

When an artifact path and content disagree, classify from content first and record the mismatch instead of silently trusting the path.

### heuristic.harness.load-smallest-context-slice: Load Smallest Context Slice

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.context-budget-discipline

Load the narrowest spec, source, or precedent slice that can govern the task, then follow pointers only when needed.

### heuristic.harness.keep-general-skills-small: Keep General Skills Small

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.few-general-skills-deep-references

Add a general skill only for a recurring workflow with a stable trigger, output, and closeout state.

### heuristic.harness.test-skill-routing: Test Skill Routing

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.progressive-disclosure-routing

Test whether a cold agent selects the intended skill before expanding that skill's detailed instructions.

## Anti-Patterns

### anti-pattern.harness.context-dump: Context Dump

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.context-budget-discipline, claim.harness.spec-source-toolchain

Problem: The harness loads whole doctrine corpora or long prompt blocks instead of targeted rule slices.

Failure mode: The agent spends context and compute on irrelevant material while repeated rules remain unenforced.

Avoidance: Use clause IDs, source locators, compact pointers, validators, templates, skills, and evals to make recurring guidance operational.

### anti-pattern.harness.personal-agent-context-silos: Personal Agent Context Silos

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.shared-instructions-in-codebase, claim.harness.knowledge-out-of-heads

Problem: Important team guidance lives only in one operator's personal agent instructions.

Failure mode: Other agents repeat the same mistakes because the knowledge never reaches the repo surfaces they inherit.

Avoidance: Promote repeated shared guidance into repo docs, skills, scripts, tests, errors, or review contracts.

## Eval Scenarios

### eval.harness.context-dump-instead-of-slice: Context Dump Instead Of Slice

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.context-budget-discipline

Given: A task needs one validation rule, but the harness loads an entire doctrine corpus and several unrelated skill files.
Should: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Expected failure: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml

### eval.harness.skill-frontmatter-not-routed: Skill Frontmatter Not Routed

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Derived from claims: claim.harness.progressive-disclosure-routing

Given: A detailed skill contains correct instructions, but cold agents often do not select it for the tasks it is meant to govern.
Should: The agent treats the short description and trigger surface as the first thing to test and repair.
Expected failure: The agent keeps adding detail to the skill body even though routing is the failing layer.
Reproduce with: tests/fixtures/valid/packs/harness-engineering/pack.yaml
