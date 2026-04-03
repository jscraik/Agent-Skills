---
source: https://docs.coderabbit.ai/api-reference/users-list
---

# Users

List all users in your organization with optional filtering by seat assignment and role status.

## GET /v1/users

Requires **Admin** role. See Role-based access for details.

This feature is available exclusively as part of the **Enterprise plan**.

### cURL Example

```bash
curl --request GET \
  --url https://api.coderabbit.ai/v1/users \
  --header 'x-coderabbitai-api-key: <api-key>'
```

### Authorization

**x-coderabbitai-api-key** (string, header, required)
API key for authentication. You can create an API key from the CodeRabbit dashboard.

### Query Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `seat_filter` | enum\<string\> | `all` | Filter users by seat assignment status. Options: `all`, `assigned`, `unassigned` |
| `role_filter` | enum\<string\> | `all` | Filter users by role status. Options: `all`, `member`, `admin` |

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

### Error Responses

| Status | Description |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 410 | Gone |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
