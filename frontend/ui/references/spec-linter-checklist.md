# Spec Quality Checklist (prevents rebuilds)

## Problem & success
- [ ] Is the core problem singular and unambiguous? (If you changed the core problem, would the UX radically change?)
- [ ] Is the job-to-be-done framed in plain language (JTBD-lite, not theory)?
- [ ] Is there a measurable success metric + clear activation?
- [ ] Are MVP vs later explicitly separated?
- [ ] Is in-scope vs out-of-scope explicit?
- [ ] Is the primary journey (happy path only) written as steps?

## UX ambiguity removal
- [ ] Did you write the mental model, not just screens?
- [ ] Did you specify information architecture (entities + relationships + where they appear)?
- [ ] Did you specify system feedback states (empty/loading/error)?

## Execution
- [ ] Can you build it epic-by-epic with clear acceptance criteria?
- [ ] Are stories small enough to implement without "big bang" prompting?
- [ ] Is there a minimal test plan that would catch regressions?
- [ ] Is Outcome → Opportunities → Solution captured (with rejected alternatives)?
- [ ] Are the top 3–5 assumptions/risks listed with mitigations?

## Communication clarity (anti–curse of knowledge)
- [ ] Could a new teammate explain the feature after reading only this doc?
- [ ] Did you define terms/entities the first time you used them?

## Evidence discipline (for Foundation Spec)
- [ ] Every paragraph ends with `Evidence:` or `Evidence gap:` line
- [ ] Sources are cited with file paths/links
- [ ] `Evidence Gaps` and `Evidence Map` sections are present and populated
