# UI Skills Shadow Results (Phase 2)

Shadow mode runs evaluator + checkpoint adversarial checks without automatic improvement writes.

## Table of Contents

- [Pilot scope](#pilot-scope)
- [Window summary](#window-summary)
- [Run log](#run-log)
- [Exit gate checks](#exit-gate-checks)

## Pilot scope

- `auth-best-practices`
- `auth-create-auth`
- `backend-backend-engineer`
- `backend-cli-spec`
- `backend-mcp-builder`
- `backend-workers-mcp`
- `frontend-graphics-better-icons`
- `frontend-graphics-favicon-generator`
- `frontend-graphics-imagegen`
- `frontend-graphics-nano-banana-builder`
- `frontend-graphics-og-image-creator`
- `frontend-graphics-sora`
- `frontend-graphics-threejs-builder`
- `frontend-stitch-react-components`
- `frontend-tools-agentation`
- `frontend-tools-figma`
- `frontend-tools-stitch-loop`
- `frontend-ui-design-system`
- `frontend-ui-frontend-ui-design`
- `frontend-ui-react-ui-patterns`
- `frontend-ui-remotion`
- `frontend-ui-shadcn-ui`
- `frontend-ui-stitch-remotion`
- `frontend-ui-ui-ux-creative-coding`
- `frontend-ui-ui-visual-regression`
- `github-gh-fix-ci`
- `github-gh-workflow`
- `github-greptile-check-pr`
- `github-greptile-greploop`
- `interview-architecture-interview`
- `interview-deep-interview`
- `interview-interview-me`
- `product-content-video-transcript-downloader`
- `product-content-youtube-hooks-scripts`
- `product-content-youtube-titles-thumbnails`
- `product-docs-agents-md`
- `product-docs-context7`
- `product-docs-docs-expert`
- `product-domain-cloudflare-deploy`
- `product-domain-oak-api`
- `product-ops-decide-build-primitive`
- `product-ops-linear`
- `product-ops-release`
- `product-security-security-best-practices`
- `product-security-security-ownership-map`
- `product-security-security-threat-model`
- `product-specs-product-spec`
- `product-strategy-brainstorming`
- `utilities-1password`
- `utilities-agent-browser`
- `utilities-alignment-checkpoint`
- `utilities-atlas`
- `utilities-beautiful-mermaid`
- `utilities-bootstrap`
- `utilities-codex-agent-creator`
- `utilities-codex-automation-architect`
- `utilities-codex-home-audit`
- `utilities-codex-sessions-skill-scan`
- `utilities-fix-mise`
- `utilities-insight-report`
- `utilities-markdown-converter`
- `utilities-notebooklm`
- `utilities-process-watch`
- `utilities-recon-workbench`
- `utilities-repoprompt`
- `utilities-skill-builder`
- `utilities-systematic-debugging`
- `utilities-test-driven-development`
- `utilities-using-git-worktrees`
- `utilities-verification-before-completion`
- `utilities-visual-explainer`
- `utilities-writing-plans`

## Window summary

- Window: `2026-03-21..2026-03-27`
- Runs total: `720`
- Runs by profile:
  - `auth-best-practices`: `10`
  - `auth-create-auth`: `10`
  - `backend-backend-engineer`: `10`
  - `backend-cli-spec`: `10`
  - `backend-mcp-builder`: `10`
  - `backend-workers-mcp`: `10`
  - `frontend-graphics-better-icons`: `10`
  - `frontend-graphics-favicon-generator`: `10`
  - `frontend-graphics-imagegen`: `10`
  - `frontend-graphics-nano-banana-builder`: `10`
  - `frontend-graphics-og-image-creator`: `10`
  - `frontend-graphics-sora`: `10`
  - `frontend-graphics-threejs-builder`: `10`
  - `frontend-stitch-react-components`: `10`
  - `frontend-tools-agentation`: `10`
  - `frontend-tools-figma`: `10`
  - `frontend-tools-stitch-loop`: `10`
  - `frontend-ui-design-system`: `10`
  - `frontend-ui-frontend-ui-design`: `10`
  - `frontend-ui-react-ui-patterns`: `10`
  - `frontend-ui-remotion`: `10`
  - `frontend-ui-shadcn-ui`: `10`
  - `frontend-ui-stitch-remotion`: `10`
  - `frontend-ui-ui-ux-creative-coding`: `10`
  - `frontend-ui-ui-visual-regression`: `10`
  - `github-gh-fix-ci`: `10`
  - `github-gh-workflow`: `10`
  - `github-greptile-check-pr`: `10`
  - `github-greptile-greploop`: `10`
  - `interview-architecture-interview`: `10`
  - `interview-deep-interview`: `10`
  - `interview-interview-me`: `10`
  - `product-content-video-transcript-downloader`: `10`
  - `product-content-youtube-hooks-scripts`: `10`
  - `product-content-youtube-titles-thumbnails`: `10`
  - `product-docs-agents-md`: `10`
  - `product-docs-context7`: `10`
  - `product-docs-docs-expert`: `10`
  - `product-domain-cloudflare-deploy`: `10`
  - `product-domain-oak-api`: `10`
  - `product-ops-decide-build-primitive`: `10`
  - `product-ops-linear`: `10`
  - `product-ops-release`: `10`
  - `product-security-security-best-practices`: `10`
  - `product-security-security-ownership-map`: `10`
  - `product-security-security-threat-model`: `10`
  - `product-specs-product-spec`: `10`
  - `product-strategy-brainstorming`: `10`
  - `utilities-1password`: `10`
  - `utilities-agent-browser`: `10`
  - `utilities-alignment-checkpoint`: `10`
  - `utilities-atlas`: `10`
  - `utilities-beautiful-mermaid`: `10`
  - `utilities-bootstrap`: `10`
  - `utilities-codex-agent-creator`: `10`
  - `utilities-codex-automation-architect`: `10`
  - `utilities-codex-home-audit`: `10`
  - `utilities-codex-sessions-skill-scan`: `10`
  - `utilities-fix-mise`: `10`
  - `utilities-insight-report`: `10`
  - `utilities-markdown-converter`: `10`
  - `utilities-notebooklm`: `10`
  - `utilities-process-watch`: `10`
  - `utilities-recon-workbench`: `10`
  - `utilities-repoprompt`: `10`
  - `utilities-skill-builder`: `10`
  - `utilities-systematic-debugging`: `10`
  - `utilities-test-driven-development`: `10`
  - `utilities-using-git-worktrees`: `10`
  - `utilities-verification-before-completion`: `10`
  - `utilities-visual-explainer`: `10`
  - `utilities-writing-plans`: `10`

### KPI snapshot

- Repeat failure pattern rate: `13.9%` (delta vs baseline: `n/a`)
- First-pass acceptance: `0.0%` (delta vs baseline: `n/a`)
- Iterations median / p90: `2.00` / `3.00`
- Quality uplift median: `0.120`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `100.0%`
- Budget compliance: `98.6%`
- Evaluator flip rate: `18.7%`
- Capture coverage: `100.0%` (`720/720` runs with capture artifacts)
- Confidence bucket distribution: `high=620` `medium=100` `low=0` `unknown=0`
- Injection usage rate: `0.0%` (`0/720` runs, total lessons `0`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=0` `observe_only=720` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=720/720` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260327T172547010324Z_2733b5_89c6da25 | utilities-visual-explainer | passed | pass | 2 | +0.120 | ✅ | 177 |
| run_20260327T172547310778Z_155995_89cb9c94 | utilities-writing-plans | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 55 |
| run_20260327T172546102340Z_79cfc8_89bbaa7c | utilities-test-driven-development | passed | pass | 3 | +0.190 | ✅ | 358 |
| run_20260327T172546403113Z_0931d0_89bc4ba0 | utilities-using-git-worktrees | passed | pass | 3 | +0.190 | ✅ | 326 |
| run_20260327T172546701865Z_f1ccf7_89c08815 | utilities-verification-before-completion | passed | pass | 2 | +0.120 | ✅ | 179 |
| run_20260327T172544908461Z_d54e6b_89b761ee | utilities-recon-workbench | passed | pass | 2 | +0.120 | ✅ | 165 |
| run_20260327T172545205065Z_79d94e_89b8f154 | utilities-repoprompt | passed | pass | 2 | +0.120 | ✅ | 153 |
| run_20260327T172545512671Z_624a34_89b91873 | utilities-skill-builder | passed | pass | 2 | +0.120 | ✅ | 165 |
| run_20260327T172545810028Z_165520_89baa71b | utilities-systematic-debugging | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 54 |
| run_20260327T172544018721Z_5cd9ba_89b3f715 | utilities-markdown-converter | passed | pass | 3 | +0.190 | ✅ | 325 |
| run_20260327T172544318313Z_f9ca05_89b403fd | utilities-notebooklm | passed | pass | 3 | +0.186 | ✅ | 324 |
| run_20260327T172544615765Z_eddfeb_89b63c35 | utilities-process-watch | passed | pass | 2 | +0.120 | ✅ | 163 |
| run_20260327T172543126527Z_03dd77_89af1fc3 | utilities-codex-sessions-skill-scan | passed | pass | 3 | +0.190 | ✅ | 333 |
| run_20260327T172543419812Z_78911e_89b0edbc | utilities-fix-mise | passed | pass | 3 | +0.190 | ✅ | 324 |
| run_20260327T172543723377Z_241369_89b19ccd | utilities-insight-report | passed | pass | 2 | +0.120 | ✅ | 163 |
| run_20260327T172541933616Z_4888ba_89ab1d2e | utilities-bootstrap | passed | pass | 3 | +0.190 | ✅ | 326 |
| run_20260327T172542239774Z_8d6129_89ac4d18 | utilities-codex-agent-creator | passed | pass | 3 | +0.190 | ✅ | 326 |
| run_20260327T172542532705Z_465545_89ad5b4f | utilities-codex-automation-architect | passed | pass | 3 | +0.190 | ✅ | 354 |
| run_20260327T172542835619Z_cc3cf2_89aea290 | utilities-codex-home-audit | passed | pass | 2 | +0.120 | ✅ | 175 |
| run_20260327T172541010457Z_2f9e66_89a825b8 | utilities-alignment-checkpoint | passed | pass | 3 | +0.190 | ✅ | 328 |
| run_20260327T172541321200Z_d47302_89a97ba7 | utilities-atlas | passed | pass | 3 | +0.190 | ✅ | 303 |
| run_20260327T172541626558Z_f51e38_89aa4325 | utilities-beautiful-mermaid | passed | pass | 3 | +0.190 | ✅ | 339 |
| run_20260327T172540095955Z_82d107_89a55513 | product-strategy-brainstorming | passed | pass | 2 | +0.120 | ✅ | 172 |
| run_20260327T172540394245Z_871a4c_89a62795 | utilities-1password | passed | pass | 3 | +0.190 | ✅ | 327 |
| run_20260327T172540706287Z_d08cac_89a74b30 | utilities-agent-browser | passed | pass | 3 | +0.190 | ✅ | 332 |
| run_20260327T172539208485Z_0d793b_89a28dca | product-security-security-ownership-map | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 63 |
| run_20260327T172539510349Z_b1ba18_89a3036f | product-security-security-threat-model | passed | pass | 2 | +0.120 | ✅ | 171 |
| run_20260327T172539803352Z_27b5c1_89a48a24 | product-specs-product-spec | passed | pass | 3 | +0.190 | ✅ | 348 |
| run_20260327T172537964396Z_94ca45_899d21e0 | product-ops-decide-build-primitive | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 59 |
| run_20260327T172538263722Z_acf147_899eaf84 | product-ops-linear | passed | pass | 2 | +0.120 | ✅ | 167 |
| run_20260327T172538566226Z_affe4a_899f063a | product-ops-release | passed | pass | 3 | +0.190 | ✅ | 327 |
| run_20260327T172538875593Z_78f4a2_89a1daf2 | product-security-security-best-practices | passed | pass | 3 | +0.190 | ✅ | 354 |
| run_20260327T172537079859Z_c575f4_89989390 | product-docs-docs-expert | passed | pass | 3 | +0.190 | ✅ | 333 |
| run_20260327T172537368728Z_f13e6a_899a3009 | product-domain-cloudflare-deploy | passed | pass | 2 | +0.120 | ✅ | 171 |
| run_20260327T172537666400Z_16a7dd_899c1017 | product-domain-oak-api | passed | pass | 2 | +0.120 | ✅ | 161 |
| run_20260327T172535902068Z_746092_89940d89 | product-content-youtube-hooks-scripts | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 60 |
| run_20260327T172536200757Z_e9f2af_89954c62 | product-content-youtube-titles-thumbnails | passed | pass | 3 | +0.190 | ✅ | 342 |
| run_20260327T172536492158Z_0e961d_899631a4 | product-docs-agents-md | passed | pass | 3 | +0.190 | ✅ | 330 |
| run_20260327T172536791228Z_48558f_899791e3 | product-docs-context7 | passed | pass | 2 | +0.120 | ✅ | 154 |
| run_20260327T172535018324Z_933bc1_8991eaba | interview-deep-interview | passed | pass | 3 | +0.190 | ✅ | 318 |

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
