# Ryan Repo Knowledge

Treat repository-local, versioned, progressively disclosed knowledge as the agent control plane.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: repo_knowledge
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.repo-knowledge-system-of-record: Repository Knowledge Should Be The System Of Record

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-ready repositories should make structured, versioned, repository-local knowledge the system of record instead of relying on large instruction blobs or external tacit context.

Interpretation notes:
- This supports a principal engineer skill that reviews repository knowledge architecture, not just code diffs.

### claim.ryan.agent-legibility: Agent Legibility Is An Engineering Goal

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Software systems should expose code, docs, schemas, plans, diagnostics, runtime state, and validation evidence in forms agents can inspect and act on.

Interpretation notes:
- This expands principal engineering review beyond static code quality into operational inspectability.

### claim.ryan.tool-discovery: Agents Need Tool Discovery

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-first tools need machine-readable discovery surfaces that expose names, descriptions, schemas, and examples.

Interpretation notes:
- This is a principal-engineering review concern for internal platform tools and CLIs.

### claim.harness.shared-instructions-in-codebase: Shared Instructions Belong In The Codebase

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Team agent instructions should live in the codebase so the leverage applies to every agent working on the team's behalf.

Interpretation notes:
- This strengthens the repo-as-harness claim with a concrete instruction-maintenance practice.

### claim.harness.context-budget-discipline: Context Budget Needs Discipline

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Harnesses should load the smallest relevant context slice and compile repeated rules into durable controls where feasible.

Interpretation notes:
- This complements the small skill set claim by treating context as a scarce execution resource.

### claim.ryan.enforce-boundaries: Enforce Boundaries And Allow Local Freedom

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: article_source_note_paraphrase

Agent-scale systems should enforce architectural invariants mechanically while leaving agents freedom inside those boundaries.

Interpretation notes:
- This should become a review rule for architecture, platform, and agent workflow changes.

### claim.harness.agent-legible-failures: Failures Should Be Agent-Legible

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Failing commands should tell agents the command, location, exit code, focused output, and likely remediation path.

Interpretation notes:
- This turns validation failure output into part of the harness, not just a terminal event.

### claim.ryan.context-seeking-framework: Agents Need Context-Seeking Frameworks

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Effective agent harnesses should teach agents how to seek task-relevant context through tools and workflows rather than relying on large piles of static rules.

Interpretation notes:
- This extends repo knowledge from storage into active context-retrieval behavior.

### claim.ryan.prompt-to-paved-workflow: Prompts Should Collapse To Paved Workflows

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent prompts should route into known workflows that explain what matters, common task shapes, and where to learn more.

Interpretation notes:
- This maps directly to skill routing and workflow front doors.

### claim.harness.progressive-disclosure-routing: Progressive Disclosure Needs Routing Proof

- Type: claim-card
- Status: reviewed
- Claim strength: inferred
- Source boundaries: local_source_reference, local_repo_or_corpus_reference

Short skill descriptions and front matter should be tested as routing surfaces, because detailed instructions only help when the agent loads them at the right time.

Interpretation notes:
- The routing-proof phrasing is an inference from the progressive-disclosure practice.

### claim.harness.small-skill-set: Shared Skills Should Stay Few And Dense

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_source_reference

Harness behavior should be concentrated into a small shared set of high-density skills before creating many fragmented workflow artifacts.

Interpretation notes:
- This claim supports skill-surface consolidation guidance.

### claim.harness.source-prompt-coverage: Source Prompt Coverage Limits Authority

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: local_repo_or_corpus_reference

Sampled or partial artifacts may support local work, but they should not become repo-wide authority without equivalent source-prompt coverage evidence.

Interpretation notes:
- This claim is especially relevant when turning research into operational doctrine.

## Principles

### principle.ryan.repo-knowledge-is-control-plane: Repository Knowledge Is The Control Plane

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_source_reference
- Derived from claims: claim.ryan.repo-knowledge-system-of-record, claim.harness.shared-instructions-in-codebase

Keep agent-operating knowledge in small, mapped, versioned repository surfaces that route to deeper sources of truth.

Rationale: Agents need progressive disclosure and mechanically checkable local context more than broad instruction dumps or inaccessible external memory.

Application notes:
- Use entry-point documents as maps, not encyclopedias.
- Link to owned deeper docs, schemas, plans, and checks.
- Make freshness, ownership, and validation mechanically inspectable where practical.

### principle.ryan.context-seeking-over-rule-piles: Context Seeking Beats Rule Piles

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified, local_source_reference, local_repo_or_corpus_reference
- Derived from claims: claim.ryan.context-seeking-framework, claim.ryan.prompt-to-paved-workflow, claim.harness.progressive-disclosure-routing

Agent instructions should define how to seek, select, and apply context instead of trying to preload every rule.

Rationale: Stochastic agents and long-running trajectories need repeatable context-recovery behavior more than static context volume.

Application notes:
- Tell agents what kind of context matters for common task shapes.
- Route prompts to paved workflows and deeper references.
- Prefer context maps, tools, hooks, and validation loops over instruction sprawl.

## Heuristics

### heuristic.ryan.make-tools-machine-discoverable: Make Tools Machine Discoverable

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase
- Derived from claims: claim.ryan.tool-discovery

If a tool matters to agent work, expose its purpose, input shape, examples, and failure modes in a machine-readable discovery surface.

Use when:
- A CLI or internal platform tool is useful but agents rarely invoke it.
- Tool use depends on human memory, training data, or shell exploration.
- The tool could be represented through MCP, schema-backed docs, command manifests, or examples.

Avoid when:
- The tool touches secrets or destructive operations without an authorization boundary.
- The discovery surface would advertise an unstable or unsupported workflow.

### heuristic.ryan.collapse-prompts-to-paved-workflows: Collapse Prompts To Paved Workflows

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.prompt-to-paved-workflow, claim.ryan.context-seeking-framework

For recurring work, make the agent translate an open-ended prompt into a named workflow with known context sources, checks, and closeout proof.

Use when:
- The task belongs to a repeated delivery, review, repair, or research pattern.
- The repo already has docs, scripts, skills, or validators for the pattern.
- Agents often ask for or miss the same context.

Avoid when:
- The task is genuinely novel and needs exploration before workflow capture.
- The workflow would hide a human decision that has not been made.

## Anti-Patterns

### anti-pattern.ryan.monolithic-agent-manual: Monolithic Agent Manual

- Type: anti-pattern
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_repo_or_corpus_reference
- Derived from claims: claim.ryan.repo-knowledge-system-of-record, claim.harness.context-budget-discipline

Problem: A single oversized agent instruction file tries to carry architecture, product, workflow, validation, and team norms.

Failure mode: Context budget is consumed by stale or competing guidance, and the agent cannot tell which deeper source is current or authoritative.

Avoidance: Keep the entry point short and route to deeper owned documents, executable plans, schemas, and checks with clear freshness and ownership expectations.

## Rubrics

### rubric.ryan.principal-engineer-agent-readiness: Principal Engineer Agent Readiness

- Type: rubric
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: article_source_note_paraphrase, local_repo_or_corpus_reference
- Derived from claims: claim.ryan.agent-legibility, claim.ryan.enforce-boundaries, claim.harness.agent-legible-failures

- local-context: Can a cold agent find the relevant source of truth without hidden human context?
  - pass: Entry points route to current repo-local docs, schemas, plans, and validation commands.
  - fail: The work depends on chat history, external docs, tacit memory, or one giant instruction blob.
- enforceable-boundaries: Are the important architectural and workflow boundaries mechanically enforced?
  - pass: Linters, schemas, tests, scripts, or diagnostics encode the boundary and recovery path.
  - fail: The boundary exists only as advice, preference, or review folklore.
- recovery-loop: Can the agent observe failure and recover through owned tools?
  - pass: Logs, metrics, traces, screenshots, tests, or command diagnostics expose the failure and next action.
  - fail: Failure requires a human to inspect inaccessible runtime state or infer missing context.
