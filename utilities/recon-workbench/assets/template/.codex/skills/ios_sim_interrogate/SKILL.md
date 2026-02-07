---
name: ios_sim_interrogate
description: Analyze iOS Simulator behavior using simctl captures, Web Inspector,
  and Instruments. Use when you need evidence from iOS simulator runs.
metadata:
  source_repo: https://github.com/jscraik/Agent-Skills
  source_rev: 7e31061c353c94746910d239ae122900cc5324fb-dirty
  source_dirty: 'true'
  source_dirty_paths: utilities/recon-workbench/references/evals.yaml, utilities/skill-creator/scripts/run_skill_evals.py,
    design/better-icons/
---

Inputs:
- Simulator context (booted simulator), and either app bundle id or URL for web content.
- Goal + scenario.

Important:
- Safari Web Inspector inspects web content and WKWebView, not native Swift call stacks.
- Use Xcode/Instruments for native Swift/ObjC behavior.

Output:
- Annotate which evidence comes from media captures vs inspector exports vs Instruments traces.

## Cognitive Support / Plain-Language
- Optimize for low cognitive load (TBI support): one task at a time, explicit steps.
- Use plain language first; define jargon in parentheses.
- Keep steps short and checklist-driven where possible.
- Externalize state: decisions, assumptions, and the next step.
- Provide ELI5 explanations for non-trivial logic.
- Ask one question at a time; prefer multiple-choice when possible.

