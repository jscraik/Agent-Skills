---
source: https://docs.coderabbit.ai/platforms/gitlab-com
---

# GitLab

Learn how to integrate CodeRabbit with GitLab.com repositories using personal or group access tokens for automated AI-powered code reviews and collaboration.

CodeRabbit enhances your GitLab.com development workflow by providing:

- **Automated code reviews** for newly created merge requests
- **AI-powered suggestions** displayed directly on merge requests
- **Interactive assistance** through the CodeRabbit bot for real-time feedback
- **Seamless integration** with your existing GitLab workflow

## GitLab Access Tokens

To enable CodeRabbit to interact with your GitLab repositories, you need to provide an access token that grants the necessary permissions for the Merge Requests and Discussions APIs.

Choose the token type that best fits your organization's needs:

### Personal Access Token

We recommend creating a new user as a service account, associating this user to the group you'd like to install CodeRabbit on, and providing CodeRabbit with the personal access token to allow access. During the installation process, CodeRabbit will automatically configure the required webhook for seamless integration.

#### Best Practices for Service Account Setup

Follow these recommendations when setting up your CodeRabbit service account:

- **Username**: Use "CodeRabbit" as the username for easy recognition
- **Email**: Use a dedicated email address for easy identification and management
- **Profile picture**: Use the CodeRabbit logo for easy recognition
- **Permissions**: Ensure the dedicated user has at least **Developer** access to the group or projects where you want to install CodeRabbit

#### Important Considerations

**Updating Expired Tokens**: If your personal access token expires, you can add a new one via the CodeRabbit UI:

1. Navigate to the **GitLab User** page in the sidebar
2. Enter the new access token and click the **Update** button

### Group Access Token

Creating a Group Access Token in GitLab automatically generates a bot user. Ensure that the token is configured with Developer access. Once set up, you only need to provide this token for integration. Note that a Group Access Token is limited to the scope of the group where it was created. To configure additional groups, you will need to generate a separate Group Access Token for each group.

### Configuring Access Tokens in CodeRabbit

GitLab onboarding requirement: The user completing the CodeRabbit onboarding flow must be a GitLab group owner. By default, if no access token is provided, CodeRabbit will prompt you to provide one during the installation process. However, if you wish to provide the token beforehand, you can do so by navigating to the **Organization Settings** tab, and selecting the **GitLab User** tab on the sidebar. Once entering the token, the token will be validated and saved for future use.

You can confirm the correct user is being selected by verifying the user ID shown on the UI with the user ID of the service account user you created.

## Repository Installation

The webhook `https://coderabbit.ai/gitlabHandler` will now be installed for the projects selected.

## Troubleshooting
