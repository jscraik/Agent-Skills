---
source: https://docs.coderabbit.ai/guide/repository
---

# Repository Setup

Set up a GitHub test repository and integrate CodeRabbit for automated code reviews.

## Before you begin

Create a new repository on GitHub. Name the new repository `coderabbit-test`, and let it have otherwise default GitHub settings.

## Integrate CodeRabbit with your GitHub account

To integrate CodeRabbit with your GitHub account, follow these steps:

1. Create an account
   Visit the CodeRabbit login page. No credit card required!
   CodeRabbit takes a moment to set up the integration. After it finishes, the CodeRabbit dashboard appears.

## Add CodeRabbit to your repository

To add CodeRabbit to your test repository, follow these steps:

2. Access repository settings
   On the CodeRabbit dashboard, click **Add Repositories**. A GitHub repository-access dialog appears.

3. Grant repository access
   Select the **Only select repositories** radio button.

4. Select your test repository
   From the **Select repositories** menu, select the `coderabbit-test` repository that you created earlier in this guide.

5. Install and authorize CodeRabbit
   Click **Install & Authorize**.

   CodeRabbit requests read and write access to your repository in order for its code review, issue management, and pull request generation features to work. CodeRabbit never stores your code. For more information, see the CodeRabbit Trust Center.

6. Complete signup if prompted
   If a CodeRabbit **Complete your signup** dialog appears, then fill it out with the requested information before continuing.

CodeRabbit is now ready to use with your test repository. The next steps demonstrate its core code-review features.
