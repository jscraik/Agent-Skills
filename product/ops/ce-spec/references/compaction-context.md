# CE Spec Compaction Context

Read when: you need expanded standards nuance and additional examples that were moved out of `SKILL.md` for line-budget governance.

## Standards snapshot nuance
- For UI work, specify interaction states, accessibility, design constraints, and measurable UX outcomes explicitly.
- For long-running or failure-prone systems, specify state, recovery, observability, and trust boundaries instead of leaving them implicit.

## Additional guiding questions
- What is the most authoritative source?
- Does this need a spec or go straight to planning?
- What must be true over time?
- What can fail and how is recovery defined?
- Does this need a companion UI contract before planning?

## Additional examples
- "Revise `docs/specs/2026-03-21-session-rotation-spec.md` so token expiry behavior, rollback conditions, and observability events are explicit."
- "This billing settings feature needs a companion UI contract before planning; write the UI spec with loading, empty, and error states plus `VAC` IDs."
