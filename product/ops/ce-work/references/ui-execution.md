# CE Work UI Execution

## Table of Contents
- [Purpose](#purpose)
- [When UI rules apply](#when-ui-rules-apply)
- [Prototype gate](#prototype-gate)
- [Production alignment](#production-alignment)
- [Evidence requirements](#evidence-requirements)

## Purpose
This note preserves the UI-specific execution behavior from the source prompts and the canonical `workflow-work.md` contract.

## When UI rules apply
Apply these rules when:
- the governing plan is a UI plan
- the plan or parent spec says `ui_required: true`
- the work changes user-visible pages, flows, screens, components, or interaction states

## Prototype gate
Do not skip the prototype decision phase when the governing artifact requires it.

Execution rules:
- if the plan says a prototype phase must happen first, complete that phase before later production phases
- if no prototype decision exists yet, run the prototype phase first instead of jumping into production code
- if a Prototype Pack was planned, preserve the decision record across variants rather than ad-libbing a fresh direction during implementation

For compatibility with the source prompt:
- broader comparison mode may require exactly four variants: `A`, `B`, `C`, `D`
- dedicated UI direction mode may use the narrower three-variant path when that is what the governing plan chose

Prototype artifacts are decision artifacts. Do not ship raw prototype HTML/CSS/JS as production unless the real product stack is also static HTML/CSS/JS.

## Production alignment
Production implementation should align to:
- the selected prototype direction
- the prototype-to-production mapping note when present
- the repo's canonical component, token, styling, accessibility, and routing patterns
- Figma design references when the plan or repo provides them

## Evidence requirements
For changed user-visible surfaces:
- capture screenshots of the shipped implementation
- include before/after evidence when the surface previously existed
- verify accessibility-sensitive states such as focus, error, empty, loading, and responsive behavior
- carry screenshot links or artifacts into the shipping handoff
