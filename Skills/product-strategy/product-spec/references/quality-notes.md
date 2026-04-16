# Quality notes

## Vibe Engineering Anti-patterns
- NEVER ship non-trivial code without tests—untested code is not complete, it's debt.
- DO NOT reinvent UI components—use the component registry/design system; custom implementations create divergence.
- Avoid "tests will come later"—write tests first (TDD) for any logic with >2 branches.
- DO NOT skip the component registry check—if a component exists, use it; if not, add it to the registry.
- Avoid hand-waving test coverage—"we tested it manually" is not evidence of reliability.
- DO NOT merge PRs with failing tests—failing tests mean the code is not ready.

## Empowerment
- Make decisions explicit: state chosen options, rejected alternatives, and rationale.
- Highlight owner and DRI for each risk/assumption and each open question.
- Encourage small, testable slices with graduation criteria before full rollout.
- Offer two to three concrete next-step choices at each review gate (accept, revise, or debate again) and ask the user to pick one.
- Ask for prioritization when scope is broad; propose a default ordering and let the user approve or reorder it.

## Compliance
- Check against GOLD Industry Standards guide in ~/.codex/AGENTS.override.md
