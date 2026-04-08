---
source: https://docs.coderabbit.ai/platforms/bitbucket-cloud
---

# Bitbucket Cloud

Learn how to integrate CodeRabbit with Bitbucket Cloud repositories for automated AI-powered code reviews.

For an overview of how CodeRabbit integrates with Git platforms, see Add CodeRabbit to your repository. For a hands-on tutorial with CodeRabbit performing code reviews on a live repository, see Quickstart.

CodeRabbit integrates with Bitbucket Cloud to improve your development workflow by:

- **Automated code reviews** for newly created merge requests
- **Intelligent comments and suggestions** displayed directly on merge requests
- **Real-time bot interaction** for immediate feedback and assistance
- **Seamless webhook integration** for continuous monitoring

This guide walks you through integrating CodeRabbit with your Bitbucket Cloud repositories.

## Configure API Token

To enable CodeRabbit to interact with your Bitbucket repositories, you need to configure an API token. This token grants the necessary permissions for interacting with the Bitbucket merge request and discussion APIs.

**Service Account Required**
You must create a dedicated Bitbucket account specifically for CodeRabbit to ensure proper permissions and security isolation.

1. **Create a CodeRabbit service account**
   Create a new Bitbucket account specifically for CodeRabbit and treat it as a service account.

2. **Configure account settings**
   - Name the account "CodeRabbit" for easy identification
   - Use a dedicated email address for this service account
   - If your Bitbucket workspace requires two-step verification, enable it on this account as well

3. **Generate API token**
   Generate an API Token to enable the integration between CodeRabbit and your Bitbucket repositories.

   We recommend creating a dedicated service account and associating it with the workspace where you want to install CodeRabbit. During the installation process, CodeRabbit will automatically configure the required webhook for seamless integration.

   If you wish to change the review user, you must provide the API token for the new user who will post reviews and comments. However, this requires manually removing the previous user from the projects and associated webhooks. Once this is done, you will need to reinstall the CodeRabbit app for each project.

### Best practices for service account setup

**Account Configuration**

- **Use "CodeRabbit" as the username** for easy recognition
- **Use a dedicated email address** for management
- **Use the CodeRabbit logo** as the profile picture (download here)

**Access Control**

- **Grant developer access** to target projects
- **Ensure workspace membership** for the service account
- **Enable two-factor authentication** if required by workspace

**Important:** Code reviews will be attributed to the owner of the API token. Ensure the service account is properly configured and recognizable to your team.

### Generate an API token

Bitbucket provides an option to generate an API token for your CodeRabbit service account. Follow these steps:

1. **Log in to your service account**
   Log in using the user designated for CodeRabbit reviews. This user serves as a service account for managing reviews and related activities.

2. **Navigate to API tokens**
   Go to API Tokens in your Atlassian account settings.

3. **Create new token**
   Click **Create API token with scopes**.

4. **Configure token details**
   - Enter a recognizable name for this API token (e.g., "CodeRabbit Integration")
   - Set an expiration date based on your security policy
   - On the next step, select **Bitbucket**

5. **Select required scopes**
   Ensure the following scopes are selected for CodeRabbit to function properly:

   | Category | Scope | Description |
   | --- | --- | --- |
   | **Account & User** | `read:account` | Access account information |
   | | `read:user:bitbucket` | Read user profile data |
   | **Repository** | `read:repository:bitbucket` | Read repository content and metadata |
   | | `write:repository:bitbucket` | Write access for code analysis |
   | **Pull Requests** | `read:pullrequest:bitbucket` | Read pull request information |
   | | `write:pullrequest:bitbucket` | Post reviews and comments |
   | **Issues** | `read:issue:bitbucket` | Read issue information |
   | | `write:issue:bitbucket` | Create and update issues |
   | **Workspace** | `read:workspace:bitbucket` | Access workspace information |
   | | `admin:project:bitbucket` | Manage project settings |
   | **Webhooks** | `read:webhook:bitbucket` | Read webhook configurations |
   | | `write:webhook:bitbucket` | Create and manage webhooks |
   | **Pipelines** | `read:pipeline:bitbucket` | Read pipeline information |
   | | `read:runner:bitbucket` | Access pipeline runner data |

6. **Generate and save token**
   - Click **Create**
   - **Important:** Copy and securely store the API token immediately as it will only be displayed once

**Security Note:** The API token will only be displayed once upon creation. Make sure to copy and store it securely before leaving the page.

### Configure API token in CodeRabbit

You can provide your API token to CodeRabbit in two ways:

- **During Installation**
- **Pre-configure Token**

CodeRabbit will automatically prompt you to provide the API token during the repository installation process if none is configured.

## Install CodeRabbit in your repositories

Once your API token is configured, you can install CodeRabbit in your Bitbucket repositories.

1. **Access repository settings**
   Navigate to the Repositories page in the CodeRabbit app.

2. **Select repositories**
   - Check the boxes next to specific repositories where you want to install CodeRabbit
   - To install on all repositories at once, select the checkbox at the top

3. **Install repositories**
   Click **Install Repositories** to complete the setup.

**Webhook Configuration:** The webhook `https://coderabbit.ai/bitbucketHandler` will be automatically installed for the selected projects, enabling CodeRabbit to monitor and review your merge requests.

## Troubleshooting

If you encounter issues during setup or operation, here are common solutions:

**Webhook Issues**

If CodeRabbit isn't accessing repositories or reviewing merge requests:

1. **Check webhook status** in your Bitbucket repository settings
2. **Manually delete the webhook** if it exists but isn't working
3. **Refresh the repository page** in the CodeRabbit app
4. **Reinstall the webhook** using the CodeRabbit interface

**Installation Problems**

If you cannot install the webhook:

- **Verify permissions**: Ensure your Bitbucket service account has the necessary permissions
- **Check API token**: Confirm the API token is properly configured with all required scopes
- **Validate account access**: Ensure the service account has developer access to target repositories

**Authentication Errors**

If you're seeing authentication issues:

- **Regenerate API token** with the correct scopes
- **Update token in CodeRabbit** Organization Settings
- **Verify service account** has workspace membership

For additional support, visit our support documentation or contact our team through the CodeRabbit app.

## What's next

- **Configure repository settings** - Customize CodeRabbit's behavior for your repositories
- **Review merge requests** - Learn how CodeRabbit reviews your merge requests
- **Set up review instructions** - Add custom guidelines for your team's code reviews
- **Best practices** - Optimize your CodeRabbit setup for maximum value
