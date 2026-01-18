# Environments: local env file

Source: https://developer.1password.com/docs/environments/local-env-file/

Key points
- The local `.env` destination writes environment variables from an Environment to a local `.env` file.
- The file is generated on your machine; do not commit it to version control.
- You can choose which environment variables are exported to the file.

Example UI labels (desktop app)
- Destinations tab > Configure destination.
- Destination type: Local .env file.
- File path: Choose a file location.
- Variable selection: Choose environment variables.

Steps (desktop app)
1) Open the environment, select the Destinations tab.
2) Choose Configure destination.
3) Select Local .env file.
4) Choose a file path (for example `.env` in your repo).
5) Choose environment variables, then Save.

Examples
- Keep `.env.tpl` in git, mount `.env` locally via Environments.
- Add `.env` to `.gitignore`.

Notes
- If the destination file is missing, Environments re-creates it when the app runs.
- If you move the file, update the destination path in the Environments UI.
