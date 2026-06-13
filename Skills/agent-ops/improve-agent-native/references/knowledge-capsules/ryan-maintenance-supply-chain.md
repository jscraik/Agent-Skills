# Maintenance And Supply Chain

Use cheap code generation to reduce maintenance burden, simplify configuration, harden dependencies, and prove practices in small repositories.

Pack id: pack.ryan-lopopolo-principal-engineering
Facet id: maintenance_supply_chain
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: reviewed

## Claim Cards

### claim.ryan.hardened-core-many-bindings: Harden One Core Before Many Implementations

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

The user-provided source note attributes to Ryan the speculation that ecosystem risk may be reduced by concentrating scrutiny into a single hardened core implementation with bindings rather than duplicating many implementations of the same concept.

Interpretation notes:
- This preserves the source's speculative modality and should not be read as an established standard or universal mandate.

### claim.ryan.harness-transfers-to-oss: Harness Practices Transfer To OSS

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Harness engineering practices can be applied outside product teams, including to Rust open-source maintenance work.

Interpretation notes:
- This supports using small projects as laboratories for harness patterns.

### claim.ryan.rand-mt-repo-harness-surface: Rand MT Shows OSS Harness Surfaces

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: public_repository_page_inspection_not_full_clone

A small Rust OSS crate can carry agent-facing and maintenance-facing harness surfaces such as AGENTS.md, architecture docs, contributing docs, scripts, tests, pinned toolchain files, and dependency policy.

Interpretation notes:
- This records visible repository surfaces only; it does not prove that the repository practices were effective without clone-level or validation evidence.

### claim.ryan.intaglio-typed-boundary-validation: Intaglio Shows Typed Boundary Validation

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: public_repository_page_inspection_not_full_clone

The public Intaglio repository page documents typed API variants and CI/sanitizer checks around unsafe-code validation.

Interpretation notes:
- This supports misuse-resistant interface and supply-chain maintenance assets.
- This records page-visible repository documentation only; it is not clone-level evidence that CI was executed or that the practice was effective.

### claim.ryan.toml-reduces-footguns: TOML Can Reduce Configuration Footguns

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Configuration formats with fewer parser ambiguities and footguns can be preferable when migrating agent-maintained configuration.

Interpretation notes:
- The date literal observation is a caveat that simpler formats still have semantics to learn.

### claim.ryan.oss-maintenance-runbooks: Agent Maintenance Needs Checked-In Runbooks

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent-maintained repositories should keep golden workflows, onboarding commands, automations, and guardrails in checked-in documentation and runbooks.

Interpretation notes:
- This connects repo knowledge architecture to recurring maintenance work.

### claim.ryan.pinned-supply-chain-cooldowns: Supply Chain Maintenance Needs Pins And Cooldowns

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent-assisted maintenance should pair pinned toolchains and dependencies with explicit dependency posture, cooldowns, and risk assessment.

Interpretation notes:
- This prevents cheap code generation from expanding unreviewed supply-chain surface.

### claim.ryan.code-free-maintenance-economics: Cheap Code Changes Maintenance Economics

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

When code is cheap to produce, principal engineers should optimize harder for maintenance burden and supply-chain risk.

Interpretation notes:
- This is a counterweight to adding code merely because generation is easy.

### claim.ryan.prompt-to-paved-workflow: Prompts Should Collapse To Paved Workflows

- Type: claim-card
- Status: reviewed
- Claim strength: direct
- Source boundaries: user_provided_excerpt_not_independently_verified

Agent prompts should route into known workflows that explain what matters, common task shapes, and where to learn more.

Interpretation notes:
- This maps directly to skill routing and workflow front doors.

## Principles

### principle.ryan.high-leverage-hardened-core: Concentrate Scrutiny In High-Leverage Cores

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.hardened-core-many-bindings

When many ecosystems need the same sensitive behavior, consider concentrating implementation and scrutiny into one hardened core with thin bindings.

Rationale: Duplicated implementations diffuse hardening effort and can leave equivalent concepts vulnerable across many stacks.

Application notes:
- Use this as an architecture question for security-sensitive or standards-heavy components.
- Validate whether the binding layer preserves semantics and safety.
- Do not over-centralize when local semantics or deployment constraints genuinely differ.

### principle.ryan.runbooks-are-automation-interface: Runbooks Are The Automation Interface

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.oss-maintenance-runbooks, claim.ryan.prompt-to-paved-workflow

Keep automation behavior in checked-in runbooks, and let thin automation prompts delegate to those durable instructions.

Rationale: Runbooks become both executable operating surfaces and agent-readable knowledge, while app-side automation stays small and stable.

Application notes:
- Link AGENTS.md to golden paths and runbooks.
- Document common commands in CONTRIBUTING.md for humans and agents.
- Keep automations short enough that repo state remains the source of truth.

### principle.ryan.code-free-still-needs-supply-chain-discipline: Cheap Code Still Needs Supply-Chain Discipline

- Type: principle
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.code-free-maintenance-economics, claim.ryan.pinned-supply-chain-cooldowns

As code generation cost falls, maintenance burden, dependency risk, and toolchain surface become more important architecture constraints.

Rationale: Cheap code can make it tempting to add layers, dependencies, and tools; principal engineering should instead reduce long-term operational surface.

Application notes:
- Prefer one toolchain when it satisfies the real constraints.
- Review top-level dependencies for need and risk profile.
- Pin and advance dependencies through runbooks, cooldowns, and risk assessment.

## Heuristics

### heuristic.ryan.apply-harness-practices-in-small: Apply Harness Practices In Small

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.harness-transfers-to-oss

Use small, real repositories as proving grounds for harness practices before scaling the pattern into larger systems.

Use when:
- A team needs to test a workflow, hook, validation loop, or context pattern.
- The practice can be evaluated in an OSS or side-project setting with real constraints.
- The goal is learning transferable mechanics, not producing a demo.

Avoid when:
- The small environment lacks the risk, scale, or workflow shape needed to test the idea.
- The experiment would create maintenance burden without an adoption path.

### heuristic.ryan.use-oss-crates-as-harness-labs: Use OSS Crates As Harness Labs

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: public_repository_page_inspection_not_full_clone, user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.rand-mt-repo-harness-surface, claim.ryan.intaglio-typed-boundary-validation, claim.ryan.harness-transfers-to-oss

Use small real OSS crates as candidate proving grounds for agent runbooks, pinned toolchains, typed boundaries, dependency policy, and validation loops before scaling them to larger repositories.

Use when:
- A harness pattern needs a realistic but bounded proving ground and the repository has been inspected beyond the public landing page.
- The repo has enough tests, docs, and toolchain policy to support agent maintenance.
- The goal is to discover transferable operating practice.

Avoid when:
- The crate lacks the risk or workflow shape needed to test the practice.
- The experiment would add maintenance burden without feeding a larger harness.
- The only available evidence is a page-visible repository surface and the decision requires proof that the practice worked.

### heuristic.ryan.prefer-simpler-config-grammars: Prefer Simpler Config Grammars

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.toml-reduces-footguns

For agent-maintained config, prefer formats whose grammar and parser behavior reduce ambiguity for both humans and agents.

Use when:
- Migrating repeated configuration surfaces.
- Parser behavior or implicit typing has caused mistakes.
- The target format is supported by the surrounding toolchain.

Avoid when:
- Existing ecosystem contracts require the current format.
- Migration churn outweighs the reduction in parser risk.

### heuristic.ryan.minimize-toolchain-surface: Minimize Toolchain Surface

- Type: heuristic
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.code-free-maintenance-economics, claim.ryan.pinned-supply-chain-cooldowns

When agents make code cheap, deliberately reduce toolchains, dependencies, and maintenance surfaces rather than adding convenience layers by default.

Use when:
- A project can satisfy its needs with one primary language or toolchain.
- A dependency exists mainly to avoid writing small, reviewable code.
- Supply-chain risk matters more than short-term convenience.

Avoid when:
- Removing the tool would recreate a complex, security-sensitive subsystem poorly.
- A standard dependency is more reviewed, safer, and cheaper to maintain than local code.

## Checklists

### checklist.ryan.agent-maintained-repo: Agent-Maintained Repository

- Type: checklist
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.oss-maintenance-runbooks, claim.ryan.pinned-supply-chain-cooldowns, claim.ryan.code-free-maintenance-economics

- [ ] AGENTS.md names the repo, operating loop, and golden-path workflows.
- [ ] CONTRIBUTING.md documents onboarding and common commands for humans and agents.
- [ ] Automations delegate to checked-in runbooks instead of embedding long prompts.
- [ ] Guardrails are organized by theme and linked from the workflow front door.
- [ ] Toolchains and dependencies are pinned with documented dependency posture.
- [ ] Dependency updates follow cooldowns, risk assessment, and validation proof.
- [ ] The project minimizes toolchain and dependency surface where the maintenance trade-off is favorable.

## Eval Scenarios

### eval.ryan.maintenance-economics-boundary: Cheap Code Still Needs Maintenance Boundaries

- Type: eval-scenario
- Status: reviewed
- Claim strength: synthesized
- Source boundaries: user_provided_excerpt_not_independently_verified
- Derived from claims: claim.ryan.code-free-maintenance-economics, claim.ryan.pinned-supply-chain-cooldowns

Given: An agent proposes adding a dependency or tool because code generation makes implementation cheap.
Should: The agent evaluates maintenance burden, supply-chain risk, toolchain surface area, pinning, cooldown policy, and whether the dependency should be removed, internalized, or avoided.
Expected failure: The agent treats low implementation cost as sufficient reason to expand the dependency or tool surface.
Reproduce with: references/evals/eval.ryan.maintenance-economics-boundary.md
