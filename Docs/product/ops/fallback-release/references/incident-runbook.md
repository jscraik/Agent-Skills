# Fallback Release Incident Runbook

Quick reference for responding to CI incidents requiring fallback release.

## Incident Severity Levels

### P1 - Critical (Immediate Fallback)
- GitHub Actions major incident affecting all workflows
- Security patch needed within 2 hours
- Release blocking production incident

**Response:** Activate fallback immediately

### P2 - High (Consider Fallback)
- Workflow queue time > 30 minutes
- API rate limit < 10%
- Minor GitHub incident affecting builds

**Response:** Wait 15 minutes, then activate fallback if not resolved

### P3 - Medium (Monitor)
- Workflow queue time 15-30 minutes
- API rate limit 10-25%
- Degraded performance

**Response:** Continue monitoring, prepare fallback

## Activation Checklist

### 1. Incident Declaration (2 minutes)
- [ ] Verify GitHub Status page shows incident
- [ ] Check #incidents Slack channel for existing thread
- [ ] Post in #incidents: "Activating fallback release for [VERSION]"

### 2. Environment Verification (5 minutes)
```bash
# Run automated verification
./Infrastructure/scripts/fallback-release/verify-env.sh

# Check primary CI status
gh run list --workflow=release.yml --limit 5
```

- [ ] Environment verification passed
- [ ] Primary CI confirmed stuck

### 3. Build Activation (20 minutes)
```bash
export FALLBACK_REASON="ci-queue-congestion"
export INCIDENT_URL="https://www.githubstatus.com/incidents/xxx"

./Infrastructure/scripts/fallback-release/build.sh \
    --version X.Y.Z \
    --output ./fallback-artifacts
```

- [ ] Build started
- [ ] Tests passing
- [ ] Artifacts generated

### 4. Artifact Signing (5 minutes)
```bash
./Infrastructure/scripts/fallback-release/sign-artifacts.sh ./fallback-artifacts
```

- [ ] Checksums generated
- [ ] GPG signatures created
- [ ] Signatures verified

### 5. Verification (10 minutes)
```bash
./Infrastructure/scripts/fallback-release/verify-artifacts.sh ./fallback-artifacts
./Infrastructure/scripts/fallback-release/test-installer.sh X.Y.Z ./fallback-artifacts
```

- [ ] Manifest valid
- [ ] Checksums verified
- [ ] Signatures valid
- [ ] Installer test passed

### 6. Publication (5 minutes)
```bash
./Infrastructure/scripts/fallback-release/publish.sh X.Y.Z ./fallback-artifacts
```

- [ ] Artifacts uploaded to cache
- [ ] Git tag created
- [ ] GitHub release published

### 7. Communication (ongoing)
- [ ] Update #incidents with completion
- [ ] Notify #releases channel
- [ ] Update status page if applicable

## Decision Flowchart

```
                    ┌─────────────────┐
                    │  CI Incident    │
                    │   Detected      │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │ Check GitHub    │
                    │ Status Page     │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        Major Incident   Minor       No Incident
              │         Incident         │
              │              │              │
        ┌─────▼─────┐   ┌──▼───┐    ┌────▼────┐
        │  P1       │   │  P2  │    │ Monitor │
        │ Immediate │   │ Wait │    │         │
        │ Fallback  │   │ 15m  │    └────┬────┘
        └─────┬─────┘   └──┬───┘         │
              │            │              │
              └────────────┼──────────────┘
                           │
                    ┌──────▼──────┐
                    │  Verify     │
                    │ Environment │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │    Build    │
                    │   Fallback  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Verify    │
                    │  Artifacts  │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Publish   │
                    │   Release   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │   Notify    │
                    │    Team     │
                    └─────────────┘
```

## Recovery Procedures

### When Primary CI Recovers

1. **Sync Artifacts to Primary Registry**
   ```bash
   ./Infrastructure/scripts/fallback-release/sync-to-primary.sh X.Y.Z
   ```

2. **Verify Artifact Parity**
   ```bash
   # Compare checksums
   diff <(curl -s $PRIMARY_URL/checksum.txt) <(curl -s $FALLBACK_URL/checksum.txt)
   ```

3. **Update Documentation**
   - Add incident to fallback release log
   - Update runbooks if new issues discovered

### Rollback Procedure

If fallback release is faulty:

```bash
# 1. Mark as pre-release (hide from default view)
gh release edit vX.Y.Z --prerelease

# 2. Yank from package registry (if applicable)
cargo yank --vers X.Y.Z

# 3. Delete tag (if needed)
git push --delete origin vX.Y.Z
git tag -d vX.Y.Z

# 4. Announce rollback
# Post in #incidents and #releases
```

## Contact Information

| Role | Contact | Escalation |
|------|---------|------------|
| Primary On-Call | #on-call | 15 min |
| Release Engineer | #releases | 30 min |
| Engineering Manager | @eng-manager | 1 hour |
| VP Engineering | @vp-eng | 2 hours |

## Reference Documents

- [Fallback Flow Specification](./fallback-flow-spec.md)
- [Environment Verification](./env-verification.md)
- [Build Manifest Schema](./manifest-schema.json)
- [Main SKILL.md](../SKILL.md)

## Post-Incident Template

```markdown
## Fallback Release Incident Report

**Date:** YYYY-MM-DD
**Severity:** P1/P2/P3
**Version:** X.Y.Z
**Duration:** HH:MM

### Summary
Brief description of the incident and resolution.

### Timeline
- HH:MM - Incident detected
- HH:MM - Fallback activated
- HH:MM - Build started
- HH:MM - Build completed
- HH:MM - Artifacts verified
- HH:MM - Release published
- HH:MM - Primary CI recovered

### Root Cause
What caused the primary CI to fail?

### Impact
- Release delayed by X minutes
- Y customers affected
- Z services waiting for deployment

### Lessons Learned
What can we improve?

### Action Items
- [ ] Item 1 (@owner, due date)
- [ ] Item 2 (@owner, due date)
```
