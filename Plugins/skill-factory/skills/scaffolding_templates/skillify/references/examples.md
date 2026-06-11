# Skillify Examples

Use this reference when the workflow needs a concrete package example instead of only the compact SKILL.md entrypoint.

## Release Triage Skill

User request: "Can you convert our repeated GitHub release triage workflow into a validated skill?"

Expected output:

- Create `SKILL.md` with frontmatter name `release-triage`.
- Write a description that names release-failure trigger phrases.
- Add four workflow steps: check current release status, identify the first broken stage, compare rollback/hotfix/pause options, and report validation evidence.
- Add `references/contract.yaml` with owner `release-engineering`, side effect class `repo-write`, required release/repository inputs, expected blocker and recommendation outputs, and validation command `./bin/ask repo closeout --changed --json --robot`.
- Add `references/evals.yaml` with one CI failure scenario and one missing-evidence scenario that asks for the release identifier instead of inventing state.

Example return:

```yaml
skill_path: Plugins/release/skills/release-triage
first_principles_gate:
  decision: BUILD_SKILL
files_changed:
  - SKILL.md
  - references/contract.yaml
  - references/evals.yaml
validation:
  - command: ./bin/ask skills audit Plugins/release/skills/release-triage --level strict --json --robot
    outcome: pass
```
