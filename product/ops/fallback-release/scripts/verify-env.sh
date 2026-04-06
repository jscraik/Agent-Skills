#!/bin/bash
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
    log_info "Git repository: $(git remote get-url origin 2>/dev/null || echo 'unknown')"
    log_info "Current branch: $(git branch --show-current)"
    log_info "Git SHA: $(git rev-parse --short HEAD)"
fi

# 2. Check disk space
log_info "Checking disk space..."
AVAILABLE_GB=$(df -BG . | awk 'NR==2 {print $4}' | tr -d 'G')
if [[ "$AVAILABLE_GB" -lt 10 ]]; then
    log_error "Insufficient disk space: ${AVAILABLE_GB}GB available (need 10GB+)"
else
    log_info "Disk space: ${AVAILABLE_GB}GB available"
fi

# 3. Check memory
log_info "Checking memory..."
if command -v free > /dev/null; then
    AVAILABLE_MEM=$(free -g | awk '/^Mem:/{print $7}')
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
check_tool "aws" "aws --version" || check_tool "s3cmd" "s3cmd --version"

# 5. Check Rust toolchain matches project
log_info "Checking Rust toolchain..."
if [[ -f rust-toolchain.toml ]]; then
    REQUIRED_RUST=$(grep -oP '(?<=channel = ")[^"]+' rust-toolchain.toml || echo "stable")
    CURRENT_RUST=$(rustc --version | grep -oP '\d+\.\d+\.\d+')
    log_info "Required Rust: $REQUIRED_RUST, Current: $CURRENT_RUST"
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
        EXPIRES_DATE=$(date -d "@$EXPIRES" 2>/dev/null || date -r "$EXPIRES")
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
    
    # Test connectivity
    if command -v aws > /dev/null && [[ -n "${AWS_ACCESS_KEY_ID:-}" ]]; then
        if aws s3 ls "s3://${FALLBACK_CACHE_BUCKET:-fallback-releases}/" > /dev/null 2>&1; then
            log_info "AWS S3 connectivity: OK"
        else
            log_error "AWS S3 connectivity failed"
        fi
    elif command -v s3cmd > /dev/null; then
        if s3cmd ls "s3://${FALLBACK_CACHE_BUCKET:-fallback-releases}/" > /dev/null 2>&1; then
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
