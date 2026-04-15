# User states

Source: https://developer.1password.com/docs/cli/user-states/

State values
- `ACTIVE` user has accepted invitation and can sign in.
- `REGISTERED` user accepted invitation but has not set up 1Password yet.
- `EXPIRED` or `EXPIRED_IN_TRAVEL_MODE` user can no longer access due to sign-in expiration or travel mode.
- `SUSPENDED` user is suspended.
- `DELETED` user deleted and cannot access.
- `TRANSFERRED` user transferred between accounts.
- `T_VAULT` user is for test/temporary vault contexts.

Examples
```bash
# List users and inspect state values
op user list --format json | jq '.[].state'
```
