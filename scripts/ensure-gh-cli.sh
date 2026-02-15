#!/usr/bin/env bash
set -euo pipefail

DRY_RUN=0
FORCE=1

usage() {
  cat <<'USAGE'
Usage: scripts/ensure-gh-cli.sh [--check-only] [--help]

Ensures the GitHub CLI (`gh`) is available.

Options:
  --check-only  Verify gh exists and return non-zero if missing.
  --help        Show this help message.
USAGE
}

while (($# > 0)); do
  case "$1" in
    --check-only)
      DRY_RUN=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "[WARN] Unknown argument: $1" >&2
      usage
      exit 2
      ;;
  esac
done

have_cmd() {
  command -v "$1" >/dev/null 2>&1
}

verify_gh() {
  if have_cmd gh; then
    echo "[OK] GitHub CLI found: $(command -v gh)"
    if gh --version >/dev/null 2>&1; then
      gh --version | sed -n '1p'
    fi
    return 0
  fi
  return 1
}

manual_install_hint() {
  local os="${1:-unknown}"
  echo ""
  echo "[WARN] Automatic installation failed or package manager unavailable."
  echo "You can install the GitHub CLI manually with one of the following:" 
  echo "- macOS: brew install gh"
  echo "- Ubuntu/Debian: sudo apt-get update && sudo apt-get install -y gh"
  echo "- Fedora/RHEL: sudo dnf install -y gh"
  echo "- Arch: sudo pacman -S --noconfirm github-cli"
  echo "- Windows: winget install --id GitHub.cli"
  echo "- Any: https://github.com/cli/cli/releases/latest"
  echo ""
  echo "Detected OS: ${os}"
}

install_gh() {
  local os="$1"
  case "$os" in
    Darwin)
      if have_cmd brew; then
        echo "[INFO] Installing via Homebrew..."
        brew install gh
        return 0
      fi
      ;;
    Linux)
      if have_cmd apt-get; then
        echo "[INFO] Installing via apt-get..."
        sudo apt-get update
        sudo apt-get install -y gh
        return 0
      fi
      if have_cmd apt; then
        echo "[INFO] Installing via apt..."
        sudo apt update
        sudo apt install -y gh
        return 0
      fi
      if have_cmd dnf; then
        echo "[INFO] Installing via dnf..."
        sudo dnf install -y gh
        return 0
      fi
      if have_cmd yum; then
        echo "[INFO] Installing via yum..."
        sudo yum install -y gh
        return 0
      fi
      if have_cmd pacman; then
        echo "[INFO] Installing via pacman..."
        sudo pacman -S --noconfirm github-cli
        return 0
      fi
      if have_cmd zypper; then
        echo "[INFO] Installing via zypper..."
        sudo zypper --non-interactive install -y gh
        return 0
      fi
      ;;
    *)
      if have_cmd winget; then
        echo "[INFO] Installing via winget..."
        winget install --id GitHub.cli --exact --silent --accept-source-agreements --accept-package-agreements
        return 0
      fi
      if have_cmd scoop; then
        echo "[INFO] Installing via scoop..."
        scoop install gh
        return 0
      fi
      if have_cmd choco; then
        echo "[INFO] Installing via chocolatey..."
        choco install gh -y
        return 0
      fi
      ;;
  esac
  return 1
}

OS="$(uname -s)"

verify_gh && exit 0

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "[ERROR] GitHub CLI (`gh`) is not installed."
  echo "Run scripts/ensure-gh-cli.sh to install it automatically when possible."
  exit 1
fi

if [[ "$FORCE" -eq 1 ]]; then
  if install_gh "$OS"; then
    if verify_gh; then
      exit 0
    fi
  fi

  manual_install_hint "$OS"
  exit 1
fi

echo "[ERROR] Unexpected install state"
exit 1
