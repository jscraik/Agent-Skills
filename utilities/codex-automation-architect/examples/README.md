# Weekly Stale PR Triage Automation

Codex automation for identifying, categorizing, and recommending actions on stale pull requests.

## Quick Start

### 1. Import the Automation

**Via Codex Desktop:**
```bash
# Copy the automation spec to your project's .codex/automations/
mkdir -p .codex/automations
cp stale-pr-triage-automation.yaml .codex/automations/weekly-stale-pr-triage.yaml
```

**Via Codex CLI:**
```bash
codex automation create --file stale-pr-triage-automation.yaml
```

### 2. Configure for Your Project

Edit the `cwds` field to match your repository:

```yaml
cwds:
  - "/path/to/your/repo"
  # or for multiple repos:
  - "/path/to/repo-one"
  - "/path/to/repo-two"
```

### 3. Adjust Schedule (Optional)

Change the `rrule` to match your preferred schedule:

| Schedule | RRULE |
|----------|-------|
| Mon 9am (default) | `FREQ=WEEKLY;BYDAY=MO;BYHOUR=9;BYMINUTE=0` |
| Wed/Fri 10am | `FREQ=WEEKLY;BYDAY=WE,FR;BYHOUR=10;BYMINUTE=0` |
| Daily 8am | `FREQ=DAILY;BYHOUR=8;BYMINUTE=0` |

### 4. Prerequisites

Ensure these tools are available in the automation environment:

```bash
# Required
gh --version        # GitHub CLI v2.0+
jq --version        # jq 1.6+
git --version       # Git 2.30+

# Authenticate gh CLI
gh auth login
```

### 5. Test Run

Before enabling the recurring schedule, run a manual test:

```bash
# Via Codex CLI
codex automation run weekly-stale-pr-triage --cwd /path/to/repo

# Or trigger manually in Codex Desktop
# → Automations → weekly-stale-pr-triage → Run Now
```

## What It Does

1. **Fetches** all open PRs from GitHub
2. **Filters** PRs with no activity for >7 days
3. **Categorizes** each stale PR:
   - `needs-review` — waiting on reviewer
   - `blocked` — CI failing or merge conflicts
   - `abandoned` — no activity for >14 days
   - `ready-to-merge` — approved, green CI, just needs button click
   - `needs-author-action` — reviewer feedback pending
4. **Recommends** specific actions with copy-paste commands
5. **Outputs** a structured markdown report

## Safety Features

| Feature | Implementation |
|---------|---------------|
| Read-only by default | `sandbox: read-only` prevents writes |
| No auto-merge | Outputs draft commands; maintainer executes |
| No auto-close | Suggests closures; maintainer confirms |
| Graceful degradation | Handles auth errors, rate limits, missing tools |

## Output Example

```markdown
# Stale PR Triage Report - 2026-03-04

## Summary
- Total open PRs: 23
- Stale (>7 days): 5
- By category: needs-review (2), blocked (1), ready-to-merge (2)

## Action Items

### Ready to Merge
| PR | Title | Command |
|----|-------|---------|
| #142 | Fix auth bug | `gh pr merge 142 --squash` |

### Needs Review
| PR | Title | Draft Ping |
|----|-------|------------|
| #138 | Add analytics | @alice friendly ping—when you have a moment for review? |
```

## Customization

### Change stale threshold

Edit the `jq` filter in the prompt:

```bash
# Current: 7 days (7*24*60*60 seconds)
select(.updatedAt < (now - 7*24*60*60 | todateiso8601))

# Change to 14 days
select(.updatedAt < (now - 14*24*60*60 | todateiso8601))
```

### Add custom categories

Add new category rules to Step 4 in the prompt:

```yaml
| `security-critical` | Label `security` AND approved by security team |
```

### Send to Slack/Discord

Pipe the output to a webhook (requires write sandbox):

```bash
# Add to end of prompt:
curl -X POST -H "Content-Type: application/json" \
  -d "{\"text\": \"$(cat report.md)\"}" \
  $SLACK_WEBHOOK_URL
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `gh auth status` fails | Run `gh auth login` in the automation environment |
| Empty results | Check `gh pr list` works manually; verify repo has open PRs |
| Wrong timezone | Add `TZ` env var to automation config |
| Rate limited | Add `GH_TOKEN` env var with a Personal Access Token |

## Schema Reference

```yaml
schema_version: "1.0"          # Contract version
automation_spec:
  name: string                 # Unique identifier
  description: string          # Human-readable purpose
  status: active|paused        # Enable/disable
  rrule: string                # iCal recurrence rule
  cwds: string[]               # Target working directories
  runtime_constraints:         # Safety bounds
    approval_policy: never|explicit
    sandbox: read-only|workspace-write|full-access
    allow_destructive: boolean
  prompt: string               # The automation instructions
```

## Related Automations

- `dependabot-merge` — Auto-merge patch/minor dependabot PRs
- `release-notes-draft` — Generate release notes from merged PRs
- `issue-triage` — Categorize and label stale issues

## License

MIT — Part of the codex-automation-architect skill collection.
