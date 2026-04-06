# Environment Verification Checklist

Use this checklist before attempting a fallback release.

## Pre-Build Verification

### Hardware Requirements
- [ ] 8GB+ RAM available
- [ ] 50GB+ disk space available
- [ ] x86_64 or arm64 architecture
- [ ] Stable network connection

### Software Requirements

#### Required Tools
- [ ] Git 2.30+
- [ ] Rust toolchain (matches `rust-toolchain.toml`)
- [ ] sha256sum or shasum
- [ ] GPG 2.2+
- [ ] jq 1.6+
- [ ] curl

#### Optional Tools
- [ ] GitHub CLI (gh) - for release creation
- [ ] AWS CLI or s3cmd - for cache upload
- [ ] Docker - for containerized builds

### Credentials

#### GPG Signing Key
```bash
# Verify key exists and is not expired
gpg --list-secret-keys --keyid-format LONG releases@company.com

# Check expiration date
gpg --list-keys --with-colons releases@company.com | grep ^pub | cut -d: -f7
```

- [ ] Key exists in keyring
- [ ] Key not expired (or expires > 30 days)
- [ ] Key has 4096-bit RSA or Ed25519
- [ ] Private key is available (not just public)

#### Artifact Cache Access
```bash
# Test S3 connectivity
aws s3 ls s3://fallback-cache-bucket/
# or
s3cmd ls s3://fallback-cache-bucket/
```

- [ ] FALLBACK_CACHE_ENDPOINT set
- [ ] FALLBACK_CACHE_BUCKET set
- [ ] AWS_ACCESS_KEY_ID or equivalent set
- [ ] Upload test succeeds

#### GitHub Access
```bash
# Verify GitHub CLI auth
gh auth status

# Verify push access
git push --dry-run origin main
```

- [ ] gh CLI authenticated
- [ ] Can read repository
- [ ] Can push tags
- [ ] Can create releases (if using gh)

### Repository State

```bash
# Verify on main branch
git branch --show-current  # Should output: main

# Verify clean working tree
git status --porcelain  # Should output nothing

# Verify no unpushed commits
git log origin/main..HEAD  # Should output nothing
```

- [ ] On `main` branch
- [ ] Clean working tree
- [ ] No unpushed commits
- [ ] Git remote accessible

### Network Connectivity

```bash
# Test external dependencies
curl -s https://github.com > /dev/null
curl -s https://crates.io > /dev/null
curl -s https://registry.npmjs.org > /dev/null
```

- [ ] github.com reachable
- [ ] crates.io reachable (Rust)
- [ ] registry.npmjs.org reachable (Node)
- [ ] pypi.org reachable (Python)

## Automated Verification

Run the automated verification script:

```bash
./scripts/fallback-release/verify-env.sh
```

Expected output:
```
=== Fallback Release Environment Verification ===
...
=== Verification Summary ===
Errors: 0
Warnings: 0

✅ Environment ready for fallback builds!
```

## Troubleshooting

### GPG Key Issues

**Problem:** `gpg: signing failed: No secret key`

**Solution:**
```bash
# Import secret key if on new machine
gpg --import /path/to/secret-key-backup.asc

# Or generate new key (if allowed by policy)
gpg --full-generate-key
```

### Rate Limiting

**Problem:** GitHub API rate limit exceeded

**Solution:**
```bash
# Wait for rate limit reset
gh api rate_limit | jq '.resources.core.reset'

# Or use authenticated requests (higher limits)
gh auth login
```

### Cache Upload Failures

**Problem:** Cannot upload to S3

**Solution:**
```bash
# Verify credentials
aws sts get-caller-identity

# Check bucket exists
aws s3 ls s3://fallback-cache-bucket/

# Test with small file
echo "test" | aws s3 cp - s3://fallback-cache-bucket/test.txt
aws s3 rm s3://fallback-cache-bucket/test.txt
```

## Sign-Off

Before proceeding with fallback build:

| Check | Verified By | Date |
|-------|-------------|------|
| Hardware requirements | | |
| Software requirements | | |
| GPG key ready | | |
| Cache credentials | | |
| GitHub access | | |
| Repository state | | |
| Network connectivity | | |
| Automated verification | | |

**Authorized Fallback Builder:** _________________ **Date:** _________________
