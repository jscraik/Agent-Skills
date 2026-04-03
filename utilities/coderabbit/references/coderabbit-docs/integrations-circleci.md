---
source: https://docs.coderabbit.ai/integrations/circleci
---

# CircleCI integration

Connect CodeRabbit to CircleCI to surface pipeline failure context directly in pull request reviews.

When you connect CircleCI to CodeRabbit, pipeline failure details are pulled into the review automatically. CodeRabbit reads the build output and posts inline comments with suggested fixes on the lines of code that caused the failure — no manual copy-pasting of logs required.

## Prerequisites

Before setting up the CircleCI integration, ensure you have:

- A CircleCI account with access to the projects you want to connect
- Permission to generate Personal API Tokens in CircleCI

## Connect CircleCI

The integration uses a CircleCI Personal API Token to authenticate.

1. **Open the CodeRabbit Integrations page** - Navigate to Integrations in the CodeRabbit app and select the **CI/CD** tab.
2. **Enable CircleCI** - Locate the CircleCI card and toggle it on. A **Connect CircleCI** dialog appears.
3. **Create a Personal API Token in CircleCI** - In a new browser tab:
   1. Go to your CircleCI User Settings.
   2. Click **Create New Token**.
   3. Give it a descriptive name, for example `CodeRabbit Integration`.
   4. Copy the generated token.
4. **Paste the token into CodeRabbit** - Back in the CodeRabbit dialog, paste the token into the **API Token** field and click **Save**.

Keep your Personal API Token secure. It grants CodeRabbit read access to your CircleCI pipeline logs. If the token is revoked or rotated, repeat the steps above to reconnect.

## How it works

After connecting:

1. A pull request is opened or updated and your CircleCI pipelines run.
2. CodeRabbit waits for the pipelines to finish.
3. CodeRabbit reads the failure output via the CircleCI pipeline API.
4. Inline comments with suggested fixes are posted on the relevant lines of code.

No additional repository-level configuration is required. CodeRabbit picks up pipeline results automatically for every pull request where CircleCI reports a failure.

## What's next

- **CI/CD pipeline analysis** - Learn how CodeRabbit analyzes pipeline failures across all supported CI/CD platforms and posts fix suggestions inline.
- **GitHub Checks configuration** - Configure the timeout and enable/disable behavior for GitHub Actions pipeline analysis.
