---
source: https://docs.coderabbit.ai/platforms/bitbucket-data-center
---

# Bitbucket Data Center

Learn how to integrate CodeRabbit with your self-hosted Bitbucket Data Center instance for AI-powered code reviews on pull requests.

For a hands-on tutorial with CodeRabbit performing code reviews on a live repository, see Quickstart.

CodeRabbit integrates with Bitbucket Data Center to bring AI-powered code reviews to your self-hosted Bitbucket instance:

- **Automated code reviews** for newly created pull requests
- **Intelligent comments and suggestions** displayed directly on pull requests
- **Real-time bot interaction** for immediate feedback and assistance
- **Seamless webhook integration** for continuous monitoring

This guide walks you through connecting your Bitbucket Data Center instance to CodeRabbit.

## Prerequisites

Before starting, you need to set up the following in your Bitbucket Data Center instance:

1. **Create a bot user**
   Create a dedicated Bitbucket user for CodeRabbit (e.g., "CodeRabbit"). This user will post code review comments on pull requests.

   - Add the bot user to each project where you want CodeRabbit to review pull requests
   - Grant the bot user **write** permissions on the relevant repositories

2. **Generate an HTTP Access Token for the bot user**
   Generate an HTTP Access Token for the bot user:

   1. Log in as the bot user
   2. Navigate to **Manage Account** and select **HTTP Access Tokens**
   3. Create a new token with **repository write** permissions

   Save the token securely. It will only be shown once.

3. **Create an OAuth consumer**
   Create an OAuth consumer in your Bitbucket Data Center administration:

   1. Navigate to **Administration** and then **Application Links**
   2. Create a new **External application** with an **Incoming link**
   3. Set the **Redirect URL** to: `https://app.coderabbit.ai/login`
   4. Grant the following permissions:
      - **Repository Read**
      - **Repository Write**
      - **Project Read**
   5. Note the **Client ID** and **Client Secret**

## Connect to CodeRabbit

1. **Navigate to the CodeRabbit login page**
   Go to the CodeRabbit login page and select **Bitbucket Data Center**.

2. **Enter your Bitbucket Data Center URL**
   Enter the URL of your Bitbucket Data Center instance (e.g., `https://bitbucket.company.com`) and click **Submit**.
   If your instance is already registered, you will be redirected to the OAuth authorization flow. Otherwise, you will be prompted to provide your credentials.

3. **Provide credentials**
   If this is the first time connecting your instance, provide:

   - **Bot Token**: The HTTP Access Token you generated for the bot user
   - **Client ID**: The OAuth consumer Client ID
   - **Client Secret**: The OAuth consumer Client Secret

   Click **Validate token** to verify the bot token before proceeding.

4. **Authorize CodeRabbit**
   You will be redirected to your Bitbucket Data Center instance to authorize CodeRabbit. Review the requested permissions and click **Allow**.

## Install CodeRabbit on your repositories

After logging in, the onboarding wizard guides you through selecting projects and repositories.

1. **Select a project**
   Choose the Bitbucket Data Center project containing the repositories you want CodeRabbit to review.

2. **Select repositories**
   - Browse or search for repositories within the selected project
   - Select the repositories where you want to enable AI code reviews
   - Click **Install** to complete the setup

CodeRabbit will automatically configure webhooks for the selected repositories. Once installed, CodeRabbit begins reviewing new pull requests immediately.

## Configure network access

If your Bitbucket Data Center instance requires IP allowlisting, add these CodeRabbit IP addresses:

```
35.222.179.152/32, 34.170.211.100/32, 136.113.208.247/32
```

## Manage credentials

You can update the bot user's HTTP Access Token at any time:

1. Navigate to **Organization Settings** in the CodeRabbit app
2. Select the **Bitbucket DC User** tab
3. Enter the new HTTP Access Token
4. Save your changes

## Troubleshooting

**Bot token validation fails**

- Verify the HTTP Access Token has the correct permissions (repository write)
- Ensure the bot user account is active and not locked
- Check that your Bitbucket Data Center URL is correct and accessible from the internet

**OAuth authorization fails**

- Verify the Client ID and Client Secret match the OAuth consumer configured in Bitbucket DC
- Ensure the callback URL is set to `https://app.coderabbit.ai/login`
- Check that the OAuth consumer has the required permissions

**Webhooks not working**

- Ensure your Bitbucket Data Center instance can reach CodeRabbit's servers
- Check webhook configurations in your repository settings
- Verify the bot user has write access to the repositories

**Reviews not posting**

- Confirm the bot user is added to the project with write permissions
- Verify the HTTP Access Token has not expired
- Check that webhooks are properly configured and active

For additional support, visit the support page.

## What's next

- **Configure CodeRabbit** - Customize review behavior, language settings, and rules for your repositories.
- **Code Review Overview** - Learn how CodeRabbit reviews your pull requests and provides actionable feedback.
- **Get Support** - Reach out to the CodeRabbit team for help with setup or integration issues.
