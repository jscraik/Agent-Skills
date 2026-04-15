---
source: https://docs.coderabbit.ai/management/audit-logs
---

# Audit Logs

The Audit Logs give Enterprise organizations a searchable record of administrative actions taken across workspace settings, billing controls, seat management, and more. Use them to answer "who changed what, and when?" whether you're investigating an incident, satisfying a compliance review, or just keeping an eye on operational changes.

## Accessing Audit Logs

### Settings UI

Open the CodeRabbit dashboard and navigate to **Settings → Audit Logs**. The page is visible to **organization admins** on the Enterprise plan.
The log table shows four columns:

| Column | Description |
| --- | --- |
| **User** | The actor who performed the action, with their role (Admin, Member, Billing Admin, Bot, or System) |
| **Action** | What happened, e.g. "Added repository" or "Created API key" |
| **Resource Summary** | A short description of the specific resource affected |
| **Recency / Time** | Relative and absolute timestamp of when the action occurred |

#### Searching and filtering

Use the search bar to find entries by actor name. Narrow results further using the filter controls:

- **Action** — select one or more event types
- **Resource type** — select one or more resource categories
- **Date range** — set an inclusive start and end date/time

All filters can be combined. Filter counts refresh automatically so repeat investigations stay fast.

### REST API

The same data is available programmatically. This is useful for exporting entries to a SIEM, building custom compliance reports, or integrating audit data into internal tooling.
See the Audit Logs API reference for the complete parameter list, response schema, and code samples.

## What is logged

The Audit Logs capture high-signal administrative changes across your workspace:

| Resource | Events tracked |
| --- | --- |
| Organization | Creation and deletion |
| Repositories | Adding and removing repositories |
| Subscription | Subscription creation, updates, and cancellation |
| Seat management | Seat assignments and removals |
| Configuration | Organization-wide and repository-level config changes |
| User roles | Role promotions and demotions |
| API keys | API key creation and deletion |

## Common use cases

**Security review** — Search for a specific user to see all actions they have taken. Filter by `api_key_create` or `api_key_delete` to audit API key lifecycle. Use the date range filter to focus on a specific incident window.
**Access management audit** — Filter on seat assignment and role change events to review who was granted or removed access, and by which admin.
**Configuration change investigation** — Filter on configuration events to identify when a setting was changed and who changed it.
**Compliance reporting** — Export entries for a date range via the API to demonstrate administrative controls and a clear chain of custody.

## What's next
