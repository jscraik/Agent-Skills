---
name: bootstrap
description: Bootstrap a local development environment from a GitHub repository URL. Use when the user asks to clone a repo, install toolchains/dependencies, and validate a working dev setup automatically.
---

# Environment Bootstrap

Create a working local dev environment from a repository with reproducible setup steps and verification output.

## When to Use

Use this skill when the user asks to quickly stand up a new repo locally, reproduce onboarding setup, or validate that a project can run from a clean environment.

## Philosophy

- Prefer deterministic setup over ad-hoc shell steps.
- Detect and report blockers early so users can recover quickly.
- Keep generated setup notes actionable for the next contributor.

## Inputs

- Repository URL (required).
- Optional target branch/tag/ref.
- Optional runtime/tooling constraints (Node/Python/Rust versions, package manager preference).

## Procedure

1. Clone the requested repository into a clean workspace.
2. Detect project type(s) and required toolchain.
3. Install or activate required tools via mise where applicable.
4. Install project dependencies with the detected package manager/workflow.
5. Prepare environment scaffolding (`.env`, service dependencies, startup prerequisites).
6. Run a minimal startup/health verification command.
7. Record outcomes and next steps in setup artifacts.

## Outputs

- Bootstrapped local repository ready for development (or clear failure report).
- Concise setup summary (commands executed, detected stack, verification result).
- Follow-up artifact (`SETUP.md` or `SETUP_FAILED.md`) with reproducible instructions.

## Constraints

- Redact secrets and sensitive data by default in logs, setup artifacts, and copied config values.
- Do not silently bypass failing prerequisites; surface explicit remediation steps.
- Avoid destructive system changes outside the requested repo context without user approval.

## Validation

- Verify clone success and expected directory structure.
- Verify dependency install command exits successfully.
- Verify at least one project health check/start command outcome is recorded.
- Fail fast on unrecoverable setup gates and report first actionable blocker.

## Anti-patterns

- Running broad system modifications without clear user consent.
- Suppressing setup failures to produce a false "success" status.
- Hardcoding environment-specific assumptions without documenting them.

## Usage

```bash
/bootstrap https://github.com/owner/repo
/bootstrap https://github.com/owner/repo --branch develop
```

## Example Output

```
🚀 Environment Bootstrap Agent Starting...
   Repository: https://github.com/vercel/next.js
   Work directory: /tmp/bootstrap-next.js-1234567890

📦 Step 1: Cloning repository...
   ✅ Repository cloned

🔍 Step 2: Detecting project type...
   Detected project type: node

🛠️  Step 3: Installing required tools...
   ✅ Tools installed

📥 Step 4: Installing dependencies...
   ✅ Dependencies installed

🚀 Step 5: Verifying project startup...
   ✅ Health check completed

📝 Step 6: Documenting setup...
   ✅ SETUP.md created

✅ Bootstrap complete!
```

## Troubleshooting

If bootstrap fails:

1. Check `SETUP_FAILED.md` in the workspace.
2. Review first failing command and remediation notes.
3. Re-run with explicit toolchain versions if auto-detection was ambiguous.
