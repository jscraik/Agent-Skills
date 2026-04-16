# op read

Source: https://developer.1password.com/docs/cli/reference/commands/read/

Key points
- Reads a secret reference and prints it to stdout by default.
- Use `--out-file` to write to a file (for example certificates/keys).
- Supports attributes and query parameters on secret references.

Examples
```bash
op read op://app-prod/db/password
op read --out-file ./cert.pem "op://Ops/Certificates/Prod TLS/cert.pem?attribute=content"
```
