# Source Parity

## Source prompts

This package preserves and restructures the following source prompt families:

1. `Infrastructure/config/codex/prompts/workflow-compound.md`
2. legacy solved-problem capture prompt family
3. structured schema-driven capture workflow preserved for Harness Engineering repositories that want stronger `docs/solutions/` contracts

## Preserved from `workflow-compound.md`

- `he-compound` remains the Harness Engineering orchestration layer
- canonical stage sequence:
  - brainstorm
  - spec
  - deepen-spec
  - technical review on spec
  - plan
  - deepen-plan
  - technical review on plan
  - work
  - review
  - compound
- explicit execution modes:
  - full lifecycle
  - resume from stage
  - incident or learning capture
- cross-stage quality gates
- planning-ledger integration
- UI branching protocol for UI-impacting work
- current stage plus next-command output contract

## Preserved from the legacy solved-problem capture prompt family

- direct solved-problem capture into `docs/solutions/`
- default `full` mode and opt-in `compact-safe` mode
- auto-memory scan and supplementary-evidence handling
- full-mode helper fan-out:
  - Context Analyzer
  - Solution Extractor
  - Related Docs Finder
  - Prevention Strategist
  - Category Classifier
- strict one-file-write rule in full mode
- selective `he-compound-refresh` follow-up logic
- discoverability-check maintenance intent after capture
- optional specialized reviewer pass
- solution categories
- overlap-aware related-doc analysis that can update an existing solution doc instead of creating a duplicate
- compact-safe caveat that accepts overlap risk when Related Docs Finder is intentionally skipped
- success-output shape and compounding philosophy

## Modernization choices

### Explicit mode split

The old materials described two legitimate jobs:
- workflow orchestration
- post-fix knowledge capture

Instead of flattening one into the other, this package keeps both as explicit `he-compound` modes:
- `full-lifecycle`
- `resume-from-stage`
- `learning-capture`

This preserves both source prompts without making the default behavior noisy or ambiguous.

### Stronger boundary with neighboring Harness Engineering skills

The package now explicitly defers actual stage work to:
- `he-brainstorm`
- `he-spec`
- `he-deepen-spec`
- `he-technical-review`
- `he-plan`
- `he-deepen-plan`
- `he-work`
- `he-code-review`

That makes `he-compound` the workflow spine rather than a duplicate megaskill.

### Bounded modern behavior

Modern improvements added without losing source strength:
- repo-truth-first and artifact-first stage validation
- explicit fail-fast validation language
- eval-backed trigger coverage for both orchestration and learning capture
- narrow refresh guidance instead of automatic broad stale-doc sweeps
- explicit high-overlap behavior that refreshes the existing durable doc and adds `last_updated`
- preservation of legacy breadth as an explicit mode rather than the universal default
- reference-first consolidation: standards/philosophy/variation and full anti-pattern catalog moved into dedicated references with explicit SKILL signposts

### Structured schema-driven capture preserved as a variant

The archived structured-capture materials contribute a stronger variant for repos that want:
- validated YAML frontmatter
- explicit enum-based categorization
- reusable troubleshooting and critical-pattern templates
- a post-documentation decision menu

Rather than splitting this into a duplicate sibling skill, the package preserves that doctrine as signposted references under `he-compound` so the repo keeps one canonical solved-problem capture lane.

## No-loss notes

- If the user starts from a feature idea, `he-compound` still acts as the lifecycle orchestrator.
- If the user starts from an already fixed issue, `he-compound` still acts as the durable learning-capture stage.
- If the user is mid-flight with existing artifacts, `he-compound` still supports resume behavior rather than restarting blindly.
- If the same solved problem appears again, `he-compound` preserves the refresh-instead-of-duplicate behavior when overlap is high.
