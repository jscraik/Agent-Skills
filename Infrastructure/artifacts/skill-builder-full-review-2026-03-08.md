# Skill Builder Full Review (2026-03-08)

- Skills reviewed: **106**
- `quick_validate`: nonzero_exit=8, warns=0, fails=0
- `skill_gate`: nonzero_exit=27, warns=1619, fails=193
- `analyze_skill`: nonzero_exit=5, warns=0, fails=13
- `openclaw_guard`: nonzero_exit=0, warns=51, fails=0

## Blocking Skills
- `product/domain/arscontexta/skill-sources/graph` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/learn` -> `skill_gate`, `analyze_skill`
- `product/domain/arscontexta/skill-sources/next` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/pipeline` -> `skill_gate`, `analyze_skill`
- `product/domain/arscontexta/skill-sources/ralph` -> `skill_gate`, `analyze_skill`
- `product/domain/arscontexta/skill-sources/reduce` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/refactor` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/reflect` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/remember` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/rethink` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/reweave` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/seed` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/stats` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/tasks` -> `skill_gate`, `analyze_skill`
- `product/domain/arscontexta/skill-sources/validate` -> `skill_gate`
- `product/domain/arscontexta/skill-sources/verify` -> `skill_gate`
- `product/domain/arscontexta/skills/help` -> `quick_validate`, `skill_gate`
- `Skills/insight-report` -> `skill_gate`, `analyze_skill`
- `Skills/notebooklm` -> `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/dependency_doctor` -> `quick_validate`, `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/interrogate` -> `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/ios_sim_interrogate` -> `quick_validate`, `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/macos_app_triage` -> `quick_validate`, `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/oss_repo_map` -> `quick_validate`, `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/report_compiler` -> `quick_validate`, `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/web_app_interrogate` -> `quick_validate`, `skill_gate`
- `Skills/recon-workbench/assets/template/.codex/skills/worst_case_interrogation` -> `quick_validate`, `skill_gate`

## Top Skill Gate Warning Signatures
- `WARN REPO_ASSETS_UNREFERENCED`: 32
- `WARN PI_TOOL_CHAIN`: 30
- `WARN SEC_EVALS_COMMAND_GUARD_MISSING`: 28
- `WARN OUT_SCHEMA_VERSION_MISSING`: 24
- `WARN PI_COMMANDS`: 24
- `WARN REPO_REFERENCES_UNREFERENCED`: 20
- `WARN SEC_EXAMPLES_MISSING`: 20
- `WARN PI_OBFUSCATION`: 19
- `WARN PATH_ABSOLUTE`: 14
- `WARN PI_OVERRIDE`: 13
- `WARN FM_DESC_WORKFLOWY`: 10
- `WARN SEC_EVALS_NEGATIVE_MISSING`: 9
- `WARN PI_BINARY_ATTACHMENT`: 7
- `WARN FM_NAME_STYLE`: 7
- `WARN SAFE_NETWORK_ALLOWLIST`: 3
