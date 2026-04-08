# Learnings

- **2026-04-08 [Codex]:** 1Password-backed SSH/Git flows can fail in login-shell automation with `Could not open a connection to your authentication agent` when `SSH_AUTH_SOCK` is only exported in `.zshrc`. Fix by exporting the 1Password socket in `.zprofile` (and keeping `.zshrc` aligned), then validate with `zsh -lc 'ssh-add -l'` and `ssh -T git@github.com`.
