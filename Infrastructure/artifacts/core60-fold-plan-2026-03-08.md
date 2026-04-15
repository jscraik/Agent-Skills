# Core 60 Fold Plan (2026-03-08)

Source baseline: [core50](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/core50-skill-list-2026-03-08.json)

Decision support matrix used: [core30 review](/Users/jamiecraik/dev/agent-skills/Infrastructure/artifacts/core30-skill-review-2026-03-08.md)

## Top60 Construction
- Base set: current core 50
- Added 10 specialists to improve fold coverage and reduce orphan skills:
  - `backend/cli-spec`
  - `frontend/ui/interface-craft`
  - `frontend/ui/ui-ux-creative-coding`
  - `frontend/ui/fixing-motion-performance`
  - `frontend/website/fixing-metadata`
  - `interview/architecture-interview`
  - `interview/bug-interview`
  - `product/security/security-threat-model`
  - `product/security/security-ownership-map`
  - `Skills/diagram-context-refresh`

## Inbound Folds (non-top60 -> top60)
- `frontend/tools/agent-trace-debug` -> `frontend/ui/ui-visual-regression` (`trace-debug` mode)
- `frontend/tools/agentation` -> `product/domain/chatgpt-apps` (`agentation-integration` mode)
- `frontend/ui/web-design-guidelines` -> `frontend/ui/frontend-ui-design` (`guideline-audit` mode)
- `product/strategy/brainstorming` -> `product/specs/product-spec` (`ideation-prep` mode)
- `product/strategy/project-improvement-ideator` -> `product/specs/product-spec` (`improvement-batch` mode)
- `product/strategy/asymmetric-ideation-engine` -> `product/specs/product-spec` (`asymmetric-ideas` mode)
- `backend/mkit-builder` -> `backend/mcp-builder` (`enterprise-profile` mode)
- `github/automate-github-issues` -> `github/gh-workflow` (`automated-triage` mode)
- `Skills/codex-prompt-creator` -> `Skills/skill-builder` (`prompt-packaging` mode)
- `Skills/skill-installer` -> `Skills/skill-builder` (`install-distribute` mode)
- `Skills/diagram-context-refresh` -> `Skills/diagram-cli` (`context-refresh` mode)

## Internal Folds (top60 -> top60)
- `frontend/ui/interface-craft` -> `frontend/ui/ui-ux-creative-coding` (`craft-profile`)
- `frontend/ui/react-best-practices` -> `frontend/ui/react-ui-patterns` (`performance-patterns`)
- `product/docs/claude-md` -> `product/docs/agents-md` (`claude-target`)
- `product/docs/gemini-md` -> `product/docs/agents-md` (`gemini-target`)
- `product/domain/chatgpt-apps-production-checklist` -> `product/domain/chatgpt-apps` (`production-gate`)
- `github/greptile/greploop` -> `github/greptile/check-pr` (`iterative-fix-loop`)
- `github/local-action-verification` -> `github/gh-fix-ci` (`local-ci-repro`)
- `interview/pm-interview` -> `interview/interview-me` (`pm-track`)
- `interview/bug-interview` -> `interview/deep-interview` (`bug-track`)
- `product/security/security-threat-model` -> `product/security/security-best-practices` (`threat-model`)
- `product/security/security-ownership-map` -> `product/security/security-best-practices` (`ownership-risk-map`)
- `Skills/executing-plans` -> `Skills/writing-plans` (`execute`)
- `Skills/verification-before-completion` -> `Skills/test-driven-development` (`final-gate`)
- `Skills/recent-code-bugfix` -> `Skills/systematic-debugging` (`recent-commit-lens`)
- `product/docs/docs-md` -> `product/docs/docs-expert` (`progressive-disclosure`)

## Do Not Fold
- `product/docs/openai-docs`
- `Skills/alignment-checkpoint`
- `Skills/visual-explainer`
- `Skills/using-git-worktrees`

## Rollout Rule
- Phase 1: Add aliases/modes only; keep legacy skills callable.
- Phase 2: Route primary triggers to destination skills and monitor one week.
- Phase 3: Retire low-traffic source skills only after zero-regression validation.
