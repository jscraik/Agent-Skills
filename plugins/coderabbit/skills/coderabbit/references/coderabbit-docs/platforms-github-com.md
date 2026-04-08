---
source: https://docs.coderabbit.ai/platforms/github-com
---

# GitHub

Learn how to integrate CodeRabbit with GitHub.com repositories for automated AI-powered code reviews, including setup, permissions, and repository configuration.

## Setup steps

### Visit CodeRabbit login page

Initiate GitHub login

### Sign in to GitHub (if required)

Click **Login with GitHub**. Your browser will redirect to GitHub.com.

If GitHub prompts you to sign in, enter your GitHub login credentials as you normally would.

### Review and authorize permissions

GitHub displays a summary of the information that CodeRabbit needs to integrate with your account. This includes read-only access to:

- Organizations and teams associated with your GitHub account
- Email addresses associated with your GitHub account

Click **Authorize coderabbitai** to grant these permissions.

### Select an organization

Choose the organization where you want to install CodeRabbit.

- If you belong to multiple organizations, select from the list
- For personal repositories, select your account name

### Install and authorize CodeRabbit

Configure repository access and review the permissions CodeRabbit needs.

#### Choose repository access

Select which repositories CodeRabbit can access:

- **All repositories**: Grants access to all current and future repositories owned by this organization, including public repositories.
- **Only select repositories**: Limits access to specific repositories you choose from the list.

You can change this setting later if needed.

#### Review permissions

CodeRabbit requires the following permissions to perform code reviews and manage pull requests:

**Read-only access:**

- Actions, checks, discussions, members, and metadata

**Read-and-write access:**

- Code, commit statuses, issues, and pull requests

CodeRabbit requests read and write access to your repository for its code review, issue management, and pull request generation features to work. **CodeRabbit never stores your code.** For more information, see the CodeRabbit Trust Center.

#### Complete installation

Click **Install & Authorize** (for new integrations) or **Save** (for existing integrations).

### Trigger your first review (optional)

After installation, you can immediately see CodeRabbit in action or skip to configure settings first.

**Option 1: Trigger a review**

1. Select a repository from your list
2. Choose an existing pull request
3. CodeRabbit will perform a code review on that pull request

**Option 2: Skip to dashboard**

Click **Skip to App** to access the CodeRabbit dashboard and configure settings before your first review.
