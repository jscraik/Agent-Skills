# PU-003 Simplify Review

Status: pass after one simplification fix

Scope reviewed:
- Infrastructure/bin/ask
- Infrastructure/scripts/lib/ask/command_metadata.py
- Infrastructure/scripts/lib/ask/commands/skills.py
- Infrastructure/scripts/lib/ask/commands/skills_impl.py
- Infrastructure/tests/test_skills_sdk_check_facade.py
- bin/skills-sdk

Findings:
- Fixed before closeout: skills_sdk_check originally passed --json --robot into _ask_validation_command, which already appends those flags. The replay command now calls _ask_validation_command("sdk", "check", target) and avoids duplicate flags.

Residual risk:
- The facade intentionally reuses skills_doctor instead of introducing a new check engine. This is simpler and keeps ./bin/ask authoritative.

