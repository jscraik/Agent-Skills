# Docs Expert Baseline Practices

## Mission

Produce documentation that gets useful information into a reader's head quickly, with minimal cognitive load, and with practical paths to success (examples plus troubleshooting).

## Standards snapshot (as of April 2026)

Use this baseline unless the repository has stricter internal policy:

- OpenAI Cookbook documentation guidance (clarity, skimmability, consistency, broad helpfulness).
- GitHub community profile and repository health files.
- GitHub discoverability signals (topics, repository metadata, social preview).
- Repo-first brand governance (official repo standards before docs-expert fallback assets).
- Optional AI-specific context files such as `llms.txt` only when explicitly requested by repo owners.

Primary writing-rules reference:
- `references/openai-doc-writing-principles.md`

## OpenAI documentation quality gates (explicit)

Apply these gates in audits and rewrites:

### Make docs easy to skim
- Split content into titled sections.
- Prefer informative sentence-like headings over abstract nouns.
- Include a table of contents for long or sectioned docs.
- Keep paragraphs short; isolate critical points in one-sentence paragraphs where useful.
- Start sections and paragraphs with standalone topic sentences.
- Put topic words early in topic sentences.
- Put takeaways before procedures.
- Use bullets and tables frequently where they improve scanning.
- Bold important text sparingly and intentionally.

### Write well
- Keep sentences simple; split long sentences.
- Prefer unambiguous sentence structures.
- Prefer right-branching phrasing when possible.
- Avoid demonstrative pronouns across sentences when they reduce clarity.
- Keep terminology, casing, and punctuation consistent.
- Do not presume reader intent with phrases like “you probably want...”.

### Be broadly helpful
- Write simply for mixed language/experience audiences.
- Avoid abbreviations unless expanded on first use.
- Proactively include likely failure fixes.
- Prefer specific, accurate terminology over insider jargon.
- Keep examples general, minimal-dependency, and self-contained.
- Prioritize high-value/common tasks.
- Do not teach bad habits (especially secret handling).
- Consider broad framing before narrow implementation details.

## Notes

- Short description: Make docs skimmable, clear, and broadly helpful.
- Version: 1.0.0.
- Category: documentation.
- Compatibility: Works best in repos with Markdown docs. Optional tooling (if present): markdownlint and vale. No internet required.

## Inputs to collect (minimal)

1. Doc target(s): file path(s) or feature/component name.
2. Audience: beginner vs experienced; known prerequisites.
3. Primary job-to-be-done: what the reader is trying to do.
4. Constraints: supported platforms, required versions, security/compliance requirements.
5. Brand source of truth: exact path(s) or URL(s) for official brand guidance.
6. Visibility scope: internal/private vs public OSS.

If the user did not provide these, infer from repo context (existing docs, package.json, tool configs) and state assumptions explicitly.

## Outputs

- Updated Markdown docs (PR-ready edits).
- A short "Doc QA" summary of what changed and what to verify.
- If information is missing or unknown: a TODO list of specific facts the team must confirm.
- If branding applies: include brand compliance results and evidence (signature and assets).
- A QA bootstrap summary listing which lint/brand files were auto-installed.
- An evidence bundle that records lint outputs, brand check output, and checklist snapshot.

## Operating procedure

### 1) Locate and scope

- Identify the canonical doc surface(s): README, /docs, /guides, /runbooks, /api, etc.
- Do not rewrite everything. Pick the smallest set of files that solves the user task.
- If the task is repo-wide, also capture **GitHub community health** gaps (README, LICENSE, CONTRIBUTING, CODE_OF_CONDUCT, SECURITY, SUPPORT, issue/PR templates). Use `references/CHECKLIST.md`.

### 1b) Resolve brand authority before writing

Use this precedence order:

1. User-provided official brand docs for the target repo.
2. Brand docs inside the target repo (`brand/*`, `docs/brand/*`, design tokens docs).
3. Organization-level standards linked by the repo.
4. `docs-expert` fallback brand profile only when 1-3 do not exist and fallback mode is approved.

Never overwrite official repo brand assets with fallback defaults.

### 1c) Scope visibility and trust signals (public repos)

When docs are public-facing, verify:

- Repository description and homepage URL.
- Repository topics.
- Social preview image.
- Ownership/security/support paths (CODEOWNERS, SECURITY, SUPPORT).
- Optional metadata when relevant (`CITATION.cff`, `FUNDING.yml`, release/changelog guidance).

### 1a) Capture doc requirements

Record these at the top of the doc or in a visible "Doc requirements" section:

- Audience tier (beginner, intermediate, expert).
- Scope and non-scope (what this doc covers and does not cover).
- Doc owner and review cadence.
- Required approvals or stakeholders.

### 2) Build a skimmable structure first

- Create or repair a clear outline with sections that match reader questions.
- Add a table of contents for longer docs.
- Use headings as informative sentences (not vague nouns).

### 3) Write for skim-reading

Apply these rules aggressively:

- Keep paragraphs short; use one-sentence paragraphs for key points.
- Start sections and paragraphs with a standalone topic sentence.
- Put the topic words at the beginning of topic sentences.
- Put takeaways before procedure (results first, then steps).
- Use bullets and tables whenever they reduce scanning time.
- Bold truly important phrases sparingly (what to do, what not to do, critical constraints).

### 4) Write clean, unambiguous prose

- Prefer simple sentences; split long ones.
- Remove filler, adverbs, and needless phrasing.
- Avoid ambiguous sentence starts.
- Prefer right-branching phrasing (tell readers early what the sentence connects to).
- Avoid "this" or "that" references across sentences; repeat the specific noun instead.
- Be consistent (terminology, casing, naming conventions, punctuation style).

### 4a) Capture risk and assumptions

If the doc involves operational steps, safety, or data impact, add a "Risks and assumptions"
section that includes:

- Assumptions the doc relies on.
- Failure modes and blast radius.
- Rollback or recovery guidance.

### 5) Be broadly helpful

- Explain simply; do not assume English fluency.
- Avoid abbreviations; write terms out on first use.
- Proactively address likely failure points (env vars, PATH, permissions, ports, tokens).
- Prefer specific, accurate terminology over insider jargon.
- Keep examples general and exportable (minimal dependencies, self-contained snippets).
- Focus on common or high-value tasks over edge cases.
- Do not teach bad habits (for example, hardcoding secrets or unsafe defaults).

### 6) Accessibility and inclusive design

- Use descriptive link text; avoid "click here".
- Ensure heading order is logical and no levels are skipped.
- Provide alt text for non-decorative images; mark decorative images as such.
- Avoid instructions that rely only on color, shape, or spatial position.
- Prefer inclusive, plain language and avoid ableist or exclusionary phrasing.

### 7) Security, privacy, and safety pass

- Never expose real secrets, tokens, or internal endpoints; use placeholders.
- Avoid encouraging destructive or irreversible commands without warnings and backups.
- Call out PII handling and data retention considerations when relevant.
- Prefer least-privilege guidance for credentials, access, and permissions.

### 8) Check content against the repo

- Never invent commands, flags, file paths, outputs, or version numbers.
- Cross-check installation steps with actual configs (package scripts, Makefile, Dockerfile, CI).
- If you cannot verify a detail, flag it as needing confirmation.

### 9) Bootstrap missing QA tooling (default)

- Preferred bootstrap step: `python scripts/bootstrap_doc_qa.py --repo . --apply --brand-profile repo` before lint and brand checks.
- If `.vale.ini` is missing, install a local Vale baseline (`.vale.ini` and `.vale/styles/Docs/`).
- If markdownlint config is missing, install `.markdownlint-cli2.yaml`.
- If `brand/` or branding constraints are missing, install neutral repo-brand placeholders and constraints first.
- Use `--brand-profile docs-expert` only when the docs-expert fallback brand profile is explicitly requested.
- Record exactly which files were created and which files were already present.

### 10) Run doc linters (when available)

- If `.vale.ini` exists, run `vale <doc>` and record results.
- If markdownlint config exists, run `markdownlint-cli2 <doc> --config <config>`.
- If link-check tooling exists, run it and record results.
- If tooling is missing, state what is missing and how to enable it.
- If `scripts/check_readability.py` exists, run it and record the score and target range (default target: 45-70 Flesch Reading Ease; override with `--min/--max` or use `--no-range`).

### 10a) Automation hooks (optional)

Example CI or pre-commit snippets, adjusted to your repo:

```sh
python /path/to/bootstrap_doc_qa.py --repo . --apply --brand-profile repo
vale <doc>
markdownlint-cli2 <doc> --config <config>
python /path/to/check_brand_guidelines.py --repo . --docs <doc> --profile repo
python /path/to/check_readability.py <doc>
```

### 11) Finish with verification hooks

- Add "Verify" steps readers can run (expected output, health checks).
- Add Troubleshooting for the top 3 predictable failures.
- Ensure the doc has a clear "Next step" path.

## Definition of Done and Evidence (Gold Standard)

For any significant doc work, provide evidence that the Gold Industry Standard bar is met.

Required evidence:

Standards mapping:
- CommonMark or Markdown structure and formatting
- Accessibility and inclusive language basics
- Security and privacy guidance for sensitive info
- GitHub repository community health basics (when repo-wide documentation is in scope)
- GitHub visibility/discoverability metadata (for public repos)
- Brand compliance (when branding or README signature applies)
- AI-ready documentation consistency (when agent-facing docs are in scope)

Automated checks (if available):
- markdownlint, vale, link check (list commands run)
- Brand check script output (if branding applies)
- Readability check output (if available)

Review artifact:
- Self-review summary or peer review note

Deviations (if any):
- Description, risk, mitigation

## Anti-patterns to avoid

- Writing without confirming audience and purpose.
- Burying key decisions or risks in long prose.
- Shipping drafts without a verification pass.

## Use judgment when context demands it

These rules are defaults, not strict dogma. Break a rule when a repository-specific constraint, audience need, or safety requirement clearly justifies it, and record the reason in the deliverable.
