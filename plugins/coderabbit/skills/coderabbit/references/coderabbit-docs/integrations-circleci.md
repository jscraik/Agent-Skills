---
source: https://docs.coderabbit.ai/integrations/circleci
---

# CircleCI Integration

Connect CodeRabbit to CircleCI so pipeline failure context can be surfaced directly inside pull-request reviews.

When connected, CodeRabbit reads failure output and can post inline suggestions on affected lines.

## Prerequisites

- CircleCI account with access to target projects
- Ability to create CircleCI Personal API Tokens

## Connect CircleCI

1. Open **Integrations** in CodeRabbit, then the **CI/CD** tab.
2. Enable CircleCI and open **Connect CircleCI**.
3. In CircleCI settings, create a Personal API Token.
4. Paste the token into CodeRabbit and save.

## Token security guidance

- Use a dedicated token for CodeRabbit only.
- Scope token access to minimum required projects.
- Store token securely and rotate it periodically.
- Revoke and replace immediately if token exposure is suspected.

If the token is revoked or rotated, reconnect with a fresh token.

## How it works

1. Pull request is opened or updated and CircleCI pipelines run.
2. CodeRabbit waits for pipeline completion.
3. CodeRabbit reads failure output from CircleCI APIs.
4. CodeRabbit posts inline comments with suggested fixes.

No repository-level config is required beyond enabling integration.

## What's next

- CI/CD pipeline analysis across supported platforms
- GitHub Checks timeout and behavior configuration
