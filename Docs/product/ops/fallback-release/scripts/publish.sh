#!/bin/bash
# Publish fallback artifacts to cache and create GitHub release

set -euo pipefail

VERSION="${1:-}"
ARTIFACT_DIR="${2:-}"

if [[ -z "$VERSION" || -z "$ARTIFACT_DIR" ]]; then
    echo "Usage: $0 <version> <artifact-directory>"
    exit 1
fi

if [[ ! -d "$ARTIFACT_DIR" ]]; then
    echo "ERROR: Artifact directory not found: $ARTIFACT_DIR"
    exit 1
fi

MANIFEST_FILE="$ARTIFACT_DIR/fallback-build-manifest.json"
if [[ ! -f "$MANIFEST_FILE" ]]; then
    echo "ERROR: Manifest not found: $MANIFEST_FILE"
    exit 1
fi

echo "=== Publishing Fallback Release ==="
echo "Version: $VERSION"
echo "Artifacts: $ARTIFACT_DIR"
echo ""

# Get build info
BUILD_ID=$(jq -r '.build_id' "$MANIFEST_FILE")
GIT_SHA=$(jq -r '.git_sha_short' "$MANIFEST_FILE")
FALLBACK_REASON=$(jq -r '.ci_fallback.reason' "$MANIFEST_FILE")

echo "Build ID: $BUILD_ID"
echo "Git SHA: $GIT_SHA"
echo "Fallback Reason: $FALLBACK_REASON"
echo ""

# 1. Verify artifacts are signed
echo "[1/4] Verifying artifacts are signed..."
UNSIGNED=0
for artifact in "$ARTIFACT_DIR"/*-"$VERSION"-*; do
    if [[ -f "$artifact" && ! "$artifact" =~ \.(sha256|asc|json)$ ]]; then
        if [[ ! -f "$artifact.asc" ]]; then
            echo "ERROR: Unsigned artifact: $(basename "$artifact")"
            ((UNSIGNED++)) || true
        fi
    fi
done

if [[ $UNSIGNED -gt 0 ]]; then
    echo ""
    echo "Run: ./Infrastructure/scripts/fallback-release/sign-artifacts.sh $ARTIFACT_DIR"
    exit 1
fi
echo "✓ All artifacts signed"

# 2. Upload to artifact cache
echo ""
echo "[2/4] Uploading to artifact cache..."

if [[ -z "${FALLBACK_CACHE_BUCKET:-}" ]]; then
    echo "WARNING: FALLBACK_CACHE_BUCKET not set, skipping cache upload"
else
    CACHE_PATH="s3://${FALLBACK_CACHE_BUCKET}/releases/${VERSION}/"
    echo "Destination: $CACHE_PATH"
    
    if command -v aws > /dev/null; then
        aws s3 sync "$ARTIFACT_DIR/" "$CACHE_PATH" --acl private
    elif command -v s3cmd > /dev/null; then
        s3cmd sync "$ARTIFACT_DIR/" "$CACHE_PATH"
    else
        echo "WARNING: No S3 client found (aws or s3cmd)"
    fi
    
    echo "✓ Artifacts uploaded"
fi

# 3. Create Git tag
echo ""
echo "[3/4] Creating Git tag..."
if git rev-parse "v$VERSION" > /dev/null 2>&1; then
    echo "Tag v$VERSION already exists"
else
    git tag -a "v$VERSION" -m "Release $VERSION (fallback build)"
    echo "Created tag: v$VERSION"
    
    # Push tag
    read -p "Push tag to origin? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "v$VERSION"
        echo "✓ Tag pushed"
    else
        echo "Tag created locally only (run: git push origin v$VERSION)"
    fi
fi

# 4. Create GitHub release (if gh CLI available)
echo ""
echo "[4/4] Creating GitHub release..."

if command -v gh > /dev/null && gh auth status > /dev/null 2>&1; then
    RELEASE_NOTES=$(cat << EOF
## Release $VERSION

**⚠️ Fallback Build**

This release was built using the fallback CI path due to primary CI unavailability.

### Build Information
- **Build ID:** $BUILD_ID
- **Git SHA:** $GIT_SHA
- **Fallback Reason:** $FALLBACK_REASON
- **Builder:** $(whoami)@$(hostname)

### Verification
\`\`\`bash
# Verify checksums
sha256sum -c *.sha256

# Verify signatures
gpg --verify *.asc *
\`\`\`

### Artifacts
$(cd "$ARTIFACT_DIR" && ls -la *-"$VERSION"-* | grep -v '\.sha256\|\.asc\|\.json' | awk '{print "- " $9 " (" $5 " bytes)"}')

---
Built with [fallback-release](../tree/main/product/Infrastructure/ops/fallback-release)
EOF
)

    # Check if release already exists
    if gh release view "v$VERSION" > /dev/null 2>&1; then
        echo "Release v$VERSION already exists"
        read -p "Update release notes? (y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            gh release edit "v$VERSION" --notes "$RELEASE_NOTES"
            echo "✓ Release updated"
        fi
    else
        gh release create "v$VERSION" \
            --title "v$VERSION (Fallback)" \
            --notes "$RELEASE_NOTES" \
            "$ARTIFACT_DIR"/*-"$VERSION"-*
        echo "✓ Release created"
    fi
else
    echo "GitHub CLI not available or not authenticated"
    echo "Create release manually at: https://github.com/$(git remote get-url origin | sed 's/.*://' | sed 's/\.git//')/releases/new"
fi

echo ""
echo "=== Publish Complete ==="
echo "Version: $VERSION"
echo "Build ID: $BUILD_ID"
echo ""
echo "Next steps:"
echo "  1. Verify release on GitHub"
echo "  2. Test installation from cache"
echo "  3. Update team on fallback release completion"
echo "  4. Document incident timeline"
