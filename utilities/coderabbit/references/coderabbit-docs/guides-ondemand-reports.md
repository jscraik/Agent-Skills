---
source: https://docs.coderabbit.ai/guides/ondemand-reports
---

# On-demand Reports

CodeRabbit offers a way to generate on-demand reports using the CodeRabbit API.

## Getting an API Key

You will need an API Key to access the CodeRabbit API and generate an on-demand report.

Sign in to your CodeRabbit account and navigate to the **API keys** page under 'Organization Settings' in the left sidebar. Click on the **Create API Key** button and enter a name for the API Key. Copy the API key, and keep it safe as it won't be visible again.

Once you have the API key, pass it in the `x-coderabbitai-api-key` header when calling the API.

## Report format

Example report output:

```
[
  {
    "group": "Developer Activity",
    "report": "*Developer Activity*:\n\n Update README.md [#10](https://gitlab.com/master-group123/sub-group/project1/-/merge_requests/10)\n• Summary: The change updates the project description and modifies a section header for clearer instructions.\n• Last activity: 1 day ago, mergeable\n• Insights:\n - @user2 Suggested updating the wording to make it clearer"
  }
]
```

The on-demand report generation endpoints take in inputs as per the API schema. See the CodeRabbit API documentation for the full request/response specification.
