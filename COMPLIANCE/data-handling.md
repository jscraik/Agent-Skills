# Data Handling Policy (Governance Baseline)

## Scope

Describe what data the repository workflows and tooling process.

- Repo code and docs.
- PR metadata required for governance evidence.
- Optional AI session traces/logs used as part of workflow output, where applicable.

## Data collection and retention

- Prefer no runtime user data collection in repository tooling.
- Do not commit secrets or user-generated secrets.
- Prefer local/offline checks for sensitive analysis before external uploads.

## Logging rules

- Logs should avoid raw secrets and credentials.
- Mask sensitive values in scripts and CI outputs.
- Remove verbose debug outputs that include tokens or private paths when uncertain.

## Incident response

- Report suspicious data handling to `SUPPORT.md` or security contact in `SECURITY.md`.
- Create an incident entry and remediation entry before next release.
