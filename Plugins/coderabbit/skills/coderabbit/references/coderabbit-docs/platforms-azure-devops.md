---
source: https://docs.coderabbit.ai/platforms/azure-devops
---

# Azure DevOps

Integrate CodeRabbit with Azure DevOps repositories.

## Prerequisites

- Active Azure DevOps account
- Organizational email (personal email accounts are unsupported)

## Integration instructions

1. Log in to CodeRabbit.
2. Complete Microsoft app-consent flow (or forward to an admin for approval).
3. Click **Continue** after approval.
4. Select the Azure DevOps organization to integrate.
5. Enter Azure DevOps Personal Access Token (PAT) in **Azure DevOps User**.
6. Toggle repositories on the **Repositories** page to install CodeRabbit.

## PAT requirements

CodeRabbit needs PAT access to Azure DevOps APIs to post pull-request reviews.

Recommended PAT setup:

- Use a dedicated service account PAT for CodeRabbit.
- Grant only required scopes (typically Work Items and Code read/write for review operations).
- Set explicit expiration and rotate before expiry.
- Store PAT in approved secret-management tooling.

If a PAT expires, update it from **Azure DevOps User** in CodeRabbit.

## Generating a PAT

1. Log in as the intended CodeRabbit service account user.
2. Open user settings (avatar/settings icon).
3. Open **Personal Access Tokens**.
4. Click **New Token**.
5. Choose organization scope (`All accessible organizations` only if required).
6. Set token name and expiration.
7. Grant required scopes for CodeRabbit review operations.
8. Create token and copy it immediately.

## Security and attribution notes

- Reviews are attributed to the PAT owner account.
- If PAT compromise is suspected, revoke immediately and issue a new token.
- Keep PAT ownership and rotation documented for auditability.
