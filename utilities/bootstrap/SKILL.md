---
name: bootstrap
description: "Clone a GitHub repo and set up a fully working local dev environment automatically."
---

# Environment Bootstrap

Clone a GitHub repo and set up a fully working local dev environment automatically.

## Usage

```bash
/bootstrap https://github.com/owner/repo
/bootstrap https://github.com/owner/repo --branch develop
```

## What It Does

1. **Clones** the repository to a temp workspace
2. **Detects** project type (Node, Python, Rust, Go, Ruby, or multi)
3. **Installs** required tools via mise (node, python, rust, go, pnpm, uv, etc.)
4. **Installs** dependencies (npm/pnpm/yarn install, pip/uv install, cargo build, etc.)
5. **Sets up** environment (.env from .env.example, docker-compose notes)
6. **Starts** the dev server and verifies it works
7. **Self-corrects** through common failures:
   - Mise trust errors
   - Engine mismatch (npm --force)
   - Permission issues (--unsafe-perm)
   - Lockfile conflicts
   - Missing build step
8. **Documents** the working setup in SETUP.md

## Supported Project Types

| Type | Detection | Package Manager |
|------|-----------|-----------------|
| Node | package.json | npm/pnpm/yarn/bun |
| Python | pyproject.toml, requirements.txt | pip/uv/poetry |
| Rust | Cargo.toml | cargo |
| Go | go.mod | go mod |
| Ruby | Gemfile | bundle |

## Example Output

```
🚀 Environment Bootstrap Agent Starting...
   Repository: https://github.com/vercel/next.js
   Work directory: /tmp/bootstrap-next.js-1234567890

📦 Step 1: Cloning repository...
   ✅ Repository cloned

🔍 Step 2: Detecting project type...
   Detected project type: node
   Configs found: package-json, pnpm-lock, mise-toml

🛠️  Step 3: Installing required tools...
   Tools to install: node@20, pnpm@latest
   Installing node@20...
   Installing pnpm@latest...
   ✅ Tools installed

📥 Step 4: Installing dependencies...
   Running: pnpm install
   ✅ Dependencies installed

⚙️  Step 5: Setting up environment...
   Found .env.example, copying to .env

🚀 Step 6: Starting dev server...
   Attempting to start: pnpm dev
   ✅ Dev server started successfully

📝 Step 7: Documenting setup...
   ✅ SETUP.md created at /tmp/bootstrap-next.js-1234567890/repo/SETUP.md

✅ Bootstrap complete!
```

## Troubleshooting

If bootstrap fails:

1. Check `SETUP_FAILED.md` in the work directory
2. Review the error log for specific failures
3. Common fixes:
   - Run `mise trust` manually if tools aren't loading
   - Check Docker is running if docker-compose is needed
   - Verify network access for package downloads
