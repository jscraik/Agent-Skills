---
name: fallback-release
description: Deploy deterministic fallback releases when primary CI is unavailable. Use this skill when GitHub Actions is stalled due to queue congestion, rate limits, or incidents and a critical release cannot wait.
metadata:
  skill-type: ci_cd_deployment
  tags: [fallback, ci-resilience, release, disaster-recovery]
---

# Fallback Release

Emergency release path when primary CI (GitHub Actions) experiences queue congestion, rate limiting, or service incidents.

## When to use

- GitHub Actions workflows are stuck in "queued" state for >30 minutes
- Rate limit errors (403/429) from GitHub API during release
- Critical security patch needs immediate deployment
- Primary CI incident declared (check [GitHub Status](https://www.githubstatus.com/))
- `just release` fails due to CI infrastructure, not code issues

## When NOT to use

- Code quality checks are failing (fix the code first)
- Tests are failing (fix the tests first)
- Version conflicts exist (resolve conflicts first)
- You have not verified the fallback builder environment

## Philosophy

Primary CI remains the default path. Fallback releases are an escape hatch for emergencies only. They require:

- Strict environment verification before building
- Deterministic, reproducible build outputs
- Complete artifact provenance (manifests, checksums, signatures)
- Verification that installer paths still work

The goal is "acceptable parity" with primary CI outputs, not perfect replication.

## Constraints

- **Primary CI is default**: Only use fallback when CI is demonstrably stuck
- **Environment verification is mandatory**: Run `verify-env.sh` before any build
- **GPG signing required**: All artifacts must be signed with a trusted key
- **Deterministic builds**: Use locked dependencies, record all toolchain versions
- **Complete provenance**: Build manifest must document why fallback was used
- **Verification required**: Installer must work with fallback artifacts before publication
- **Network domains**: Scripts access github.com, crates.io, S3-compatible storage (configured by env)
- **Redaction required**: Redact secrets, credentials, token values, and signed-key material from logs, manifests, and incident summaries before sharing

## Required inputs

- [ ] Target version (semver, e.g., `1.4.2`)
- [ ] Confirmation primary CI is blocked (screenshot or status page link)
- [ ] Fallback builder environment verified (`./Infrastructure/scripts/fallback-release/verify-env.sh`)
- [ ] GPG signing key available for artifact signatures
- [ ] S3/cache destination credentials for artifact upload

## Deliverables

- Signed release artifacts with SHA256 checksums
- Fallback build manifest (`fallback-build-manifest.json`)
- Verification report confirming installer compatibility
- Incident documentation for post-mortem

## Failure mode

- **Environment verification fails:** Stop immediately. Do not attempt builds on unverified environments as they may produce non-reproducible artifacts.
- **GPG signing key unavailable:** Abort the release. Unsigned artifacts break the trust chain and cannot be published.
- **Cache/S3 upload fails:** Retries up to 3 times with exponential backoff. If still failing, document the issue and consider alternative storage locations.
- **Installer verification fails:** Do not publish. Fallback artifacts must be installer-compatible before release.
- **Checksum mismatch detected:** Treat as potential supply chain issue. Investigate before proceeding.

## Gotchas

- **Clock skew:** Ensure fallback builder has accurate time (use NTP) or GPG signatures may fail verification.
- **Stale dependencies:** `build.sh` uses locked dependencies, but verify the lock file is recent before starting.
- **Disk space:** Fallback builds can be large; ensure at least 10GB free on the artifact output directory.
- **Network egress:** Fallback uploads may incur egress charges; verify S3/cache credentials have write permissions.
- **Git state:** The build scripts require a clean git state. Any uncommitted changes will abort the build.

## Examples

Quick activation (5 minutes):

```bash
# 1. Verify CI is stuck
github-status  # Check https://www.githubstatus.com

# 2. Verify environment
./Infrastructure/scripts/fallback-release/verify-env.sh

# 3. Build
export FALLBACK_REASON="ci-queue-congestion"
./Infrastructure/scripts/fallback-release/build.sh --version 1.4.2 --output ./artifacts

# 4. Sign & verify
./Infrastructure/scripts/fallback-release/sign-artifacts.sh ./artifacts
./Infrastructure/scripts/fallback-release/verify-artifacts.sh ./artifacts

# 5. Publish
./Infrastructure/scripts/fallback-release/publish.sh 1.4.2 ./artifacts
```

Monitoring setup:

```bash
# Add to crontab for automated CI health monitoring
*/5 * * * * /path/to/repo/Infrastructure/scripts/fallback-release/monitor-ci.sh
```

## Procedure

### Phase 1: Incident Verification (5 min)

```bash
# Check GitHub Actions queue status
gh run list --workflow=release.yml --limit 5

# Check if this is a known incident
curl -s https://www.githubstatus.com/api/v2/status.json | jq '.status.indicator'

# Document the blockage
ask fallback-release verify-incident --version X.Y.Z
```

### Phase 2: Environment Validation (10 min)

```bash
# Verify fallback builder has all dependencies
./Infrastructure/scripts/fallback-release/verify-env.sh

# Check artifact cache connectivity
./Infrastructure/scripts/fallback-release/test-cache-upload.sh

# Validate signing key
 gpg --list-secret-keys --keyid-format LONG "releases@company.com"
```

### Phase 3: Deterministic Build (15 min)

```bash
# Build with locked dependencies (reproducible)
./Infrastructure/scripts/fallback-release/build.sh --version X.Y.Z --output ./artifacts

# Generate checksums and signatures
./Infrastructure/scripts/fallback-release/sign-artifacts.sh ./artifacts

# Create build manifest
./Infrastructure/scripts/fallback-release/generate-manifest.sh --version X.Y.Z --artifacts ./artifacts
```

### Phase 4: Verification (10 min)

```bash
# Verify artifacts match expected format
./Infrastructure/scripts/fallback-release/verify-artifacts.sh ./artifacts

# Test installer path works with fallback artifacts
./Infrastructure/scripts/fallback-release/test-installer.sh --version X.Y.Z --artifact-dir ./artifacts

# Compare checksums against previous releases for anomalies
./Infrastructure/scripts/fallback-release/checksum-audit.sh ./artifacts
```

### Phase 5: Publication (5 min)

```bash
# Upload to artifact cache/S3
./Infrastructure/scripts/fallback-release/publish.sh --version X.Y.Z --artifacts ./artifacts

# Create Git tag and release notes
./Infrastructure/scripts/fallback-release/create-release.sh --version X.Y.Z --fallback

# Notify team of fallback release completion
```

## Validation

Validation runs in fail-fast mode: stop at the first failed gate.

- [ ] Environment verified (`verify-env.sh` exits 0)
- [ ] Git state clean (`git status --porcelain` empty)
- [ ] On `main` branch (`git branch --show-current`)
- [ ] `fallback-build-manifest.json` exists and is valid JSON
- [ ] All artifacts have `.sha256` checksum files
- [ ] All artifacts have `.asc` GPG signatures
- [ ] Checksums verify (`sha256sum -c *.sha256`)
- [ ] Signatures verify (`gpg --verify *.asc`)
- [ ] Installer script successfully installs from fallback artifacts
- [ ] Version in artifacts matches target version
- [ ] Build timestamp is recent (< 1 hour)

If any validation fails, stop immediately and do not publish.

## Anti-patterns

- Using fallback path when primary CI is healthy (creates drift)
- Skipping GPG signatures for "speed" (breaks trust chain)
- Building without locked dependencies (non-reproducible)
- Not documenting the incident that triggered fallback
- Forgetting to sync fallback artifacts back to primary registry

## Recovery Checklist (Post-Incident)

After primary CI recovers:

1. [ ] Verify fallback artifacts match what primary CI would have built
2. [ ] Sync artifacts to primary artifact store
3. [ ] Update release notes with fallback provenance
4. [ ] Document incident timeline
5. [ ] Schedule post-mortem if downtime > 1 hour

## See Also

| Skill                              | When to use together                           |
| ---------------------------------- | ---------------------------------------------- |
| [[release]]                        | Primary release path when CI is healthy        |
| [[production-deployment]]          | Deploy fallback-built artifacts to production  |
| [[verification-before-completion]] | Validate fallback artifacts before publication |

**Topic map:** [[ops-engineering]]

## References

- [Fallback Release Flow Specification](/docs/product/ops/fallback-release/references/fallback-flow-spec.md)
- [Environment Verification Checklist](/docs/product/ops/fallback-release/references/env-verification.md)
- [Build Manifest Schema](/docs/product/ops/fallback-release/references/manifest-schema.json)
- [Incident Response Runbook](/docs/product/ops/fallback-release/references/incident-runbook.md)
