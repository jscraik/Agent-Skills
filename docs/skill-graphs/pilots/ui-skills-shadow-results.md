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
- Runs total: `804`
- Runs by profile:
  - `auth-best-practices`: `11`
  - `auth-create-auth`: `11`
  - `backend-backend-engineer`: `11`
  - `backend-cli-spec`: `11`
  - `backend-mcp-builder`: `11`
  - `backend-workers-mcp`: `11`
  - `frontend-graphics-better-icons`: `11`
  - `frontend-graphics-favicon-generator`: `11`
  - `frontend-graphics-imagegen`: `11`
  - `frontend-graphics-nano-banana-builder`: `11`
  - `frontend-graphics-og-image-creator`: `11`
  - `frontend-graphics-sora`: `11`
  - `frontend-graphics-threejs-builder`: `11`
  - `frontend-stitch-react-components`: `11`
  - `frontend-tools-agentation`: `11`
  - `frontend-tools-figma`: `11`
  - `frontend-tools-stitch-loop`: `11`
  - `frontend-ui-design-system`: `11`
  - `frontend-ui-frontend-ui-design`: `11`
  - `frontend-ui-react-ui-patterns`: `11`
  - `frontend-ui-remotion`: `11`
  - `frontend-ui-shadcn-ui`: `11`
  - `frontend-ui-stitch-remotion`: `11`
  - `frontend-ui-ui-ux-creative-coding`: `11`
  - `frontend-ui-ui-visual-regression`: `11`
  - `github-gh-fix-ci`: `11`
  - `github-gh-workflow`: `11`
  - `github-greptile-check-pr`: `11`
  - `github-greptile-greploop`: `11`
  - `interview-architecture-interview`: `11`
  - `interview-deep-interview`: `11`
  - `interview-interview-me`: `11`
  - `product-content-video-transcript-downloader`: `11`
  - `product-content-youtube-hooks-scripts`: `11`
  - `product-content-youtube-titles-thumbnails`: `11`
  - `product-docs-agents-md`: `11`
  - `product-docs-context7`: `11`
  - `product-docs-docs-expert`: `11`
  - `product-domain-cloudflare-deploy`: `11`
  - `product-domain-oak-api`: `11`
  - `product-ops-decide-build-primitive`: `11`
  - `product-ops-linear`: `11`
  - `product-ops-release`: `11`
  - `product-security-security-best-practices`: `11`
  - `product-security-security-ownership-map`: `11`
  - `product-security-security-threat-model`: `11`
  - `product-specs-product-spec`: `11`
  - `product-strategy-brainstorming`: `11`
  - `utilities-1password`: `11`
  - `utilities-agent-browser`: `11`
  - `utilities-alignment-checkpoint`: `11`
  - `utilities-atlas`: `11`
  - `utilities-beautiful-mermaid`: `11`
  - `utilities-bootstrap`: `11`
  - `utilities-codex-agent-creator`: `11`
  - `utilities-codex-automation-architect`: `11`
  - `utilities-codex-home-audit`: `11`
  - `utilities-codex-sessions-skill-scan`: `11`
  - `utilities-fix-mise`: `11`
  - `utilities-insight-report`: `11`
  - `utilities-markdown-converter`: `12`
  - `utilities-notebooklm`: `12`
  - `utilities-process-watch`: `12`
  - `utilities-recon-workbench`: `12`
  - `utilities-repoprompt`: `12`
  - `utilities-skill-builder`: `12`
  - `utilities-systematic-debugging`: `12`
  - `utilities-test-driven-development`: `12`
  - `utilities-using-git-worktrees`: `12`
  - `utilities-verification-before-completion`: `12`
  - `utilities-visual-explainer`: `12`
  - `utilities-writing-plans`: `12`

### KPI snapshot

- Repeat failure pattern rate: `21.6%` (delta vs baseline: `-78.4pp`)
- First-pass acceptance: `27.4%` (delta vs baseline: `+27.4pp`)
- Iterations median / p90: `2.00` / `3.00`
- Quality uplift median: `0.120`; positive uplift rate: `100.0%`
- Critical non-regression compliance: `100.0%`
- Budget compliance: `100.0%`
- Evaluator flip rate: `20.1%`
- Capture coverage: `100.0%` (`804/804` runs with capture artifacts)
- Confidence bucket distribution: `high=630` `medium=174` `low=0` `unknown=0`
- Injection usage rate: `0.0%` (`0/804` runs, total lessons `0`, suppressed-by-controls runs `0`)
- Rollout mode distribution: `active=0` `observe_only=804` `off=0` `other=0`
- Uplift gate decisions (promotion/auto-apply): `pass=0/0` `insufficient_data=804/804` `regressed=0/0`

## Run log

| Run | Profile | Status | Stop reason | Iterations | Uplift | Non-regression | Tokens |
|---|---|---|---|---:|---:|:---:|---:|
| run_20260327T173800952712Z_f1ccf7_952d8815 | utilities-verification-before-completion | escalated | escalated | 1 | +0.050 | ✅ | 61 |
| run_20260327T173801292095Z_2733b5_952eda25 | utilities-visual-explainer | escalated | escalated | 1 | +0.050 | ✅ | 57 |
| run_20260327T173801629908Z_155995_952f9c94 | utilities-writing-plans | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 55 |
| run_20260327T173759816085Z_165520_952aa71b | utilities-systematic-debugging | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 54 |
| run_20260327T173800254010Z_79cfc8_952baa7c | utilities-test-driven-development | escalated | escalated | 1 | +0.050 | ✅ | 61 |
| run_20260327T173800600754Z_0931d0_952c4ba0 | utilities-using-git-worktrees | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173758884265Z_79d94e_9527f154 | utilities-repoprompt | escalated | escalated | 1 | +0.050 | ✅ | 49 |
| run_20260327T173759403804Z_624a34_95281873 | utilities-skill-builder | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173758004300Z_eddfeb_95233c35 | utilities-process-watch | escalated | escalated | 1 | +0.050 | ✅ | 52 |
| run_20260327T173758405144Z_d54e6b_952461ee | utilities-recon-workbench | escalated | escalated | 1 | +0.050 | ✅ | 54 |
| run_20260327T173756830545Z_5cd9ba_951ff715 | utilities-markdown-converter | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173757533564Z_f9ca05_952203fd | utilities-notebooklm | escalated | escalated | 1 | +0.050 | ✅ | 51 |
| run_20260327T173756094311Z_78911e_951dedbc | utilities-fix-mise | escalated | escalated | 1 | +0.050 | ✅ | 51 |
| run_20260327T173756433908Z_241369_951e9ccd | utilities-insight-report | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173754839617Z_465545_951a5b4f | utilities-codex-automation-architect | escalated | escalated | 1 | +0.050 | ✅ | 59 |
| run_20260327T173755376814Z_cc3cf2_951ba290 | utilities-codex-home-audit | escalated | escalated | 1 | +0.050 | ✅ | 57 |
| run_20260327T173755767428Z_03dd77_951c1fc3 | utilities-codex-sessions-skill-scan | escalated | escalated | 1 | +0.050 | ✅ | 56 |
| run_20260327T173754255763Z_8d6129_95174d18 | utilities-codex-agent-creator | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173753062286Z_d47302_95127ba7 | utilities-atlas | escalated | escalated | 1 | +0.050 | ✅ | 46 |
| run_20260327T173753413592Z_f51e38_95134325 | utilities-beautiful-mermaid | escalated | escalated | 1 | +0.050 | ✅ | 54 |
| run_20260327T173753789754Z_4888ba_95141d2e | utilities-bootstrap | escalated | escalated | 1 | +0.050 | ✅ | 51 |
| run_20260327T173752058401Z_871a4c_950e2795 | utilities-1password | escalated | escalated | 1 | +0.050 | ✅ | 51 |
| run_20260327T173752386381Z_d08cac_950f4b30 | utilities-agent-browser | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173752728731Z_2f9e66_951125b8 | utilities-alignment-checkpoint | escalated | escalated | 1 | +0.050 | ✅ | 54 |
| run_20260327T173751060095Z_b1ba18_950b036f | product-security-security-threat-model | escalated | escalated | 1 | +0.050 | ✅ | 58 |
| run_20260327T173751386354Z_27b5c1_950c8a24 | product-specs-product-spec | escalated | escalated | 1 | +0.050 | ✅ | 57 |
| run_20260327T173751721034Z_82d107_950d5513 | product-strategy-brainstorming | escalated | escalated | 1 | +0.050 | ✅ | 57 |
| run_20260327T173750064181Z_affe4a_9507063a | product-ops-release | escalated | escalated | 1 | +0.050 | ✅ | 50 |
| run_20260327T173750408511Z_78f4a2_9508daf2 | product-security-security-best-practices | escalated | escalated | 1 | +0.050 | ✅ | 61 |
| run_20260327T173750723088Z_0d793b_950a8dca | product-security-security-ownership-map | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 63 |
| run_20260327T173749042292Z_16a7dd_95031017 | product-domain-oak-api | escalated | escalated | 1 | +0.050 | ✅ | 52 |
| run_20260327T173749378931Z_94ca45_950421e0 | product-ops-decide-build-primitive | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 59 |
| run_20260327T173749723896Z_acf147_9506af84 | product-ops-linear | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173748060318Z_48558f_94ff91e3 | product-docs-context7 | escalated | escalated | 1 | +0.050 | ✅ | 49 |
| run_20260327T173748380571Z_c575f4_95009390 | product-docs-docs-expert | escalated | escalated | 1 | +0.050 | ✅ | 54 |
| run_20260327T173748713556Z_f13e6a_95013009 | product-domain-cloudflare-deploy | escalated | escalated | 1 | +0.050 | ✅ | 57 |
| run_20260327T173747096582Z_746092_94fa0d89 | product-content-youtube-hooks-scripts | escalated | evaluator_conflict | 1 | +0.050 | ✅ | 60 |
| run_20260327T173747417480Z_e9f2af_94fc4c62 | product-content-youtube-titles-thumbnails | escalated | escalated | 1 | +0.050 | ✅ | 59 |
| run_20260327T173747740250Z_0e961d_94fd31a4 | product-docs-agents-md | escalated | escalated | 1 | +0.050 | ✅ | 53 |
| run_20260327T173746076847Z_933bc1_94f7eaba | interview-deep-interview | escalated | escalated | 1 | +0.050 | ✅ | 51 |

## Exit gate checks

- Scoring variance + evaluator consistency observed in this window.
- Failure taxonomy and stop reasons captured per run.
- Governance/security controls remain required before promotions.

Related:
- [UI skills pilot readout](/docs/skill-graphs/pilots/ui-skills-pilot-readout.md)
