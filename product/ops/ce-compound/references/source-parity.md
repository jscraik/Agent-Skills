# Source Parity

## Source prompts

This package preserves and restructures three source prompt families:

1. `config/codex/prompts/workflow-compound.md`
2. legacy `ce:compound` solved-problem capture prompt
3. upstream `compound-docs` schema-driven capture workflow

## Preserved from `workflow-compound.md`

- `ce-compound` remains the compound-engineering orchestration layer
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

## Preserved from the legacy `ce:compound` prompt

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
- selective `ce:compound-refresh` follow-up logic
- optional specialized reviewer pass
- solution categories
- success-output shape and compounding philosophy

## Modernization choices

### Explicit mode split

The old materials described two legitimate jobs:
- workflow orchestration
- post-fix knowledge capture

Instead of flattening one into the other, this package keeps both as explicit `ce-compound` modes:
- `full-lifecycle`
- `resume-from-stage`
- `learning-capture`

This preserves both source prompts without making the default behavior noisy or ambiguous.

### Stronger boundary with neighboring CE skills

The package now explicitly defers actual stage work to:
- `ce-brainstorm`
- `ce-spec`
- `ce-deepen-spec`
- `ce-technical-review`
- `ce-plan`
- `ce-deepen-plan`
- `ce-work`
- `ce-review`

That makes `ce-compound` the workflow spine rather than a duplicate megaskill.

### Bounded modern behavior

Modern improvements added without losing source strength:
- repo-truth-first and artifact-first stage validation
- explicit fail-fast validation language
- eval-backed trigger coverage for both orchestration and learning capture
- narrow refresh guidance instead of automatic broad stale-doc sweeps
- preservation of legacy breadth as an explicit mode rather than the universal default

### Upstream schema-driven capture preserved as a variant

The imported `compound-docs` package contributes a stronger structured-capture variant for repos that want:
- validated YAML frontmatter
- explicit enum-based categorization
- reusable troubleshooting and critical-pattern templates
- a post-documentation decision menu

Rather than splitting this into a duplicate sibling skill, the package preserves that doctrine as signposted references under `ce-compound` so the repo keeps one canonical solved-problem capture lane.

## No-loss notes

- If the user starts from a feature idea, `ce-compound` still acts as the lifecycle orchestrator.
- If the user starts from an already fixed issue, `ce-compound` still acts as the durable learning-capture stage.
- If the user is mid-flight with existing artifacts, `ce-compound` still supports resume behavior rather than restarting blindly.
