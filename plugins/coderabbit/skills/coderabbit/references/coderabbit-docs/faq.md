---
source: https://docs.coderabbit.ai/faq
---

# CodeRabbit Documentation - AI code reviews on pull requests, IDE, and CLI

Frequently asked questions about CodeRabbit.

## General Questions

### How to trigger a CodeRabbit Review?

Once installed, CodeRabbit automatically triggers a review when a pull request is opened against the main branch of any repository. We automatically detect the name of the primary branch (whether this be master, main, dev, etc). This branch restriction can be customized in your settings.
You can also manually trigger a review at any time by commenting on a pull request with one of these commands (see Commands for full list):

- `@coderabbitai review` - Triggers a standard review
- `@coderabbitai full review` - Triggers a comprehensive review

### How to run a review from my IDE?

You can trigger CodeRabbit reviews directly from your IDE using our editor plugins:

- VS Code Extension - For VS Code, Cursor or Windsurf users

These plugins allow you to request reviews without leaving your development environment. See the individual plugin documentation for installation and usage instructions.

### How to install CodeRabbit?

View step by step instructions depending on your platform:

- GitHub
- GitLab
- Bitbucket
- Azure DevOps

### How accurate is CodeRabbit?

> CodeRabbit demonstrates high accuracy in code reviews based on early adoption results. While 100% accuracy isn't guaranteed due to AI's evolving nature, our technology continuously improves through:

- Regular model updates
- Enhanced pattern recognition
- Growing language support
- Refined code analysis

### Language Support

CodeRabbit works with all programming languages, with varying proficiency based on:

- Language popularity
- Available training data
- Community usage patterns

### What's the difference between CodeRabbit Code Reviews and CodeRabbit Reports?

CodeRabbit offers two distinct features that serve different roles in your development workflow:

#### CodeRabbit Code Reviews

**Role**: Developer, QA, and Code Reviewer
**Access Level**: Full code access with comprehensive analysis capabilities
**Key Features:**

- **Complete Toolchain**: Runs all available analysis tools on your codebase
- **Static Analysis**: Can execute shell commands and perform deep static analysis against your codebase
- **Direct Code Access**: Has full access to code in issues and pull requests
- **Interactive Chat**: Provides chat features for real-time collaboration and questions
- **Comprehensive Review**: Analyzes code quality, security, performance, and best practices
- **Actionable Feedback**: Provides specific, line-by-line suggestions and improvements
- **Comment Interaction**: Engages with users through comments in pull requests and issues for clarifications and discussions
- **Available in All Tiers**: All features are available across Free, OSS and Pro plans

#### CodeRabbit Reports

**Role**: Project Manager and Communication Hub
**Access Level**: Summary-only access without direct code interaction
**Key Features:**

- **Summary Generation**: Creates convenient, formatted summaries of all your recent pull requests
- **Customizable Prompts**: Allows you to select or create your own summarization templates
- **High-Level Overview**: Focuses on project progress and changes without code details
- **Comment Analysis**: Reads and summarizes existing comments and discussions
- **No Code Access**: Operates only on summaries and metadata, not the actual codebase
- **Communication Tool**: Designed for stakeholders who need updates without technical details
- **Multi-Channel Delivery**: Sends reports through various communication channels:
  - Email notifications
  - Slack integration
  - Discord webhooks
  - Microsoft Teams updates
- **Pro Plan Exclusive**: Reports feature is available only in the Pro plan tier

**In Summary:**

- **Code Reviews** = Technical analysis with full code access for developers
- **Reports** = High-level summaries with no code access for project management

### Data Security

Your proprietary code remains confidential with CodeRabbit. You can opt out of data storage. However, opting in helps us fine-tune the reviews for you based on your usage.

- Code Privacy
- Code Storage
- Training Data

- Your code is shared with OpenAI and/or Anthropic for reviewing purposes only
- Neither CodeRabbit nor OpenAI or Anthropic uses your code to train our models
- We adhere to rigorous privacy policies to guarantee the safety and confidentiality of your code
- Complete data isolation for your proprietary code

- Caching of encrypted code and dependency archives for faster reviews
- Code indexing in which we store vector representations of code for efficient code base context
- Both caching and code indexing can be disabled which means we store nothing post-review
- You can opt out of data storage at any time

- CodeRabbit uses open-source project code to train our system
- No proprietary code usage for training
- Private repositories excluded from training data

### Organization Management

Switch between organizations easily:

1. Click organization name (top-left corner)
2. Select desired organization
3. Access organization-specific settings

### Comparison with Other Tools

> Code reviews remain essential, whether the code is written by a human or a bot. This is mainly because the perspective of the reviewer differs from that of the code generator, whether human or machine. This distinction is precisely why human peer reviews have been effective for so long. While AI-powered code-generation tools like GitHub Copilot hold immense potential, it's important to recognize that these generators are still in their early stages and may not be equipped to auto-generate meaningful code for moderately complex applications.

#### vs AI Code Generators

- Provides review perspective different from code generation
- Complements tools like GitHub Copilot
- Focuses on code quality and best practices

#### vs Traditional Review Tools

- Context-aware feedback
- Actionable suggestions
- Direct commit capabilities
- AI-powered intent understanding

## Usage and Configuration

### When Does CodeRabbit Review PRs?

- **New PRs**: Automatic review when created
- **New Commits**: Automatic review when pushed to any PR
- **Older PRs**: Use `@coderabbitai review` to trigger manually

### Customization Options

#### How to Add or Update Your Billing Email

To add or update your billing email, navigate to the Subscription page and
select Manage Subscription > **Billing Address**. Enter your email address in the
Email field and click Update to save your changes.

### Usage and Configuration

- **Language Settings**: Configure review language in repository settings
- **Review Rules**: Customize via review instructions
- **Branch Selection**: Default branch reviews enabled by default (configurable)

### Access & Permissions

- Minimal repository access required
- Review permissions during installation
- Individual developer support available

### Interaction Guide

Interact with CodeRabbit by:

1. Replying directly to CodeRabbit comments
2. Tagging `@coderabbitai` in PR discussions
3. Adding review comments for specific lines
4. Customize via review instructions

### Usage Limits

The following limits are enforced _per developer_:

| Feature | Free Plan | Trial Plan | OSS Plan | Pro Plan | Enterprise Plan |
| --- | --- | --- | --- | --- | --- |
| Files per review | 150 | 150 | 150 | 300 | 300 |
| Reviews per hour | 3/hour (Summary only) | 4/hour | 2/hour | 8/hour | 12/hour |
| Reviews per hour (IDE Extension) | 3/hour | 4/hour | 2/hour | 8/hour | 12/hour |
| Reviews per hour (CLI) | 3/hour | 4/hour | 2/hour | 8/hour | 12/hour |
| Chat | N/A | 50/hour | 25/hour | 50/hour | 100/hour |

## Integration Guide

### Prerequisites

- Organization admin access
- Domain allowlist (GitLab: add `coderabbit.ai`)
- Default branch configuration

### Quick Setup

1. Sign up at coderabbit.ai using your GitHub account
2. Add your repository through the dashboard
3. That's it. CodeRabbit will automatically start reviewing your PRs

#### Unable to View Repositories in GitLab

If you cannot view repositories in the CodeRabbit UI, please ensure that you
are added as a Developer in the primary group for GitLab Cloud or in the first
level group for Self-Hosted GitLab.

#### Unable to Enable Repositories in GitLab

If you're having trouble enabling the GitLab Repositories toggle, confirm that
you have Maintainer access in the primary group for GitLab Cloud or in the first
level group for Self-Hosted GitLab.

## Account Management

### How to troubleshoot CodeRabbit not functioning on certain repositories?

If CodeRabbit is not functioning on certain repositories, it is likely due to the repository not being accessible to CodeRabbit and you must reinstall the GitHub App or GitLab Integration.
To troubleshoot this issue, please attempt to reinstall the GitHub App or GitLab Integration by following the steps below:

- General Instructions
- GitHub
- GitLab

1. Remove OAuth App from User Settings > Applications
2. Remove Webhook from Group > Project Settings > Webhooks
3. Go into the Coderabbit App and install it again.

### How do I delete my CodeRabbit account?

- Account Deletion Steps
- GitHub Cleanup
- GitLab Cleanup
- Azure DevOps Cleanup
- Bitbucket Cleanup

1. Sign into your CodeRabbit account
2. Navigate to the **Subscription** page
3. Click the **Delete Account** button
4. Review the deletion confirmation modal
5. Type "delete" to confirm
6. Complete platform-specific cleanup on the tab above.

A confirmation modal will appear explaining the consequences of account deletion. You can expand each section for detailed information.

After account deletion, you must:

**Remove OAuth App:**

1. Go to Organization settings
2. Click **OAuth Application Policy**
3. Find **coderabbitai** and click the pencil icon
4. Click **Revoke**

**Uninstall GitHub App:**

1. Go to Organization settings
2. Click **GitHub Apps**
3. Select **Configure**
4. Click **Uninstall**

Complete these steps:

1. Remove OAuth App from User Settings > Applications
2. Remove Webhook from Group > Project Settings > Webhooks
3. Remove Bot User from Group > Manage > Members

1. Go to Project Settings > Service Hooks
2. Delete CodeRabbit webhooks
3. Remove CodeRabbit user or delete associated Personal Access Token

1. Go to Project Settings > Webhooks
2. Delete CodeRabbit webhooks
3. Remove CodeRabbit user or delete associated App Passwords
