# Threat Model (Repository Controls)

## Assets

- Default branch integrity and PR merge quality
- Secret/config content in repository history
- Workflow definitions and template files
- Release artifacts and audit records

## Attack surfaces

- PR body can omit required evidence to hide risks.
- Dependency manifest changes with unreviewed vulnerabilities.
- Secret leakage through commits/PR descriptions.
- Workflow script drift to weaken checks.

## Abuse cases

1. **Evidence bypass:** contributor submits low-content PR with placeholders.
2. **Dependency drift:** updates dependency files without vulnerability checks.
3. **Workflow tampering:** changes gate script/workflow to report success incorrectly.
4. **Secret commit:** credentials committed in changed files.

## Controls

- PR evidence checklist gates for governance/security-relevant edits.
- Optional scanner steps in `.github/scripts/gov_security_gates.py`.
- `CODEOWNERS` and branch policy manifest for policy-path protection.
- Exception/incidents records for bypasses.

## Severity response

- High/severe issues must be documented immediately in `GOVERNANCE/exceptions.md` and `GOVERNANCE/incidents.md`.
