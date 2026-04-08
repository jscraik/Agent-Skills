---
source: https://docs.coderabbit.ai/api-reference/users-list
---

# Users

List users in your organization with optional filtering by seat assignment and role.

## GET /v1/users

Requires **Admin** role. This feature is available only on the **Enterprise plan**.

### cURL example

```bash
curl --request GET \
  --url https://api.coderabbit.ai/v1/users \
  --header 'x-coderabbitai-api-key: <api-key>'
```

### Authorization

**x-coderabbitai-api-key** (string, header, required)

API key for authentication. Create API keys in the CodeRabbit dashboard.

### Query parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `seat_filter` | enum<string> | `all` | Filter by seat status: `all`, `assigned`, `unassigned`. |
| `role_filter` | enum<string> | `all` | Filter by role: `all`, `cr_member`, `cr_admin`. |

### Response (200)

```json
{
  "users": [
    {
      "user_id": "121358802",
      "seat_assigned": true,
      "role": "cr_admin"
    }
  ]
}
```

### Error responses

| Status | Description |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 410 | Gone |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
