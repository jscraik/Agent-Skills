---
source: https://docs.coderabbit.ai/management/custom-roles
---

# Custom roles and permissions

Create and manage custom roles with granular permissions for your Enterprise organization in CodeRabbit.

This feature is available exclusively as part of the Enterprise plan. Please refer to our pricing page for more information about our plans and features.

## Overview

CodeRabbit includes three built-in system roles -- **Admin**, **Member**, and **Billing Admin** -- that cover common access patterns. With Custom RBAC (Role-Based Access Control), Enterprise customers can go further by defining additional roles with specific permissions tailored to their organization's structure and workflows. Each custom role controls access to individual resources at one of three levels: no access, read only, or read and write. Once created, custom roles are available across your organization, including in Team Management for per-user assignment.

- **Custom role creation** -- Create roles with a unique name and an optional description to reflect their purpose in your organization.
- **Granular permissions** -- Control access to each resource independently using **No access**, **Read only**, or **Read and Write** -- giving you precise control over what each role can do.
- **Default role assignment** -- Designate any custom role as the default so new users joining your organization are automatically assigned the right level of access.
- **Team Management integration** -- Assign custom roles to individual users directly from the Team Management page, alongside the built-in system roles.

**Navigation paths for Roles and permissions settings:**

- **Cloud:** `/settings/roles-permissions`
- **Self-hosted:** `/settings/account/roles-permissions`

---

## View roles and permissions

1. **Navigate to Roles and permissions** -- Go to your organization settings and open the **Roles and permissions** page. You will see a table listing all roles in your organization.
2. **Review the roles table** -- The table displays:
   - **Role name** -- the display name of the role
   - **Role type** -- labeled **System** for built-in roles (Admin, Member, Billing Admin) or **Custom** for user-created roles
   - **Description** -- optional text describing the role's purpose
   - **Number of assigned users** -- how many users currently hold this role
   - **Default role indicator** -- a star icon marks the role that is automatically assigned to new users
3. **Search for a role** -- Use the **Search** field at the top of the table to filter roles by name or description.
4. **Filter by role type** -- Use the **Filter** dropdown to narrow the list by type:
   - **All** (default) -- shows every role
   - **System** -- shows only the built-in Admin, Member, and Billing Admin roles
   - **Custom** -- shows only user-created custom roles

---

## Create a custom role

1. **Navigate to Roles and permissions** -- Go to your organization settings and open the **Roles and permissions** page.
2. **Open the creation form** -- Click the **Create role** button in the top-right corner.
3. **Enter a name** -- Enter a **Name** for the role. This field is required. Role names must be unique within your organization.
4. **Add an optional description** -- Optionally enter a **Description** to explain what the role is for.
5. **Save the role** -- Click **Save**. The new role is created and automatically populated with the default member role permissions as a baseline.
6. **Configure permissions** -- After saving, you are taken to the role detail page where you can adjust the permission matrix.

---

## Duplicate an existing role

Duplicating a role copies all of its permission settings into a new role, saving time when you need a role that is similar to an existing one.

1. **Locate the role to duplicate** -- On the **Roles and permissions** page, find the role you want to duplicate.
2. **Open the Actions menu** -- Click the **Actions** menu (the three-dot icon) at the far right of the role's row.
3. **Select Duplicate** -- A new role is immediately created with all the same permissions as the original. The new role's name is prefixed with **"Copy of"** followed by the original role name.
4. **Rename and adjust** -- Click the duplicated role's name to open its detail page. Update the name, description, and any permissions as needed.

---

## Edit role permissions

### Role detail page

When you open a custom role by clicking its name on the Roles and permissions page, the detail page displays:

- **Assigned users** -- the number of users currently assigned to this role
- **Role type** -- **System** or **Custom**
- **Created by** -- the user who created the role
- **Created on** -- the date the role was created

### Permission matrix

Each resource can be configured independently. Select the access level that applies to this role for each resource:

| Resource | No access | Read only | Read and Write |
| --- | --- | --- | --- |
| Organization settings | yes | yes | yes |
| Repository settings | yes | yes | yes |
| Reports | yes | yes | yes |
| Learnings | yes | yes | yes |
| Team Management | yes | yes | yes |
| Billing | yes | yes | -- |
| API access | yes | yes | -- |

System roles -- **Admin**, **Member**, and **Billing Admin** -- are view-only and cannot be edited. Their permission matrices are displayed for reference but all controls are disabled.

### Save or discard changes

1. On the **Roles and permissions** page, click the name of the custom role you want to edit.
2. For each resource in the permission matrix, select the desired access level: **No access**, **Read only**, or **Read and Write**.
3. Click **Save** to apply your changes. Click **Discard** to cancel all unsaved changes.

---

## Set a default role

The default role is automatically assigned to new users when they join your organization.

1. Go to **Roles and permissions**.
2. Click the **Actions** menu (three-dot icon) next to the role you want to set as the default.
3. Select **Set as default** from the dropdown menu. The role now displays a star icon in the **Default** column.
4. To remove the default designation, click the **Actions** menu next to the current default role and select **Remove as default**.

Only one role can be the default at a time. Setting a new role as default automatically removes the default designation from the previously assigned role.

---

## Delete a custom role

Deletion is blocked when one or more users are assigned to the role. All users must be reassigned to a different role before deletion is possible.

1. Go to **Roles and permissions**.
2. Check the **Assigned users** count. If greater than 0, go to **Team Management** and reassign those users first.
3. Click the **Actions** menu next to the role.
4. Select **Delete** from the dropdown menu.
5. Confirm the deletion in the confirmation dialog. This action cannot be undone.

---

## Assign roles in Team Management

The **Team Management** page supports both system and custom roles in the role selector.

1. Navigate to **Team Management**.
2. Find the user whose role you want to change.
3. Click the **Role** dropdown next to the user's name.
4. Select the desired role from the dropdown. The change is applied immediately.
5. If the update fails, the role assignment is automatically rolled back and an error message is displayed.

**Filter members by role:** Use the **Role** filter dropdown in the members list header to display only users assigned to a specific role. This filter includes custom roles.
