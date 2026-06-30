# Skill Routing

Keep skill entrypoints compact, prove routing by content shape, and put durable leverage in shared references and repo context.

Pack id: pack.harness-engineering
Facet id: skill_routing
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: validated

## Claim Cards

### claim.harness.small-skill-set: Shared Skills Should Stay Few And Dense

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Harness behavior should be concentrated into a small shared set of high-density skills before creating many fragmented workflow artifacts.

Interpretation notes:
- This claim supports skill-surface consolidation guidance.

### claim.harness.content-shape-beats-path: Content Shape Beats Path

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Artifact classification should be based on frontmatter, H1, sections, source links, identifiers, and evidence shape before directory path.

Interpretation notes:
- This claim protects routing from directory-name overconfidence.

### claim.harness.progressive-disclosure-routing: Progressive Disclosure Needs Routing Proof

- Type: claim-card
- Status: reviewed
- Claim strength: inferred
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

Short skill descriptions and front matter should be tested as routing surfaces, because detailed instructions only help when the agent loads them at the right time.

Interpretation notes:
- The routing-proof phrasing is an inference from the progressive-disclosure practice.

### claim.harness.few-general-skills-deep-references: Few General Skills Need Deep References

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Keep only a handful of general workflow skills, then put additional leverage in references, scripts, docs, and tests attached to those workflows.

Interpretation notes:
- This extends the earlier small-skill-set claim with the placement rule for extra detail.

### claim.harness.shared-instructions-in-codebase: Shared Instructions Belong In The Codebase

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Team agent instructions should live in the codebase so the leverage applies to every agent working on the team's behalf.

Interpretation notes:
- This strengthens the repo-as-harness claim with a concrete instruction-maintenance practice.

### claim.harness.source-prompt-coverage: Source Prompt Coverage Limits Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Sampled or partial artifacts may support local work, but they should not become repo-wide authority without equivalent source-prompt coverage evidence.

Interpretation notes:
- This claim is especially relevant when turning research into operational doctrine.

### claim.harness.stage-arc-boundary: Stages Need Arc Boundaries

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Every lifecycle stage should name what came before it, what it owns now, and what proof or artifact it hands off next.

Interpretation notes:
- This claim makes stage ownership explicit instead of letting one stage imply whole-program closure.

### claim.harness.lifecycle-exit-proof: Exit Needs Status And Proof

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

A lifecycle stage should not claim done without validation evidence or a concrete reason validation is not applicable.

Interpretation notes:
- This claim supports closure-grade output rules.

### claim.harness.knowledge-out-of-heads: Knowledge Must Leave Individual Heads

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Harness engineering should move repeated team knowledge out of individual heads into repo surfaces that every agent can use.

Interpretation notes:
- This is a knowledge-management claim with agent-readiness consequences.

### claim.harness.context-budget-discipline: Context Budget Needs Discipline

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Harnesses should load the smallest relevant context slice and compile repeated rules into durable controls where feasible.

Interpretation notes:
- This complements the small skill set claim by treating context as a scarce execution resource.

### claim.harness.spec-source-toolchain: Specifications Need A Toolchain

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Specifications should be treated as versioned source artifacts with linting, examples, tests, graders, changelogs, and release gates.

Interpretation notes:
- This supports moving repeated prompt instructions into durable specs, validators, skills, tests, and evals.

## Principles

### principle.harness.stage-owns-one-arc: A Stage Owns One Arc

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.stage-arc-boundary, claim.harness.lifecycle-exit-proof

Treat each lifecycle stage as owning a bounded arc, not the whole program.

Rationale: Downstream agents need to know the entry evidence, active authority, exit proof, handoff target, and closure boundary before trusting a stage output.

Application notes:
- Name left, active, and right arcs before mutating files, trackers, PRs, or closure state.
- Preserve unfinished scope when a stage lacks authority to close it.

### principle.harness.skill-surface-stays-small: Skill Surface Stays Small

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.small-skill-set, claim.harness.few-general-skills-deep-references

Keep skills few, workflow-shaped, and backed by deeper local references.

Rationale: A small high-quality skill surface is easier for agents to route to, while references, scripts, docs, and tests can hold detail without fragmenting triggers.

Application notes:
- Make a new skill only when the trigger and output contract are durable.
- Put variant detail into references, fixtures, scripts, or repo docs.
- Review skill sprawl as a routing risk.

### principle.harness.shared-repo-context-over-personal-context: Shared Repo Context Over Personal Context

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.shared-instructions-in-codebase, claim.harness.knowledge-out-of-heads

Put recurring agent context where the team and every agent can inherit it.

Rationale: Personal instructions help one operator, but repo-owned docs, skills, scripts, tests, and errors compound across the whole team.

Application notes:
- Move repeated personal reminders into repo-visible artifacts.
- Keep private preferences private, but promote shared operating knowledge.
- Prefer surfaces that travel with the code under review.

## Heuristics

### heuristic.harness.classify-by-content-shape: Classify By Content Shape

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.content-shape-beats-path

When an artifact path and content disagree, classify from content first and record the mismatch instead of silently trusting the path.

Use when:
- Resuming from an existing .harness artifact.
- A plan, spec, review, or eval appears in an unexpected directory.

Avoid when:
- The artifact is a simple local note with no lifecycle authority claim.
- The user explicitly asks only for file organization.

### heuristic.harness.load-smallest-context-slice: Load Smallest Context Slice

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.context-budget-discipline

Load the narrowest spec, source, or precedent slice that can govern the task, then follow pointers only when needed.

Use when:
- A large instruction corpus contains a small relevant rule subset.
- Context size competes with problem-solving compute.
- Clause IDs or source locators can target the right fragment.

Avoid when:
- The user asks for a broad synthesis or audit.
- The task risk requires reading the full governing contract.

### heuristic.harness.keep-general-skills-small: Keep General Skills Small

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.few-general-skills-deep-references

Add a general skill only for a recurring workflow with a stable trigger, output, and closeout state.

Use when:
- A team wants to encode repeated agent behavior.
- Existing skills are becoming long or hard to route.

Avoid when:
- The need is one-off project context that belongs in local docs or tests.
- The proposed skill only wraps reference material with no workflow contract.

### heuristic.harness.test-skill-routing: Test Skill Routing

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.progressive-disclosure-routing

Test whether a cold agent selects the intended skill before expanding that skill's detailed instructions.

Use when:
- A skill has short front matter that gates a longer workflow.
- Agents keep missing or misapplying the intended instruction surface.

Avoid when:
- The skill is manually invoked by the user every time.
- The failure is in the detailed workflow after routing already succeeds.

## Anti-Patterns

### anti-pattern.harness.context-dump: Context Dump

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.context-budget-discipline, claim.harness.spec-source-toolchain

Problem: The harness loads whole doctrine corpora or long prompt blocks instead of targeted rule slices.

Failure mode: The agent spends context and compute on irrelevant material while repeated rules remain unenforced.

Avoidance: Use clause IDs, source locators, compact pointers, validators, templates, skills, and evals to make recurring guidance operational.

### anti-pattern.harness.personal-agent-context-silos: Personal Agent Context Silos

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.harness.shared-instructions-in-codebase, claim.harness.knowledge-out-of-heads

Problem: Important team guidance lives only in one operator's personal agent instructions.

Failure mode: Other agents repeat the same mistakes because the knowledge never reaches the repo surfaces they inherit.

Avoidance: Promote repeated shared guidance into repo docs, skills, scripts, tests, errors, or review contracts.

## Eval Scenarios

### eval.harness.context-dump-instead-of-slice: Context Dump Instead Of Slice

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_repo_or_corpus_reference
- Derived from claims: claim.harness.context-budget-discipline

Knowledge claim: Principle under test: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Behavior under test: Observable agent behavior when an task needs one validation rule, but the harness loads an entire doctrine corpus and several unrelated skill files.
Failure mode: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.
Expected agent move: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Skill lift target: The response avoids the weak pattern (The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced) and instead shows the expected behavior (The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.context-dump-instead-of-slice.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: A task needs one validation rule, but the harness loads an entire doctrine corpus and several unrelated skill files.
Should: The agent uses the narrow rule locator or clause ID and follows deeper references only if the task requires them.
Expected failure: The agent treats maximum context as safer even though it crowds out task reasoning and leaves repeated rules unenforced.
Reproduce with: references/evals/eval.harness.context-dump-instead-of-slice.md

### eval.harness.skill-frontmatter-not-routed: Skill Frontmatter Not Routed

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.harness.progressive-disclosure-routing

Knowledge claim: Principle under test: The agent treats the short description and trigger surface as the first thing to test and repair.
Behavior under test: Observable agent behavior when an detailed skill contains correct instructions, but cold agents often do not select it for the tasks it is meant to govern.
Failure mode: The agent keeps adding detail to the skill body even though routing is the failing layer.
Expected agent move: The agent treats the short description and trigger surface as the first thing to test and repair.
Skill lift target: The response avoids the weak pattern (The agent keeps adding detail to the skill body even though routing is the failing layer) and instead shows the expected behavior (The agent treats the short description and trigger surface as the first thing to test and repair).
Proof route: references/evals.yaml
Fixture path: references/evals/eval.harness.skill-frontmatter-not-routed.md
Promotion status: candidate
Capsule refs: harness-engineering
Weak eval flags: none

Given: A detailed skill contains correct instructions, but cold agents often do not select it for the tasks it is meant to govern.
Should: The agent treats the short description and trigger surface as the first thing to test and repair.
Expected failure: The agent keeps adding detail to the skill body even though routing is the failing layer.
Reproduce with: references/evals/eval.harness.skill-frontmatter-not-routed.md
