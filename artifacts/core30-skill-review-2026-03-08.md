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
- `utilities/codex-automation-architect`
- `utilities/executing-plans`
- `utilities/recent-code-bugfix`
- `utilities/run-tests-and-write-artifacts`
- `utilities/skill-builder`
- `utilities/systematic-debugging`
- `utilities/test-driven-development`
- `utilities/using-git-worktrees`
- `utilities/verification-before-completion`
- `utilities/visual-explainer`
- `utilities/writing-plans`

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
| `product/docs/claude-md` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/docs/context7` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/docs/docs-expert` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/docs/docs-md` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `product/docs/gemini-md` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
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
| `product/ops/compound-engineering-router` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/ops/decide-build-primitive` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/ops/linear` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `product/ops/release` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
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
| `skills-antigravity-test/ui-ux-creative-coding` | `retire` | Test-copy skill path; duplicate of canonical production skill. |
| `utilities/1password` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/agent-browser` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/alignment-checkpoint` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/apple-app-creator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/atlas` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/beautiful-mermaid` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/bootstrap` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/codex-agent-creator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/codex-automation-architect` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/codex-home-audit` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/codex-prompt-creator` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/codex-sessions-skill-scan` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/diagram-cli` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/diagram-context-refresh` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/executing-plans` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/fix-mise` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/insight-report` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/markdown-converter` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/notebooklm` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/process-watch` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/recent-code-bugfix` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/recon-workbench` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/repoprompt` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/run-tests-and-write-artifacts` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/simple-tasks` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/skill-builder` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/skill-installer` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
| `utilities/systematic-debugging` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/test-driven-development` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/using-git-worktrees` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/verification-before-completion` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/visual-explainer` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/writing-plans` | `keep-core-30` | High-frequency, broad utility, and strong leverage across common workflows. |
| `utilities/xcode-makefiles` | `merge` | Consolidate into nearest core workflow to reduce routing overlap. |
