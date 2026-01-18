# SSH keys

Source: https://developer.1password.com/docs/cli/ssh-keys/

Key points
- Generate or retrieve SSH keys stored in 1Password using the CLI.
- Use `op read` with `ssh-format=openssh` to output the private key in OpenSSH format.
- Prefer storing keys as items in a dedicated vault with least-privilege access.

Examples
```bash
op read "op://Ops/Deploy Key/private key?ssh-format=openssh" > id_ed25519
chmod 600 id_ed25519
```
