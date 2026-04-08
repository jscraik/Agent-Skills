---
source: https://docs.coderabbit.ai/pr-reviews/slop-detection
---

Automatically detect low-quality, AI-generated pull requests on public GitHub repositories.

When a pull request is opened on a public GitHub repository, CodeRabbit analyzes the changes for signals of low-quality, AI-generated content. If the PR is classified as slop, CodeRabbit notes this in the PR Walkthrough comment. Additionally, you can configure a label in your settings to get the suspicious PRs labeled automatically.
The detection runs as part of CodeRabbit's standard review pipeline, no additional setup is required.

## Configuration

- Configuration file
- Web UI

Configure the `slop_detection` section in your `.coderabbit.yaml` file:

.coderabbit.yaml

```
reviews:
  slop_detection:
    enabled: true   # Runs automatically on public repos unless disabled
    label: "slop"   # Add a label to apply when slop is detected (no label applied by default)
```

1. Go to `CodeRabbit settings` for your repository or organization.
2. Switch the mode (bottom-left) to **All Settings**.
3. Navigate to **Reviews → General**.
4. Scroll down to the **Anti-Slop** section to toggle **Enabled** on or off, and optionally set a custom **Label**.

### Disabling Slop Detection

To disable Slop Detection on a repository, set `enabled` to `false` or disable it in the web UI:

.coderabbit.yaml

```
reviews:
  slop_detection:
    enabled: false
```

### Label flagged PRs

By default, Slop Detection does not apply any label, it only adds a note to the PR Walkthrough comment. To also apply a label to flagged PRs, set the `label` field:

.coderabbit.yaml

```
reviews:
  slop_detection:
    label: "slop"   # Or any label name you prefer, e.g. "ai-spam"
```

## Frequently asked questions

Does Slop Detection work on private repositories?

No. Slop Detection only runs on public GitHub repositories.

Will Slop Detection block a PR from being merged?

No. Slop Detection does not block merges. When a PR is classified as slop, a note is added to the PR Walkthrough comment. If a label is configured, it is also applied so maintainers can filter and triage PRs at their discretion.

Can I automatically close slop PRs?

Not at the moment. CodeRabbit is currently gathering data and tuning the detection mechanism to ensure accuracy.
