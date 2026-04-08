---
source: https://docs.coderabbit.ai/platforms/self-hosted-gitlab
---

# Self-managed GitLab

Learn how to integrate CodeRabbit with your self-managed GitLab instance through automated or manual onboarding, including OAuth setup, user configuration, and webhook installation.

**Version Requirements:** CodeRabbit supports GitLab `16.x` and above. Version `15.x` may experience unexpected issues such as review comments not being posted or the sign-up process not working at all. We recommend upgrading your GitLab instance to obtain the intended experience.

## Getting Started

To integrate your self-managed GitLab with CodeRabbit, we require specific information for the initial setup within your domain. Once this setup is complete, you can log in directly using the OAuth2 flow.

1. **Visit CodeRabbit login page** -- Navigate to the CodeRabbit login page and select **Self-Hosted GitLab**.
2. **Enter your GitLab instance URL** -- Enter the URL of your self-managed GitLab instance and click **Submit**. We'll check our database for an existing record of your organization and start the login process if found. If your self-managed GitLab instance is not found, we'll initiate the onboarding process.
3. **Choose onboarding method** -- You can choose between automated or manual onboarding based on your security preferences and administrative access.

## Onboarding Options

### Automated Onboarding (Recommended)

The admin access token is required to set up a new CodeRabbit bot user within your self-managed instance. The token is needed only once during the initial setup process. Once generated, you can set its minimum expiration period.

Note: This does not automatically install the CodeRabbit app across all projects. You will add CodeRabbit manually to the projects you wish to integrate.

### Manual Onboarding

For the manual onboarding process, you need to create the CodeRabbit user and the OAuth2 GitLab application.

#### Creating CodeRabbit User

This feature will work with any user from your organization, but we strongly recommend creating a dedicated user called **CodeRabbitAI**. This ensures clarity about which user is used for our application and allows for better fine-grained access control.

1. **Create the user** -- Log in with an instance admin account and follow the GitLab documentation to create a new user.
2. **Retrieve user information** -- After the user is created, retrieve the **User ID** from that user's profile.
3. **Generate access token** -- Generate an **access token** for this user. The access token is used to post reviews on merge requests.

**Recommendations for the CodeRabbit user:**
- Use **"CodeRabbitAI"** as the username for easy identification
- Use the CodeRabbit logo as the profile picture for easy recognition
- Ensure the user has appropriate permissions for the repositories you want to integrate

If you prefer, you can create a Group Access Token which will create a dedicated user on your behalf.

#### Creating OAuth2 Application

For self-managed GitLab, we recommend creating an instance-wide application unless you want the reviews to be limited to a single group or user.

**OAuth2 Application Requirements:**
- **Scopes:** `api read_user email openid`
- **Callback URL:** `https://app.coderabbit.ai/login`

#### Generating Personal Access Token

GitLab offers an option to generate a personal access token for adding a new user and setting up the application in the self-managed instance.

1. Login to your self-hosted instance. For automated onboarding, ensure you have admin rights.
2. On the left sidebar, select your avatar, then select **Edit profile**.
3. On the left sidebar, select **Access Tokens**.
4. Select **Add new token**.
5. Configure token settings:
   - Enter a name and expiry date for the token
   - We need this for the initial setup, so the minimum expiry time is sufficient
   - If you do not enter an expiry date, it defaults to 365 days from the current date
   - Select the required scopes: `api`, `read_api`, `read_user`
6. Select **Create personal access token** and note down the token as it will only be displayed once.

### Paste the details and click submit

- Submit the form.
- We will handle the setup process for you.
- On subsequent visits, your setup will be automatically detected, allowing for direct login.

### Allow list CodeRabbit IP address

Use this CodeRabbit IP if your instance requires IP allow listing.

```
35.222.179.152/32, 34.170.211.100/32
```

### Manual Webhook Installation

For administrators managing many GitLab projects, you can use a script to bulk-install webhooks across all projects.

1. Login to CodeRabbit UI through your GitLab self-managed instance.
2. On the bottom left sidebar, select **Account**.
3. On the left sidebar, select **Webhook Secret**.
4. Input a webhook secret. This secret will be used by CodeRabbit to verify incoming webhook events from your GitLab instance.
5. Use a script to install webhooks across your GitLab projects or groups. The script requires:
   - Your GitLab host URL
   - The CodeRabbit webhook URL: `https://coderabbit.ai/gitlabHandler`
   - The webhook secret you created in Step 1
   - A GitLab access token with API permissions

**Example: Install webhook on a single project**

```bash
export GITLAB_TOKEN="glpat-xxxxx"
./gitlab-webhook.sh \
  -h "gitlab.example.com" \
  -u "https://coderabbit.ai/gitlabHandler" \
  -s "your-webhook-secret" \
  -p 42
```

**Example: Install webhooks on all projects in a group (including subgroups)**

```bash
export GITLAB_TOKEN="glpat-xxxxx"
./gitlab-webhook.sh \
  -h "gitlab.example.com" \
  -u "https://coderabbit.ai/gitlabHandler" \
  -s "your-webhook-secret" \
  -g "mygroup/mysubgroup"
```
