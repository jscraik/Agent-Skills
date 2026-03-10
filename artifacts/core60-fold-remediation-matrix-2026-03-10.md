# Core60 Fold Remediation Matrix (2026-03-10)

## Update After Repair

The sections below capture the initial audit state from earlier on March 10, 2026.

Since that audit, the repo has been remediated in these areas:

- Restored standalone skill: `frontend/tools/agentation`
- Restored standalone skill: `product/security/security-threat-model`
- Restored standalone skill: `product/security/security-ownership-map`
- Restored standalone skill: `utilities/verification-before-completion`
- Restored destination skill: `frontend/ui/react-ui-patterns`
- Restored destination skill: `utilities/test-driven-development`
- Rehydrated real folded mode guidance in `utilities/skill-builder` for:
  - `install-distribute`
- Rehydrated real folded mode guidance in `interview/interview-me` for:
  - `pm-track`
- Rehydrated real folded mode guidance in `interview/deep-interview` for:
  - `bug-track`
- Rehydrated real folded mode guidance in `frontend/ui/ui-visual-regression` for:
  - `trace-debug`
- Replaced truncated folded legacy descriptions in the matching `references/folded-legacy-modes-core60.md` files.
- Removed folded legacy ownership claims for the restored standalone skills from:
  - `product/domain/chatgpt-apps/SKILL.md`
  - `product/security/security-best-practices/SKILL.md`
- Updated the root skill index so the restored skills are discoverable again.
- Validated the repaired destination skills with `python3 scripts/diagnose_skill.py`:
  - `skill-builder`
  - `interview-me`
  - `deep-interview`
  - `ui-visual-regression`

The matrix tables below should therefore be read as the pre-remediation diagnosis, not the current post-repair repo state.

## Scope

Audit every fold listed in [artifacts/core60-fold-plan-2026-03-08.md](/Users/jamiecraik/dev/agent-skills/artifacts/core60-fold-plan-2026-03-08.md) against current repo state on March 10, 2026.

Questions answered:

1. Does the destination skill path still exist?
2. Does the destination body contain source-specific workflow content, or only a folded-mode label?
3. Is the folded reference usable, or only a summary stub?

## Method

Signals used:

- Destination path exists or is missing.
- Count of source-specific keyword hits in the destination body.
- Whether the folded reference file contains only summary metadata.
- Whether the folded reference appears truncated or incomplete.

Classification:

- `broken`: destination skill path is missing or retired.
- `shallow`: destination exists, but the old workflow mostly survives only as a folded label or thin reference note.
- `medium`: destination exists and overlaps the old intent, but mode-specific migration is still summary-only or incomplete.
- `likely-ok`: destination appears to cover most of the legacy workflow intent, but still uses the same fold-summary structure and should not be treated as fully regression-proof.

## Summary

- Total folds audited: `26`
- `broken`: `2`
- `shallow`: `2`
- `medium`: `5`
- `likely-ok`: `17`

## Semantic disposition

This section answers a different question from the repo-state audit:

- repo-state audit: "is the fold currently implemented correctly?"
- semantic disposition: "should this skill live in that destination at all?"

Disposition types:

- `repair-in-place`: destination is conceptually reasonable; migrate the missing workflow properly.
- `restore-destination`: the chosen destination is conceptually fine, but the destination skill itself is missing and must be restored first.
- `restore-standalone`: the fold appears semantically wrong or too lossy; safest repair is to restore the source skill as its own skill.
- `reroute`: destination is conceptually wrong and should be moved to a better surviving skill.

Disposition summary:

- `repair-in-place`: `18`
- `restore-destination`: `1`
- `restore-standalone`: `6`
- `reroute`: `1`

## Priority Queue

### P0 Broken destinations

| Source | Destination | Mode | Status | Why it is broken | Recommended fix |
|---|---|---|---|---|---|
| `frontend/ui/react-best-practices` | `frontend/ui/react-ui-patterns` | `performance-patterns` | `broken` | Destination skill path is missing, but the root skill index and fold plan still reference it. | Restore the destination skill or reroute the fold to a real destination, then repair all references and inventories. |
| `utilities/verification-before-completion` | `utilities/test-driven-development` | `final-gate` | `broken` | Destination skill path is missing, but the root skill index and fold plan still reference it. | Restore the destination skill or reroute the fold to a real destination, then repair all references and inventories. |

### P1 Shallow folds

| Source | Destination | Mode | Status | Why it is shallow | Recommended fix |
|---|---|---|---|---|---|
| `frontend/tools/agentation` | `product/domain/chatgpt-apps` | `agentation-integration` | `shallow` | Destination body only shows the folded mode label; the old operational workflow lives mostly as a summary stub in the folded reference. | Rehydrate the old Agentation workflow into a dedicated mode/profile section or mark this fold as deprecated and non-equivalent. |
| `utilities/skill-installer` | `utilities/skill-builder` | `install-distribute` | `shallow` | Destination body barely reflects install/distribute behavior beyond the folded block; the folded reference is a summary, not runnable guidance. | Add a real install/distribute mode section, with install/update validation flow and source-of-truth paths. |

### P2 Medium-risk folds

| Source | Destination | Mode | Status | Why it needs follow-up | Recommended fix |
|---|---|---|---|---|---|
| `frontend/tools/agent-trace-debug` | `frontend/ui/ui-visual-regression` | `trace-debug` | `medium` | Destination overlaps some trace/debug ideas, but the fold still depends on a thin folded reference for source-specific procedure. | Pull over the exact trace-debug procedure or explicitly narrow the claimed coverage. |
| `interview/pm-interview` | `interview/interview-me` | `pm-track` | `medium` | Destination strongly overlaps PM discovery, but the folded reference is visibly truncated and incomplete. | Replace the truncated folded summary with a real PM-track section or full reference. |
| `interview/bug-interview` | `interview/deep-interview` | `bug-track` | `medium` | Destination overlaps bug interrogation, but the folded reference is visibly truncated and incomplete. | Replace the truncated folded summary with a real bug-track section or full reference. |
| `product/security/security-threat-model` | `product/security/security-best-practices` | `threat-model` | `medium` | Destination overlaps the domain, but the fold is still described as a summary mode and not a migrated threat-model workflow. | Add a dedicated threat-model path with assets, trust-boundary, and abuse-case steps. |
| `product/security/security-ownership-map` | `product/security/security-best-practices` | `ownership-risk-map` | `medium` | Destination overlaps security analysis, but ownership-mapping workflow and outputs are still only summarized in folded metadata. | Add a dedicated ownership-risk mode or move this to a destination that actually performs repo ownership analysis. |

## Full Matrix

| Source | Destination | Mode | Status | Notes |
|---|---|---|---|---|
| `frontend/tools/agent-trace-debug` | `frontend/ui/ui-visual-regression` | `trace-debug` | `medium` | Present destination; source-specific procedure appears only partially reflected in body. |
| `frontend/tools/agentation` | `product/domain/chatgpt-apps` | `agentation-integration` | `shallow` | Same mistake class as the original Agentation finding. |
| `frontend/ui/web-design-guidelines` | `frontend/ui/frontend-ui-design` | `guideline-audit` | `likely-ok` | Strong domain overlap and multiple source-specific signals present. |
| `product/strategy/brainstorming` | `product/specs/product-spec` | `ideation-prep` | `likely-ok` | Destination body already carries strong ideation/planning overlap. |
| `product/strategy/project-improvement-ideator` | `product/specs/product-spec` | `improvement-batch` | `likely-ok` | Destination body reflects scoring/improvement language well. |
| `product/strategy/asymmetric-ideation-engine` | `product/specs/product-spec` | `asymmetric-ideas` | `likely-ok` | Destination body reflects ideation-specific framing and artifacts. |
| `backend/mkit-builder` | `backend/mcp-builder` | `enterprise-profile` | `likely-ok` | Destination body strongly overlaps MCP/server enterprise workflow. |
| `github/automate-github-issues` | `github/gh-workflow` | `automated-triage` | `likely-ok` | Destination body contains strong issue/triage flow overlap. |
| `utilities/codex-prompt-creator` | `utilities/skill-builder` | `prompt-packaging` | `likely-ok` | Destination body strongly overlaps prompt/skill packaging. |
| `utilities/skill-installer` | `utilities/skill-builder` | `install-distribute` | `shallow` | Install/update workflow was not really migrated into destination body. |
| `utilities/diagram-context-refresh` | `utilities/diagram-cli` | `context-refresh` | `likely-ok` | Destination body strongly overlaps diagram refresh workflow. |
| `frontend/ui/interface-craft` | `frontend/ui/ui-ux-creative-coding` | `craft-profile` | `likely-ok` | Destination body reflects craft/motion/quality guidance well. |
| `frontend/ui/react-best-practices` | `frontend/ui/react-ui-patterns` | `performance-patterns` | `broken` | Destination path missing. |
| `product/docs/claude-md` | `product/docs/agents-md` | `claude-target` | `likely-ok` | Destination body strongly overlaps AGENTS/agent-doc authoring. |
| `product/docs/gemini-md` | `product/docs/agents-md` | `gemini-target` | `likely-ok` | Destination body strongly overlaps agent-doc authoring. |
| `product/domain/chatgpt-apps-production-checklist` | `product/domain/chatgpt-apps` | `production-gate` | `likely-ok` | Destination body already has strong deploy/submission/checklist overlap. |
| `github/greptile/greploop` | `github/greptile/check-pr` | `iterative-fix-loop` | `likely-ok` | Destination body overlaps readiness/review loop work. |
| `github/local-action-verification` | `github/gh-fix-ci` | `local-ci-repro` | `likely-ok` | Destination body overlaps CI repro and verification behavior. |
| `interview/pm-interview` | `interview/interview-me` | `pm-track` | `medium` | Destination is plausible, but folded reference is truncated. |
| `interview/bug-interview` | `interview/deep-interview` | `bug-track` | `medium` | Destination is plausible, but folded reference is truncated. |
| `product/security/security-threat-model` | `product/security/security-best-practices` | `threat-model` | `medium` | Threat-model workflow appears summarized, not migrated. |
| `product/security/security-ownership-map` | `product/security/security-best-practices` | `ownership-risk-map` | `medium` | Ownership-map workflow appears summarized, not migrated. |
| `utilities/executing-plans` | `utilities/writing-plans` | `execute` | `likely-ok` | Destination body overlaps planning plus execution checkpoints. |
| `utilities/verification-before-completion` | `utilities/test-driven-development` | `final-gate` | `broken` | Destination path missing. |
| `utilities/recent-code-bugfix` | `utilities/systematic-debugging` | `recent-commit-lens` | `likely-ok` | Destination body overlaps commit-based debugging strongly. |
| `product/docs/docs-md` | `product/docs/docs-expert` | `progressive-disclosure` | `likely-ok` | Destination body strongly overlaps docs audit/rewrite structure. |

## Concrete repair order

1. Repair the two dangling destinations before touching any summary-only folds.
2. Fix the two shallow folds next:
   - `agentation-integration`
   - `install-distribute`
3. Replace truncated folded references:
   - `pm-track`
   - `bug-track`
4. Decide whether `security-best-practices` should truly own:
   - `threat-model`
   - `ownership-risk-map`
5. Rebuild inventories so active, retired, and root skill indexes agree with the live tree.

## Semantic repair matrix

| Source | Current destination | Mode | Disposition | Why |
|---|---|---|---|---|
| `frontend/tools/agent-trace-debug` | `frontend/ui/ui-visual-regression` | `trace-debug` | `repair-in-place` | Trace/debugging visual diffs is close enough to visual-regression review that a dedicated mode is plausible. |
| `frontend/tools/agentation` | `product/domain/chatgpt-apps` | `agentation-integration` | `restore-standalone` | Agentation is a frontend integration/annotation automation workflow across React, Next, Vite, and Tauri. That is materially broader and different from ChatGPT Apps SDK work. |
| `frontend/ui/web-design-guidelines` | `frontend/ui/frontend-ui-design` | `guideline-audit` | `repair-in-place` | Design-guideline review fits naturally inside frontend UI design. |
| `product/strategy/brainstorming` | `product/specs/product-spec` | `ideation-prep` | `repair-in-place` | Ideation is a natural upstream phase of product specification. |
| `product/strategy/project-improvement-ideator` | `product/specs/product-spec` | `improvement-batch` | `repair-in-place` | Improvement ideation fits as a product-spec mode. |
| `product/strategy/asymmetric-ideation-engine` | `product/specs/product-spec` | `asymmetric-ideas` | `repair-in-place` | This is still product ideation/spec work rather than a separate domain. |
| `backend/mkit-builder` | `backend/mcp-builder` | `enterprise-profile` | `repair-in-place` | `mkit-builder` and `mcp-builder` are close enough in domain and artifact shape. |
| `github/automate-github-issues` | `github/gh-workflow` | `automated-triage` | `repair-in-place` | Issue triage belongs under the broader GitHub workflow skill. |
| `utilities/codex-prompt-creator` | `utilities/skill-builder` | `prompt-packaging` | `repair-in-place` | Prompt packaging is an extension of skill creation and packaging. |
| `utilities/skill-installer` | `utilities/skill-builder` | `install-distribute` | `repair-in-place` | Installation/distribution belongs with skill lifecycle management, but needs a real workflow. |
| `utilities/diagram-context-refresh` | `utilities/diagram-cli` | `context-refresh` | `repair-in-place` | Context refresh is a valid sub-mode of diagram CLI operations. |
| `frontend/ui/interface-craft` | `frontend/ui/ui-ux-creative-coding` | `craft-profile` | `repair-in-place` | Interface craft is a stylistic profile of creative coding work. |
| `frontend/ui/react-best-practices` | `frontend/ui/react-ui-patterns` | `performance-patterns` | `restore-destination` | Folding React best-practice guidance into a React UI patterns skill is conceptually fine, but the destination skill must exist. |
| `product/docs/claude-md` | `product/docs/agents-md` | `claude-target` | `repair-in-place` | Agent-flavored AGENTS authoring belongs inside `agents-md`. |
| `product/docs/gemini-md` | `product/docs/agents-md` | `gemini-target` | `repair-in-place` | Same reasoning as `claude-md`. |
| `product/domain/chatgpt-apps-production-checklist` | `product/domain/chatgpt-apps` | `production-gate` | `repair-in-place` | Production-readiness is a valid phase of ChatGPT Apps work. |
| `github/greptile/greploop` | `github/greptile/check-pr` | `iterative-fix-loop` | `repair-in-place` | Review-loop and PR readiness live in the same narrow domain. |
| `github/local-action-verification` | `github/gh-fix-ci` | `local-ci-repro` | `repair-in-place` | Local CI repro is a valid subworkflow of GitHub CI fixing. |
| `interview/pm-interview` | `interview/interview-me` | `pm-track` | `repair-in-place` | PM discovery fits the broader interview-me intake model. |
| `interview/bug-interview` | `interview/deep-interview` | `bug-track` | `repair-in-place` | Bug interrogation is a specialized deep interview. |
| `product/security/security-threat-model` | `product/security/security-best-practices` | `threat-model` | `restore-standalone` | Threat modeling is a distinct AppSec workflow with different outputs, questions, and stopping points from generic best-practices review. |
| `product/security/security-ownership-map` | `product/security/security-best-practices` | `ownership-risk-map` | `restore-standalone` | Ownership graph analysis is a separate git-history and artifact-generation workflow, not just a best-practices pass. |
| `utilities/executing-plans` | `utilities/writing-plans` | `execute` | `reroute` | Execution is adjacent to planning, but not the same job. The safer fix is to move execution guidance to an execution-oriented surviving skill or restore it separately if no such destination exists. |
| `utilities/verification-before-completion` | `utilities/test-driven-development` | `final-gate` | `restore-standalone` | Verification-before-completion is its own decision gate. It should not depend on a TDD skill, and the destination is also missing. |
| `utilities/recent-code-bugfix` | `utilities/systematic-debugging` | `recent-commit-lens` | `repair-in-place` | Recent-commit analysis is a valid debugging lens, not a separate domain. |
| `product/docs/docs-md` | `product/docs/docs-expert` | `progressive-disclosure` | `repair-in-place` | Progressive-disclosure doc authoring fits naturally inside docs-expert. |

## Notable semantic corrections

### Agentation

`agentation -> chatgpt-apps` is the clearest example of a semantically weak fold.

Why it looks wrong:

- Old Agentation scope was frontend integration and local automation across `React`, `Next.js`, `Vite`, and `Tauri`.
- It dealt with local widget mounting, MCP/webhook transport, submit-driven automation, and annotation tooling.
- `chatgpt-apps` is a much more specific domain skill for ChatGPT Apps SDK apps, MCP servers, and ChatGPT widget wiring.

Conclusion:

- The current location is not just shallow, it is conceptually mismatched.
- Safest repair: restore Agentation as a standalone skill.

### Threat modeling and security ownership mapping

Both security folds also look semantically too lossy for `security-best-practices`.

Why:

- `security-threat-model` is a structured modeling exercise with trust boundaries, assets, abuse paths, and mitigation ranking.
- `security-ownership-map` is a graph/artifact-producing git-history analysis workflow.
- `security-best-practices` is primarily a review-and-recommendation skill.

Conclusion:

- Both should be restored as standalone skills unless a more specific surviving AppSec destination is introduced.

### Verification-before-completion

This fold looks wrong even before considering the missing destination.

Why:

- Verification-before-completion is a universal completion gate.
- TDD is a development style for behavior change implementation.
- One should not depend on the other conceptually.

Conclusion:

- Restore as standalone.

## Commands run

```bash
sed -n '1,220p' artifacts/core60-phase3-retire-list-2026-03-08.txt
sed -n '1,260p' artifacts/core60-fold-plan-2026-03-08.md
rg -n "core60|folded legacy|Source skill:" . -S
git show 5b3090f32ee9653249929965bcd35fd5b65b530a:<source>/SKILL.md
python3 /tmp/core60_fold_audit.py > /tmp/core60_fold_audit.json
jq -r '.[] | ...' /tmp/core60_fold_audit.json
fd -HI -t f SKILL.md ...
rg -n "react-ui-patterns|test-driven-development|verification-before-completion" . -S
```

## Notes

- This matrix is intentionally conservative. `likely-ok` means "not immediately alarming from repo evidence," not "proven regression-free."
- The fold design pattern itself is too summary-heavy. Even where the destination looks healthy, the migration style still depends on folded metadata more than true content transfer.
