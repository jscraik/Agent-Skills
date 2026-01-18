# Management: user

Source: https://developer.1password.com/docs/cli/reference/management-commands/user/

Key points
- User commands manage users, invitations, and suspension state.
- Cross-check user states with the user-states reference.

Examples
```bash
op user list --format json | jq '.[].state'
```
