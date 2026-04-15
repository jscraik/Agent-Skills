---
source: https://docs.coderabbit.ai/platforms/gitlab-com
---

# GitLab

Learn how to integrate CodeRabbit with GitLab.com repositories using personal or group access tokens for automated AI-powered code reviews.

CodeRabbit enhances GitLab workflows by providing:

- Automated reviews for newly created merge requests
- AI suggestions directly on merge requests
- Interactive bot assistance for follow-up questions
- Integration with existing GitLab workflows

## GitLab access tokens

To allow CodeRabbit to interact with GitLab repositories, provide an access token with the permissions required by Merge Requests and Discussions APIs.

### Personal access token

A common setup is creating a dedicated service account user in GitLab, adding it to the required groups/projects, and providing that account's personal access token to CodeRabbit.

Recommended setup:

- Use a dedicated service account
- Use recognizable profile identity (for example `CodeRabbit`)
- Grant least privilege required, typically **Developer** for target repos/groups
- Store and rotate the token using your org secret-management process

If the token expires, update it in CodeRabbit UI:

1. Open **GitLab User** in the sidebar.
2. Enter the new token.
3. Click **Update**.

### Group access token

GitLab Group Access Tokens create a bot user automatically. Use this when you want group-scoped installation. Each group needs its own token.

## Configure token in CodeRabbit

GitLab onboarding requires a group owner to complete installation. You can provide a token during onboarding, or later via **Organization Settings → GitLab User**.

After saving, verify the UI user ID matches the service account/bot user you intended.

## Repository installation

CodeRabbit installs webhook `https://coderabbit.ai/gitlabHandler` on selected projects.

## Troubleshooting

- **Token validation fails**: Confirm token has not expired and has API scope required by MR/discussion access.
- **Reviews not posted on merge requests**: Verify webhook exists on the project and merge-request events are enabled.
- **Wrong user appears in comments**: Re-check token owner in **GitLab User** settings and replace token with the intended service account token.
- **Only some groups work**: Group Access Tokens are group-scoped; create and configure tokens per additional group.
