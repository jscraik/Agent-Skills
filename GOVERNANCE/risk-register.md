# Governance Risk Register

Last updated: 2026-02-18

| ID | Risk | Likelihood | Impact | Owner | Mitigation | Review cadence | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| R-001 | Governance files drift from required baseline across repos. | Medium | High | Jamie | Monthly governance sweep + gate checks on policy paths. | Monthly | open |
| R-002 | Security evidence is missing in policy-sensitive pull requests. | Medium | High | Jamie | PR template required sections + `gov-security-gates` workflow. | Per PR | open |
| R-003 | Secret leakage or vulnerable dependency updates slip through review. | Low | High | Jamie | Secret scanning + dependency audit checks in CI when available. | Per PR | open |

## Notes

- Add new risks as they are discovered.
- Close risks only after mitigation is implemented and verified.
