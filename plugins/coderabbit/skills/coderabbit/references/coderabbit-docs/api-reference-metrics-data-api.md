---
source: https://docs.coderabbit.ai/api-reference/metrics-data-api
---

# Metrics Data

Access CodeRabbit metrics data programmatically via REST API.

## GET /v1/metrics/reviews

Returns metrics for merged pull requests including complexity scores, review times, and comment breakdowns by severity and category.

This feature is available exclusively as part of the **Enterprise plan**.

### CSV Format

When using `format=csv`, the API returns a flat CSV structure with one row per pull request. The nested `coderabbit_comments` object is flattened into individual columns (e.g., `total_coderabbit_comments_posted`, `critical_comments_accepted`).
For the complete list of CSV columns and field descriptions, see Data Export - Exported fields.

### cURL Example

```bash
curl --request GET \
  --url 'https://api.coderabbit.ai/v1/metrics/reviews?start_date=2026-01-01&end_date=2026-01-20' \
  --header 'x-coderabbitai-api-key: <api-key>'
```

### Authorization

**x-coderabbitai-api-key** (string, header, required)
API key for authentication. You can create an API key from the CodeRabbit dashboard.

### Query Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `start_date` | string\<date\> | Yes | Start date in ISO 8601 format (YYYY-MM-DD) |
| `end_date` | string\<date\> | Yes | End date in ISO 8601 format (YYYY-MM-DD) |
| `organization_ids` | string | No | Filter by organization Git provider IDs (comma-separated, max 10). Self-hosted instances only. |
| `repository_ids` | string | No | Filter by repository Git provider IDs (comma-separated, max 10). |
| `user_ids` | string | No | Filter by author Git provider IDs (comma-separated, max 10). |
| `format` | enum\<string\> | No | Response format. Default: `json`. Options: `json`, `csv` |
| `limit` | integer | No | Maximum records to return. Default: 1000 |
| `cursor` | string | No | Pagination cursor for fetching next page of results |

### Response (200)

```json
{
  "data": [
    {
      "pr_url": "<string>",
      "author_id": "<string>",
      "author_username": "<string>",
      "organization_id": "<string>",
      "organization_name": "<string>",
      "repository_id": "<string>",
      "repository_name": "<string>",
      "created_at": "2023-11-07T05:31:56Z",
      "first_human_review_at": "2023-11-07T05:31:56Z",
      "last_commit_at": "2023-11-07T05:31:56Z",
      "merged_at": "2023-11-07T05:31:56Z",
      "estimated_complexity": 123,
      "estimated_review_minutes": 123,
      "coderabbit_comments": {
        "total": {
          "posted": 123,
          "accepted": 123
        },
        "severity": {
          "critical": { "posted": 123, "accepted": 123 },
          "major": { "posted": 123, "accepted": 123 },
          "minor": { "posted": 123, "accepted": 123 },
          "trivial": { "posted": 123, "accepted": 123 },
          "info": { "posted": 123, "accepted": 123 }
        },
        "category": {
          "security_and_privacy": { "posted": 123, "accepted": 123 },
          "performance_and_scalability": { "posted": 123, "accepted": 123 },
          "functional_correctness": { "posted": 123, "accepted": 123 },
          "maintainability_and_code_quality": { "posted": 123, "accepted": 123 },
          "data_integrity_and_integration": { "posted": 123, "accepted": 123 },
          "stability_and_availability": { "posted": 123, "accepted": 123 }
        }
      }
    }
  ],
  "next_cursor": "<string>"
}
```

### Error Responses

| Status | Description |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 413 | Payload Too Large |
| 429 | Too Many Requests |
