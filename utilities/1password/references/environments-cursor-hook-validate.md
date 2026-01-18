# Environments: Cursor hook validation

Source: https://developer.1password.com/docs/environments/cursor-hook-validate/

Key points
- The Cursor hook validates that required environment variables exist before running a command.
- Useful to prevent tooling from running when secrets are missing.
- Intended for teams using Cursor with 1Password Environments.

Example file locations (from docs)
- Hook script: `~/.cursor/hooks/1password-validate-env`
- Cursor hooks config: `~/.cursor/hooks.json`
- Environments config: `~/.1password/environments.toml`
- Log file: `/tmp/1password-cursor-hooks.log`

Example workflow
1) Configure required env vars in the Environments UI.
2) Ensure `~/.1password/environments.toml` includes `required` env vars and `mount_paths`.
3) Add the hook to `~/.cursor/hooks.json` under `beforeShellExecution`.
4) Run a command in Cursor; hook blocks if required vars are missing.

Notes
- Use `DEBUG=1` when running the hook to get verbose logging.
- Keep required vars minimal and aligned to project needs.
