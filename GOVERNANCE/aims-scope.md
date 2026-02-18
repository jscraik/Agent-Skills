# AIMS Scope

- Scope owner: Jamie (repo owner)
- Scope date: 2026-02-18
- Goal: Establish a lightweight AI and security governance baseline for this repository while keeping delivery fast for a solo maintainer.

## In scope

- Repository governance docs and policies:
  - `SECURITY.md`
  - `GOVERNANCE/*`
  - `COMPLIANCE/*`
- PR quality controls for policy-related files
- Branch-protection evidence and exception/incidence documentation

## In-scope assets

- Source files and workflow automation in this repository
- Tool configuration that affects review/merge, release, or dependency checks
- Any PR that touches `GOVERNANCE/`, `COMPLIANCE/`, `SECURITY/`, or `.github/` policy files

## Exclusions

- Runtime product behavior not directly related to governance/process
- Third-party service operations outside this repository

## Roles

- Jamie: Author, approver, and final risk decision owner
- Codex/automation: Evidence collector, checklist and diff verifier

## Review cadence

- Monthly quick governance review
- Immediate post-incident follow-up for exceptions and incidents
- Annual governance baseline revalidation
