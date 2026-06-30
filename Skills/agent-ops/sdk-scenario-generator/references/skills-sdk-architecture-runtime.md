# Architecture And Runtime

Use skills as progressively loaded procedural capability packages while keeping runtime loading separate from behavior proof.

Pack id: pack.skills-sdk
Facet id: architecture_runtime
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.skills.agent-skills-load-procedural-context: Agent Skills Load Procedural Context

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Agent skills extend LLM agents through composable packages of instructions, code, and resources that can be loaded on demand instead of encoding all procedural knowledge in model weights.

Interpretation notes:
- Treat skill packages as runtime capability surfaces, not only documentation.

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

### claim.skills.adapters-can-represent-behavior: Adapters Can Represent Skill Behavior

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill-to-LoRA represents skill behavior as dynamically loaded adapters, using full skill text offline to synthesize demonstrations while omitting that full document at runtime.

Interpretation notes:
- Adapter-based skill delivery is a possible runtime optimization, but the pack should keep it distinct from ordinary text-based skill packaging.

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

### claim.skills.libraries-accumulate-technical-debt: Skill Libraries Accumulate Technical Debt

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Skill libraries can accumulate library-level defects as skills are added, reused, patched, and linked to changing dependencies, creating skill technical debt.

Interpretation notes:
- Skill quality work needs library-time maintenance, not only task-time repair.

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

## Principles

### principle.skills.progressive-disclosure-with-proof: Progressive Disclosure With Proof

- Type: principle
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.agent-skills-load-procedural-context, claim.skills.curated-skills-improve-unevenly

Load skill context progressively, but require behavioral proof before claiming that the loaded skill improved the agent.

Rationale: Progressive disclosure makes skills practical at runtime, while SkillsBench shows that skill effects are uneven and must be measured rather than assumed.

Application notes:
- Treat activation, selection, and context loading as separate from task success.
- Compare no-skill, curated-skill, and generated-skill behavior when a lift claim matters.
- Preserve the selected skill version and task domain with the result.

## Heuristics

### heuristic.skills.separate-text-from-learned-behavior: Separate Text From Learned Behavior

- Type: heuristic
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.adapters-can-represent-behavior

Consider learned behavior adapters only after the text skill has a clear behavior target, demonstration source, baseline, and runtime token-cost problem.

Use when:
- Full skill text is repeatedly injected and token cost is a material runtime constraint.
- The skill behavior can be demonstrated offline and compared online.

Avoid when:
- Auditability, human review, or rapid editing matters more than token reduction.
- The skill has not yet shown value as ordinary text or trace-grounded procedure.

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

### eval.skills.skill-mcp-boundary-required: Skill MCP Boundary Required

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.execution-modifies-preparation, claim.skills.mcp-complementary-layers, claim.skills.verification-gates-need-permission-manifest

Knowledge claim: Skills prepare the agent while MCP and tools provide connectivity, so the SDK must keep procedure, tool access, and permission evidence separate.
Behavior under test: The Skills SDK gate refuses to hide MCP/tool dependencies inside skill prose.
Failure mode: A skill package is accepted even though its runtime dependencies and permissions are not declared.
Expected agent move: Require explicit MCP/tool dependency declaration, permission manifest, and a later observed-behavior check.
Skill lift target: The answer names skill procedure, MCP connectivity, declared permissions, and observed behavior as separate checks.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.skill-mcp-boundary-required.md
Promotion status: candidate
Capsule refs: skills-sdk:architecture_runtime
Weak eval flags: none

Given: A proposed skill teaches a workflow that depends on a database MCP server and shell scripts, but the package records those dependencies only in prose and has no explicit tool, MCP, or permission boundary.
Should: The agent blocks SDK readiness until the skill separates procedural guidance from MCP/tool connectivity and records declared capabilities that can be compared with observed behavior.
Expected failure: The agent treats the workflow prose as enough to authorize runtime tool and MCP access.
Reproduce with: references/evals/eval.skills.skill-mcp-boundary-required.md

### eval.skills.adapter-optimization-premature: Adapter Optimization Premature

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.skills.adapters-can-represent-behavior, claim.skills.adapters-require-alignment-and-stable-workflows, claim.skills.curated-skills-improve-unevenly

Knowledge claim: Learned behavior adapters are useful only after stable skill behavior and alignment controls exist.
Behavior under test: The Skills SDK gate blocks premature runtime optimization.
Failure mode: Token-cost pressure is treated as enough to replace auditable skill text.
Expected agent move: Require behavior proof, workflow stability, schema/verifier evidence, and adapter-alignment controls before optimization.
Skill lift target: The answer names behavior proof, workflow stability, artifact schema, verifier pattern, and adapter controls.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.skills.adapter-optimization-premature.md
Promotion status: candidate
Capsule refs: skills-sdk:architecture_runtime
Weak eval flags: none

Given: A team wants to convert a new skill into adapter-like learned behavior to reduce context cost, but the text skill has no baseline lift, unstable workflow steps, and no adapter-alignment controls.
Should: The agent keeps adapterization as a later optimization lane and requires proven text-skill behavior, stable workflow evidence, artifact schema, verifier pattern, and wrong/shared-adapter controls first.
Expected failure: The agent recommends adapterization because long skill text costs tokens, without proving the skill behavior or alignment.
Reproduce with: references/evals/eval.skills.adapter-optimization-premature.md
