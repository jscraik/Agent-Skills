# Learning Capture

Read when: the selected `he-compound` mode is `learning-capture`.

## Canonical purpose

Capture a recently solved problem while the context is fresh, creating structured documentation in `docs/solutions/` with YAML frontmatter for searchability and future reuse.

Knowledge compounds:
- first solve takes research
- documented solution makes the next occurrence much faster

## Modes

### Full mode

Default behavior.

Proceed directly in full mode unless the user explicitly asks for `compact-safe`.

Critical rule:
- Only one file gets written: the final documentation artifact.
- Phase 1 helpers return text data to the orchestrator.
- Helpers must not write drafts, temp markdowns, or intermediate solution files.
- Only the orchestrator writes `docs/solutions/[category]/[filename].md`.

### Compact-safe mode

Use only when:
- the user explicitly asks for compact mode
- the session is context-constrained enough that the full fan-out would be wasteful

Critical rule:
- no helper fan-out
- one sequential pass
- minimal but complete solution document
- only the orchestrator writes `docs/solutions/[category]/[filename].md`

## Phase 0.5: Auto memory scan

Before full-mode helper fan-out:
1. read `MEMORY.md` from the runtime's auto-memory directory when that path is available
2. if the directory or file does not exist, is empty, or is unreadable, skip this step
3. scan entries semantically for notes relevant to the problem being documented
4. if relevant entries exist, prepare this labeled supplement:

```markdown
## Supplementary notes from auto memory
Treat as additional context, not primary evidence. Conversation history
and codebase findings take priority over these notes.

[relevant entries here]
```

Rules:
- pass the supplement to the Context Analyzer and Solution Extractor in full mode
- if memory notes materially influence the final doc, label them with `(auto memory)`
- if memory notes contradict the verified fix or conversation, treat them as cautionary context rather than truth

## Full-mode phases

### Phase 1: Parallel research

Launch these helpers in parallel. They return text only.

1. Context Analyzer
   - extract conversation history
   - identify problem type, component, and track
   - incorporate any auto-memory excerpt as supplementary evidence
   - validate against the documentation schema when the repo uses the preserved schema-driven variant
   - map the problem into the correct `docs/solutions/` category
   - suggest a path-safe filename slug
   - return: YAML frontmatter skeleton, category path, suggested filename, and track notes

2. Solution Extractor
   - analyze investigation steps
   - identify root cause
   - extract the working solution with code examples when useful
   - use auto memory only as secondary evidence
   - adapt the output shape to the repo's active solution-doc contract
   - return: solution content block

3. Related Docs Finder
   - search `docs/solutions/` for related documentation
   - identify cross-references and related issues
   - flag docs that may now be stale, contradicted, or overly broad
   - assess overlap against the new learning across:
     - problem statement
     - root cause
     - solution approach
     - referenced files
     - prevention rules
   - score overlap as:
     - `High`: essentially the same problem solved again
     - `Moderate`: same area but different angle, root cause, or solution
     - `Low`: related but distinct
   - return: links, relationships, refresh candidates, and overlap assessment

4. Prevention Strategist
   - develop prevention strategies
   - create best-practice guidance
   - generate test ideas where applicable
   - return: prevention and testing content

5. Category Classifier
   - determine the best `docs/solutions/` category
   - validate the category
   - suggest the filename slug
   - return: final path and filename

6. Session Historian (optional, explicit opt-in only)
   - only run when the user explicitly asks for session-history enrichment
   - gather relevant prior-session context that materially helps the current solved-problem capture
   - return: concise supporting context with provenance markers

### Phase 2: Assembly and write

Wait for all Phase 1 helpers to complete.

The orchestrator then:
1. collects all text results
2. checks the overlap assessment before deciding what to write:
   - `High` -> update the existing doc with fresher context instead of creating a duplicate
   - `Moderate` -> create the new doc and flag the overlap for selective refresh or consolidation review
   - `Low` -> create the new doc normally
3. assembles the complete markdown file
4. validates YAML frontmatter
5. creates the directory when needed for new-doc writes
6. writes the single final file

When updating an existing doc due to high overlap:
- preserve the file path and frontmatter structure
- refresh the solution details, code examples, prevention tips, and stale references
- add `last_updated: YYYY-MM-DD`
- do not change the title unless the problem framing materially shifted

### Phase 2.5: Selective refresh check

`he-compound-refresh` is not a default follow-up. Use it selectively only after the new learning is written.

Good reasons to refresh:
- the new fix contradicts an older learning or pattern doc
- the new fix supersedes a documented solution
- a refactor, migration, rename, or dependency upgrade likely invalidated older references
- a pattern doc is now overly broad or outdated
- Related Docs Finder surfaced strong stale-doc candidates
- Related Docs Finder reported moderate overlap, suggesting that a targeted consolidation review may be useful

Do not refresh when:
- no related docs were found
- related docs still appear consistent
- overlap is superficial
- the evidence is too weak and would require a broad historical sweep

Scope rules:
- one obvious stale candidate -> recommend or invoke refresh with the specific file or narrowest useful hint
- multiple candidates in one area -> ask whether to run a targeted refresh for that module, category, or pattern set
- compact-safe sessions -> do not broaden into a large refresh sweep

Example arguments:
- `/ce:compound-refresh plugin-versioning-requirements`
- `/ce:compound-refresh payments`
- `/ce:compound-refresh performance-issues`
- `/ce:compound-refresh critical-patterns`

### Phase 2.75: Discoverability check (instruction docs)

After writing the final solution doc, verify whether root instruction docs make `docs/solutions/` discoverable to future agents.

1. Check root instruction files (`AGENTS.md`, `CLAUDE.md`) and identify whether one is a shim include pointing to the other.
2. Assess whether the substantive instruction doc clearly communicates:
   - a searchable solution knowledge store exists
   - category structure and frontmatter semantics are present
   - when the store should be consulted during implementation/debugging
3. If discoverability is unclear:
   - ask for explicit user consent before editing instruction docs
   - propose the smallest natural addition in existing instruction sections
4. In `compact-safe` mode or autonomous/non-interactive runs:
   - prefer recording a recommendation over editing instruction docs

### Phase 3: Optional enhancement

After the final learning is written, optionally run specialized reviewers based on problem type:
- `performance_issue` -> `performance-oracle`
- `security_issue` -> `security-sentinel`
- `database_issue` -> `data-integrity-guardian`
- `test_failure` -> `cora-test-reviewer`
- code-heavy issue -> `kieran-rails-reviewer` plus `code-simplicity-reviewer`

Use these to review the documentation and prevention guidance, not to spawn a second hidden implementation workflow.

## Compact-safe workflow

In one sequential pass:
1. extract problem, root cause, and solution from conversation and artifacts
2. optionally read `MEMORY.md` and use only relevant supplementary notes
3. classify category and filename
4. write a minimal but complete solution document with:
   - YAML frontmatter
   - problem description
   - root cause
   - solution with key snippets when useful
   - one prevention tip
5. skip specialized reviewer fan-out

Compact-safe success output should make it clear that:
- the documentation is complete
- it was created in compact-safe mode
- a richer rerun is possible later in a fresh session

Compact-safe caveat:
- overlap review is skipped because there is no Related Docs Finder helper
- a compact-safe run may create a doc that overlaps with an older one
- that is acceptable; recommend `he-compound-refresh` only when there is an obvious narrow refresh target

## What the artifact should capture

- exact symptom or observable behavior
- investigation steps that mattered
- root cause analysis
- working solution
- prevention strategies
- cross-references to related issues or docs

## Schema-driven variant

Use the imported upstream `compound-docs` variant when the target repository already expects structured YAML-frontmatter solution docs or wants stronger capture ceremony.

That variant adds:
- enum-validated YAML frontmatter before writing
- a disciplined filename pattern
- richer troubleshooting and critical-pattern templates
- an explicit post-capture decision menu after documentation lands

Preserved references:
- `Infrastructure/references/upstream-compound-docs-guide.md`
- `Infrastructure/references/compound-docs-yaml-schema.md`
- `Infrastructure/references/compound-docs-resolution-template.md`
- `Infrastructure/references/compound-docs-critical-pattern-template.md`

Rules:
- preserve the local `he-compound` one-file-write contract
- treat the upstream schema and templates as richer guidance, not disposable background
- if the target repo does not use schema-driven `docs/solutions/`, fall back to the canonical local categories and shape

## Project Brain Integration (Dual Write)

When the target repo has a `.harness/` directory, use dual-write to both `docs/solutions/` and Project Brain:

### Phase: Dual Write (after creating docs/solutions/ doc)

1. **Map to domain**: Determine `.harness/knowledge/{domain}/` from problem category
   - build-errors → build
   - test-failures → testing
   - runtime-errors → runtime
   - performance-issues → performance
   - security-issues → security
   - database-issues → data
   - etc.

2. **Write to knowledge**: Append to `.harness/knowledge/{domain}/knowledge.md`:

   ```yaml
   ---
   title: "{problem summary}"
   type: knowledge
   confirmed: YYYY-MM-DD
   source: docs/solutions/{category}/{filename}.md
   tags: [he-compound, {category}]
   ---
   
   ## Problem
   {symptom}
   
   ## Root Cause
   {root cause}
   
   ## Solution
   {solution}
   
   ## Prevention
   {prevention strategy}
   ```

3. **Sync to Local Memory MCP**:

   ```text
   observe(
     content="{problem summary} → {solution summary}",
     level="learning",
     tags=[
       "project-brain:{repo}",
       "type:knowledge",
       "domain:{domain}",
       "source:he-compound"
     ],
     session_id="project-brain:{repo}"
   )
   ```

4. **Check for promotion**: If similar solution exists 3+ times:
   - Promote to `.harness/knowledge/{domain}/rules.md`
   - Update observe() tags to include `"type:rule"`
   - Mark as "Promoted from knowledge (3+ confirmations)"

### Promotion Path

```text
First capture     → docs/solutions/ + .harness/knowledge/{domain}/knowledge.md
                  → observe(tags=["type:knowledge", ...])
                  
Second occurrence → Update existing knowledge.md, increment frequency counter

Third occurrence  → Promote to rules.md
                  → observe(tags=["type:rule", ...])
                  → Mark status: "Active (promoted YYYY-MM-DD)"
```

### Anti-patterns to Avoid
- Writing only to docs/solutions/ when .harness/ exists
- Creating duplicate entries in knowledge.md without checking
- Forgetting to sync to Local Memory MCP
- Promoting to rules without 3+ confirmations

## Preconditions

Advisory checks:
- the problem is solved, not merely in progress
- the solution is verified
- the problem is non-trivial enough to justify a durable artifact

## Categories

Use these exact categories unless the repo has an explicitly broader schema:
- `build-errors/`
- `test-failures/`
- `runtime-errors/`
- `performance-issues/`
- `database-issues/`
- `security-issues/`
- `ui-bugs/`
- `integration-issues/`
- `logic-errors/`

## Success output

Summarize:
- whether auto memory contributed supplementary evidence
- helper-role results in full mode
- optional specialized reviewer results
- the created or updated solution artifact path
- the likely future module or problem space this learning helps

## Auto-invoke cues

Direct entry into learning-capture mode is justified when the user says things like:
- "that worked"
- "it's fixed"
- "working now"
- "problem solved"

Manual override:
- use `he-compound [context]` to capture the learning immediately without waiting for an explicit auto-detect-style cue

---

## Common Mistakes to Avoid

| ❌ Wrong | ✅ Correct |
|----------|-----------|
| Subagents write files like `context-analysis.md`, `solution-draft.md` | Subagents return text data; orchestrator writes one final file |
| Research and assembly run in parallel | Research completes → then assembly runs |
| Multiple files created during workflow | One solution doc written or updated: `docs/solutions/[category]/[filename].md` (plus optional small edit to AGENTS.md/CLAUDE.md for discoverability) |
| Creating a new doc when an existing doc covers the same problem | Check overlap assessment; update the existing doc when overlap is high |
| Skipping to implementation without validating upstream artifacts | Resume from earliest incomplete or untrusted stage |
| Documenting unverified or still-changing fixes | Wait for verified solution before learning capture |
| Broadening `he-compound-refresh` into repo-wide sweep without evidence | Recommend refresh only for clear stale-doc candidates |
