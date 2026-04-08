---
source: https://docs.coderabbit.ai/guides/scheduled-reports
---

CodeRabbit Pro offers automated recurring reports that provide insights into your organization’s activities. These reports can be customized and delivered through various channels to help teams stay informed about development progress.

## Setting up a recurring report

Navigate to Recurring Reports

Create new report

Click **Create Report**

Configure settings

Configure the following settings based on your team’s needs

### Schedule configuration

![Schedule Configuration](https://mintcdn.com/coderabbit/69LGK0BhaHIxrC15/images/guides/assets/images/report-params-f367cab2fedf802ef4ad557bf4cc3da8.png?fit=max&auto=format&n=69LGK0BhaHIxrC15&q=85&s=2876cdcee12cd3b332777e166123c50a)
The schedule configuration allows you to set precise timing for your reports:

#### Frequency options

* Days of Week
* Days of Month

* Select any combination of days (Sun-Sat)
* Set frequency (every 1-3 weeks)
* Ideal for weekly team syncs or sprint reviews

* Select specific dates (1-31)
* Special date handling:
  + **31st**: Runs on the last day of every month
  + **30th**: Skips February
  + **29th**: Only runs in February during leap years

#### Time settings

* Set specific time for report generation
* Choose from comprehensive timezone list (e.g., America/New\_York)
* Reports run at the specified time in the selected timezone

Choose a time that works for all team members, especially for distributed
teams across different time zones.

### Report parameters

Reports can be filtered using multiple parameters, match pull requests using the **IN** option and exclude pull requests using the **NOT\_IN** option:

## Repositories

Select specific repositories to monitor

## Labels

Filter by labels with operators:

* **IN**: Match any selected label
* **NOT\_IN**: Exclude any pr with select label
* **ALL**: Match all selected labels

## Users

Filter by specific users

## Teams

Filter by organization teams

Team filtering is not available for GitLab repositories

Each parameter can be:

* Added or removed as needed
* Combined with other parameters for precise filtering
* Modified using different operators

### Report content

Reports include comprehensive PR information:

* Labels and reviewers
* Comments and discussions
* Team associations

* Repository context
* Author information

PRs are marked as stale after 168 hours (7 days) of inactivity. This helps
identify potential workflow bottlenecks.

### Report templates

CodeRabbit offers several built-in templates:

## Daily Standup Report

A concise summary of pull requests and activities

## Sprint Report

A structured overview of sprint goals, completed tasks, in-progress work,
and blockers

## Release Notes

A high-level changelog with summary and significant changes

## Custom Templates

Create your own format using prompts. Allows for endless customization such
as native language reporting (Japanese, Spanish, French, etc.), custom
formatting, custom titles, and more. [Learn more about custom reports
→](/guides/custom-reports)

Example custom prompt:

```
Please provide a summary of:- All pull request activities- Related issues and comments- Code review discussions- Quality gate statusDo not include:- Bot conversations- Sequence diagrams
```

### Communication channels

Configure where your reports will be delivered:
![Report Delivery Platforms](https://mintcdn.com/coderabbit/69LGK0BhaHIxrC15/images/guides/assets/images/report-platforms-a696bfc2f918addcfb1d762df8a8f491.png?fit=max&auto=format&n=69LGK0BhaHIxrC15&q=85&s=1d90d45c6e95236fb4386c9e91b78206)

* Email
* Slack/Discord
* Microsoft Teams

* Enter individual email addresses
* Use distribution lists for team-wide delivery

Connect workspace

Connect your workspace through OAuth

Select channels

Select target channels

Bot installation

CodeRabbit bot will be installed automatically

Create webhook

Create a webhook in your Teams channel

Add URL

Add the webhook URL to CodeRabbit

Select channels

Select target channels

Create separate reports if you need to send to multiple channels with
different formats. Learn more about [custom report
formats](/guides/custom-reports).

## Managing reports

### Preview reports

Test your configuration using the **Preview Report** button to generate a
sample report instantly.

### Grouping options

Reports can be organized hierarchically using groups and subgroups:

* Primary Grouping
* Subgrouping

Select from these options to organize your main report structure:

* **None**: No grouping, flat list of items
* **Repository**: Group by source repository
* **Label**: Group by PR labels
* **Team**: Group by team ownership
* **User**: Group by PR author

After selecting a primary group, you can add a secondary level of organization:

* Choose any remaining grouping option for further categorization
* Subgroups create a nested hierarchy within primary groups
* Select “None” to use only primary grouping

Choose grouping options that match your team’s workflow. For example:

* Use Repository → Team for large multi-team organizations
* Use User → Label to track individual contributions by type
* Use Team → Repository to monitor team activity across repos

### Report lifecycle management

Control your reports through their entire lifecycle:

#### Editing reports

Make changes

Make your desired changes to any configuration settings

Save changes

Click the **Save** button to apply your changes

Changes take effect

Changes take effect from the next scheduled run

Remember to click **Save** when you’re done making changes. Your modifications
will be discarded if you navigate away without saving.

#### Disabling reports

Toggle the **Active** switch to temporarily pause a report.
Disabled reports:

* Maintain their configuration
* Skip scheduled runs
* Can be re-enabled at any time
* Show “Disabled” status in the dashboard

#### Deleting reports

Click delete

Click the **Delete** button (trash icon) next to the report

Confirm deletion

Confirm deletion in the modal

This action is permanent and cannot be undone. All report history and
configuration will be removed.

Deleting a report will immediately stop all scheduled runs and remove access
to historical reports. Consider disabling instead of deleting if you might
need the report again.

## Best practices

## Scheduling

* Align report timing with your team’s workflow
* Consider timezone differences for distributed teams

## Content

* Keep prompts focused on actionable information
* Use grouping to improve readability
* Exclude unnecessary details that may create noise

## Distribution

* Use channels your team actively monitors
* Consider creating separate reports for different audiences (e.g., management vs. development team)

## Custom Reports

Create personalized report formats

## What’s next

## Customize reports

Learn how to create custom report formats and prompts
