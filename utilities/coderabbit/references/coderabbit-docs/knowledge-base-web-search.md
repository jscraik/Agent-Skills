---
source: https://docs.coderabbit.ai/knowledge-base/web-search
---

# Web Search

CodeRabbit can perform web queries during reviews and chat to fetch the latest documentation and external content, improving the accuracy and relevance of its output. Web search is enabled by default for all users.

## How it works

When reviewing a pull request or responding in chat, CodeRabbit may perform web queries to include publicly available information — such as current documentation — that may not have been included in the underlying AI model's training data.

You can see when web search was used by checking the **Review details** section in the walkthrough summary comment (requires `review_details: true` in your configuration).

## Configuration

Control web search with the `knowledge_base.web_search` setting in your `.coderabbit.yaml` file.

```
knowledge_base:
  web_search:
    enabled: true  # default
```

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `knowledge_base.web_search.enabled` | boolean | `true` | Use web search to gather additional context. |

## Disabling web search

You may want to disable web search in situations such as:

- **Air-gapped or restricted environments** — where outbound network access from the review process is not permitted.
- **Policy requirements** — where your organization restricts use of external data sources during code review.

To disable, set `enabled` to `false`:

```
knowledge_base:
  web_search:
    enabled: false
```

## What's next
