# Pattern Fit And Liability

Reject pattern authority unless local forces, stable variation, ownership, compatibility, and liabilities are visible.

Pack id: pack.codebase-architecture
Facet id: pattern_fit_and_liability
Runtime dependency: none; this slice is generated from a KnowledgeOS pack export.
Lifecycle status: draft

## Claim Cards

### claim.arch.patterns-need-forces-and-liabilities: Patterns Need Forces And Liabilities

- Type: claim-card
- Status: draft
- Claim strength: direct
- Source boundaries: local_source_reference

Pattern names are useful only when local forces, stable variation, collaboration shape, consequences, and liabilities are visible in the codebase.

Interpretation notes:
- This claim supports rejecting pattern authority without local evidence.
- It should keep pattern vocabulary subordinate to repo-specific language.

## Anti-Patterns

### anti-pattern.arch.pattern-authority-without-fit: Pattern Authority Without Fit

- Type: anti-pattern
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.patterns-need-forces-and-liabilities

Problem: A review recommends a pattern because the name sounds professional, while local forces, stable variation, caller simplification, compatibility rules, and liabilities remain unproven.

Failure mode: The new abstraction adds files and vocabulary but hides no behavior, creates more caller knowledge, and makes future agents follow pattern ceremony instead of repo evidence.

Avoidance: Require local forces, at least one real variation or extension need, an owned public contract, a compatibility test, and an explicit liability before introducing a named pattern.

## Eval Scenarios

### eval.arch.pattern-name-launders-no-variation: Pattern Name Launders No Variation

- Type: eval-scenario
- Status: draft
- Claim strength: synthesized
- Source boundaries: local_source_reference
- Derived from claims: claim.arch.patterns-need-forces-and-liabilities

Knowledge claim: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Behavior under test: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Failure mode: The reviewer praises the pattern because it matches a book category while ignoring local forces and liabilities.
Expected agent move: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Skill lift target: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Proof route: references/evals.yaml
Fixture path: references/evals/eval.arch.pattern-name-launders-no-variation.md
Promotion status: candidate
Capsule refs: codebase-architecture
Weak eval flags: none

Given: A refactor proposal introduces a factory, strategy, broker, plugin, or layered pattern around one implementation with no stable variation, compatibility test, or caller simplification.
Should: The reviewer rejects the pattern as premature, names the missing forces, and recommends the smallest behavior-preserving move.
Expected failure: The reviewer praises the pattern because it matches a book category while ignoring local forces and liabilities.
Reproduce with: references/evals/eval.arch.pattern-name-launders-no-variation.md
