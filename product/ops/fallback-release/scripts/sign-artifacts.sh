#!/bin/bash
# Sign artifacts with GPG and generate checksums

set -euo pipefail

ARTIFACT_DIR="${1:-}"
GPG_KEY="${FALLBACK_GPG_KEY:-releases@company.com}"

if [[ -z "$ARTIFACT_DIR" ]]; then
    echo "Usage: $0 <artifact-directory>"
    exit 1
fi

if [[ ! -d "$ARTIFACT_DIR" ]]; then
    echo "ERROR: Directory not found: $ARTIFACT_DIR"
    exit 1
fi

echo "=== Signing Artifacts ==="
echo "Directory: $ARTIFACT_DIR"
echo "GPG Key: $GPG_KEY"
echo ""

# Find all binary artifacts (not checksums/signatures/manifests)
mapfile -d '' artifacts < <( \
    find "$ARTIFACT_DIR" -maxdepth 1 -type f \
    ! -name "*.sha256" \
    ! -name "*.asc" \
    ! -name "*.json" \
    ! -name "*.md" \
    -print0 \
)

if [[ ${#artifacts[@]} -eq 0 ]]; then
    echo "ERROR: No artifacts found in $ARTIFACT_DIR"
    exit 1
fi

echo "Found ${#artifacts[@]} artifact(s) to sign"
echo ""

# Verify GPG key is available
echo "Verifying GPG key..."
if ! gpg --list-secret-keys --keyid-format LONG "$GPG_KEY" > /dev/null 2>&1; then
    echo "ERROR: GPG key not found: $GPG_KEY"
    echo "Set FALLBACK_GPG_KEY environment variable or generate a key:"
    echo "  gpg --full-generate-key"
    exit 1
fi

KEY_ID=$(gpg --list-secret-keys --keyid-format LONG "$GPG_KEY" | grep sec | head -1 | awk '{print $2}' | cut -d'/' -f2)
echo "Using key: $KEY_ID"
echo ""

# Sign each artifact
for artifact in "${artifacts[@]}"; do
    # Remove null byte from find output
    artifact="${artifact%$'\0'}"
    
    name=$(basename "$artifact")
    echo "Signing: $name"
    
    # Generate SHA256 checksum
    sha256sum "$artifact" > "$artifact.sha256"
    echo "  ✓ SHA256: $(cut -d' ' -f1 < "$artifact.sha256")"
    
    # Create GPG detached signature
    gpg --detach-sign --armor \
        --local-user "$GPG_KEY" \
        --output "$artifact.asc" \
        "$artifact"
    echo "  ✓ Signature: $name.asc"
    
    # Verify signature immediately
    if gpg --verify "$artifact.asc" "$artifact" > /dev/null 2>&1; then
        echo "  ✓ Signature verified"
    else
        echo "  ✗ Signature verification failed!"
        exit 1
    fi
    
    echo ""
done

# Update manifest with signature status
MANIFEST_FILE="$ARTIFACT_DIR/fallback-build-manifest.json"
if [[ -f "$MANIFEST_FILE" ]]; then
    echo "Updating manifest..."
    
    # Create signature verification data
    sig_data='{}'
    for artifact in "${artifacts[@]}"; do
        artifact="${artifact%$'\0'}"
        name=$(basename "$artifact")
        if gpg --verify "$artifact.asc" "$artifact" > /dev/null 2>&1; then
            sig_data=$(echo "$sig_data" | jq --arg n "$name" '. + {($n): true}')
        else
            sig_data=$(echo "$sig_data" | jq --arg n "$name" '. + {($n): false}')
        fi
    done
    
    # Update manifest
    jq --argjson sigs "$sig_data" '
        .artifacts = [.artifacts[] | .signature_valid = ($sigs[.name] // false)]
    ' "$MANIFEST_FILE" > "${MANIFEST_FILE}.tmp" && mv "${MANIFEST_FILE}.tmp" "$MANIFEST_FILE"
    
    echo "✓ Manifest updated"
fi

echo ""
echo "=== Signing Complete ==="
echo "Artifacts signed: ${#artifacts[@]}"
echo ""
echo "To verify:"
echo "  sha256sum -c *.sha256"
echo "  gpg --verify *.asc *"
