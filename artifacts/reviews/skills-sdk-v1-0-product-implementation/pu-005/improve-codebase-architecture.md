# PU-005 Improve Codebase Architecture Review

Status: pass

Scope reviewed:
- Skills SDK facade routing
- Install preview builder boundary
- Lockfile preview model
- Tests and goal-board updates

Findings:
- None requiring changes.

Assessment:
The change preserves ./bin/ask as the control plane: bin/skills-sdk still delegates to ask sdk, and the new install preview route lives under the existing ask.commands.sdk facade. Product logic is isolated in ask.skills_sdk.install_preview, which keeps the large skills_impl.py module from owning lockfile modeling details. Non-preview install attempts fail closed, so there is no accidental path from product CLI naming to real install writes.

Tradeoff:
The preview builder duplicates a small amount of path modeling rather than sharing it with the existing GitHub install command. That is deliberate because PU-005 must not inherit the real installer write path.
