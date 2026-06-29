# Agent Instruction Map

## Table of Contents

- [How to use this folder](#how-to-use-this-folder)
- [Instruction files](#instruction-files)
- [Quick picks](#quick-picks)

## How to use this folder

1. Start at repository root `AGENTS.md`.
2. On a fresh checkout, prove command reachability with
   `bash scripts/bootstrap-ask.sh --json`, then verify the fallback with
   `python3 bin/ask repo status --json`.
3. Use this folder for detailed policy only.
4. If two docs conflict, escalate before proceeding.

## Instruction files

- [01-instruction-map](/Docs/agents/01-instruction-map.md)
- [02-tooling-policy](/Docs/agents/02-tooling-policy.md)
- [03-local-memory](/Docs/agents/03-local-memory.md)
- [04-validation](/Docs/agents/04-validation.md)
- [05-contradictions-and-cleanup](/Docs/agents/05-contradictions-and-cleanup.md)
- [06-security-and-governance](/Docs/agents/06-security-and-governance.md)
- [07a-role-governance](/Docs/agents/07a-role-governance.md)
- [07b-agent-governance](/Docs/agents/07b-agent-governance.md)
- [08-release-and-change-control](/Docs/agents/08-release-and-change-control.md)
- [09-audit-trail-policy](/Docs/agents/09-audit-trail-policy.md)
- [10-agent-testing-gates](/Docs/agents/10-agent-testing-gates.md)
- [11-ai-review-governance](/Docs/agents/11-ai-review-governance.md)
- [12-ci-required-checks](/Docs/agents/12-ci-required-checks.md)
- [13-workflow-and-safety-guidance](/Docs/agents/13-workflow-and-safety-guidance.md)
- [14-path-ownership-boundaries](/Docs/agents/14-path-ownership-boundaries.md)
- [15-repo-surface-ownership](/Docs/agents/15-repo-surface-ownership.md)
- [16-agent-operating-contract](/Docs/agents/16-agent-operating-contract.md)
- [17-skill-management](/Docs/agents/17-skill-management.md)
- [18-browser-and-local-preview](/Docs/agents/18-browser-and-local-preview.md)
- [19-high-signal-steering-feedback](/Docs/agents/19-high-signal-steering-feedback.md)
- [20-misuse-resistant-interface-design](/Docs/agents/20-misuse-resistant-interface-design.md)
- [21-zero-setup-agent-workspace](/Docs/agents/21-zero-setup-agent-workspace.md)
- [22-systems-thinking-product-rule](/Docs/agents/22-systems-thinking-product-rule.md)
- [23-ctf-workflow-evals](/Docs/agents/23-ctf-workflow-evals.md)
- [24-tessl-live-skill-eval-workflow](/Docs/agents/24-tessl-live-skill-eval-workflow.md)
- [25-sdk-runtime-lane-contract](/Docs/agents/25-sdk-runtime-lane-contract.md)
- [26-pm-thread-coordination](/Docs/agents/26-pm-thread-coordination.md)
- [ask product golden path command contracts](/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md)

## Quick picks

| Need                                              | Open                                                                                                                               |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| Tooling and command policy                        | [/Docs/agents/02-tooling-policy.md](/Docs/agents/02-tooling-policy.md)                                                             |
| Validation order and checks                       | [/Docs/agents/04-validation.md](/Docs/agents/04-validation.md)                                                                     |
| Security and governance                           | [/Docs/agents/06-security-and-governance.md](/Docs/agents/06-security-and-governance.md)                                           |
| Release and risky git controls                    | [/Docs/agents/08-release-and-change-control.md](/Docs/agents/08-release-and-change-control.md)                                     |
| Canonical vs runtime edit ownership               | [/Docs/agents/14-path-ownership-boundaries.md](/Docs/agents/14-path-ownership-boundaries.md)                                       |
| Repo surface classification and cleanup ownership | [/Docs/agents/15-repo-surface-ownership.md](/Docs/agents/15-repo-surface-ownership.md)                                             |
| Repo command behavior and robot mode              | [/Docs/agents/16-agent-operating-contract.md](/Docs/agents/16-agent-operating-contract.md)                                         |
| Skill install, audit, fold, and line budgets      | [/Docs/agents/17-skill-management.md](/Docs/agents/17-skill-management.md)                                                         |
| Browser and local preview fallback                | [/Docs/agents/18-browser-and-local-preview.md](/Docs/agents/18-browser-and-local-preview.md)                                       |
| Steering feedback and durable uptake              | [/Docs/agents/19-high-signal-steering-feedback.md](/Docs/agents/19-high-signal-steering-feedback.md)                               |
| Misuse-resistant API and helper design            | [/Docs/agents/20-misuse-resistant-interface-design.md](/Docs/agents/20-misuse-resistant-interface-design.md)                       |
| Zero-setup agent workspace product rule           | [/Docs/agents/21-zero-setup-agent-workspace.md](/Docs/agents/21-zero-setup-agent-workspace.md)                                     |
| Systems thinking and blocker empowerment          | [/Docs/agents/22-systems-thinking-product-rule.md](/Docs/agents/22-systems-thinking-product-rule.md)                               |
| CTF-style workflow evals and skill self-refinement | [/Docs/agents/23-ctf-workflow-evals.md](/Docs/agents/23-ctf-workflow-evals.md)                                                     |
| Tessl private evals and scenario generation       | [/Docs/agents/24-tessl-live-skill-eval-workflow.md](/Docs/agents/24-tessl-live-skill-eval-workflow.md)                             |
| Skills SDK runtime lane proof                     | [/Docs/agents/25-sdk-runtime-lane-contract.md](/Docs/agents/25-sdk-runtime-lane-contract.md)                                       |
| PM thread delegation and reply delivery           | [/Docs/agents/26-pm-thread-coordination.md](/Docs/agents/26-pm-thread-coordination.md)                                             |
| Product command contracts                         | [/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md](/Docs/cli-specs/2026-05-01-ask-product-golden-path-contracts.md) |
