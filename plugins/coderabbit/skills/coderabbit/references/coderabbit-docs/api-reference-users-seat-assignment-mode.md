---
source: https://docs.coderabbit.ai/api-reference/users-seat-assignment-mode
---

# Seat Assignment Mode

Update the organization seat-assignment mode. This endpoint is available only to fully self-hosted organizations on enterprise plans.

## POST /v1/users/seats/assignment

Requires **Admin** role. See Seat assignment docs for mode behavior.

To fetch the current mode before updating, call `GET /v1/users` and read the seat-assignment mode in the response payload.

### cURL example

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

### Body parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `mode` | enum<string> | Yes | Seat assignment mode: `automatic`, `manual`. |

### Response (200)

```json
{
  "mode": "manual"
}
```

### Error responses

| Status | Description |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized |
| 402 | Payment Required |
| 403 | Forbidden |
| 410 | Gone |
| 429 | Too Many Requests |
| 500 | Internal Server Error |
