## Doc QA checklist (docs-expert)

### Structure and navigation
- [ ] Title states the doc's purpose (not a vague label).
- [ ] Headings are informative sentences where possible.
- [ ] Table of contents exists if the doc is long/sectioned.
- [ ] Reader can find: prerequisites -> quickstart -> common tasks -> troubleshooting.

### Skimmability
- [ ] Paragraphs are short; key points are isolated when needed.
- [ ] Each section starts with a standalone topic sentence.
- [ ] Topic words appear early in topic sentences.
- [ ] Bullets/tables used where they improve scanning.
- [ ] Takeaways appear before long procedures.

### Clarity and style
- [ ] Sentences are simple and unambiguous.
- [ ] No fragile "this/that" references across sentences; nouns are explicit.
- [ ] Consistent terminology/casing across the doc.
- [ ] No mind-reading phrases ("you probably want...", "now you'll...").

### Broad helpfulness
- [ ] Terms are explained simply; abbreviations expanded on first use.
- [ ] Likely setup pitfalls are addressed (env vars, permissions, ports, PATH).
- [ ] Code examples are minimal, self-contained, and reusable.
- [ ] Security hygiene is correct (no secrets in code; safe defaults).

### Correctness and verification
- [ ] Steps match repo reality (scripts/configs/paths verified).
- [ ] Includes a "Verify" section with expected results.
- [ ] Troubleshooting covers top failure modes.
- [ ] Unknowns are called out explicitly as items to confirm.

### Requirements, risks, and lifecycle
- [ ] Doc requirements recorded (audience tier, scope/non-scope, owner, review cadence).
- [ ] Risks and assumptions documented when operational or data impact exists.
- [ ] "Last updated" and owner are present for top-level docs.
- [ ] Acceptance criteria included (5-10 items).

### GitHub repository community health (repo-wide)
- [ ] README exists and answers: what it is, who it’s for, quickstart, verify, troubleshooting, how to get help.
- [ ] LICENSE exists (or the repo explicitly documents why it’s absent).
- [ ] CONTRIBUTING guide exists (how to propose changes, run checks, style/commit conventions).
- [ ] CODE_OF_CONDUCT exists (or repo explicitly documents why it’s absent).
- [ ] SECURITY policy exists (how to report vulnerabilities; do not direct reporters to public issues).
- [ ] SUPPORT guidance exists (where users should ask questions; what maintainers will/won’t support).
- [ ] Issue intake exists (`.github/ISSUE_TEMPLATE/*` issue templates or issue forms).
- [ ] PR intake exists (`.github/PULL_REQUEST_TEMPLATE.md` or equivalent).
- [ ] Changelog / release notes exist when the project is versioned (CHANGELOG.md or Releases guidance).
- [ ] Ownership is discoverable (CODEOWNERS and/or “Maintainers” section in docs) when the project has multiple contributors.

### GitHub visibility and trust signals (public repos)
- [ ] Repository description clearly states value and audience.
- [ ] Homepage URL points to canonical docs/site.
- [ ] Relevant repository topics are configured.
- [ ] Social preview image is configured and current.
- [ ] CITATION metadata exists when citation is relevant (`CITATION.cff`).
- [ ] Funding metadata exists when sponsorship is accepted (`.github/FUNDING.yml`).

### Brand compliance (when applicable)
- [ ] Brand source-of-truth path is cited in the deliverable.
- [ ] Root README includes the documentation signature (image or ASCII fallback).
- [ ] Brand assets exist in `brand/` and match approved formats.
- [ ] No watermark usage in README or technical docs.
- [ ] Visual styling follows brand guidance only when requested.

### AI-ready documentation (when applicable)
- [ ] Human-facing docs remain authoritative and complete.
- [ ] Agent-facing docs (for example `AGENTS.md`) do not contradict canonical docs.
- [ ] Optional `llms.txt` is only added when requested and labeled as optional/emerging.
- [ ] High-value workflows have retrieval-friendly headings and concise command examples.

### Evidence bundle
- [ ] QA bootstrap output recorded when baseline files were installed.
- [ ] Lint outputs recorded (Vale/markdownlint/link check).
- [ ] Brand check output recorded when branding applies.
- [ ] Readability output recorded when available.
- [ ] Checklist snapshot included with the deliverable.
