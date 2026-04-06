#!/bin/bash
# Fallback Release Build Script
# Creates deterministic, reproducible builds with full provenance

set -euo pipefail

VERSION=""
OUTPUT_DIR=""
SKIP_TESTS=false

usage() {
    cat << USAGE
Usage: $0 --version VERSION --output DIR [OPTIONS]

Required:
  --version X.Y.Z    Version to build (semver)
  --output DIR       Output directory for artifacts

Options:
  --skip-tests       Skip test suite (not recommended)
  --help             Show this help

Environment:
  FALLBACK_REASON    Reason for fallback (e.g., "ci-queue-congestion")
  INCIDENT_URL       Link to incident status page

Example:
  $0 --version 1.4.2 --output ./fallback-artifacts
USAGE
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --version) VERSION="$2"; shift 2 ;;
        --output) OUTPUT_DIR="$2"; shift 2 ;;
        --skip-tests) SKIP_TESTS=true; shift ;;
        --help) usage; exit 0 ;;
        *) echo "Unknown option: $1"; usage; exit 1 ;;
    esac
done

# Validate inputs
if [[ -z "$VERSION" ]]; then
    echo "ERROR: --version is required"
    usage
    exit 1
fi

if [[ -z "$OUTPUT_DIR" ]]; then
    echo "ERROR: --output is required"
    usage
    exit 1
fi

# Validate semver
if ! [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.-]+)?$ ]]; then
    echo "ERROR: Version '$VERSION' is not valid semver"
    exit 1
fi

echo "=== Fallback Release Build ==="
echo "Version: $VERSION"
echo "Output: $OUTPUT_DIR"
echo "Reason: ${FALLBACK_REASON:-manual}"
echo ""

# 1. Verify clean git state
echo "[1/8] Verifying git state..."
if [[ -n $(git status --porcelain) ]]; then
    echo "ERROR: Working tree not clean"
    git status -sb
    exit 1
fi

if [[ "$(git branch --show-current)" != "main" ]]; then
    echo "ERROR: Not on main branch (current: $(git branch --show-current))"
    exit 1
fi

GIT_SHA=$(git rev-parse HEAD)
GIT_SHA_SHORT=$(git rev-parse --short HEAD)
echo "Git SHA: $GIT_SHA_SHORT"

# 2. Check version doesn't already exist
echo "[2/8] Checking version availability..."
if git rev-parse "v$VERSION" > /dev/null 2>&1; then
    echo "ERROR: Tag v$VERSION already exists"
    exit 1
fi
if [[ -f Cargo.toml ]]; then
    CURRENT_VERSION=$(grep -oP '(?<=^version = ")[^"]+' Cargo.toml | head -1)
    echo "Current version in Cargo.toml: $CURRENT_VERSION"
fi

# 3. Prepare output directory
echo "[3/8] Preparing output directory..."
mkdir -p "$OUTPUT_DIR"
MANIFEST_FILE="$OUTPUT_DIR/fallback-build-manifest.json"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
BUILD_ID=$(uuidgen 2>/dev/null || cat /proc/sys/kernel/random/uuid 2>/dev/null || echo "build-$(date +%s)")

# 4. Create initial manifest
echo "[4/8] Creating build manifest..."
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
  "toolchain": {},
  "artifacts": [],
  "build_log": []
}
MANIFEST

# Log build step
log_step() {
    local step="$1"
    local timestamp
    timestamp=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
    jq --arg step "$step" --arg time "$timestamp" \
        '.build_log += [{"step": $step, "timestamp": $time}]' \
        "$MANIFEST_FILE" > "${MANIFEST_FILE}.tmp" && mv "${MANIFEST_FILE}.tmp" "$MANIFEST_FILE"
}

# 5. Record toolchain versions
echo "[5/8] Recording toolchain..."
TOOLCHAIN='{}'
if command -v rustc > /dev/null; then
    TOOLCHAIN=$(echo "$TOOLCHAIN" | jq --arg v "$(rustc --version)" '. + {rust: $v}')
fi
if command -v cargo > /dev/null; then
    TOOLCHAIN=$(echo "$TOOLCHAIN" | jq --arg v "$(cargo --version)" '. + {cargo: $v}')
fi
if command -v node > /dev/null 2>&1; then
    TOOLCHAIN=$(echo "$TOOLCHAIN" | jq --arg v "$(node --version)" '. + {node: $v}')
fi
if command -v python3 > /dev/null; then
    TOOLCHAIN=$(echo "$TOOLCHAIN" | jq --arg v "$(python3 --version)" '. + {python: $v}')
fi

jq --argjson tc "$TOOLCHAIN" '.toolchain = $tc' "$MANIFEST_FILE" > "${MANIFEST_FILE}.tmp" && mv "${MANIFEST_FILE}.tmp" "$MANIFEST_FILE"
log_step "toolchain_recorded"

# 6. Run tests (unless skipped)
if [[ "$SKIP_TESTS" == false ]]; then
    echo "[6/8] Running tests..."
    if ! cargo test --locked; then
        echo "ERROR: Tests failed"
        exit 1
    fi
    log_step "tests_passed"
else
    echo "[6/8] Skipping tests (--skip-tests)"
    log_step "tests_skipped"
fi

# 7. Build release artifacts
echo "[7/8] Building release artifacts..."
if [[ -f Cargo.toml ]]; then
    # Rust project
    echo "Building with cargo..."
    cargo build --release --locked
    
    # Strip binaries for smaller size
    find target/release -maxdepth 1 -type f -executable | while read -r binary; do
        strip "$binary" 2>/dev/null || true
    done
    
    # Copy artifacts
    for binary in target/release/*; do
        if [[ -f "$binary" && -x "$binary" && ! "$binary" =~ \.(d|rlib|so|dylib)$ ]]; then
            name=$(basename "$binary")
            cp "$binary" "$OUTPUT_DIR/${name}-${VERSION}-${GIT_SHA_SHORT}"
        fi
    done
else
    echo "ERROR: No recognized project type (Cargo.toml not found)"
    exit 1
fi

log_step "build_complete"

# 8. Update manifest with artifacts
echo "[8/8] Finalizing manifest..."
ARTIFACTS='[]'
for artifact in "$OUTPUT_DIR"/*-"${VERSION}"-"${GIT_SHA_SHORT}"; do
    if [[ -f "$artifact" ]]; then
        name=$(basename "$artifact")
        sha256=$(sha256sum "$artifact" | cut -d' ' -f1)
        size=$(stat -c%s "$artifact" 2>/dev/null || stat -f%z "$artifact")
        
        ARTIFACTS=$(echo "$ARTIFACTS" | jq --arg n "$name" --arg p "$name" --arg s "$sha256" --argjson sz "$size" \
            '. + [{"name": $n, "path": $p, "sha256": $s, "size": $sz, "signature_valid": false}]')
    fi
done

# Fail if no artifacts were produced
if [[ $(echo "$ARTIFACTS" | jq length) -eq 0 ]]; then
    echo "ERROR: No build artifacts were produced"
    exit 1
fi

jq --argjson artifacts "$ARTIFACTS" '.artifacts = $artifacts' "$MANIFEST_FILE" > "${MANIFEST_FILE}.tmp" && mv "${MANIFEST_FILE}.tmp" "$MANIFEST_FILE"
log_step "manifest_finalized"

# Summary
echo ""
echo "=== Build Complete ==="
echo "Artifacts: $(echo "$ARTIFACTS" | jq length)"
echo "Manifest: $MANIFEST_FILE"
echo "Build ID: $BUILD_ID"
echo ""
echo "Next steps:"
echo "  1. Sign artifacts: ./scripts/fallback-release/sign-artifacts.sh $OUTPUT_DIR"
echo "  2. Verify artifacts: ./scripts/fallback-release/verify-artifacts.sh $OUTPUT_DIR"
echo "  3. Test installer: ./scripts/fallback-release/test-installer.sh $VERSION $OUTPUT_DIR"
echo "  4. Publish: ./scripts/fallback-release/publish.sh $VERSION $OUTPUT_DIR"
