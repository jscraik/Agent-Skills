# Source Parity Notes

## Table of Contents
- [Source input](#source-input)
- [Preserved behaviors](#preserved-behaviors)
- [Intentional modernizations](#intentional-modernizations)
- [Known constraints](#known-constraints)

## Source input
This package was synthesized from the supplied `ce:compound-refresh` prompt that defines the maintenance workflow for stale or drifting `docs/solutions/` learnings and pattern docs.

## Preserved behaviors
- `interactive` versus `mode:autonomous` execution
- argument stripping for `mode:autonomous`
- autonomous rules:
  - no user questions
  - process all matched docs
  - apply safe actions directly
  - continue after write failures
  - report `Applied` versus `Recommended`
  - stale-mark ambiguous cases conservatively
- learning-first, pattern-second refresh order
- the four primary outcomes:
  - `Keep`
  - `Update`
  - `Replace`
  - `Archive`
- explicit `Stale` handling when evidence is insufficient or ambiguity remains
- ordered scope narrowing:
  - directory
  - frontmatter
  - filename
  - content search
- focused, batch, and broad routing with broad-scope triage
- investigation dimensions:
  - references
  - recommended solution
  - code examples
  - related docs
  - auto memory
- update-versus-replace boundary
- problem-domain check before archive
- replacement via successor writing in `ce-compound` learning-capture format
- full markdown report for every processed file
- branch-aware commit follow-up after refresh actions

## Intentional modernizations
- kept the skill tightly scoped to stale-doc maintenance rather than letting it drift into generic code review or generic doc editing
- aligned the package to current OpenAI/Codex skill guidance:
  - one reusable job
  - routing-first description
  - references for detailed decision trees
  - realistic positive and negative examples
  - eval-backed trigger coverage
- made repo-truth-first behavior explicit, with OpenAI docs first for OpenAI-product claims and Context7 only when current framework or library semantics matter
- softened the subagent file-tool instruction just enough to remain portable across current harnesses while preserving the original dedicated-file-tools preference
- elevated `Stale` to a first-class reported outcome so autonomous conservatism is visible rather than implicit

## Known constraints
- the source prompt assumed platform-specific blocking question tools. This package preserves the one-question-at-a-time behavior, but actual question tooling remains harness-dependent.
- the source prompt described direct git and PR actions. This package preserves the decision logic and defaults, but actual git/PR execution still depends on repository permissions and available CLI tooling.
