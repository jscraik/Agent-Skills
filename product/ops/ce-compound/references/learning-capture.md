# Learning Capture

Read when: the selected `ce-compound` mode is `learning-capture`.

## Canonical purpose

Capture a recently solved problem while the context is fresh, creating structured documentation in `docs/solutions/` with YAML frontmatter for searchability and future reuse.

Knowledge compounds:
- first solve takes research
- documented solution makes the next occurrence much faster

## Modes

### Full mode

Default behavior.

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
- if memory notes materially influence the final doc, label them with `(auto memory [claude])`
- if memory notes contradict the verified fix or conversation, treat them as cautionary context rather than truth

## Full-mode phases

### Phase 1: Parallel research

Launch these helpers in parallel. They return text only.

1. Context Analyzer
   - extract conversation history
   - identify problem type, component, and symptoms
   - incorporate any auto-memory excerpt as supplementary evidence
   - validate against the documentation schema
   - return: YAML frontmatter skeleton

2. Solution Extractor
   - analyze investigation steps
   - identify root cause
   - extract the working solution with code examples when useful
   - use auto memory only as secondary evidence
   - return: solution content block

3. Related Docs Finder
   - search `docs/solutions/` for related documentation
   - identify cross-references and related issues
   - flag docs that may now be stale, contradicted, or overly broad
   - return: links, relationships, and refresh candidates

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

### Phase 2: Assembly and write

Wait for all Phase 1 helpers to complete.

The orchestrator then:
1. collects all text results
2. assembles the complete markdown file
3. validates YAML frontmatter
4. creates the directory when needed
5. writes the single final file

### Phase 2.5: Selective refresh check

`ce-compound-refresh` is not a default follow-up. Use it selectively only after the new learning is written.

Good reasons to refresh:
- the new fix contradicts an older learning or pattern doc
- the new fix supersedes a documented solution
- a refactor, migration, rename, or dependency upgrade likely invalidated older references
- a pattern doc is now overly broad or outdated
- Related Docs Finder surfaced strong stale-doc candidates

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
- `references/upstream-compound-docs-guide.md`
- `references/compound-docs-yaml-schema.md`
- `references/compound-docs-resolution-template.md`
- `references/compound-docs-critical-pattern-template.md`

Rules:
- preserve the local `ce-compound` one-file-write contract
- treat the upstream schema and templates as richer guidance, not disposable background
- if the target repo does not use schema-driven `docs/solutions/`, fall back to the canonical local categories and shape

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
- the created solution artifact path
- the likely future module or problem space this learning helps

## Auto-invoke cues

Direct entry into learning-capture mode is justified when the user says things like:
- "that worked"
- "it's fixed"
- "working now"
- "problem solved"

Manual override:
- use `ce-compound [context]` to capture the learning immediately without waiting for an explicit auto-detect-style cue
