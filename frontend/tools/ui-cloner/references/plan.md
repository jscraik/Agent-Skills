# Plan for UI Cloner

## Goal
Create a standalone UI replication skill that keeps `cf-crawl` focused on crawl orchestration while allowing an explicit handoff for URL manifest + markdown corpus generation.

## Execution steps
1. Scaffold `frontend/tools/ui-cloner` with Codex-targeted instruction templates.
2. Replace placeholders in `SKILL.md` with routing boundaries, output artifacts, safety constraints, and workflow.
3. Add explicit upstream handoff rule: use `cf-crawl` first for large or unclear site structures.
4. Define contract and eval fixtures for trigger coverage and negative controls.
5. Configure `agents/openai.yaml` interface metadata.
6. Run skill validators and repo-level checks.

## Done criteria
- `SKILL.md` has no template placeholders.
- `references/contract.yaml` and `references/evals.yaml` are aligned with skill behavior.
- Core skill-builder validators pass.
- Repo checks pass (`sync_skills`, docs lint, `just validate`).
