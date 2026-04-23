# Core 30 Skill Rationalization (2026-03-08)

- Canonical skills reviewed: **144**
- Keep core: **30**
- Merge: **94**
- Retire: **20**

## Core 30
- `backend/backend-engineer`
- `frontend/ui/design-system`
- `frontend/ui/frontend-ui-design`
- `frontend/ui/react-ui-patterns`
- `frontend/website/fixing-accessibility`
- `github/gh-fix-ci`
- `github/gh-workflow`
- `github/greptile/check-pr`
- `github/greptile/greploop`
- `interview/deep-interview`
- `interview/interview-me`
- `interview/pm-interview`
- `product/docs/agents-md`
- `product/docs/context7`
- `product/docs/docs-expert`
- `product/docs/docs-md`
- `product/docs/openai-docs`
- `product/security/security-best-practices`
- `product/specs/product-spec`
- `Skills/codex-automation-architect`
- `Skills/executing-plans`
- `Skills/recent-code-bugfix`
- `Skills/run-tests-and-write-artifacts`
- `Skills/skill-builder`
- `Skills/systematic-debugging`
- `Skills/test-driven-development`
- `Skills/using-git-worktrees`
- `Skills/verification-before-completion`
- `Skills/visual-explainer`
- `Skills/writing-plans`

## Full Decision Matrix
| scope_skill | decision | reason |
|---|---|---|
| `auth/best-practices` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `auth/create-auth` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `backend/backend-engineer` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `backend/cli-spec` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `backend/mcp-builder` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `backend/mkit-builder` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `backend/workers-mcp` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/graphics/better-icons` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/graphics/favicon-generator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/graphics/imagegen` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/graphics/nano-banana-builder` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/graphics/og-image-creator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/graphics/sora` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/graphics/threejs-builder` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/stitch-design-md` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/stitch-enhance-prompt` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/stitch-react-components` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/tools/agent-trace-debug` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/tools/agentation` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/tools/figma` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/tools/stitch-design-md` | `retire` | Duplicate or near-duplicate naming with canonical Stitch skill paths. |
| `frontend/tools/stitch-loop` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/baseline-ui` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/design-system` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `frontend/ui/fixing-motion-performance` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/frontend-ui-design` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `frontend/ui/interface-craft` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/react-best-practices` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/react-ui-patterns` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `frontend/ui/remotion` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/shadcn-ui` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/stitch-react-components` | `retire` | Duplicate or near-duplicate naming with canonical Stitch skill paths. |
| `frontend/ui/stitch-remotion` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/ui-ux-creative-coding` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/ui-visual-regression` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/ui/web-design-guidelines` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `frontend/website/fixing-accessibility` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `frontend/website/fixing-metadata` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `github/automate-github-issues` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `github/gh-fix-ci` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `github/gh-workflow` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `github/greptile/check-pr` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `github/greptile/greploop` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `github/local-action-verification` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `interview/architecture-interview` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `interview/bug-interview` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `interview/deep-interview` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `interview/interview-kernel` | `retire` | Internal engine skill; not intended for direct invocation. |
| `interview/interview-me` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `interview/pm-interview` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `personas/benjitaylor-persona` | `retire` | Persona-style variants are optional tone overlays; low core workflow value. |
| `personas/emilkowalski-persona` | `retire` | Persona-style variants are optional tone overlays; low core workflow value. |
| `personas/jenny-wen-persona` | `retire` | Persona-style variants are optional tone overlays; low core workflow value. |
| `personas/jh3yy-persona` | `retire` | Persona-style variants are optional tone overlays; low core workflow value. |
| `personas/kubadesign-persona` | `retire` | Persona-style variants are optional tone overlays; low core workflow value. |
| `personas/steipete-persona` | `retire` | Persona-style variants are optional tone overlays; low core workflow value. |
| `product/content/video-transcript-downloader` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/content/youtube-hooks-scripts` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/content/youtube-titles-thumbnails` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/docs/agents-md` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/docs/codex-md` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/docs/context7` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/docs/docs-expert` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/docs/docs-md` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/docs/openai-md` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/docs/openai-docs` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/domain/arscontexta` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/domain/arscontexta/skill-sources/graph` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/learn` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/next` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/pipeline` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/ralph` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/reduce` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/refactor` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/reflect` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/remember` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/rethink` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/reweave` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/seed` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/stats` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/tasks` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/validate` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skill-sources/verify` | `merge` | Consider collapsing micro-commands into fewer operator-facing entry skills. |
| `product/domain/arscontexta/skills/help` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/domain/chatgpt-apps` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/domain/chatgpt-apps-production-checklist` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/domain/cloudflare-deploy` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/domain/oak-api` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/Infrastructure/ops/compound-engineering-router` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/Infrastructure/ops/decide-build-primitive` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/Infrastructure/ops/linear` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/Infrastructure/ops/release` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/security/security-best-practices` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/security/security-ownership-map` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/security/security-threat-model` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/specs/_archive/prd-to-accessibility` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/prd-to-api-lite` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/prd-to-arch-lite` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/prd-to-qa-cases` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/prd-to-risk` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/prd-to-roadmap` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/prd-to-security-review` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/prd-to-ui-spec` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/ui-spec-to-prompts` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/_archive/ux-spec-to-prompts` | `retire` | Archived spec transformers; superseded by product-spec plus interviews. |
| `product/specs/product-spec` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/strategy/asymmetric-ideation-engine` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/strategy/brainstorming` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/strategy/project-improvement-ideator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `skills-codex-test/ui-ux-creative-coding` | `retire` | Test-copy skill path; duplicate of canonical production skill. |
| `Skills/1password` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/agent-browser` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/alignment-checkpoint` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/apple-app-creator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/atlas` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/beautiful-mermaid` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/bootstrap` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/codex-agent-creator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/codex-automation-architect` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/codex-home-audit` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/codex-prompt-creator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/codex-sessions-skill-scan` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/diagram-cli` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/diagram-context-refresh` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/executing-plans` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/fix-mise` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/insight-report` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/markdown-converter` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/notebooklm` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/process-watch` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/recent-code-bugfix` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/recon-workbench` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/repoprompt` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/run-tests-and-write-artifacts` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/simple-tasks` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/skill-builder` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/skill-installer` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `Skills/systematic-debugging` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/test-driven-development` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/using-git-worktrees` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/verification-before-completion` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/visual-explainer` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/writing-plans` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `Skills/xcode-makefiles` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
