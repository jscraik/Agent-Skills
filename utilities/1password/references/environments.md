# 1Password Environments

Source: https://developer.1password.com/docs/environments/

Key points
- Environments (beta) store project secrets as environment variables in a dedicated 1Password location.
- Each environment is self-contained and can map to a project, stage, or app.
- Supports importing existing `.env` files and managing variables via the desktop app.
- Destinations currently include AWS Secrets Manager sync and local `.env` file mounting.

Requirements (from docs)
- 1Password subscription and desktop app on Windows or Linux.
- 1Password Developer experience enabled in the desktop app.

Example UI labels (desktop app)
- Enable Developer: Settings > Developer > Show 1Password Developer experience.
- Open Environments: Developer > View Environments.
- Create environment: New environment.
- Manage environment: Manage environment (Rename environment / Delete environment).
- Manage access: Manage environment > Manage access.
- Add people: Add People, then View & Edit permission choice.
- Add variables: Import .env file or New variable (Name, Value).
- Destinations: Destinations tab (Configure destination).

Steps (desktop app)
1) Open and unlock the 1Password desktop app.
2) Select your account/collection, then Settings > Developer > Show 1Password Developer experience.
3) Developer > View Environments.
4) Select New environment, name it, choose account, Save.
5) Add variables via Import .env file or New variable.
6) Configure destinations in the Destinations tab.

Examples
- Use one environment per repo (for example `app-prod`, `app-staging`).
- Import a `.env` file to seed variables, then manage per-variable access.

Notes
- Access is granted per environment; add members in Manage environment > Manage access.
- Deleting an environment is irreversible and stops integrations.
