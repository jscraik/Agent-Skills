# Generation And Revision

Convert traces and generated drafts into useful skills through execution-grounded diagnosis, revision, and reruns.

Pack id: pack.skills-sdk
Facet id: generation_revision
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.skills.self-generated-skills-no-average-benefit: Self Generated Skills Show No Average Benefit

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Self-generated skills did not improve benchmark performance on average in SkillsBench, suggesting that models do not reliably author the procedural knowledge they benefit from consuming.

Interpretation notes:
- Generation pipelines should be judged by behavior, not by plausible-looking skill text.

### claim.skills.trajectory-mining-readable-not-transfer: Trajectory Mining Is Readable But Not Transfer

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Mined GUI trajectory clusters can expose inspectable skill structure, but readable clusters do not necessarily transfer into reliable cross-domain policy improvement.

Interpretation notes:
- Inspectability is a useful diagnostic signal but not a substitute for transfer proof.

### claim.skills.boundary-detectors-over-split: Trajectory Boundary Detectors Over Split Skills

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Action-jump trajectory segmentation can find many true skill boundaries but also over-splits ordinary within-skill behavior and is not stable across domains.

Interpretation notes:
- Trace mining should preserve uncertainty around boundary detection instead of converting every segment into a skill.

### claim.skills.frequency-priors-needed-for-mined-skills: Mined Skills Need Frequency-Prior Controls

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Mined-skill methods should be compared against frequency and transition priors because simple priors can explain apparent gains from repeated workflow structure.

Interpretation notes:
- Skills SDK evals for generated skills should include trivial baselines before claiming learned skill value.

### claim.skills.revision-needs-execution-evidence: Skill Revision Needs Execution Evidence

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Trace-conditioned skill revision improves initial LLM-authored skills by diagnosing defects from execution evidence, applying execution-anchored edits, and re-executing candidates.

Interpretation notes:
- Cold-start skill authoring should include a repair loop tied to real execution traces.

### claim.skills.skillrevise-improves-cold-start: SkillRevise Improves Cold Start Skills

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

SkillRevise improved SkillsBench base-agent success from 36.05% to 61.63% by revising initial imperfect skills with execution evidence and re-execution.

Interpretation notes:
- This is evidence for trace-conditioned revision as a Skills SDK improvement lane, not proof that every generated skill is reliable.

### claim.skills.curated-skills-improve-unevenly: Curated Skills Improve Unevenly

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Curated skills can improve agent task success, but measured lift varies by domain and some tasks can regress.

Interpretation notes:
- Skill value claims need baseline comparisons and per-domain breakdowns.

### claim.skills.libraries-accumulate-technical-debt: Skill Libraries Accumulate Technical Debt

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill libraries can accumulate library-level defects as skills are added, reused, patched, and linked to changing dependencies, creating skill technical debt.

Interpretation notes:
- Skill quality work needs library-time maintenance, not only task-time repair.

### claim.skills.registries-need-format-and-coherence: Registries Need Format And Coherence Checks

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill package registries need compiler-style format conformance diagnostics and bundled skillsets that preserve shared context across related skills.

Interpretation notes:
- Registry tooling should evaluate both individual skill shape and cross-skill coherence.

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

### claim.skills.absolute-and-normalized-gain-needed: Skill Benchmarks Need Absolute And Normalized Gain

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

SkillsBench reports both absolute improvement and normalized gain because normalized gain alone can hide the difference between ceiling effects and substantial scaffolding.

Interpretation notes:
- Skills SDK receipts should keep absolute delta, normalized gain, baseline pass rate, and task denominator visible.

### claim.skills.skillops-low-overhead-maintenance: SkillOps Adds Low Overhead Library Maintenance

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

SkillOps models skills with typed contracts, organizes them in a hierarchical ecosystem graph, and diagnoses utility, compatibility, risk, and validation with low library-time overhead.

Interpretation notes:
- Skills SDK maintenance gates can be library-time checks that do not add task-time context or calls.

### claim.skills.skilldex-separates-conformance-from-semantics: Skilldex Separates Conformance From Semantics

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skilldex treats format conformance as objectively scoreable but says semantic description quality and reliable triggering are not solved by word count or parseable frontmatter.

Interpretation notes:
- Skills SDK gates should avoid turning description-length checks into routing-quality proof.

## Principles

### principle.skills.behavioral-lift-over-structural-presence: Behavioral Lift Over Structural Presence

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.curated-skills-improve-unevenly, claim.skills.self-generated-skills-no-average-benefit, claim.skills.trajectory-mining-readable-not-transfer

A skill artifact is useful only when it changes observable behavior on the target task, not merely when it is readable, well-formed, or present in a registry.

Rationale: The benchmark and trajectory-mining papers both separate inspectable skill structure from demonstrated downstream improvement.

Application notes:
- Require a baseline, target task, model, skill version, and observed delta for improvement claims.
- Treat readable clusters or valid frontmatter as diagnostic inputs, not final evidence.
- Keep negative or neutral deltas visible so skill packaging can improve.

## Heuristics

### heuristic.skills.revise-from-traces: Revise From Traces

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.revision-needs-execution-evidence

When a skill fails, revise from concrete execution traces and re-run candidates before asking for another one-shot rewrite.

Use when:
- The skill is syntactically valid but the agent still misses constraints, tool steps, or recovery behavior.
- Cold-start skill generation produced plausible text without task success.

Avoid when:
- The failure is caused by unavailable tools, missing credentials, or a broken environment rather than skill content.
- There is no safe way to preserve representative execution evidence.

### heuristic.skills.require-trivial-baselines-for-generated-skills: Require Trivial Baselines For Generated Skills

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.frequency-priors-needed-for-mined-skills, claim.skills.boundary-detectors-over-split

For mined or generated skills, prove value against frequency, transition-memory, and modality-matched supervised controls before comparing against larger LLM baselines.

Use when:
- A trace-mining or auto-generation pipeline claims skill discovery or policy-transfer lift.
- Repetitive workflows, class imbalance, or output-format adaptation could explain the improvement.

Avoid when:
- The work is a manual knowledge-packaging pass with no generated-skill lift claim.
- The only available proof is qualitative, in which case label it review evidence rather than benchmark evidence.

## Anti-Patterns

### anti-pattern.skills.syntax-valid-behavior-weak: Syntax Valid Behavior Weak

- Type: anti-pattern
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.self-generated-skills-no-average-benefit, claim.skills.revision-needs-execution-evidence

Problem: A generated or reviewed skill looks well formed, so the team treats it as behaviorally ready.

Failure mode: The skill passes structural review but does not improve the agent on the target task, or even regresses a subset of tasks.

Avoidance: Pair structural checks with task baselines, execution traces, and trace-conditioned revision before readiness claims.

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

## Eval Scenarios

### eval.skills.trace-revision-required: Trace Revision Required

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.revision-needs-execution-evidence, claim.skills.skillrevise-improves-cold-start, claim.skills.frequency-priors-needed-for-mined-skills

Knowledge claim: Generated skill revision should be grounded in execution traces and re-execution, not only prose quality.
Behavior under test: The Skills SDK gate requires trace evidence and reruns before accepting a generated-skill revision.
Failure mode: A one-shot rewrite is accepted as a fix because it sounds better.
Expected agent move: Ask for the failing trace, defect class, repair principle, candidate rerun, verifier result, and baseline comparison.
Skill lift target: The answer names trace, defect, repair, rerun, and baseline evidence as required.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.trace-revision-required.md
Promotion status: candidate
Capsule refs: skills-sdk:generation_revision
Weak eval flags: none

Given: A generated skill failed on a verifier-backed task, and the proposed fix is a polished rewrite based on the task prompt alone with no failing trace, defect diagnosis, candidate rerun, or trivial baseline comparison.
Should: The agent rejects the one-shot rewrite as insufficient and routes the fix through trace-conditioned diagnosis, execution-anchored edits, candidate re-execution, and baseline controls.
Expected failure: The agent accepts plausible new skill text without execution evidence.
Reproduce with: references/evals/eval.skills.trace-revision-required.md
