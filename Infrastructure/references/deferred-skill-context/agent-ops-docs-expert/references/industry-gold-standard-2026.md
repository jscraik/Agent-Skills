# Industry Gold Standard (April 2026)

Use this reference to keep `docs-expert` aligned with current technical documentation best practices.

## Source authority order

When guidance conflicts, resolve it in this order:

1. Project-specific documentation and brand guidance.
2. Platform or product documentation standards that govern the target surface.
3. Established technical writing references used as defaults:
   - Diataxis for documentation architecture
   - Google developer documentation style guide for procedures, accessibility, and developer-doc clarity
   - GitHub Docs for repository trust and community-health expectations
   - Write the Docs for maintainership and documentation-program practice

## Documentation architecture

- Organize documentation around user need, not writer convenience.
- Prefer Diataxis-style separation between tutorials, how-to guides, reference, and explanation.
- Keep one dominant document type per page.
- If a page starts mixing user needs, split it or cross-link to the correct companion page.
- Treat information architecture as part of documentation quality, not cleanup work.

## Reader-first writing rules

- Lead with user goal, task, or takeaway instead of internal implementation detail.
- Prefer stable, descriptive headings so readers and retrieval systems can navigate quickly.
- Put the distinguishing information early in paragraphs and list items.
- Favor clear, direct sentences over hedging or stacked qualifiers.
- Use consistent terminology and define unfamiliar abbreviations on first use.

## Procedure-writing rules

- Use one step per action unless the actions are tiny and inseparable.
- State where the action happens before the action itself.
- When useful, state the goal before the action.
- Keep procedures short; if steps get long, split them.
- Avoid repeating procedures; link to the canonical one instead.
- Include a verification or expected result when the user needs confidence that the step worked.

## Accessibility and global-readability rules

- Do not rely on color, size, or position alone to convey meaning.
- Avoid directional language such as "above", "below", or "on the right".
- Use descriptive headings, labels, alt text, and captions.
- Ensure the content still works without images, sound, color, or pointer-only interaction.
- Prefer plain language, shorter sentences, and parallel structure in lists and procedures.

## Repository trust and discoverability

- For public repositories, README, LICENSE, CONTRIBUTING, SECURITY, SUPPORT, and CODE_OF_CONDUCT should be considered baseline trust surfaces.
- Include repository metadata checks such as description, homepage, topics, and social preview where relevant.
- Prefer explicit support and security-reporting paths over vague “open an issue” guidance.
- When a repository is public, treat community-health and security posture as part of documentation quality.

## AI-ready but human-first

- Keep docs human-first; AI-consumable structure should support, not replace, readable documentation.
- Use stable headings, explicit examples, and compact context blocks.
- Keep machine-oriented context files aligned with human docs to avoid contradiction drift.
- Prefer small, linkable documents over giant omnibus pages.

## Maintenance expectations

- Documentation quality includes ownership, upkeep cadence, and verification strategy.
- Prefer docs that point to canonical commands and sources instead of copying fragile details repeatedly.
- Where possible, encode recurring doc quality checks in tooling or templates rather than relying on memory.
