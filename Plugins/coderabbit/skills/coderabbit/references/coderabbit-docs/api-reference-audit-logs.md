---
source: https://docs.coderabbit.ai/api-reference/audit-logs
---

# Audit Logs

Returns a paginated list of organization-level audit log entries. Requires the Enterprise plan, Admin role, and a non-agentic API key.

## Request

### cURL

```
curl --request GET \
  --url 'https://api.coderabbit.ai/v1/audit-logs?page=1&page_size=25' \
  --header 'x-coderabbitai-api-key: <api-key>'
```

### Response (200)

```json
{
  "data": [
    {
      "id": "<string>",
      "action": "<string>",
      "actionLabel": "<string>",
      "resourceType": "<string>",
      "resourceTypeLabel": "<string>",
      "resourceSummary": "<string>",
      "actor": {
        "name": "<string>",
        "subtitle": "<string>",
        "isBot": true,
        "avatarUrl": "<string>"
      },
      "metadata": {},
      "ipAddress": "<string>",
      "createdAt": "2023-11-07T05:31:56Z",
      "relativeTime": "<string>"
    }
  ],
  "pagination": {
    "page": 123,
    "page_size": 123,
    "total_count": 123,
    "total_pages": 123,
    "has_next_page": true,
    "has_previous_page": true
  },
  "filter_options": {
    "actions": [
      {
        "value": "<string>",
        "label": "<string>",
        "count": 123
      }
    ],
    "resource_types": [
      {
        "value": "<string>",
        "label": "<string>",
        "count": 123
      }
    ]
  }
}
```

## Description

Returns a paginated list of organization-level audit log entries. Use the `search`, `actions`, `resource_types`, `date_from`, and `date_to` query parameters to filter results. Unknown query parameters are rejected with a `400` error.

For a guided overview of the feature, see the Audit Logs documentation.

## Authorizations

### x-coderabbitai-api-key

- **Type:** string (header, required)
- API key for authentication. You can create an API key from the CodeRabbit dashboard.

## Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `search` | string | - | Case-insensitive partial match on actor name. Max 200 characters. |
| `actions` | string | - | Comma-separated list of action keys to filter by. Up to 50 values. Example: `repository_create,api_key_delete` |
| `resource_types` | string | - | Comma-separated list of resource type keys to filter by. Up to 50 values. Example: `repository,api_key` |
| `date_from` | string (date-time) | - | Inclusive lower bound for the event timestamp, in ISO 8601 format. |
| `date_to` | string (date-time) | - | Inclusive upper bound for the event timestamp, in ISO 8601 format. Must be on or after `date_from`. |
| `page` | integer | 1 | Page number (1-based). |
| `page_size` | integer | 10 | Number of results per page. Max 100. |

## Response

### 200 - application/json

A paginated list of audit log entries.

| Field | Type | Description |
|---|---|---|
| `data` | object[] (required) | List of audit log entries for the current page. |
| `pagination` | object (required) | Pagination metadata. |
| `filter_options` | object (required) | Distinct action and resource type values present in the organization's log, useful for building filter UIs. |
