# Operations And Registry

Maintain skill libraries as software ecosystems with contracts, shared context, conformance checks, and library-time health.

Pack id: pack.skills-sdk
Facet id: operations_registry
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.skills.libraries-accumulate-technical-debt: Skill Libraries Accumulate Technical Debt

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill libraries can accumulate library-level defects as skills are added, reused, patched, and linked to changing dependencies, creating skill technical debt.

Interpretation notes:
- Skill quality work needs library-time maintenance, not only task-time repair.

### claim.skills.skillops-low-overhead-maintenance: SkillOps Adds Low Overhead Library Maintenance

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

SkillOps models skills with typed contracts, organizes them in a hierarchical ecosystem graph, and diagnoses utility, compatibility, risk, and validation with low library-time overhead.

Interpretation notes:
- Skills SDK maintenance gates can be library-time checks that do not add task-time context or calls.

### claim.skills.library-size-can-degrade-selection: Large Skill Libraries Can Degrade Selection

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

The survey reports a phase-transition concern where skill selection accuracy degrades beyond a critical library size, implying practical limits on how many skills a single agent can manage.

Interpretation notes:
- Skill library growth should be gated by routing quality and selection accuracy, not only package count.

### claim.skills.quality-metrics-beyond-task-completion: Skill Quality Metrics Go Beyond Task Completion

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill ecosystems need metrics for reusability, composability, and maintainability, because ordinary task-completion benchmarks rarely assess skill quality directly.

Interpretation notes:
- Skills SDK gates should distinguish one task pass from reusable skill quality.

### claim.skills.registries-need-format-and-coherence: Registries Need Format And Coherence Checks

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill package registries need compiler-style format conformance diagnostics and bundled skillsets that preserve shared context across related skills.

Interpretation notes:
- Registry tooling should evaluate both individual skill shape and cross-skill coherence.

### claim.skills.skilldex-separates-conformance-from-semantics: Skilldex Separates Conformance From Semantics

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skilldex treats format conformance as objectively scoreable but says semantic description quality and reliable triggering are not solved by word count or parseable frontmatter.

Interpretation notes:
- Skills SDK gates should avoid turning description-length checks into routing-quality proof.

### claim.skills.execution-modifies-preparation: Skill Execution Modifies Agent Preparation

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

A skill changes the agent's preparation by injecting procedural context and activating execution capabilities before the response, unlike a function call that directly returns a result.

Interpretation notes:
- Skills SDK gates should test routing, context injection, and capability activation separately from final answer quality.

### claim.skills.mcp-complementary-layers: Skills And MCP Are Complementary Layers

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skills package procedural expertise while MCP standardizes connections to tools and data, so a Skills SDK should keep skill guidance and external tool connectivity as complementary layers.

Interpretation notes:
- A skill package should not hide tool permissions or MCP dependencies inside prose.

### claim.skills.absolute-and-normalized-gain-needed: Skill Benchmarks Need Absolute And Normalized Gain

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

SkillsBench reports both absolute improvement and normalized gain because normalized gain alone can hide the difference between ceiling effects and substantial scaffolding.

Interpretation notes:
- Skills SDK receipts should keep absolute delta, normalized gain, baseline pass rate, and task denominator visible.

### claim.skills.adapters-require-alignment-and-stable-workflows: Skill Adapters Require Alignment And Stable Workflows

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill-to-LoRA gains depend on skill-specific adapter alignment and are most suitable for stable procedural workflows with artifact schemas and verification patterns.

Interpretation notes:
- Adapter routing should be a later optimization gate after text-skill behavior and workflow stability are proven.

### claim.skills.curated-skills-improve-unevenly: Curated Skills Improve Unevenly

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Curated skills can improve agent task success, but measured lift varies by domain and some tasks can regress.

Interpretation notes:
- Skill value claims need baseline comparisons and per-domain breakdowns.

### claim.skills.self-generated-skills-no-average-benefit: Self Generated Skills Show No Average Benefit

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Self-generated skills did not improve benchmark performance on average in SkillsBench, suggesting that models do not reliably author the procedural knowledge they benefit from consuming.

Interpretation notes:
- Generation pipelines should be judged by behavior, not by plausible-looking skill text.

### claim.skills.revision-needs-execution-evidence: Skill Revision Needs Execution Evidence

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Trace-conditioned skill revision improves initial LLM-authored skills by diagnosing defects from execution evidence, applying execution-anchored edits, and re-executing candidates.

Interpretation notes:
- Cold-start skill authoring should include a repair loop tied to real execution traces.

### claim.skills.metadata-is-attack-surface: Skill Metadata Is An Attack Surface

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

SKILL.md metadata and instructions are operational text that can affect discovery, selection, loading, and governance decisions, creating semantic supply-chain risk.

Interpretation notes:
- Skill registry and installation checks should treat natural-language fields as security-relevant inputs.

### claim.skills.verification-gates-need-permission-manifest: Verification Gates Need Permission Manifests

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

The survey proposes staged skill trust gates that combine static scanning, semantic intent checks, sandboxed behavior, and validation of a permission manifest against observed behavior.

Interpretation notes:
- Skills SDK security gates should compare declared permissions with actual behavior rather than trusting metadata alone.

### claim.skills.verification-needs-negative-tests: Skill Verification Needs Negative Tests

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill verification should include negative tests for hallucinated procedures, cascading execution failures, conflicting skills, silent permission escalation, and adversarial skill chaining.

Interpretation notes:
- Candidate Skills SDK evals should include bad-answer and overreach patterns, not only happy-path tasks.

### claim.skills.trajectory-mining-readable-not-transfer: Trajectory Mining Is Readable But Not Transfer

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Mined GUI trajectory clusters can expose inspectable skill structure, but readable clusters do not necessarily transfer into reliable cross-domain policy improvement.

Interpretation notes:
- Inspectability is a useful diagnostic signal but not a substitute for transfer proof.

### claim.skills.agent-skills-load-procedural-context: Agent Skills Load Procedural Context

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Agent skills extend LLM agents through composable packages of instructions, code, and resources that can be loaded on demand instead of encoding all procedural knowledge in model weights.

Interpretation notes:
- Treat skill packages as runtime capability surfaces, not only documentation.

## Principles

### principle.skills.skills-are-maintained-ecosystems: Skills Are Maintained Ecosystems

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.libraries-accumulate-technical-debt, claim.skills.registries-need-format-and-coherence

Treat a skill library as a maintained software ecosystem with contracts, shared context, dependency drift, compatibility checks, and registry governance.

Rationale: SkillOps highlights library-time debt, while Skilldex highlights conformance diagnostics and skillset-level shared context.

Application notes:
- Maintain contracts and shared assets alongside individual skill entrypoints.
- Audit utility, compatibility, risk, and validation at the library level.
- Prefer coherent skillsets when related skills depend on the same vocabulary or templates.

### principle.skills.gate-by-evidence-plane: Gate Skills By Evidence Plane

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.execution-modifies-preparation, claim.skills.mcp-complementary-layers, claim.skills.absolute-and-normalized-gain-needed, claim.skills.adapters-require-alignment-and-stable-workflows, claim.skills.skilldex-separates-conformance-from-semantics, claim.skills.quality-metrics-beyond-task-completion

Gate skill readiness by separate evidence planes: format conformance, routing quality, behavioral lift, reusability, composability, maintainability, and security.

Rationale: The papers repeatedly show that each evidence plane answers a different question and cannot substitute for the others.

Application notes:
- Keep conformance score, trigger success, baseline lift, and security review as distinct receipt fields.
- Record both absolute and normalized benchmark movement when claiming skill lift.
- Treat missing evidence as a named blocker rather than collapsing it into a pass/fail label.

## Anti-Patterns

### anti-pattern.skills.task-time-only-maintenance: Task Time Only Maintenance

- Type: anti-pattern
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.libraries-accumulate-technical-debt

Problem: Skill quality is repaired only when a task fails, while library-level compatibility, risk, and dependency drift are ignored.

Failure mode: The library accumulates defects that harm retrieval, composition, or future execution without showing up as one isolated skill failure.

Avoidance: Add library-time maintenance checks for utility, compatibility, risk, validation, shared assets, and dependency changes.

## Checklists

### checklist.skills.skill-packaging-evaluation-loop: Skill Packaging Evaluation Loop

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.curated-skills-improve-unevenly, claim.skills.self-generated-skills-no-average-benefit, claim.skills.revision-needs-execution-evidence, claim.skills.libraries-accumulate-technical-debt, claim.skills.registries-need-format-and-coherence, claim.skills.metadata-is-attack-surface

- [ ] Name the target behavior, domain, model, and task set before packaging the skill.
- [ ] Keep the skill or facet focused enough that its effect can be measured.
- [ ] Preserve source material, claim lineage, and any generated demonstrations separately.
- [ ] Run or record a no-skill, prior-skill, or full-skill-text baseline before claiming lift.
- [ ] Inspect negative and neutral deltas by domain instead of reporting only average lift.
- [ ] Revise failed skills from execution traces and re-run candidates before acceptance.
- [ ] Check skill package format, frontmatter, structure, and shared asset coherence.
- [ ] Audit descriptions and trigger text for discovery, selection, and governance manipulation risk.
- [ ] Track library-level utility, compatibility, risk, validation, and dependency drift over time.
- [ ] Record whether runtime optimization is ordinary text loading, selected slices, or learned behavior adapters.

### checklist.skills.sdk-gate-evidence: Skills SDK Gate Evidence Checklist

- Type: checklist
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.verification-gates-need-permission-manifest, claim.skills.verification-needs-negative-tests, claim.skills.absolute-and-normalized-gain-needed, claim.skills.skillops-low-overhead-maintenance, claim.skills.skilldex-separates-conformance-from-semantics, claim.skills.metadata-is-attack-surface

- [ ] Record the skill source, version, selected facet or package, and target task domain.
- [ ] Record format conformance separately from semantic description quality and routing quality.
- [ ] Include no-skill, prior-skill, or trivial-baseline results before claiming lift.
- [ ] Report absolute delta, normalized gain, baseline pass rate, task denominator, and negative deltas.
- [ ] Include negative tests for hallucinated procedures, permission escalation, conflicting skills, and adversarial chaining.
- [ ] Compare declared permissions with sandbox-observed behavior before elevating trust.
- [ ] Capture trace evidence and rerun candidates when revising generated or weak skills.
- [ ] Check library-level utility, compatibility, risk, validation, shared assets, and dependency drift.
- [ ] Treat registry-facing descriptions, triggers, and examples as operational control inputs.
- [ ] Mark downstream Skills SDK execution proof as pending until the consumer repo runs its own eval lane.

## Rubrics

### rubric.skills.skill-readiness: Skill Readiness Rubric

- Type: rubric
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.curated-skills-improve-unevenly, claim.skills.trajectory-mining-readable-not-transfer, claim.skills.libraries-accumulate-technical-debt, claim.skills.metadata-is-attack-surface

- behavioral-lift: Does the skill improve observable behavior on its target task?
  - pass: The report includes a baseline, task set, model, skill version, and measured improvement or clearly documented non-improvement.
  - fail: The report treats installation, readability, registry score, or structural validity as proof of behavior.
- transfer-boundary: Is the domain boundary for the skill explicit?
  - pass: The skill names the domain where it was tested and calls out domains or tasks with neutral or negative deltas.
  - fail: The skill presents an average lift as universal readiness without per-domain caveats.
- revision-evidence: Are revisions tied to execution evidence?
  - pass: Skill changes cite traces, failure modes, candidate reruns, or verifier outcomes.
  - fail: Skill changes are one-shot rewrites with no evidence that the new text fixes the observed failure.
- library-health: Is the skill safe to maintain inside a library?
  - pass: Contracts, shared assets, dependencies, compatibility, risk, and validation status are tracked.
  - fail: Only the single skill file is checked, leaving library-level drift and composition failures invisible.
- semantic-security: Are registry-facing text fields reviewed as operational control inputs?
  - pass: Descriptions, triggers, examples, and governance-facing text are checked for manipulation and evasion risk.
  - fail: Natural-language metadata is trusted because it passes syntax or frontmatter validation.

## Lenses

### lens.skills.skill-lifecycle-boundary: Skill Lifecycle Boundary Lens

- Type: lens
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.agent-skills-load-procedural-context, claim.skills.curated-skills-improve-unevenly, claim.skills.libraries-accumulate-technical-debt, claim.skills.metadata-is-attack-surface

- Separate skill discovery, selection, loading, execution, revision, registry publication, and library maintenance as different evidence lanes.
- Treat structural conformance, human readability, and registry presence as weaker evidence than task-level behavior.
- Preserve baseline, domain, model, task, and skill-version context for every lift claim.
- Treat skill descriptions and trigger text as operational inputs that can influence retrieval, selection, governance, and security.
- Prefer focused skill modules, selected knowledge capsules, or skillsets with shared assets over broad undifferentiated documentation.

## Eval Scenarios

### eval.skills.library-maintenance-required: Library Maintenance Required

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.libraries-accumulate-technical-debt, claim.skills.skillops-low-overhead-maintenance, claim.skills.library-size-can-degrade-selection, claim.skills.quality-metrics-beyond-task-completion

Knowledge claim: Skill libraries need library-time maintenance because individual task success does not prove ecosystem health.
Behavior under test: The Skills SDK gate requires library-level health evidence before SDK readiness claims.
Failure mode: Task-time repair success is treated as library readiness.
Expected agent move: Request contract catalog, graph or dependency view, utility/compatibility/risk/validation checks, shared-asset coherence, and routing-quality evidence.
Skill lift target: The answer names contract, graph, utility, compatibility, risk, validation, shared-asset, and routing evidence.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.library-maintenance-required.md
Promotion status: candidate
Capsule refs: skills-sdk:operations_registry
Weak eval flags: none

Given: A skill library grows after several successful task-time fixes, but there is no library-level contract catalog, dependency or shared-asset check, utility/compatibility/risk/validation report, or routing-quality check as the library size increases.
Should: The agent classifies this as skill technical debt risk and asks for library-time maintenance evidence before treating the library as SDK-ready.
Expected failure: The agent treats successful individual task repairs as proof that the library is healthy.
Reproduce with: references/evals/eval.skills.library-maintenance-required.md

### eval.skills.description-routing-not-conformance: Description Routing Not Conformance

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.registries-need-format-and-coherence, claim.skills.skilldex-separates-conformance-from-semantics, claim.skills.metadata-is-attack-surface

Knowledge claim: Format conformance is not semantic routing quality.
Behavior under test: The Skills SDK gate separates description conformance from trigger reliability.
Failure mode: Description length and parseability are accepted as routing proof.
Expected agent move: Keep conformance green, mark routing quality unproven, and request trigger/non-trigger selection evidence.
Skill lift target: The answer names conformance, semantic routing, and selection evidence as separate lanes.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.description-routing-not-conformance.md
Promotion status: candidate
Capsule refs: skills-sdk:operations_registry, skills-sdk:supply_chain_security
Weak eval flags: none

Given: A skill package passes frontmatter validation and description-length checks, but cold agents still select it for unrelated tasks and miss it for its intended task because the description uses broad generic language.
Should: The agent classifies conformance as passed but routing quality as unproven, then asks for trigger/non-trigger examples or selection evidence before readiness.
Expected failure: The agent treats valid frontmatter and a long description as proof that the skill routes correctly.
Reproduce with: references/evals/eval.skills.description-routing-not-conformance.md

### eval.skills.routing-scale-regression: Routing Scale Regression

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.library-size-can-degrade-selection, claim.skills.libraries-accumulate-technical-debt, claim.skills.skillops-low-overhead-maintenance

Knowledge claim: Growing a skill library can degrade selection quality even when individual skill files are valid.
Behavior under test: The Skills SDK gate requires routing regression checks after library growth.
Failure mode: Individual package validation is accepted as library-level routing health.
Expected agent move: Request selection accuracy, negative routing, duplicate-overlap, and library maintenance checks.
Skill lift target: The answer names selection accuracy, non-trigger, duplicate-overlap, and maintenance checks.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.routing-scale-regression.md
Promotion status: candidate
Capsule refs: skills-sdk:operations_registry
Weak eval flags: none

Given: A registry import adds many related skills and the package audit passes, but no one reruns selection accuracy checks, non-trigger cases, or duplicate-overlap analysis after the library size increase.
Should: The agent treats library growth as a routing-regression risk and asks for selection, non-selection, overlap, and maintenance evidence before accepting the import.
Expected failure: The agent accepts the larger library because every individual skill package validates.
Reproduce with: references/evals/eval.skills.routing-scale-regression.md

### eval.skills.task-completion-not-quality: Task Completion Not Quality

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.quality-metrics-beyond-task-completion, claim.skills.curated-skills-improve-unevenly, claim.skills.libraries-accumulate-technical-debt

Knowledge claim: Task completion does not prove reusable, composable, or maintainable skill quality.
Behavior under test: The Skills SDK gate keeps task pass evidence separate from ecosystem-quality evidence.
Failure mode: A one-task pass is overclaimed as broad skill quality.
Expected agent move: Report local task proof, block reusable-quality claims, and request cross-task, composition, and drift evidence.
Skill lift target: The answer names local behavior proof and blocks broader quality claims pending additional evidence.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.task-completion-not-quality.md
Promotion status: candidate
Capsule refs: skills-sdk:evaluation_benchmarks, skills-sdk:operations_registry
Weak eval flags: none

Given: A skill passes one verifier-backed task, and the report claims the skill is reusable and maintainable without any cross-task reuse, composition, or environment-change evidence.
Should: The agent accepts the task pass as local behavior evidence but refuses broader skill-quality claims until reusability, composability, and maintainability evidence exists.
Expected failure: The agent turns a single task-completion pass into reusable skill-quality proof.
Reproduce with: references/evals/eval.skills.task-completion-not-quality.md
