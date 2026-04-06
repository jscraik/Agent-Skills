#!/bin/bash
# Verify fallback artifacts match expected format and are installable

set -euo pipefail

ARTIFACT_DIR="${1:-}"
EXIT_CODE=0

if [[ -z "$ARTIFACT_DIR" ]]; then
    echo "Usage: $0 <artifact-directory>"
    exit 1
fi

if [[ ! -d "$ARTIFACT_DIR" ]]; then
    echo "ERROR: Directory not found: $ARTIFACT_DIR"
    exit 1
fi

echo "=== Verifying Fallback Artifacts ==="
echo "Directory: $ARTIFACT_DIR"
echo ""

# 1. Check manifest exists
echo "[1/6] Checking manifest..."
MANIFEST_FILE="$ARTIFACT_DIR/fallback-build-manifest.json"
if [[ ! -f "$MANIFEST_FILE" ]]; then
    echo "ERROR: Build manifest not found: $MANIFEST_FILE"
    exit 1
fi

if ! jq empty "$MANIFEST_FILE" 2>/dev/null; then
    echo "ERROR: Manifest is not valid JSON"
    exit 1
fi

echo "✓ Manifest exists and is valid JSON"
VERSION=$(jq -r '.version' "$MANIFEST_FILE")
BUILD_ID=$(jq -r '.build_id' "$MANIFEST_FILE")
echo "  Version: $VERSION"
echo "  Build ID: $BUILD_ID"

# 2. Verify manifest schema
echo ""
echo "[2/6] Verifying manifest schema..."
REQUIRED_FIELDS=("schema_version" "build_id" "version" "git_sha" "timestamp" "builder" "ci_fallback" "artifacts")
for field in "${REQUIRED_FIELDS[@]}"; do
    if ! jq -e ".$field" "$MANIFEST_FILE" > /dev/null 2>&1; then
        echo "ERROR: Missing required field: $field"
        EXIT_CODE=1
    fi
done

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✓ All required fields present"
fi

# 3. Verify artifacts exist
echo ""
echo "[3/6] Verifying artifact files..."
ARTIFACT_COUNT=$(jq '.artifacts | length' "$MANIFEST_FILE")
echo "Expected artifacts: $ARTIFACT_COUNT"

jq -r '.artifacts[].name' "$MANIFEST_FILE" | while read -r name; do
    artifact_path="$ARTIFACT_DIR/$name"
    if [[ ! -f "$artifact_path" ]]; then
        echo "ERROR: Artifact missing: $name"
        EXIT_CODE=1
    fi
done

if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✓ All artifacts present"
fi

# 4. Verify checksums
echo ""
echo "[4/6] Verifying checksums..."
cd "$ARTIFACT_DIR"
CHECKSUM_ERRORS=0
CHECKSUM_COUNT=0

for shafile in *.sha256; do
    if [[ -f "$shafile" ]]; then
        ((CHECKSUM_COUNT++)) || true
        if ! sha256sum -c "$shafile" > /dev/null 2>&1; then
            echo "ERROR: Checksum failed for $shafile"
            ((CHECKSUM_ERRORS++)) || true
        fi
    fi
done

if [[ $CHECKSUM_COUNT -eq 0 ]]; then
    echo "ERROR: No checksum files found"
    EXIT_CODE=1
elif [[ $CHECKSUM_ERRORS -eq 0 ]]; then
    echo "✓ All checksums valid ($CHECKSUM_COUNT files)"
else
    echo "✗ $CHECKSUM_ERRORS checksum(s) failed"
    EXIT_CODE=1
fi

# 5. Verify signatures
echo ""
echo "[5/6] Verifying GPG signatures..."
SIG_ERRORS=0
SIG_COUNT=0

for sigfile in *.asc; do
    if [[ -f "$sigfile" ]]; then
        ((SIG_COUNT++)) || true
        artifact="${sigfile%.asc}"
        if [[ -f "$artifact" ]]; then
            if ! gpg --verify "$sigfile" "$artifact" > /dev/null 2>&1; then
                echo "ERROR: Signature verification failed for $artifact"
                ((SIG_ERRORS++)) || true
            fi
        fi
    fi
done

if [[ $SIG_COUNT -eq 0 ]]; then
    echo "ERROR: No signature files found"
    EXIT_CODE=1
elif [[ $SIG_ERRORS -eq 0 ]]; then
    echo "✓ All signatures valid ($SIG_COUNT files)"
else
    echo "✗ $SIG_ERRORS signature(s) failed"
    EXIT_CODE=1
fi

# 6. Compare with previous release (anomaly detection)
echo ""
echo "[6/6] Running anomaly checks..."

# Check file sizes are reasonable
SIZE_ANOMALIES=0
while IFS= read -r artifact; do
    name=$(echo "$artifact" | jq -r '.name')
    size=$(echo "$artifact" | jq -r '.size')
    
    # Flag if size is unusually small (< 1KB) or large (> 500MB)
    if [[ $size -lt 1024 ]]; then
        echo "WARNING: $name is very small (${size} bytes)"
        ((SIZE_ANOMALIES++)) || true
    elif [[ $size -gt 524288000 ]]; then
        echo "WARNING: $name is very large ($(numfmt --to=iec $size))"
        ((SIZE_ANOMALIES++)) || true
    fi
done < <( jq -c '.artifacts[]' "$MANIFEST_FILE" )

if [[ $SIZE_ANOMALIES -eq 0 ]]; then
    echo "✓ No size anomalies detected"
else
    echo "⚠ $SIZE_ANOMALIES size anomaly/ies detected (review recommended)"
fi

# Summary
echo ""
echo "=== Verification Summary ==="
if [[ $EXIT_CODE -eq 0 ]]; then
    echo "✅ All verification checks passed"
    echo ""
    echo "Artifacts ready for publication"
else
    echo "❌ Verification failed with errors"
    echo ""
    echo "Fix errors before publishing"
fi

exit $EXIT_CODE
