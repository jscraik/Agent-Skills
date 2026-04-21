# Refresh Workflow

Read when: the request has routed to `he-compound-refresh`.

## Mode detection

Check whether the arguments contain `mode:autonomous` or the upstream alias `mode:autofix`.

- If yes, strip that token, normalize the run to `autonomous`, and use the remaining text as the scope hint.
- If no, run in `interactive` mode.

### Autonomous mode rules

- Skip all user questions.
- Process the entire matched scope. If no scope hint exists, process everything discovered under `docs/solutions/`.
- Apply all unambiguous `Keep`, `Update`, `Consolidate`, auto-`Archive`, and `Replace` actions when evidence is sufficient.
- If a write succeeds, report it as `Applied`.
- If a write fails, continue and report the same action as `Recommended`.
- If classification is genuinely ambiguous or replacement evidence is insufficient, mark the artifact stale in place with:
  - `status: stale`
  - `stale_reason`
  - `stale_date: YYYY-MM-DD`
- If the stale-mark write fails, report stale-marking as a recommendation.
- Use conservative confidence. Borderline interactive cases become stale in autonomous mode.
- Always generate the full report.

## Interaction principles

These apply only in `interactive` mode.

- Ask one question at a time.
- Prefer multiple choice.
- Start with scope and intent, then narrow only when needed.
- Do not ask the user to classify artifacts before you have evidence.
- Lead with a recommendation and one concise rationale.

## Refresh order

Refresh in this order:
1. individual learning docs
2. derived pattern docs

If the user starts with a pattern doc, inspect it first only to understand the concern, then inspect the supporting learnings before changing the pattern.

Why this order:
- learnings are the primary evidence
- patterns are derived from learnings
- stale learnings can falsely prop up a stale pattern

## Maintenance model

| Outcome | Meaning | Default action |
|---|---|---|
| `Keep` | Still accurate and still useful | No file edit by default |
| `Update` | Core solution is still correct, but references drifted | Apply evidence-backed in-place edits |
| `Consolidate` | Two or more docs overlap heavily but still contain compatible truth | Merge the unique value into one canonical doc, then archive or retire the redundant doc |
| `Replace` | Old artifact is now misleading, but a known better successor exists | Write a trustworthy successor, then archive or supersede the old artifact |
| `Archive` | No longer useful or applicable | Move to `docs/solutions/_archived/` with archive metadata |
| `Stale` | Not trustworthy enough to keep, but not trustworthy enough to replace or archive decisively | Mark in place with stale metadata |

## Core judgment rules

1. Evidence informs judgment. Use engineering judgment; do not treat this as a blind scorecard.
2. Prefer no-write `Keep`.
3. Match docs to current reality, not the reverse.
4. Be decisive when evidence is clear. In interactive mode, ask only on real ambiguity. In autonomous mode, stale-mark borderline cases.
5. Avoid low-value churn. Typos or wording polish alone are not refresh reasons.
6. Use `Update` only for meaningful, evidence-backed drift.
7. Use `Replace` only when a real successor can be documented honestly.
8. Missing referenced implementation with no successor is strong archive evidence, but only after checking whether the problem domain itself still exists.
9. Evaluate document-set design, not just single-file accuracy. If several docs now say the same thing, decide whether they still deserve separate retrieval value.
10. Use archival rather than direct deletion in this local package. The upstream donor deletes redundant docs; this package preserves the same maintenance intent while keeping an explicit archive trail in `docs/solutions/_archived/`.

## Scope selection

Search `docs/solutions/` for `.md` files, excluding:
- `README.md`
- `docs/solutions/_archived/`

If `docs/solutions/_archived/` exists, record it in the report as a legacy directory to review for restore-or-delete cleanup.

When a scope hint exists, try these strategies in order and stop at the first that yields matches:
1. directory match
2. frontmatter match on `module`, `component`, or `tags`
3. filename match
4. content search

If no matches are found:
- interactive mode: report the miss and ask for one clarification
- autonomous mode: report the miss and stop

If there are no candidate docs at all, report:

```text
No candidate docs found in docs/solutions/.
Run `he-compound` after solving problems to start building your knowledge base.
```

Regardless of run mode, keep report sections explicit:
- `Applied`: actions successfully written
- `Recommended`: actions that were not written, with rationale

## Route by scope

| Scope | When | Interaction style |
|---|---|---|
| `focused` | 1-2 likely files or a named doc | Investigate directly, then present a recommendation |
| `batch` | Up to about 8 mostly independent docs | Investigate first, then present grouped recommendations |
| `broad` | 9+ docs, ambiguous, or repo-wide sweep | Triage first, then investigate in batches |

### Broad-scope triage

For broad sweeps:
1. inventory frontmatter across all candidate docs
2. cluster by module, component, or category
3. prioritize the densest clusters with the strongest missing-reference signals
4. in interactive mode, recommend the highest-impact starting area
5. in autonomous mode, process clusters in impact order without asking

Example recommendation:

```text
Found 24 learnings across 5 areas.

The auth module has 5 learnings and 2 pattern docs that cross-reference
each other, and 3 of them point to files that no longer exist.
I'd start there.
```

## Phase 1: Investigate candidate learnings

For each learning, verify:
- references still exist
- recommended solution still matches current code behavior
- code examples still reflect the implementation
- related docs are still present and consistent
- auto-memory notes in the same problem domain provide supplementary drift signals

### Auto memory

Read `MEMORY.md` from the runtime's auto-memory directory when available.

Rules:
- if missing, empty, or unreadable, skip it
- use semantic judgment, not keyword matching
- treat memory as supplementary only
- tag any memory-sourced evidence with `(auto memory)`
- if memory contradicts codebase evidence, treat it as cautionary context rather than truth

### Update vs Replace

The crucial distinction is whether drift is cosmetic or substantive.

`Update` territory:
- file paths moved
- classes or modules renamed
- links broke
- metadata drifted
- code snippets need factual refresh while the recommended solution stays the same

`Replace` territory:
- recommended solution conflicts with current code
- architectural approach changed
- troubleshooting path is materially different
- the old doc is now actively misleading

Boundary rule:
- if you are rewriting what the learning recommends, that is `Replace`, not `Update`

### Consolidate

Choose `Consolidate` when document-set analysis shows that multiple docs are still materially correct but one canonical doc should absorb the others.

Use it when:
- two docs describe the same problem and compatible solution
- one doc is a narrow precursor and a newer doc covers the same ground more comprehensively
- the secondary doc contains edge cases, prevention rules, or context that should survive inside the canonical doc

Do not use it when:
- the docs cover genuinely different sub-problems
- the merge would create an unwieldy artifact that hurts retrieval more than it helps

`Consolidate` vs `Archive`:
- if the redundant doc has unique value worth preserving, consolidate first
- if it adds no unique value, archive it directly once the canonical doc is clearly identified

### Memory-sourced drift signals

Memory-only drift is never enough by itself for `Replace` or `Archive`.

Use it to:
- corroborate codebase drift
- trigger deeper investigation
- add nuance to the evidence report

In autonomous mode, memory-only drift with no codebase corroboration should result in `Stale`, not an aggressive rewrite.

### Judgment guidelines

- contradiction with current code is a strong `Replace` signal
- age alone is not staleness
- before `Replace` or `Archive`, look for successors in newer learnings, patterns, PRs, or issues

## Phase 1.25: Document-set analysis

After investigating individual docs, step back and evaluate the document set as a whole.

### Overlap detection

For docs that share the same module, component, tags, or problem domain, compare:
- problem statement
- solution shape
- referenced files
- prevention rules
- root cause

High overlap across three or more dimensions is a strong `Consolidate` signal.

Record for each overlap:
- the file paths involved
- which dimensions overlap
- which doc appears broader, newer, or more accurate
- whether the secondary doc contains unique content worth preserving

### Canonical doc identification

Within each overlap cluster, identify the canonical source of truth:
- usually the broadest, clearest, and most current doc
- the doc a maintainer should find first
- the doc other related docs should point to rather than duplicate

All other docs in the cluster are either:
- `Distinct`: still worth separate retrieval
- `Subsumed`: should be consolidated into the canonical doc
- `Redundant`: adds no unique value and can be archived after consolidation analysis

### Retrieval-value test

Before leaving two similar docs separate, ask:

`Would a maintainer searching for this topic later benefit from these being separate, or am I only preserving drift risk?`

Keep docs separate only when:
- they cover genuinely different sub-problems
- they serve meaningfully different audiences or contexts
- merging would make the canonical doc materially harder to use

### Cross-doc conflict check

Look for contradictions:
- one doc recommends an approach another rejects
- one doc references a path another marks deprecated
- two docs describe the same problem with materially different root causes

Contradictions are higher urgency than ordinary drift. Resolve them through `Consolidate`, `Replace`, or `Archive`; do not leave both docs untouched.

## Phase 1.5: Investigate pattern docs

After learning review, inspect any relevant pattern docs under `docs/solutions/patterns/`.

Pattern docs are high leverage, so stale guidance is especially dangerous.

Evaluate:
- whether refreshed learnings still support the generalized rule
- whether examples remain representative
- whether the pattern still deserves elevated guidance

A pattern doc with no clear supporting learnings is a stale signal.

## Subagent strategy

Choose the lightest approach that fits:

| Approach | When |
|---|---|
| main thread only | small scope, short docs, or any run where delegation was not explicitly requested or approved |
| sequential subagents | 1-2 artifacts with heavy supporting reads after explicit user request or approval |
| parallel subagents | 3+ independent artifacts with low overlap after explicit user request or approval |
| batched subagents | broad sweeps after triage narrows scope and the user has approved delegation |

If the user has not already explicitly asked for delegation or sub-agents, ask a short blocking approval question via `request_user_input` before spawning any subagent.

When spawning any approved subagent, include this instruction:

> Use dedicated file search and read tools for all investigation. Do not use shell commands for file operations unless those tools are unavailable in the current harness. Also read `MEMORY.md` from the auto-memory directory if it exists, and report memory-sourced drift signals separately from codebase-sourced evidence, tagged with `(auto memory)`.

Subagent roles:
- investigation subagents: read-only, return file path, evidence, recommended action, confidence, and open questions
- replacement subagents: write a single successor learning, one at a time, sequentially

The orchestrator:
- merges findings
- resolves contradictions
- owns archival and metadata edits
- asks interactive questions only when needed
- stale-marks ambiguous autonomous cases

## Phase 2: Classify the action

### Keep

- still accurate
- still useful
- no edit by default
- add `last_refreshed` only if another meaningful update is already happening

### Update

Valid examples:
- rename `app/models/auth_token.rb` references to `app/models/session_token.rb`
- update moved module or component names
- repair related-doc links
- refresh implementation notes after a directory move

Invalid `Update` examples:
- style-only prose edits
- typo-only churn
- rewording that does not improve trustworthiness
- materially changed solution guidance

### Replace

Use `Replace` when the old guidance is now misleading.

#### Sufficient evidence

Proceed when you understand:
- what the old learning recommended
- what the current code now does
- why the old guidance is misleading

Then:
1. spawn one replacement subagent
2. pass it the old learning, investigation summary, and target path
3. have it write the successor using `he-compound` learning-capture format
4. update the old learning with `superseded_by`
5. move the old learning to `docs/solutions/_archived/`

#### Insufficient evidence

Mark stale in place:
- `status: stale`
- `stale_reason`
- `stale_date: YYYY-MM-DD`

Then report:
- what evidence exists
- what is missing
- why `he-compound` should capture the area after the next real encounter

### Archive

Choose `Archive` when:
- the code or workflow no longer exists
- the learning is obsolete with no valuable successor
- the learning is redundant and adds no distinct value

Before archiving, reason about whether the problem domain still exists.

Examples:
- if `auth_token.rb` is gone but the app still manages session tokens, the problem domain persists -> prefer `Replace`
- if the whole feature is gone, the problem domain is gone -> `Archive`

Auto-archive only when both are true:
- the referenced implementation is gone
- the problem domain is no longer active or a clearly better successor exists

Archive action:
- move the file to `docs/solutions/_archived/`
- add `archived_date: YYYY-MM-DD`
- add `archive_reason`

## Pattern guidance

Patterns use the same outcomes, but evaluate them as derived guidance:
- `Keep`: refreshed learnings still support the rule
- `Update`: the rule holds, but examples, scope, links, or references drifted
- `Consolidate`: two patterns now teach the same lesson and should become one canonical pattern
- `Replace`: the generalized rule is misleading and refreshed learnings support a different synthesis
- `Archive`: the pattern is no longer valid, no longer recurring, or fully subsumed by a stronger pattern
- `Stale`: evidence is not strong enough for archive, replace, or update, but leaving the pattern as trustworthy would be misleading

If "archive" feels too strong but the pattern should no longer be elevated, reduce its prominence only if the docs structure explicitly supports that.

## Phase 3: Interactive decisions

Skip this entire phase in autonomous mode.

In interactive mode, ask only when:
- `Update` vs `Replace` vs `Consolidate` vs `Archive` is genuinely ambiguous
- archive evidence is not strong enough for auto-archive
- a consolidation cluster has no obvious canonical doc
- a successor doc is about to be created and user awareness is useful

Question style:
- one question at a time
- recommendation first
- short rationale
- only plausible options

Focused-scope example:

```text
This learning looks like an Update.

Why: the references moved, but the recommended solution still matches
the current code.

What would you like to do?

1. Apply the update
2. Skip for now
```

Batch-scope order:
1. grouped keeps and straightforward updates
2. consolidation clusters where the canonical doc is clear
3. replace cases one at a time or in very small groups
4. archive cases individually unless they meet auto-archive criteria

Broad-scope order:
1. triage a manageable batch
2. present recommendations
3. continue batch by batch

## Phase 4: Execute the chosen action

### Keep flow
- no edit by default
- report why the artifact remains trustworthy

### Update flow
- apply only meaningful in-place factual fixes
- do not use this flow for materially changed solutions

### Consolidate flow
- choose the canonical doc explicitly
- merge unique content from the subsumed doc into the canonical doc in a natural location
- update any affected cross-references
- archive the subsumed doc with metadata that points at the surviving canonical artifact

### Replace flow
- run replacements one at a time
- write the successor first
- then archive or supersede the old artifact

### Archive flow
- archive only when clearly obsolete, redundant, or problem-domain-gone

### Stale flow
- mark in place when ambiguity or insufficient evidence blocks a trustworthy rewrite

## Output format

Always print the full markdown report.

Summary header:

```text
Harness Engineering Compound Refresh Summary
========================
Scanned: N artifacts (N learnings, M patterns)

Kept: X
Updated: Y
Consolidated: C
Replaced: Z
Archived: W
Marked stale: S
```

Then for every processed file include:
- file path
- classification
- evidence found
- action taken or recommended
- for `Consolidate`, identify the canonical doc, the unique content preserved, and the archived or retired file

For `Keep`, include a reviewed-without-edits section so the result is visible without git churn.

### Autonomous-mode report sections

Split actions into:
- `Applied`
- `Recommended`

`Applied` covers writes that succeeded.

`Recommended` covers writes that failed, including enough detail for a human to apply them manually or rerun interactively.

If all writes succeed, `Recommended` may be empty.
If no writes succeed, the report becomes a maintenance plan.

## Phase 5: Commit changes

Skip if no files changed.

### Detect git context

Check:
1. current branch
2. whether unrelated dirty changes exist
3. recent commit style

Stage only the files modified by `he-compound-refresh`.

### Autonomous defaults

| Context | Default action |
|---|---|
| default branch | create a specific docs-refresh branch, commit, attempt PR |
| feature branch | commit as a separate commit on the current branch |
| git failure | include recommended git commands in the report |

### Interactive options

If on the default branch:
1. create a branch, commit, and open a PR
2. commit directly to the current branch
3. do not commit

If on a clean feature branch:
1. commit to the current branch as a separate commit
2. create a separate branch and commit
3. do not commit

If on a dirty feature branch with unrelated changes:
1. commit only the refresh files to the current branch
2. do not commit

### Commit message

Write a succinct message that summarizes what was refreshed and matches repo conventions, for example:
- `docs: refresh 3 auth learnings and archive 1 obsolete pattern`

## Relationship to he-compound

- `he-compound` captures newly solved, verified problems
- `he-compound-refresh` maintains older learnings as the codebase evolves

Use `Replace` only when the refresh process has enough real evidence to write a trustworthy successor. Otherwise stale-mark and recommend `he-compound` after the next real encounter with that area.
