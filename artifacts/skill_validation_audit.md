# Skill Audit Report

Generated: /Users/jamiecraik/dev/agent-skills/artifacts/skill_validation_report.json

| Metric | Count |
|---|---:|
| Total skills scanned | 117 |
| Fully passing (all 3 checks) | 33 |
| Any check failed | 84 |
| quick_validate failures | 74 |
| skill_gate failures | 29 |
| openclaw failures | 1 |

## Failure summary

| Skill | quick_validate | skill_gate | openclaw | primary_issue |
|---|---|---|---|---|
| `.` | FAIL | FAIL | FAIL | [FAIL] Missing YAML frontmatter. Expected `---` as the first non-empty line. |
| `.agents/skills/draftpr` | PASS | FAIL | PASS | [WARN] Description may be too vague; consider including explicit trigger language (e.g., 'Use when ...'). |
| `auth/best-practices` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `auth/create-auth` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `backend/backend-engineer` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `backend/cli-spec` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `backend/mcp-builder` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `backend/mkit-builder` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `backend/workers-mcp` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `design/better-icons` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/graphics/favicon-generator` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/graphics/imagegen` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `frontend/graphics/og-image-creator` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/graphics/threejs-builder` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/seo/seo-optimizer` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/tools/codex-ui-kit-installer` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/tools/nano-banana-builder` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/ui/frontend-ui-design` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/ui/interface-craft` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: argument-hint. Allowed: description, name |
| `frontend/ui/react-best-practices` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: license, metadata. Allowed: description, name |
| `frontend/ui/react-ui-patterns` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/ui/ui-visual-regression` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `frontend/ui/web-design-guidelines` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `github/gh-fix-ci` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `interview/architecture-interview` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `interview/bug-interview` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `interview/deep-interview` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `interview/interview-kernel` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `interview/interview-me` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `interview/pm-interview` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `personas/steipete` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/content/youtube-hooks-scripts` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/content/youtube-titles-thumbnails` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/design/ui-ux-creative-coding` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/docs/agents-md` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/docs/context7` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/docs/docs-expert` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/docs/openai-docs` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `product/domain/cloudflare-deploy` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `product/domain/oak-api` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/ops/decide-build-primitive` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/ops/linear` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/ops/release` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/review/codex-wrapped` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/review/llm-design-review` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/review/product-design-review` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/security/security-best-practices` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `product/security/security-ownership-map` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `product/security/security-threat-model` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `product/specs/_archive/prd-to-accessibility` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/prd-to-api-lite` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/prd-to-arch-lite` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/prd-to-qa-cases` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/prd-to-risk` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/prd-to-roadmap` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/prd-to-security-review` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/prd-to-ui-spec` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/ui-spec-to-prompts` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/_archive/ux-spec-to-prompts` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/specs/product-spec` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/strategy/project-improvement-ideator` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `product/tech/tech-spec` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `skills-system/skill-installer` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `skills/.system/skill-creator` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `skills/.system/skill-installer` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/1password` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/agent-browser` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/atlas` | PASS | FAIL | PASS | [OK] SKILL.md frontmatter looks valid. |
| `utilities/beautiful-mermaid` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/markdown-converter` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/process-watch` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/dependency_doctor` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/interrogate` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/ios_sim_interrogate` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/macos_app_triage` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/oss_repo_map` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/report_compiler` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/web_app_interrogate` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/recon-workbench/assets/template/.codex/skills/worst_case_interrogation` | FAIL | FAIL | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/remotion` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/repoprompt` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/skill-installer` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
| `utilities/systematic-debugging` | PASS | FAIL | PASS | [WARN] Description may be too vague; consider including explicit trigger language (e.g., 'Use when ...'). |
| `utilities/video-transcript-downloader` | FAIL | PASS | PASS | [FAIL] Unknown frontmatter key(s) in strict mode: metadata. Allowed: description, name |
