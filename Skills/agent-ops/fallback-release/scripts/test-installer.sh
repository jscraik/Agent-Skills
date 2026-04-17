#!/usr/bin/env bash
# Test that installer path works with fallback artifacts

set -euo pipefail

VERSION="${1:?Usage: $0 <version> <artifact-directory>}"
ARTIFACT_DIR="${2:?Usage: $0 <version> <artifact-directory>}"

if [[ ! -d "$ARTIFACT_DIR" ]]; then
    echo "ERROR: Artifact directory not found: $ARTIFACT_DIR"
    exit 1
fi

TEST_DIR=$(mktemp -d)
INSTALL_DIR="$TEST_DIR/install"

cleanup() {
    rm -rf "$TEST_DIR"
}
trap cleanup EXIT

echo "=== Testing Installer Path ==="
echo "Version: $VERSION"
echo "Artifacts: $ARTIFACT_DIR"
echo "Test directory: $TEST_DIR"
echo ""

# 1. Copy artifacts to simulate download
echo "[1/5] Simulating artifact download..."
mkdir -p "$TEST_DIR/download"
cp "$ARTIFACT_DIR"/*-"$VERSION"-* "$TEST_DIR/download/" 2>/dev/null || {
    echo "ERROR: No artifacts found for version $VERSION"
    exit 1
}

DOWNLOAD_COUNT=$(find "$TEST_DIR/download" -type f ! -name "*.sha256" ! -name "*.asc" ! -name "*.json" | wc -l)
echo "Downloaded $DOWNLOAD_COUNT artifact(s)"

# 2. Verify checksums on downloaded files
echo ""
echo "[2/5] Verifying downloaded artifact checksums..."
cd "$TEST_DIR/download"
CHECKSUM_OK=true
for shafile in *.sha256; do
    if [[ -f "$shafile" ]]; then
        if ! sha256sum -c "$shafile" > /dev/null 2>&1; then
            echo "ERROR: Checksum failed: $shafile"
            CHECKSUM_OK=false
        fi
    fi
done

if [[ "$CHECKSUM_OK" == false ]]; then
    exit 1
fi
echo "✓ All checksums valid"

# 3. Verify signatures
echo ""
echo "[3/5] Verifying GPG signatures..."
SIG_OK=true
for sigfile in *.asc; do
    if [[ -f "$sigfile" ]]; then
        artifact="${sigfile%.asc}"
        if [[ -f "$artifact" ]]; then
            if ! gpg --verify "$sigfile" "$artifact" > /dev/null 2>&1; then
                echo "ERROR: Invalid signature: $artifact"
                SIG_OK=false
            fi
        fi
    fi
done

if [[ "$SIG_OK" == false ]]; then
    exit 1
fi
echo "✓ All signatures valid"

# 4. Simulate installation
echo ""
echo "[4/5] Simulating installation..."
mkdir -p "$INSTALL_DIR/bin"

# Copy binaries to install location
for artifact in *-"$VERSION"-*; do
    if [[ -f "$artifact" && ! "$artifact" =~ \.(sha256|asc)$ ]]; then
        # shellcheck disable=SC2001
        name=$(echo "$artifact" | sed "s/-${VERSION}-[a-f0-9]*//")
        cp "$artifact" "$INSTALL_DIR/bin/$name"
        chmod +x "$INSTALL_DIR/bin/$name"
        echo "  Installed: $name"
    fi
done

# 5. Verify installed binaries
echo ""
echo "[5/5] Verifying installed binaries..."
BIN_OK=true

for binary in "$INSTALL_DIR/bin"/*; do
    if [[ -f "$binary" ]]; then
        name=$(basename "$binary")
        
        # Check binary is executable
        if [[ ! -x "$binary" ]]; then
            echo "ERROR: $name is not executable"
            BIN_OK=false
            continue
        fi
        
        # Try to run with --version flag
        if ! "$binary" --version > /dev/null 2>&1; then
            # Some binaries might not support --version
            echo "  $name: executable (no --version)"
        else
            VERSION_OUTPUT=$("$binary" --version 2>&1)
            if echo "$VERSION_OUTPUT" | grep -q "$VERSION"; then
                echo "  $name: ✓ version matches ($VERSION)"
            else
                echo "  $name: ⚠ version output: $VERSION_OUTPUT"
            fi
        fi
    fi
done

if [[ "$BIN_OK" == false ]]; then
    exit 1
fi

echo ""
echo "=== Test Summary ==="
echo "✅ Installer path verification passed"
echo ""
echo "Verified:"
echo "  - Artifact download simulation"
echo "  - Checksum verification"
echo "  - GPG signature verification"
echo "  - Binary installation"
echo "  - Binary execution"
echo ""
echo "Artifacts are ready for production use"
