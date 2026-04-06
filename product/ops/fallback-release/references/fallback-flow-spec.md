# Fallback Release Flow Specification

## Overview

This document specifies the deterministic fallback release process when primary CI (GitHub Actions) is unavailable due to:
- Queue congestion (>30 min queue time)
- Rate limiting (API 403/429 responses)
- Service incidents (GitHub Status page confirms)
- Scheduled maintenance windows

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Primary CI    │────→│   Health Check   │────→│  Normal Release │
│ (GitHub Actions)│     │   (Every 5 min)  │     │   (Default)     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               │ Unhealthy
                               ▼
                       ┌──────────────────┐
                       │ Incident Detected│
                       │   (Manual + Auto)│
                       └──────────────────┘
                               │
                               ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Build Manifest │←────│  Fallback Build  │────→│  GPG Signatures │
│    (JSON)       │     │  (Local/Builder) │     │  + SHA256 Sums  │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                               │
                               ▼
                       ┌──────────────────┐
                       │  Artifact Cache  │
                       │  (S3/Minio/R2)   │
                       └──────────────────┘
                               │
                               ▼
                       ┌──────────────────┐
                       │  Git Tag + Notes │
                       │  (via API/CLI)   │
                       └──────────────────┘
```

## Stuck/Timeout Detection

### Detection Methods

1. **Automated Monitoring** (`scripts/fallback-release/monitor-ci.sh`)
   ```bash
   # Polls GitHub Actions API every 5 minutes
   # Triggers alert if:
   # - Workflow queued > 30 minutes
   # - API returns 403/429
   # - Status page shows incident
   ```

2. **Manual Verification Commands**
   ```bash
   # Check recent workflow runs
   gh run list --workflow=release.yml --limit 5 --json status,startedAt
   
   # Check specific run status
   gh run view $(gh run list --workflow=release.yml --limit 1 --json databaseId -q '.[0].databaseId')
   
   # Verify GitHub API rate limits
   gh api rate_limit | jq '.resources.core'
   ```

### Decision Matrix

| Condition | Threshold | Action |
|-----------|-----------|--------|
| Workflow queued | > 30 minutes | Consider fallback |
| API rate limit remaining | < 10% | Consider fallback |
| GitHub Status | Major incident | Activate fallback |
| Security patch needed | < 2 hours | Activate fallback |
| Release blocker | End of business | Activate fallback |

## Alternate Build Path

### Builder Environment Requirements

**Hardware:**
- x86_64 or arm64 Linux/macOS
- 8GB+ RAM
- 50GB+ free disk
- Network access to package registries

**Software (Pinned Versions):**
```bash
# Fallback builder uses exact same versions as CI
RUST_VERSION="1.75.0"          # From rust-toolchain.toml
NODE_VERSION="20.10.0"         # From .nvmrc
PYTHON_VERSION="3.12.1"        # From .python-version
JUST_VERSION="1.22.0"          # From Cargo.lock
```

### Build Process

```bash
#!/bin/bash
# scripts/fallback-release/build.sh

set -euo pipefail

VERSION="$1"
OUTPUT_DIR="$2"
MANIFEST_FILE="$OUTPUT_DIR/fallback-build-manifest.json"

# 1. Verify clean git state
if [[ -n $(git status --porcelain) ]]; then
    echo "ERROR: Working tree not clean"
    exit 1
fi

# 2. Verify we're on main
if [[ $(git branch --show-current) != "main" ]]; then
    echo "ERROR: Not on main branch"
    exit 1
fi

# 3. Create build manifest start
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BUILD_ID=$(uuidgen)
GIT_SHA=$(git rev-parse HEAD)
GIT_SHA_SHORT=$(git rev-parse --short HEAD)

cat > "$MANIFEST_FILE" << MANIFEST
{
  "schema_version": "1.0.0",
  "build_id": "$BUILD_ID",
  "version": "$VERSION",
  "git_sha": "$GIT_SHA",
  "git_sha_short": "$GIT_SHA_SHORT",
  "timestamp": "$TIMESTAMP",
  "builder": {
    "hostname": "$(hostname)",
    "os": "$(uname -s)",
    "arch": "$(uname -m)",
    "user": "$(whoami)"
  },
  "ci_fallback": {
    "reason": "${FALLBACK_REASON:-manual}",
    "incident_url": "${INCIDENT_URL:-null}",
    "triggered_by": "$(whoami)"
  },
  "toolchain": {
    "rust": "$(rustc --version)",
    "cargo": "$(cargo --version)",
    "node": "$(node --version 2>/dev/null || echo 'N/A')",
    "python": "$(python3 --version)"
  },
  "artifacts": []
}
MANIFEST

# 4. Build with locked dependencies (reproducible)
echo "Building version $VERSION..."
cargo build --release --locked

# 5. Strip and optimize binaries
strip target/release/my-binary

# 6. Package artifacts
mkdir -p "$OUTPUT_DIR"
cp target/release/my-binary "$OUTPUT_DIR/my-binary-$VERSION-${GIT_SHA_SHORT}"

# 7. Generate checksums
cd "$OUTPUT_DIR"
for f in my-binary-*; do
    sha256sum "$f" > "$f.sha256"
    gpg --detach-sign --armor --output "$f.asc" "$f"
done

# 8. Update manifest with artifacts
jq --arg dir "$OUTPUT_DIR" '
  .artifacts = [
    $dir + "/" + (inputs | select(test("my-binary-")))
    | {
        name: (. | split("/") | last),
        path: .,
        sha256: (input_line | capture("(?<hash>[0-9a-f]{64})") | .hash),
        size: (input_line | capture("(?<size>[0-9]+)") | .size | tonumber)
      }
  ]
' < <(sha256sum my-binary-*) > "$MANIFEST_FILE.tmp"
mv "$MANIFEST_FILE.tmp" "$MANIFEST_FILE"

echo "Build complete: $OUTPUT_DIR"
echo "Manifest: $MANIFEST_FILE"
```

## Deterministic Checksums and Signatures

### Checksum Generation

All artifacts must have:
1. **SHA256 checksum** (hex-encoded, 64 chars)
2. **File size** in bytes
3. **GPG detached signature** (ASCII-armored)

```bash
# Standard checksum format (sha256sum compatible)
echo "a1b2c3d4...e5f6  my-binary-1.4.2-abc123" > my-binary-1.4.2-abc123.sha256

# Verification
sha256sum -c my-binary-1.4.2-abc123.sha256
```

### GPG Signing Requirements

```bash
# Key requirements:
# - 4096-bit RSA or Ed25519
# - Expiration > 1 year
# - Published to keyservers (keys.openpgp.org)
# - Email: releases@company.com

# Sign artifacts
gpg --detach-sign --armor \
    --local-user "releases@company.com" \
    --output my-binary-1.4.2-abc123.asc \
    my-binary-1.4.2-abc123

# Verify signature
gpg --verify my-binary-1.4.2-abc123.asc my-binary-1.4.2-abc123
```

### Build Manifest Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "Fallback Build Manifest",
  "type": "object",
  "required": [
    "schema_version",
    "build_id",
    "version",
    "git_sha",
    "timestamp",
    "builder",
    "ci_fallback",
    "artifacts"
  ],
  "properties": {
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$"
    },
    "build_id": {
      "type": "string",
      "format": "uuid"
    },
    "version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+(-[a-zA-Z0-9.-]+)?$"
    },
    "git_sha": {
      "type": "string",
      "pattern": "^[a-f0-9]{40}$"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "builder": {
      "type": "object",
      "properties": {
        "hostname": { "type": "string" },
        "os": { "type": "string" },
        "arch": { "type": "string" },
        "user": { "type": "string" }
      }
    },
    "ci_fallback": {
      "type": "object",
      "properties": {
        "reason": { "type": "string" },
        "incident_url": { "type": ["string", "null"] },
        "triggered_by": { "type": "string" }
      }
    },
    "artifacts": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "name": { "type": "string" },
          "path": { "type": "string" },
          "sha256": { "type": "string", "pattern": "^[a-f0-9]{64}$" },
          "size": { "type": "integer" },
          "signature_valid": { "type": "boolean" }
        }
      }
    }
  }
}
```

## Installer Path Verification

### Test Script

```bash
#!/bin/bash
# scripts/fallback-release/test-installer.sh

set -euo pipefail

VERSION="$1"
ARTIFACT_DIR="$2"
TEST_DIR=$(mktemp -d)

echo "Testing installer with fallback artifacts..."
echo "Version: $VERSION"
echo "Artifacts: $ARTIFACT_DIR"
echo "Test dir: $TEST_DIR"

# 1. Download artifacts from cache (simulate fresh install)
mkdir -p "$TEST_DIR/download"
cp "$ARTIFACT_DIR"/my-binary-"$VERSION"-* "$TEST_DIR/download/"

# 2. Verify checksums
cd "$TEST_DIR/download"
sha256sum -c ./*.sha256

# 3. Verify signatures
gpg --verify ./*.asc ./* 2>&1 | grep -q "Good signature"

# 4. Run installer
# (Assumes installer.sh is in the repo)
../repo/installer.sh \
    --version "$VERSION" \
    --binary-dir "$TEST_DIR/download" \
    --install-dir "$TEST_DIR/install"

# 5. Verify installation
if [[ ! -x "$TEST_DIR/install/bin/my-binary" ]]; then
    echo "ERROR: Binary not installed correctly"
    exit 1
fi

# 6. Test binary runs
"$TEST_DIR/install/bin/my-binary" --version | grep -q "$VERSION"

# Cleanup
rm -rf "$TEST_DIR"

echo "✅ Installer verification passed"
```

### Verification Checklist

- [ ] All artifacts download successfully
- [ ] SHA256 checksums match
- [ ] GPG signatures are valid
- [ ] Installer completes without errors
- [ ] Installed binary runs and reports correct version
- [ ] Installed binary passes basic functionality test
- [ ] Uninstaller works (if applicable)

## Artifact Cache Configuration

### S3/Minio/R2 Setup

```bash
# Environment variables for cache upload
export FALLBACK_CACHE_ENDPOINT="s3.amazonaws.com"
export FALLBACK_CACHE_BUCKET="mycompany-fallback-releases"
export FALLBACK_CACHE_REGION="us-east-1"
export AWS_ACCESS_KEY_ID="${FALLBACK_CACHE_KEY}"
export AWS_SECRET_ACCESS_KEY="${FALLBACK_CACHE_SECRET}"

# Upload script
s3cmd sync \
    --acl-public \
    "$ARTIFACT_DIR/" \
    "s3://$FALLBACK_CACHE_BUCKET/releases/$VERSION/"
```

### Cache Structure

```
s3://fallback-cache-bucket/
└── releases/
    └── 1.4.2/
        ├── fallback-build-manifest.json
        ├── my-binary-1.4.2-abc123
        ├── my-binary-1.4.2-abc123.sha256
        └── my-binary-1.4.2-abc123.asc
```

## Incident Documentation Template

```markdown
## Fallback Release Incident: $VERSION

**Date:** 2026-04-06  
**Version:** 1.4.2  
**Triggered by:** @username  
**CI Status:** [GitHub Status Incident](https://www.githubstatus.com/incidents/...)

### Root Cause
GitHub Actions queue congestion caused by infrastructure incident.

### Timeline
- 14:00 UTC: Release workflow triggered
- 14:30 UTC: Jobs still queued, incident detected
- 14:35 UTC: Fallback release initiated
- 14:50 UTC: Fallback artifacts built and signed
- 14:55 UTC: Artifacts uploaded to cache
- 15:00 UTC: Git tag created, release published

### Artifacts
- Build ID: `uuid-here`
- Cache URL: `s3://.../releases/1.4.2/`
- SHA256: `a1b2c3d4...`

### Verification
- [ ] Checksums match primary CI format
- [ ] GPG signatures valid
- [ ] Installer works correctly

### Follow-up
- [ ] Sync artifacts to primary registry
- [ ] Update runbooks if needed
```

## Recovery Procedures

### Post-Incident Sync

When primary CI recovers, sync fallback artifacts:

```bash
#!/bin/bash
# scripts/fallback-release/sync-to-primary.sh

VERSION="$1"
FALLBACK_URL="s3://$FALLBACK_CACHE_BUCKET/releases/$VERSION/"
PRIMARY_REGISTRY="..."

# Download from fallback
temp_dir=$(mktemp -d)
s3cmd sync "$FALLBACK_URL" "$temp_dir/"

# Verify integrity
cd "$temp_dir"
sha256sum -c ./*.sha256
gpg --verify ./*.asc ./*

# Upload to primary registry
# (registry-specific commands here)

# Update release notes
curl -X PATCH \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo/releases/$RELEASE_ID \
  -d '{
    "body": "...(updated with fallback provenance)..."
  }'
```

## Rollback Procedure

If fallback release is faulty:

```bash
# 1. Immediately mark release as pre-release (hidden)
gh release edit "v$VERSION" --prerelease

# 2. If published to package registry, yank/unlist
cargo yank --vers "$VERSION"
# or
npm unpublish "@scope/package@$VERSION"

# 3. Restore previous version as latest
git tag -d "v$VERSION"
git push --delete origin "v$VERSION"

# 4. Notify team
```
