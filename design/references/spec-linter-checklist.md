# Spec Quality Checklist (prevents rebuilds)

## Problem & success
- [ ] Is the core problem singular and unambiguous? (If you changed the core problem, would the UX radically change?)
- [ ] Is there a measurable success metric + clear activation?
- [ ] Are MVP vs later explicitly separated?

## UX ambiguity removal
- [ ] Did you write the mental model, not just screens?
- [ ] Did you specify information architecture (entities + relationships + where they appear)?
- [ ] Did you specify system feedback states (empty/loading/error)?

## Execution
- [ ] Can you build it epic-by-epic with clear acceptance criteria?
- [ ] Are stories small enough to implement without "big bang" prompting?
- [ ] Is there a minimal test plan that would catch regressions?

## Communication clarity (anti–curse of knowledge)
- [ ] Could a new teammate explain the feature after reading only this doc?
- [ ] Did you define terms/entities the first time you used them?

## Evidence discipline (for Foundation Spec)
- [ ] Every paragraph ends with `Evidence:` or `Evidence gap:` line
- [ ] Sources are cited with file paths/links
- [ ] `Evidence Gaps` and `Evidence Map` sections are present and populated
