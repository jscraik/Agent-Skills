# Fallback Release Quick Start

Emergency release path when GitHub Actions is unavailable.

## ⚡ 5-Minute Activation

### 1. Verify CI is Actually Stuck (30 seconds)

```bash
# Check if workflow has been queued > 30 minutes
gh run list --workflow=release.yml --limit 5

# Check GitHub Status
open https://www.githubstatus.com/
```

### 2. Verify Environment (1 minute)

```bash
./Infrastructure/scripts/fallback-release/verify-env.sh
```

If you see ✅, proceed. If you see errors, fix them first.

### 3. Build (2 minutes)

```bash
export FALLBACK_REASON="ci-queue-congestion"
export INCIDENT_URL="https://www.githubstatus.com/incidents/xxx"

./Infrastructure/scripts/fallback-release/build.sh \
    --version 1.4.2 \
    --output ./fallback-artifacts
```

### 4. Sign & Verify (1 minute)

```bash
# Sign artifacts
./Infrastructure/scripts/fallback-release/sign-artifacts.sh ./fallback-artifacts

# Quick verify
./Infrastructure/scripts/fallback-release/verify-artifacts.sh ./fallback-artifacts
```

### 5. Publish (30 seconds)

```bash
./Infrastructure/scripts/fallback-release/publish.sh 1.4.2 ./fallback-artifacts
```

Done! Your fallback release is live.

## 📋 Pre-Flight Checklist

Before you start, have these ready:

- [ ] Target version number (e.g., `1.4.2`)
- [ ] GitHub incident URL or evidence CI is stuck
- [ ] GPG key configured (`gpg --list-secret-keys`)
- [ ] Artifact cache credentials set
- [ ] On `main` branch with clean working tree

## 🔍 Common Issues

### "GPG key not found"

```bash
# Check available keys
gpg --list-secret-keys --keyid-format LONG

# Set the key to use
export FALLBACK_GPG_KEY=your-key@company.com
```

### "AWS credentials not found"

```bash
# For AWS S3
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export FALLBACK_CACHE_BUCKET=my-bucket

# Or for alternative S3 (Minio, R2)
export FALLBACK_CACHE_ENDPOINT=s3.example.com
```

### "Not on main branch"

```bash
git checkout main
git pull origin main
```

### "Working tree not clean"

```bash
# See what's uncommitted
git status

# Stash or commit changes
git stash
# or
git add . && git commit -m "wip"
```

## 🧪 Testing Without Publishing

Want to test the fallback flow without creating a release?

```bash
# Build with --skip-tests for speed (not recommended for real releases)
./Infrastructure/scripts/fallback-release/build.sh \
    --version 1.4.2 \
    --output ./test-artifacts \
    --skip-tests

# Verify everything works
./Infrastructure/scripts/fallback-release/verify-artifacts.sh ./test-artifacts
./Infrastructure/scripts/fallback-release/test-installer.sh 1.4.2 ./test-artifacts

# Clean up
rm -rf ./test-artifacts
```

## 📊 Monitoring CI Health

Set up automated monitoring:

```bash
# Add to crontab (runs every 5 minutes)
*/5 * * * * /path/to/repo/Infrastructure/scripts/fallback-release/monitor-ci.sh

# With Slack alerts
export FALLBACK_ALERT_WEBHOOK="https://hooks.slack.com/services/xxx"
*/5 * * * * /path/to/repo/Infrastructure/scripts/fallback-release/monitor-ci.sh
```

## 🚨 When NOT to Use Fallback

Don't use fallback if:

- Tests are failing (fix code first)
- Version conflicts exist (resolve first)
- Primary CI is healthy (wait for normal build)
- You haven't verified the environment

## 📚 Full Documentation

- [Complete Flow Specification](/docs/product/ops/fallback-release/references/fallback-flow-spec.md)
- [Environment Verification](/docs/product/ops/fallback-release/references/env-verification.md)
- [Incident Runbook](/docs/product/ops/fallback-release/references/incident-runbook.md)
- [Build Manifest Schema](/docs/product/ops/fallback-release/references/manifest-schema.json)

## 🆘 Getting Help

Stuck? Check these in order:

1. Run `./Infrastructure/scripts/fallback-release/verify-env.sh` - it tells you what's wrong
2. Check [Troubleshooting in env-verification.md](/docs/product/ops/fallback-release/references/env-verification.md#troubleshooting)
3. Review [Incident Runbook](/docs/product/ops/fallback-release/references/incident-runbook.md)
4. Ask in #releases or #incidents Slack channel
