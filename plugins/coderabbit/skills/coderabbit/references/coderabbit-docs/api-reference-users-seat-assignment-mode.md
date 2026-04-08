---
source: https://docs.coderabbit.ai/api-reference/users-seat-assignment-mode
---

# Seat Assignment Mode

Update the seat assignment mode for the organization. Only accessible by fully self-hosted organizations with enterprise plans.

## POST /v1/users/seats/assignment

Requires **Admin** role. See Role-based access for details.

Only available for **fully self-hosted** organizations. See Seat assignment for details on assignment modes.

To retrieve the current seat assignment mode, use the Users endpoint. The seat assignment mode is included in the response.

### cURL Example

```bash
curl --request POST \
  --url https://api.coderabbit.ai/v1/users/seats/assignment \
  --header 'Content-Type: application/json' \
  --header 'x-coderabbitai-api-key: <api-key>' \
  --data '{
  "mode": "manual"
}'
```

### Authorization

**x-coderabbitai-api-key** (string, header, required)
API key for authentication. You can create an API key from the CodeRabbit dashboard.

### Body Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `mode` | enum\<string\> | Yes | The seat assignment mode to set. Options: `automatic`, `manual` |

### Response (200)

```json
{
  "mode": "manual"
}
```

### Error Responses

| Status | Description |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized |
| 402 | Payment Required |
| 403 | Forbidden |
| 410 | Gone |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
