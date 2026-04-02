---
source: https://docs.coderabbit.ai/management/seat-assignment
---

# Seat Assignment

Understand how CodeRabbit assigns seats to users, including trial mode, manual approval, and auto-approval methods.

CodeRabbit ingests users from your git provider (GitHub, GitLab, Bitbucket, and Azure DevOps) and assigns seats based on your organization's active seat assignment mode. Understanding these modes helps you control who gets access to CodeRabbit reviews and how billing is affected.

## Seat assignment methods

### Trial mode

This mode is only active during the trial. In trial mode, users are automatically provisioned with a seat when they raise a PR in a repository where CodeRabbit is installed.

### Manual approval

In this mode, admins can update their seat counts manually. When a user without a seat raises a PR in a repository where CodeRabbit is installed, they receive a note on their PR indicating that they do not have a seat and will receive a free tier summary.

### Auto-approval

In this mode, users are automatically provisioned seats when they raise a PR in a repository where CodeRabbit is installed.
If there is an existing user with a seat who has not raised a CodeRabbit pull request in the last 30 days, that seat is reallocated to the new user. If all seats are taken, a new license is provisioned.

## Managing seat assignments

To change your seat assignment mode, navigate to **Team Management** in the CodeRabbit dashboard and click the settings icon next to **Invite Billing Admin**. From this menu, you can switch between auto-approval and manual approval modes. Click **Confirm** to save your changes.

## Pending unassignment

When you unassign a seat from a user on a monthly paid subscription, the seat is marked as "Pending unassignment" rather than being immediately unassigned. This allows for more flexibility in managing your team while maintaining fair billing practices.

### How "Pending unassignment" works

- **Delayed unassignment**: When you unassign a seat from a monthly subscriber, it remains active until the end of your current billing cycle
- **Continued access**: Users with "Pending unassignment" seats retain full CodeRabbit access until the billing cycle ends
- **Automatic cleanup**: At the end of the billing cycle, all "Pending unassignment" seats are automatically unassigned, and the users will lose the seat

### Billing implications

"Pending unassignment" seats are still counted as active seats for billing purposes during the current cycle. You will continue to be charged for these seats until they are automatically unassigned at the end of your billing period.
This approach ensures you get full value from your subscription while giving you the flexibility to adjust your team composition as needed.

## Troubleshooting

### Existing users having their seats removed

When auto-approval mode is enabled, users have their seats reassigned if they have not raised a PR in the last 30 days and a new user without a seat opens a PR.

### New users in auto-approval mode getting new licenses despite open seats

This is likely due to bot users or external users that have seats. These users are displayed separately from regular git provider organization members.

### Users without seats still receiving CodeRabbit reviews on their PRs

Users without paid seats to CodeRabbit still receive free-tier CodeRabbit reviews unless the `enable_free_tier` setting is disabled.

### Why does a user still have access after I unassigned their seat?

For monthly paid subscriptions, unassigned seats are marked as "Pending unassignment" and remain active until the end of the current billing cycle. This means users retain full CodeRabbit access during this period. See the Pending unassignment section for more details on this behavior.

### When will a "Pending unassignment" seat become available for reassignment?

"Pending unassignment" seats are automatically unassigned at the end of your billing cycle. Once the billing cycle ends, the seat becomes fully available for reassignment to a new user. Until then, the seat remains allocated to the original user.

## What's next
