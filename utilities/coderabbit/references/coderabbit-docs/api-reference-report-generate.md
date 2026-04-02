---
source: https://docs.coderabbit.ai/api-reference/report-generate
---

# Report Generate

Generate a developer activity report based on the provided parameters and date range. This endpoint may take up to 10 minutes to respond depending on the data volume.

## POST /v1/report.generate

### cURL Example

```bash
curl --request POST \
  --url https://api.coderabbit.ai/v1/report.generate \
  --header 'Content-Type: application/json' \
  --header 'x-coderabbitai-api-key: <api-key>' \
  --data '{
  "from": "2024-05-01",
  "to": "2024-05-15"
}'
```

### Authorization

**x-coderabbitai-api-key** (string, header, required)
API key for authentication. You can create an API key from the CodeRabbit dashboard.

### Body Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `from` | string\<date\> | Yes | Start date for the report in ISO 8601 format (YYYY-MM-DD) |
| `to` | string\<date\> | Yes | End date for the report in ISO 8601 format (YYYY-MM-DD) |
| `scheduleRange` | enum\<string\> | No | Available options: `Dates` |
| `prompt` | string | No | Custom prompt to specify what information should be included in the report and how it should be formatted |
| `promptTemplate` | enum\<string\> | No | Pre-defined template for the report format. Options: `Daily Standup Report`, `Sprint Report`, `Release Notes`, `Custom` |
| `parameters` | object[] | No | Array of filter parameters to narrow down the report scope |
| `groupBy` | enum\<string\> | No | Primary grouping for the report. Options: `NONE`, `REPOSITORY`, `LABEL`, `TEAM`, `USER`, `SOURCEBRANCH`, `TARGETBRANCH`, `STATE` |
| `subgroupBy` | enum\<string\> | No | Secondary grouping for the report. Options: `NONE`, `REPOSITORY`, `LABEL`, `TEAM`, `USER`, `SOURCEBRANCH`, `TARGETBRANCH`, `STATE` |
| `orgId` | string | No | Organization ID (optional) |

### Response (200)

```json
[
  {
    "group": "Developer Activity",
    "report": "*Developer Activity*:\n\n 🟢 **Update README.md** [#10](https://gitlab.com/master-group123/sub-group/project1/-/merge_requests/10)\n• Summary: The change updates the project description and modifies a section header for clearer instructions.\n• Last activity: 1 day ago, mergeable\n• Insights:\n - :magnifying_glass: @user2 Suggested updating the wording to make it clearer"
  }
]
```

### Error Responses

| Status | Description |
|---|---|
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 429 | Too Many Requests |
