# Source Parity Notes

## Table of Contents
- [Source input](#source-input)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)
- [Known constraints](#known-constraints)

## Source input
This package is aligned against the upstream donor skill at:

- repository: `EveryInc/compound-engineering-plugin`
- commit: `4e0ed2cc8ddadf6d5504210e1210728e6f7cc9aa`
- path: `plugins/compound-engineering/skills/ce-compound-refresh/SKILL.md`

The local package still applies Codex/OpenAI progressive-disclosure packaging on top of that donor.

## Preserved behaviors
- `interactive` versus `mode:autonomous` execution
- argument stripping for `mode:autonomous`
- compatibility handling for the upstream `mode:autofix` token
- autonomous rules:
  - no user questions
  - process all matched docs
  - apply safe actions directly
  - continue after write failures
  - report `Applied` versus `Recommended`
  - stale-mark ambiguous cases conservatively
- learning-first, pattern-second refresh order
- maintenance outcomes:
  - `Keep`
  - `Update`
  - `Consolidate`
  - `Replace`
  - `Archive`
- explicit `Stale` handling when evidence is insufficient or ambiguity remains
- ordered scope narrowing:
  - directory
  - frontmatter
  - filename
  - content search
- focused, batch, and broad routing with broad-scope triage
- interactive question pacing that avoids front-loading large decision queues before evidence
- investigation dimensions:
  - references
  - recommended solution
  - code examples
  - related docs
  - auto memory
- document-set analysis:
  - overlap detection
  - canonical-doc selection
  - retrieval-value test
  - cross-doc conflict checks
- update-versus-replace boundary
- problem-domain check before archive
- replacement via successor writing in `ce-compound` learning-capture format
- full markdown report for every processed file
- branch-aware commit follow-up after refresh actions

## Intentional modernizations
- April 12, 2026 parity refresh imported two deterministic behaviors from upstream while preserving local archive semantics:
  - report contract now explicitly requires `Applied` and `Recommended` sections,
  - `_archived/` detection is now surfaced as a reportable legacy-cleanup signal.
- kept the skill tightly scoped to stale-doc maintenance rather than letting it drift into generic code review or generic doc editing
- aligned the package to current OpenAI/Codex skill guidance:
  - one reusable job
  - routing-first description
  - references for detailed decision trees
  - realistic positive and negative examples
  - eval-backed trigger coverage
- made repo-truth-first behavior explicit, with OpenAI docs first for OpenAI-product claims and Context7 only when current framework or library semantics matter
- adapted the upstream direct-delete policy into this package's existing archive-first workflow:
  - consolidate still identifies the canonical doc and redundant sibling
  - fully redundant or obsolete docs are archived with metadata rather than removed outright
  - this preserves local safety and traceability while keeping the donor's document-set analysis intact
- preserved upstream autonomous strictness while keeping local archive semantics:
  - autonomous runs do not ask questions
  - ambiguous cases are stale-marked conservatively
  - write failures move to report recommendations without blocking the run
- softened the subagent file-tool instruction just enough to remain portable across current harnesses while preserving the original dedicated-file-tools preference
- elevated `Stale` to a first-class reported outcome so autonomous conservatism is visible rather than implicit
- moved standards/philosophy/discoverability/empowerment detail into `references/style-and-operating-guidance.md` so `SKILL.md` stays routing-first while preserving high-value operating context

## Known constraints
- the source prompt assumed platform-specific blocking question tools. This package preserves the one-question-at-a-time behavior, but actual question tooling remains harness-dependent.
- the source prompt described direct git and PR actions. This package preserves the decision logic and defaults, but actual git/PR execution still depends on repository permissions and available CLI tooling.
- this package does not require a separate post-report discoverability review step; discoverability constraints are enforced through routing, references, and validation gates already defined in the package.
