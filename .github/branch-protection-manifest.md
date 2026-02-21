# Branch protection baseline (operational target)

## Target branch

- `main`

## Baseline checks expected for protected branches

| Control | Setting | Target |
| --- | --- | --- |
| Review | Required reviewers | 1 approving review by repository owner (`@jscraik`) |
| Review | Code owner approval | Required for policy/security files |
| Merge | Commit style | Linear history only |
| Merge | Direct pushes | Block force pushes |
| Merge | Branch state | Conversation resolution required |
| Merge | Checks | All required status checks must pass |
| Security | Status checks | Governance/security workflow + existing repo checks |

## Required status checks (minimum)

- `gov-security-gates`
- Existing project checks (repo-specific CI / docs lint / build)

## Sensitive path protection recommendation

Apply code-owner review and stricter review expectations for:

- `.github/PULL_REQUEST_TEMPLATE.md`
- `.github/workflows/**`
- `.github/scripts/gov_security_gates.py`
- `.github/CODEOWNERS`
- `GOVERNANCE/**`
- `COMPLIANCE/**`
- `SECURITY/**`
- `EVALUATION/**`
- `.github/branch-protection-manifest.md`

## Evidence and cadence

- Update and sign-off this manifest monthly.
- Record policy changes by updating `GOVERNANCE/incidents.md` when guardrail drift is detected.
- Record intentional bypasses in `GOVERNANCE/exceptions.md` and close them with date + approver.
