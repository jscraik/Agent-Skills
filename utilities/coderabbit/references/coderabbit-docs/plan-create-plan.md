---
source: https://docs.coderabbit.ai/plan/create-plan
---

# Create a plan

Create a Coding Plan from free-form descriptions, PRDs, designs, or attached files in the CodeRabbit web app.

The CodeRabbit web app lets you create Coding Plans from free-form descriptions, PRDs, designs, or attached files, without going through an issue tracker. This is the fastest way to start planning when you already know what you want to build.

## Creating a plan

1. **Open the New Plan page** -- Navigate to **Plan > New Plan** in the CodeRabbit web app, or go directly to app.coderabbit.ai/plan/new.

2. **Describe what you want to build** -- Enter a description of the feature, bug fix, or change you want to implement. Include goals, scope, and constraints. The more context you provide, the better the plan.

3. **Attach files (optional)** -- Click the paperclip icon to attach supporting documents such as PRDs, design specs, architecture diagrams, or screenshots. Supported formats include text files, PDFs, and images.

4. **Select the target repository** -- Choose the repository CodeRabbit should analyze when generating the plan. This ensures the plan references the correct files, patterns, and conventions.

5. **Click Create plan** -- CodeRabbit analyzes your repository and connected data sources, then generates a full Coding Plan. Plan generation typically takes between 5 and 10 minutes depending on codebase complexity.

## Managing plans

Browse all plans for your organization from the plans list, where you can:

- **Search** by title or ticket ID to find existing plans.
- **View status** to see whether a plan is in progress, completed, or needs review.
- **Open a plan** to view its full structure, refine it through chat, or hand it off to a coding agent.

## Configuration

If you also use issue-tracker-based planning, you can configure auto-planning rules and issue planning toggles from the CodeRabbit web app. These settings control when Coding Plans are generated automatically from issues on GitHub, GitLab, Jira, or Linear.

See the issue-based planning guides for platform-specific auto-planning configuration.

## Next Step

### Plan structure and refinement

Learn what each section of a Coding Plan contains and how to iterate on it before handoff.
