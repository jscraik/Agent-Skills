## Frontmatter Trigger Sweep

Date: 2026-03-23
Mode: improve
Scope: canonical skill files only; excluded generated projections under `skills-antigravity/` and plugin copies under `Plugins/`

### Goal

Tighten `description` frontmatter across the skill graph so agents are more likely to select the correct skill and less likely to mis-trigger on neighboring skills.

### Audit Heuristics

- descriptions that started with vague `Use when...` phrasing without a leading owner noun/verb
- descriptions that still used placeholder language like `when the user requests this capability`
- multiline or wrapped descriptions whose primary trigger surface was buried
- overlap-heavy pairs whose exclusions were still too soft

### Updated Areas

- auth owners: `best-practices`, `create-auth`
- interview owners: `architecture-interview`, `deep-interview`, `interview-me`
- docs and reference owners: `context7`, `docs-expert`, `agents-md`, `openai-docs`
- GitHub and Greptile owners: `gh-fix-ci`, `check-pr`, `greploop`, `resolve-pr-parallel`
- CE stage owners: `ce-brainstorm`, `ce-deepen-plan`, `ce-deepen-spec`, `ce-ideate`, `ce-plan`, `ce-review`, `ce-spec`, `ce-technical-review`, `ce-compound-refresh`, `compound-engineering-router`
- UI/design owners: `frontend-design`, `frontend-ui-design`, `baseline-ui`, `design-system`, `ui-visual-regression`, `ui-ux-creative-coding`, `ui-cloner`, `react-components`
- media/content owners: `video-transcript-downloader`, `youtube-hooks-scripts`, `youtube-titles-thumbnails`, `every-style-editor`, `imagegen`, `sora`, `slides`, `spreadsheet`, `visual-explainer`
- Codex/meta owners: `skill-builder`, `skill-creator`, `codex-agent-builder`, `codex-hooks-builder`, `codex-plugin-builder`, `codex-home-audit`, `codex-automation-architect`, `codex-sessions-skill-scan`, `orchestrating-subagents`
- infra/utility owners: `rclone`, `cf-crawl`, `fix-mise`, `diagram-cli`, `repoprompt`, `simple-tasks`, `writing-plans`, `notebooklm`, `atlas`

### Result

- The sweep removed the most common weak patterns:
  - placeholder trigger language
  - buried primary owner/action
  - insufficient exclusion boundaries in overlap-heavy families
- The re-audit left one deliberate heuristic flag:
  - `product/Infrastructure/ops/ce-plan/SKILL.md` remains slightly long because it intentionally owns both compound-engineering planning and the generic planning wrapper path

### Remaining Judgment Calls

- `ce-plan` is intentionally broader than most skills because the repo now routes generic planning through it.
- If a future pass wants even tighter routing, the next best candidates are example-driven eval additions rather than further shortening the frontmatter.
