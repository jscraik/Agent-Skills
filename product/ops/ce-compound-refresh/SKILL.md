---
name: ce-compound-refresh
description: Review and refresh stale `docs/solutions/` learnings and pattern docs against the current codebase, including overlap consolidation when multiple docs now cover the same ground after refactors, migrations, or dependency upgrades.
metadata:
  skill-type: team_automation
---

# CE Compound Refresh

## Table of Contents
- [Working agreement](#working-agreement)
- [When to use](#when-to-use)
- [Required inputs](#required-inputs)
- [Deliverables](#deliverables)
- [Failure mode](#failure-mode)
- [Constraints](#constraints)
- [Acceptance criteria](#acceptance-criteria)
- [Standards snapshot (March 2026)](#standards-snapshot-march-2026)
- [Philosophy](#philosophy)
- [Workflow](#workflow)
- [Modes](#modes)
- [Maintenance model](#maintenance-model)
- [Execution rules](#execution-rules)
- [Validation](#validation)
- [Anti-patterns](#anti-patterns)
- [Encouraging variation](#encouraging-variation)
- [Examples](#examples)
- [References](#references)
- [See Also](#see-also)
- [Decision feedback protocol](#decision-feedback-protocol)
- [Gotchas](#gotchas)

## Working agreement
- Treat `ce-compound-refresh` as the maintenance stage for `docs/solutions/`, not as a generic doc-polish or code-review lane.
- Keep the refresh order explicit: inspect individual learnings first, then inspect derived pattern docs that depend on them.
- Evaluate document-set shape as well as single-doc accuracy. If multiple docs now cover the same problem with compatible guidance, consolidate the set instead of preserving silent drift risk.
- Match documentation to current repo truth. If the code changed, refresh the doc; do not debate whether the code change was intentional inside this workflow.
- Prefer no-write `Keep` outcomes over churn. Only edit when the result materially improves trustworthiness.
- Use external docs only when a stale claim depends on current framework or library behavior; otherwise stay repo-first.

## When to use
Use this skill when the user wants stale or drifting `docs/solutions/` learnings and pattern docs reviewed against the current codebase and refreshed with the smallest trustworthy maintenance action.

Primary triggers:
- "run `ce:compound-refresh` on auth"
- "review `docs/solutions/` for stale learnings"
- "this pattern doc no longer matches the code"
- "after the refactor, update or archive the old solution docs"
- "a retrieved learning looks outdated or wrong"
- "refresh the payments learnings in autonomous mode"
- "dependency upgrade probably made these docs stale"
- "these two learnings now overlap; consolidate the right one"
- "multiple docs cover the same workaround now; clean up the document set"

Non-triggers:
- the user wants to capture a newly solved issue for the first time; use `ce-compound`
- the user wants implementation or bug fixing; use `ce-work`
- the user wants broad readiness critique of a PR or artifact; use `ce-review` or `ce-technical-review`
- the user only wants wording cleanup, typo fixes, or editorial polish with no accuracy drift

## Required inputs
- a scope hint, file path, module, category, pattern topic, or explicit request to sweep all of `docs/solutions/`
- optional `mode:autonomous` argument when the run should avoid all user questions
- optional upstream alias `mode:autofix`, which should be normalized to `mode:autonomous`
- access to the current codebase and the in-scope `docs/solutions/` artifacts
- optional current artifact or conversation context if a recently solved issue is driving the refresh

If the user gives no scope hint:
- interactive mode may narrow scope after inventory
- autonomous mode processes the full discovered scope

## Deliverables
- a chosen mode: `interactive | autonomous`
- a scope route: `focused | batch | broad`
- one classification per processed artifact or overlap cluster: `Keep | Update | Consolidate | Replace | Archive | Stale`
- applied in-place refreshes, consolidation merges, successor creation, stale marking, or archival changes when evidence supports them
- a full markdown report covering:
  - scanned artifact counts
  - per-file or per-cluster evidence
  - actions applied
  - recommendations when writes could not be completed
- optional commit or PR follow-up when files changed
- `schema_version: 1` in structured summaries when the user requests a structured output

## Failure mode
If no candidate docs exist under `docs/solutions/`, stop and say:

`No candidate docs found in docs/solutions/. Run ce:compound after solving problems to start building your knowledge base.`

If a scope hint finds no matches, report the miss clearly. In interactive mode, ask for one narrower clarification. In autonomous mode, stop without guessing.

If evidence is insufficient to write a trustworthy replacement, do not invent a new learning. Mark the artifact stale when possible, explain what evidence is missing, and recommend `ce-compound` after the next real encounter with that problem area.

## Constraints
- redact secrets, tokens, credentials, and sensitive data by default in reports, examples, stale reasons, and any copied evidence
- do not turn this into generic code review or implementation work
- do not update docs just to leave a breadcrumb that they were reviewed
- do not ask whether current code is "correct" or "intentional"; this skill maintains doc accuracy against current reality
- do not archive a learning merely because it is old
- do not keep a learning merely because its advice is generally sound when the concrete implementation it documents is gone
- do not broaden a narrow refresh into a repo-wide sweep without evidence
- do not use external docs when repo evidence is sufficient
- do not let auto-memory notes outrank conversation or codebase evidence

## Acceptance criteria
- the skill chooses `interactive` or `autonomous` before asking questions or applying actions
- in-scope learnings are investigated before dependent pattern docs
- overlap analysis happens before duplicate docs are left in place
- each artifact or overlap cluster receives exactly one maintenance outcome backed by explicit evidence
- `Keep` does not create churn by default
- `Update` is used only for meaningful evidence-backed drift
- `Consolidate` is used only when overlapping docs are both materially correct and one canonical doc is clear
- `Replace` is used only when the old guidance is misleading and successor evidence is sufficient
- ambiguous autonomous cases are marked stale rather than guessed
- the final report is full markdown, not a one-line summary
- if any required check fails, stop at the first failed gate and do not proceed until it is fixed or triaged

## Standards snapshot (March 2026)
- Keep the skill scoped to one reusable maintenance job, with routing language that says what it does and when to use it.
- Prefer repo truth, explicit evidence, and selective external verification over speculative rewriting.
- Keep `SKILL.md` lean and move detailed decision trees, report formats, and git follow-up logic into `references/`.
- Use realistic positive and negative examples plus eval-backed trigger coverage instead of relying on hidden prompt assumptions.
- When current framework or library behavior matters, verify with primary docs first; for OpenAI product behavior use official OpenAI docs first, and use Context7 only when current library semantics materially affect the maintenance decision.

## Philosophy
- `ce-compound-refresh` protects the trustworthiness of accumulated team knowledge.
- The right default is conservative accuracy, not maximum rewriting.
- A stale learning is better marked stale than silently left misleading.
- Pattern docs deserve extra skepticism because they influence future work more broadly than incident-level learnings.
- Refresh work should feel like precise gardening, not a repo-wide cleanup frenzy.

Guiding questions:
- What is the smallest useful scope that will materially improve trust right now?
- Is this artifact still describing how the system actually works, or only how it used to work?
- Would a future engineer be safer with a factual in-place update, a real successor, or an explicit stale warning?
- Does this report make the next maintenance decision easier, or am I creating churn without increasing trust?

## Workflow
### Phase 0: Detect mode and scope
Choose `interactive` by default. If the argument contains `mode:autonomous`, strip that token, use the remaining text as the scope hint, and run without user questions.

Treat the upstream `mode:autofix` token as a compatibility alias. Normalize it to the same autonomous behavior rather than rejecting the request.

Start with the smallest useful scope that matches the evidence. Only widen after discovery shows broader drift.

Discover candidate artifacts under `docs/solutions/`, excluding:
- `README.md`
- anything under `docs/solutions/_archived/`

Use the narrowest successful scope match in this order:
1. directory match
2. frontmatter match on `module`, `component`, or `tags`
3. filename match
4. content search

### Phase 1: Route by scope size
Choose the lightest route that fits:
- `focused` for 1-2 likely files or a specific named doc
- `batch` for up to about 8 mostly independent docs
- `broad` for 9+ docs, ambiguous sweeps, or repo-wide stale-doc review

For broad scope, run triage first. Use the inventory, impact clustering, missing-reference spot checks, and starting-area recommendation rules in `references/refresh-workflow.md`.

### Phase 2: Investigate learnings first
Review each learning against the current codebase and supporting artifacts before touching dependent patterns.

Check:
- references still exist
- the recommended solution still matches current code behavior
- code examples remain representative
- related learnings and patterns remain consistent
- auto-memory notes supply supplementary drift signals
- overlap signals note when another doc in scope covers the same problem, files, root cause, or prevention advice

Use the Update vs Replace boundary, memory-signal rules, and successor checks in `references/refresh-workflow.md`.

### Phase 3: Analyze the document set
After individual learnings are investigated, step back and compare overlapping docs before treating the set as final.

Check:
- whether one doc is now the canonical source and another is mostly a narrower precursor
- whether multiple docs share the same problem, solution shape, files, or prevention rules
- whether keeping them separate still improves retrieval value enough to justify drift risk
- whether outright contradictions between docs need immediate consolidation, replacement, or archival follow-up

Use the document-set analysis and consolidation rules in `references/refresh-workflow.md`.

### Phase 4: Investigate pattern docs
After the underlying learnings are classified, inspect any affected pattern docs under `docs/solutions/patterns/`.

Treat patterns as derived guidance:
- stronger stale risk
- same five primary outcomes
- no new generalized rules without evidence from refreshed learnings

### Phase 5: Classify the maintenance action
Pick one action per artifact or overlap cluster:
- `Keep`
- `Update`
- `Consolidate`
- `Replace`
- `Archive`
- `Stale` when autonomous ambiguity or insufficient replacement evidence prevents a trustworthy write

Use the execution rules, archive-vs-replace boundary, and pattern-specific guidance in `references/refresh-workflow.md`.

### Phase 6: Execute and report
Apply unambiguous actions directly.

Interactive mode:
- ask only on genuine ambiguity or non-obvious archive/replace calls

Autonomous mode:
- skip all questions
- apply safe actions directly
- mark ambiguous cases stale
- continue after write failures and move them into the report's `Recommended` section

Always finish with the full markdown report and optional git follow-up rules from `references/refresh-workflow.md`.

## Modes
Use `interactive` when:
- the user is present and ambiguous maintenance choices may need confirmation
- the refresh is narrow and the user likely wants to steer edge cases

Use `autonomous` when:
- the arguments include `mode:autonomous` or the upstream alias `mode:autofix`
- the user wants a no-interruption maintenance sweep
- the best safe behavior is to apply unambiguous actions and stale-mark borderline cases

## Maintenance model
- `Keep`: still accurate and still useful; no edit by default
- `Update`: core guidance still correct, but references or examples drifted
- `Consolidate`: multiple docs are still materially correct, but one canonical doc should absorb the others
- `Replace`: old guidance is misleading and strong successor evidence exists
- `Archive`: implementation and problem domain are gone, or the doc is plainly obsolete or redundant
- `Stale`: evidence is not strong enough for update, replace, or archive, but leaving the doc as trustworthy would be misleading

## Execution rules
- Prefer the main thread for small scopes, short docs, or any run where delegation was not explicitly requested or approved.
- If 1-2 heavy artifacts would benefit from delegation and the user has not already explicitly asked for sub-agents, ask a short blocking approval question via `request_user_input` before spawning sequential subagents.
- Use sequential subagents for 1-2 heavy artifacts only after explicit user request or approval.
- Use parallel investigation subagents only for independent artifacts with low overlap and only after explicit user request or approval.
- Use replacement subagents one at a time, sequentially, and only after explicit user request or approval.
- When spawning subagents, preserve the dedicated file-search/read-first instruction and separate memory-sourced evidence from codebase-sourced evidence.
- When replacing a learning, write the successor in `ce-compound` learning-capture format and archive the superseded source after the successor exists.

## Validation
- fail fast: stop at the first failed gate, fix or report it, rerun that gate, then continue
- verify the chosen scope actually matches discovered `docs/solutions/` artifacts
- verify learnings were reviewed before dependent patterns
- verify overlap analysis happened before duplicate docs were left in place
- verify each action is backed by concrete evidence rather than age or guesswork
- verify `Update` was not used for a materially changed solution
- verify `Consolidate` preserved any unique content from a subsumed doc before archival follow-up
- verify `Archive` was not used when the problem domain still exists and should be replaced instead
- verify autonomous ambiguous cases were stale-marked, not guessed through
- verify the final report includes every processed file and any write failures

## Anti-patterns
- treating `ce-compound-refresh` as generic doc cleanup
- reviewing pattern docs before the learnings that support them
- using age alone as the stale signal
- updating solution prose when the actual solution changed materially
- leaving overlapping docs in place without checking whether they should be consolidated
- archiving a learning because the file paths moved without checking whether the problem domain still exists
- replacing a learning without enough evidence to document the current solution honestly
- asking the user whether code drift was intentional instead of matching docs to reality
- turning autonomous mode into silent guesswork
- NEVER rewrite docs to sound current without checking the codebase they describe
- DO NOT archive a still-relevant problem domain just because the original implementation vanished
- DO NOT use `Update` as a disguised rewrite when the solution itself changed
- AVOID broad stale-doc sweeps that skip triage, evidence gathering, or per-file reporting

## Encouraging variation
IMPORTANT: Outputs should vary based on scope, evidence quality, and mode.
- Focused runs should feel decisive and compact.
- Batch runs should group obvious keeps and updates, then isolate higher-risk replace or archive decisions.
- Broad sweeps should feel incremental and triaged rather than dumping a giant queue.
- Reports should differ meaningfully when the evidence points to mostly Keeps, mostly Updates, or heavy stale marking.

## Examples
When the user asks things like:
- "Run `ce:compound-refresh auth` after the auth refactor and update anything stale."
- "Use `ce:compound-refresh mode:autonomous payments` and just apply safe maintenance without questions."
- "Use `ce:compound-refresh mode:autofix auth` and normalize that older flag to the current autonomous flow."
- "These retry learnings overlap now. Consolidate the canonical doc and archive the redundant one if it adds no unique value."
- "This solution doc was retrieved during debugging, but it no longer matches the code. Refresh it."
- "Review the `docs/solutions/patterns/` docs for CI because the old learnings may have drifted."
- "We renamed the session-token stack months ago. Find the related learnings and either update, replace, or archive them."

## References
- Contract: `references/contract.yaml`
- Evals: `references/evals.yaml`
- Prompt parity map: `references/source-parity.md`
- Detailed refresh workflow: `references/refresh-workflow.md`

## See Also

| Skill | When to use together |
|---|---|
| [[ce-compound]] | Capture newly solved issues before or after targeted refresh maintenance |
| [[ce-review]] | Validate current implementation readiness when drift in docs may reflect broader product risk |
| [[ce-technical-review]] | Audit focused technical correctness when the stale-doc signal points to code-level risk, not just doc maintenance |

**Topic map:** [[product-ops]]

## Decision feedback protocol
<!-- decision-feedback-protocol:v2 -->
- If post-run feedback capture is enabled for this runtime, emit a non-blocking `post_run_feedback` event via `request_user_input` after result delivery.
- Capture `decision`, `outcome`, and `confidence`.
- Persist feedback with `python3 utilities/skill-builder/scripts/record_skill_feedback.py --skill-path <path/to/SKILL.md> --decision <...> --outcome <...> --confidence <...> --notes "..."`.
<!-- /decision-feedback-protocol -->

## Gotchas
- None yet. Capture recurring failures here as symptom -> cause -> do instead -> check.
