---
source: https://docs.coderabbit.ai/management/roles
---

# Role-based access

Control access to CodeRabbit administrative features by assigning Admin, Member, or Billing Admin roles to organization users.

## Overview of CodeRabbit roles

Every CodeRabbit account has exactly one role per organization. Each role determines access to billing, account management, and administrative functions.

### Admin

Full read/write access to all administrative features. Can manage other users' roles.

### Member

Read-only access to limited administrative settings. Appropriate for most developers.

### Billing Admin

Read/write access to subscription and billing management. Limited other administrative access.

CodeRabbit roles are independent from Git platform roles (GitHub, GitLab, etc.). Changing a CodeRabbit role doesn't affect Git platform permissions, and vice versa.

Roles only affect administrative features. All users can access developer features like code reviews based on their seat assignments, regardless of role.

## Default roles

CodeRabbit automatically assigns default roles based on Git platform permissions:

- **Admin (default)**: Users with ownership-level Git platform roles (GitHub Admin, Bitbucket Owner) receive the Admin role
- **Member (default)**: All other users receive the Member role by default

Default assignments happen only during initial account setup. Subsequent Git platform changes don't affect CodeRabbit roles.

## Manage user roles

### View current roles

1. Go to the CodeRabbit dashboard.
2. Choose the organization from the sidebar dropdown.
3. Click **Subscription** in the sidebar.

The main table shows Admin and Member accounts with their current roles. Click the **Billing Admins** tab to view billing administrators.

### Change user roles

You must have the Admin role to modify other users' roles.

1. Follow the steps above to reach your organization's Subscription page.
2. Click the dropdown in the user's **Role** column and select the new role.

You can only assign Admin and Member roles through this method. Billing Admin requires a separate invitation process.

### Add billing administrators

Billing Admin users don't consume seat licenses. Add them regardless of available seats.

1. Navigate to your organization's Subscription page.
2. Click **Invite Billing Admin**.
3. Provide the name and email address of the billing administrator.

Once a `Billing Administrator` has been successfully invited, they should use the following login process:

1. Navigate to the Sign in with email page.
2. Enter tenant name and email address.
3. A login pass should be received via email.
4. Use this login pass to access the account.

## Role permissions

Administrative functionality available by role:

| Resource | Admin | Member | Billing Admin |
| --- | --- | --- | --- |
| Learning Resources (Web Interface) | Read/Write | Read/Write | No access |
| Metrics/Dashboard | Read/Write | Read/Write | No access |
| Reports | Read/Write | Read/Write | No access |
| Integrations | Read/Write | Read/Write | No access |
| Repository Settings | Read/Write | Read/Write | No access |
| Organization Settings | Read/Write | Read-only | No access |
| User Management | Read/Write | Read-only | Read-only |
| Subscription Management | Read/Write | Read-only | Read/Write |
| Billing Management | Read/Write | No access | Read/Write |

All users can manage learnings through pull request comments regardless of role. The Learning Resources permissions apply only to web interface management.

## Custom roles for Enterprise

This feature is available exclusively as part of the Enterprise plan.

Enterprise customers can create custom roles with granular permissions beyond the built-in Admin, Member, and Billing Admin roles. Custom roles let you define exactly what each role can access — from organization settings to reports, learnings, and team management features.

For full details on creating and managing custom roles, see Custom roles and permissions.

## What's next

- Manage your subscription — Configure seat assignments, billing settings, and subscription details for your organization
- Custom roles and permissions — Create custom roles with granular permissions (Enterprise)
