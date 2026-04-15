#!/usr/bin/env bash
# Fallback Release Environment Verification
# Exits 0 if environment is ready for fallback builds, 1 otherwise

set -euo pipefail

ERRORS=0
WARNINGS=0

log_info() { echo "[INFO] $*"; }
log_warn() { echo "[WARN] $*"; ((WARNINGS++)) || true; }
log_error() { echo "[ERROR] $*"; ((ERRORS++)) || true; }

echo "=== Fallback Release Environment Verification ==="
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")"
echo ""

# 1. Check Git repository state
log_info "Checking git repository..."
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    log_error "Not in a git repository"
else
    # Sanitize git URL to remove credentials before logging
    raw_url=$(git remote get-url origin 2>/dev/null || echo 'unknown')
    # Remove user:password@ from URLs (e.g., https://user:pass@host -> https://host)
    sanitized_url=$(echo "$raw_url" | sed -E 's|://[^:]+:[^@]+@|://|g')
    log_info "Git repository: $sanitized_url"
    log_info "Current branch: $(git branch --show-current)"
    log_info "Git SHA: $(git rev-parse --short HEAD)"
fi

# 2. Check disk space (portable: works on both Linux and macOS)
log_info "Checking disk space..."
# Use df without -BG flag (GNU-only) and parse generically
AVAILABLE_KB=$(df . | awk 'NR==2 {print $4}')
# Convert KB to GB (handle both 1024 and 1000 based)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: df returns 512-byte blocks by default
    AVAILABLE_GB=$((AVAILABLE_KB / 1024 / 1024))
else
    # Linux: df returns 1K blocks by default
    AVAILABLE_GB=$((AVAILABLE_KB / 1024 / 1024))
fi
if [[ "$AVAILABLE_GB" -lt 10 ]]; then
    log_error "Insufficient disk space: ${AVAILABLE_GB}GB available (need 10GB+)"
else
    log_info "Disk space: ${AVAILABLE_GB}GB available"
fi

# 3. Check memory (portable: works on both Linux and macOS)
log_info "Checking memory..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS: use vm_statistics or sysctl
    if command -v sysctl > /dev/null; then
        # Get free memory in bytes (vm_statistics for page-based calc or sysctl for total)
        PAGE_SIZE=$(vm_statistics 2>/dev/null | awk '/page size/{print $8}' || echo 4096)
        FREE_PAGES=$(vm_statistics 2>/dev/null | awk '/Pages free/{print $3}' || echo 0)
        INACTIVE_PAGES=$(vm_statistics 2>/dev/null | awk '/Pages inactive/{print $3}' || echo 0)
        if [[ "$FREE_PAGES" -gt 0 ]]; then
            FREE_BYTES=$(( (FREE_PAGES + INACTIVE_PAGES) * PAGE_SIZE ))
            AVAILABLE_MEM=$(( FREE_BYTES / 1024 / 1024 / 1024 ))
            if [[ "$AVAILABLE_MEM" -lt 4 ]]; then
                log_warn "Low memory: ${AVAILABLE_MEM}GB available (recommend 8GB+)"
            else
                log_info "Memory: ${AVAILABLE_MEM}GB available"
            fi
        else
            # Fallback: total memory from sysctl
            TOTAL_BYTES=$(sysctl -n hw.memsize 2>/dev/null || echo 0)
            TOTAL_GB=$(( TOTAL_BYTES / 1024 / 1024 / 1024 ))
            log_info "Total memory: ${TOTAL_GB}GB (cannot determine free memory)"
        fi
    else
        log_warn "Cannot check memory (sysctl not available)"
    fi
elif command -v free > /dev/null; then
    # Linux: use free without -g flag and parse
    AVAILABLE_KB=$(free | awk '/^Mem:/{print $7}')
    AVAILABLE_MEM=$((AVAILABLE_KB / 1024 / 1024))
    if [[ "$AVAILABLE_MEM" -lt 4 ]]; then
        log_warn "Low memory: ${AVAILABLE_MEM}GB available (recommend 8GB+)"
    else
        log_info "Memory: ${AVAILABLE_MEM}GB available"
    fi
else
    log_warn "Cannot check memory (free command not available)"
fi

# 4. Check required tools
log_info "Checking required tools..."

check_tool() {
    local tool="$1"
    local version_cmd="${2:-$1 --version}"
    
    if command -v "$tool" > /dev/null 2>&1; then
        local version
        version=$(eval "$version_cmd" 2>&1 | head -1 || echo "version unknown")
        log_info "$tool: $version"
        return 0
    else
        log_error "$tool: not found"
        return 1
    fi
}

check_tool "git"
check_tool "cargo" "cargo --version"
check_tool "rustc" "rustc --version"
check_tool "sha256sum"
check_tool "gpg" "gpg --version | head -1"
check_tool "jq"
check_tool "curl"
# Check for S3 client: aws first, then s3cmd - only error if both fail
if ! check_tool "aws" "aws --version" 2>/dev/null; then
    if ! check_tool "s3cmd" "s3cmd --version" 2>/dev/null; then
        log_error "No S3 client found (tried: aws, s3cmd)"
    fi
fi

# 5. Check Rust toolchain matches project
log_info "Checking Rust toolchain..."
if [[ -f rust-toolchain.toml ]]; then
    # Portable alternative to grep -oP (Perl regex)
    REQUIRED_RUST=$(sed -n 's/.*channel = "\([^"]*\)".*/\1/p' rust-toolchain.toml | head -1)
    REQUIRED_RUST=${REQUIRED_RUST:-stable}
    # Only check rustc if it's installed
    if command -v rustc >/dev/null 2>&1; then
        CURRENT_RUST=$(rustc --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        log_info "Required Rust: $REQUIRED_RUST, Current: $CURRENT_RUST"
    else
        CURRENT_RUST="not installed"
        log_warn "Required Rust: $REQUIRED_RUST, Current: $CURRENT_RUST"
    fi
else
    log_warn "No rust-toolchain.toml found"
fi

# 6. Check GPG signing key
log_info "Checking GPG signing key..."
GPG_KEY="${FALLBACK_GPG_KEY:-releases@company.com}"
if gpg --list-secret-keys --keyid-format LONG "$GPG_KEY" > /dev/null 2>&1; then
    KEY_ID=$(gpg --list-secret-keys --keyid-format LONG "$GPG_KEY" | grep sec | head -1 | awk '{print $2}' | cut -d'/' -f2)
    log_info "GPG key found: $KEY_ID"
    
    # Check key expiration
    EXPIRES=$(gpg --list-keys --with-colons "$GPG_KEY" | grep ^pub | cut -d: -f7)
    if [[ -n "$EXPIRES" ]]; then
        # Portable date formatting: Linux uses -d @timestamp, macOS uses -r timestamp
        if [[ "$OSTYPE" == "darwin"* ]]; then
            EXPIRES_DATE=$(date -r "$EXPIRES" 2>/dev/null || echo "unknown")
        else
            EXPIRES_DATE=$(date -d "@$EXPIRES" 2>/dev/null || echo "unknown")
        fi
        DAYS_UNTIL=$(( (EXPIRES - $(date +%s)) / 86400 ))
        if [[ $DAYS_UNTIL -lt 30 ]]; then
            log_warn "GPG key expires in $DAYS_UNTIL days"
        else
            log_info "GPG key expires: $EXPIRES_DATE ($DAYS_UNTIL days)"
        fi
    fi
else
    log_error "GPG signing key not found: $GPG_KEY"
    log_info "Generate key: gpg --full-generate-key --batch <<EOF
Key-Type: RSA
Key-Length: 4096
Name-Real: Release Signer
Name-Email: $GPG_KEY
Expire-Date: 2y
EOF"
fi

# 7. Check artifact cache credentials
log_info "Checking artifact cache credentials..."
if [[ -n "${FALLBACK_CACHE_ENDPOINT:-}" ]]; then
    log_info "Cache endpoint: $FALLBACK_CACHE_ENDPOINT"
    
    # Test connectivity (honor FALLBACK_CACHE_ENDPOINT if set)
    if command -v aws > /dev/null && [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
        aws_endpoint_args=""
        if [[ -n "${FALLBACK_CACHE_ENDPOINT:-}" ]]; then
            aws_endpoint_args="--endpoint-url $FALLBACK_CACHE_ENDPOINT"
        fi
        # shellcheck disable=SC2086
        if aws s3 ls "s3://${FALLBACK_CACHE_BUCKET:-fallback-releases}/" $aws_endpoint_args > /dev/null 2>&1; then
            log_info "AWS S3 connectivity: OK"
        else
            log_error "AWS S3 connectivity failed"
        fi
    elif command -v s3cmd > /dev/null; then
        s3cmd_host_args=""
        if [[ -n "${FALLBACK_CACHE_ENDPOINT:-}" ]]; then
            s3cmd_host_args="--host $FALLBACK_CACHE_ENDPOINT --host-bucket $FALLBACK_CACHE_ENDPOINT"
        fi
        # shellcheck disable=SC2086
        if s3cmd ls "s3://${FALLBACK_CACHE_BUCKET:-fallback-releases}/" $s3cmd_host_args > /dev/null 2>&1; then
            log_info "S3cmd connectivity: OK"
        else
            log_error "S3cmd connectivity failed"
        fi
    else
        log_warn "No S3 client available to test connectivity"
    fi
else
    log_warn "FALLBACK_CACHE_ENDPOINT not set"
fi

# 8. Check GitHub CLI auth
log_info "Checking GitHub CLI..."
if command -v gh > /dev/null; then
    if gh auth status > /dev/null 2>&1; then
        log_info "GitHub CLI: authenticated"
    else
        log_error "GitHub CLI: not authenticated (run 'gh auth login')"
    fi
else
    log_warn "GitHub CLI not installed"
fi

# 9. Verify network connectivity
log_info "Checking network connectivity..."
if curl -s --max-time 5 https://github.com > /dev/null; then
    log_info "GitHub.com: reachable"
else
    log_warn "GitHub.com: connectivity issues"
fi

if curl -s --max-time 5 https://crates.io > /dev/null; then
    log_info "crates.io: reachable"
else
    log_warn "crates.io: connectivity issues"
fi

# Summary
echo ""
echo "=== Verification Summary ==="
echo "Errors: $ERRORS"
echo "Warnings: $WARNINGS"

if [[ $ERRORS -gt 0 ]]; then
    echo ""
    echo "Environment NOT ready for fallback builds."
    echo "Fix errors above and re-run this script."
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    echo ""
    echo "Environment ready with warnings."
    echo "Review warnings before proceeding."
    exit 0
else
    echo ""
    echo "✅ Environment ready for fallback builds!"
    exit 0
fi
