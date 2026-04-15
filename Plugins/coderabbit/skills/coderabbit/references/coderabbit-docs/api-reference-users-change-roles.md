---
source: https://docs.coderabbit.ai/api-reference/users-change-roles
---

# Roles

Bulk change roles for up to 500 users. Returns partial success with details of which users succeeded or failed.

## POST /v1/users/roles

Requires **Admin** role. See Role-based access for details.

This feature is available exclusively as part of the **Enterprise plan**.

### cURL Example (promote)

```bash
curl --request POST \
  --url https://api.coderabbit.ai/v1/users/roles \
  --header 'Content-Type: application/json' \
  --header 'x-coderabbitai-api-key: <api-key>' \
  --data '{
  "role": "cr_admin",
  "user_ids": [
    "121358802",
    "22605247"
  ]
}'
```

### Authorization

**x-coderabbitai-api-key** (string, header, required)
API key for authentication. You can create an API key from the CodeRabbit dashboard.

### Body Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `role` | enum\<string\> | Yes | CodeRabbit user role to assign. Options: `cr_admin`, `cr_member` |
| `user_ids` | string[] | Yes | Array of provider user IDs. Length: 1-500 elements |

### Response (200)

```json
{
  "status": "success",
  "succeeded": ["121358802", "22605247"],
  "failed": []
}
```

Response for bulk operations with partial success model:

| Field | Type | Description |
|---|---|---|
| `status` | enum\<string\> | `success`, `partial_success`, or `failure` |
| `succeeded` | string[] | Array of user IDs that were successfully processed |
| `failed` | object[] | Array of failures with error details |

### Error Responses

| Status | Description |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 410 | Gone |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
