#!/usr/bin/env bash
# Shared Semgrep bootstrap helpers for repository hook and CI scripts.
set -euo pipefail

if [[ -z "${REPO_ROOT:-}" ]]; then
  REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
fi

SEMGREP_VERSION="${SEMGREP_VERSION:-1.153.1}"
SEMGREP_VERSION_SERIES="${SEMGREP_VERSION%.*}"
DEFAULT_SEMGREP_PIP_SPEC="semgrep>=${SEMGREP_VERSION},<2.0.0"
if [[ "$SEMGREP_VERSION_SERIES" == *.* ]]; then
  semgrep_series_major="${SEMGREP_VERSION_SERIES%%.*}"
  semgrep_series_minor="${SEMGREP_VERSION_SERIES##*.}"
  if [[ "$semgrep_series_major" =~ ^[0-9]+$ && "$semgrep_series_minor" =~ ^[0-9]+$ ]]; then
    semgrep_next_minor="$((semgrep_series_minor + 1))"
    DEFAULT_SEMGREP_PIP_SPEC="semgrep>=${SEMGREP_VERSION},<${semgrep_series_major}.${semgrep_next_minor}.0"
  fi
fi
SEMGREP_PIP_SPEC="${SEMGREP_PIP_SPEC:-$DEFAULT_SEMGREP_PIP_SPEC}"
DEFAULT_SEMGREP_STATE_ROOT="$REPO_ROOT/.cache/semgrep"

SEMGREP_STATE_ROOT="${SEMGREP_STATE_ROOT:-$DEFAULT_SEMGREP_STATE_ROOT}"
HOST_CACHE_HOME="${XDG_CACHE_HOME:-$HOME/.cache}"
SEMGREP_RUNTIME_CACHE_ROOT="${SEMGREP_RUNTIME_CACHE_ROOT:-$SEMGREP_STATE_ROOT/cache}"
SEMGREP_RUNTIME_USER_HOME="${SEMGREP_USER_HOME:-$SEMGREP_STATE_ROOT/home}"
SEMGREP_RUNTIME_LOG_FILE="${SEMGREP_LOG_FILE:-$SEMGREP_STATE_ROOT/semgrep.log}"
resolve_semgrep_python() {
  if [[ -n "${SEMGREP_BOOTSTRAP_PYTHON:-}" ]]; then
    if [[ -x "$SEMGREP_BOOTSTRAP_PYTHON" ]]; then
      printf '%s\n' "$SEMGREP_BOOTSTRAP_PYTHON"
      return 0
    fi
    if command -v "$SEMGREP_BOOTSTRAP_PYTHON" >/dev/null 2>&1; then
      command -v "$SEMGREP_BOOTSTRAP_PYTHON"
      return 0
    fi
    return 1
  fi

  if command -v uv >/dev/null 2>&1; then
    local uv_python
    if uv_python="$(uv python find 3.12 2>/dev/null)" && [[ -x "$uv_python" ]]; then
      printf '%s\n' "$uv_python"
      return 0
    fi
  fi

  command -v python3
}
SEMGREP_BOOTSTRAP_PYTHON="${SEMGREP_BOOTSTRAP_PYTHON:-}"
resolve_semgrep_python_cache_tag() {
  "$SEMGREP_BOOTSTRAP_PYTHON" - <<'PY'
import sys
print(f"py{sys.version_info.major}.{sys.version_info.minor}")
PY
}
SEMGREP_PYTHON_CACHE_TAG="${SEMGREP_PYTHON_CACHE_TAG:-}"

if [[ -z "${SSL_CERT_FILE:-}" ]]; then
  for cert_path in /etc/ssl/cert.pem /etc/ssl/certs/ca-certificates.crt; do
    if [[ -f "$cert_path" ]]; then
      export SSL_CERT_FILE="$cert_path"
      break
    fi
  done
fi

SEMGREP_CACHE_ROOT="${SEMGREP_CACHE_ROOT:-$SEMGREP_STATE_ROOT/tool-cache}"
SEMGREP_VENV_DIR="${SEMGREP_VENV_DIR:-}"
SEMGREP_BIN="${SEMGREP_BIN:-}"
SEMGREP_PYSEMGREP_BIN="${SEMGREP_PYSEMGREP_BIN:-}"
SEMGREP_SYSTEM_BIN="${SEMGREP_SYSTEM_BIN:-}"
SEMGREP_PYTHON="${SEMGREP_PYTHON:-}"
SEMGREP_SITE_PACKAGES_DIR="${SEMGREP_SITE_PACKAGES_DIR:-}"
SEMGREP_PROBE_TIMEOUT_SECONDS="${SEMGREP_PROBE_TIMEOUT_SECONDS:-20}"

ensure_semgrep_cache_paths() {
  if [[ -n "${SEMGREP_CACHE_PATHS_READY:-}" ]]; then
    return 0
  fi

  if [[ -z "${SEMGREP_BOOTSTRAP_PYTHON:-}" ]]; then
    if ! SEMGREP_BOOTSTRAP_PYTHON="$(resolve_semgrep_python)"; then
      SEMGREP_BOOTSTRAP_PYTHON=""
      return 1
    fi
  fi
  if [[ ! -x "$SEMGREP_BOOTSTRAP_PYTHON" ]]; then
    return 1
  fi

  if [[ -z "${SEMGREP_PYTHON_CACHE_TAG:-}" ]]; then
    SEMGREP_PYTHON_CACHE_TAG="$(resolve_semgrep_python_cache_tag)"
  fi

  SEMGREP_VENV_DIR="${SEMGREP_CACHE_ROOT}/semgrep-venv-${SEMGREP_VERSION}-${SEMGREP_PYTHON_CACHE_TAG}"
  SEMGREP_BIN="$SEMGREP_VENV_DIR/bin/semgrep"
  SEMGREP_PYSEMGREP_BIN="$SEMGREP_VENV_DIR/bin/pysemgrep"
  SEMGREP_PYTHON="$SEMGREP_VENV_DIR/bin/python"
  SEMGREP_SITE_PACKAGES_DIR="${SEMGREP_CACHE_ROOT}/semgrep-site-packages-${SEMGREP_VERSION}-${SEMGREP_PYTHON_CACHE_TAG}"
  SEMGREP_CACHE_PATHS_READY=1
}

semgrep_probe_command() {
  if command -v timeout >/dev/null 2>&1; then
    timeout "$SEMGREP_PROBE_TIMEOUT_SECONDS" "$@"
    return
  fi
  if command -v gtimeout >/dev/null 2>&1; then
    gtimeout "$SEMGREP_PROBE_TIMEOUT_SECONDS" "$@"
    return
  fi
  "$@" &
  local probe_pid=$!
  (
    sleep "$SEMGREP_PROBE_TIMEOUT_SECONDS"
    kill "$probe_pid" >/dev/null 2>&1 || true
    sleep 1
    kill -9 "$probe_pid" >/dev/null 2>&1 || true
  ) &
  local watchdog_pid=$!
  local probe_status=0
  if wait "$probe_pid"; then
    probe_status=0
  else
    probe_status=$?
  fi
  kill "$watchdog_pid" >/dev/null 2>&1 || true
  wait "$watchdog_pid" >/dev/null 2>&1 || true
  return "$probe_status"
}

resolve_semgrep_bin() {
  ensure_semgrep_cache_paths || return 1
  if [[ -x "$SEMGREP_PYSEMGREP_BIN" ]]; then
    printf '%s\n' "$SEMGREP_PYSEMGREP_BIN"
    return 0
  fi
  if [[ -x "$SEMGREP_BIN" ]]; then
    printf '%s\n' "$SEMGREP_BIN"
    return 0
  fi
  return 1
}

semgrep_binary_usable() {
  ensure_semgrep_cache_paths || return 1
  local semgrep_bin
  if ! semgrep_bin="$(resolve_semgrep_bin)"; then
    return 1
  fi

  XDG_CACHE_HOME="$SEMGREP_RUNTIME_CACHE_ROOT" \
    SEMGREP_USER_HOME="$SEMGREP_RUNTIME_USER_HOME" \
    SEMGREP_LOG_FILE="$SEMGREP_RUNTIME_LOG_FILE" \
    semgrep_probe_command "$semgrep_bin" --version >/dev/null 2>&1
}

semgrep_site_packages_usable() {
  ensure_semgrep_cache_paths || return 1
  if [[ ! -d "$SEMGREP_SITE_PACKAGES_DIR/semgrep" ]]; then
    return 1
  fi

  PYTHONPATH="$SEMGREP_SITE_PACKAGES_DIR${PYTHONPATH:+:$PYTHONPATH}" \
    XDG_CACHE_HOME="$SEMGREP_RUNTIME_CACHE_ROOT" \
    SEMGREP_USER_HOME="$SEMGREP_RUNTIME_USER_HOME" \
    SEMGREP_LOG_FILE="$SEMGREP_RUNTIME_LOG_FILE" \
    semgrep_probe_command "$SEMGREP_BOOTSTRAP_PYTHON" -c 'import sys; from semgrep.console_scripts.entrypoint import main; raise SystemExit(main())' --version >/dev/null 2>&1
}

semgrep_version_at_least() {
  "$SEMGREP_BOOTSTRAP_PYTHON" - "$1" "$2" <<'PY'
import re
import sys

detected, required = sys.argv[1:3]


def parse(version: str):
    match = re.match(r"^(\d+)\.(\d+)\.(\d+)", version.strip())
    if not match:
        return None
    return tuple(int(part) for part in match.groups())


detected_version = parse(detected)
required_version = parse(required)
if detected_version is None or required_version is None:
    raise SystemExit(1)
raise SystemExit(0 if detected_version >= required_version else 1)
PY
}

resolve_system_semgrep_bin() {
  if [[ -n "$SEMGREP_SYSTEM_BIN" ]]; then
    if [[ -x "$SEMGREP_SYSTEM_BIN" ]]; then
      printf '%s\n' "$SEMGREP_SYSTEM_BIN"
      return 0
    fi
    if command -v "$SEMGREP_SYSTEM_BIN" >/dev/null 2>&1; then
      command -v "$SEMGREP_SYSTEM_BIN"
      return 0
    fi
    return 1
  fi

  local candidate
  for candidate in pysemgrep semgrep; do
    if command -v "$candidate" >/dev/null 2>&1; then
      command -v "$candidate"
      return 0
    fi
  done

  return 1
}

semgrep_system_binary_usable() {
  local semgrep_bin
  if ! semgrep_bin="$(resolve_system_semgrep_bin)"; then
    return 1
  fi

  local detected_version
  if ! detected_version="$(XDG_CACHE_HOME="$SEMGREP_RUNTIME_CACHE_ROOT" \
    SEMGREP_USER_HOME="$SEMGREP_RUNTIME_USER_HOME" \
    SEMGREP_LOG_FILE="$SEMGREP_RUNTIME_LOG_FILE" \
    semgrep_probe_command "$semgrep_bin" --version 2>/dev/null | tr -d "[:space:]")"; then
    return 1
  fi

  semgrep_version_at_least "$detected_version" "$SEMGREP_VERSION"
}

detect_semgrep_package_version() {
  ensure_semgrep_cache_paths || return 1
  if semgrep_binary_usable; then
    "$SEMGREP_PYTHON" - <<'PY' 2>/dev/null
import importlib.metadata
print(importlib.metadata.version("semgrep"))
PY
    return
  fi

  PYTHONPATH="$SEMGREP_SITE_PACKAGES_DIR${PYTHONPATH:+:$PYTHONPATH}" \
    "$SEMGREP_BOOTSTRAP_PYTHON" - <<'PY' 2>/dev/null
import importlib.metadata
print(importlib.metadata.version("semgrep"))
PY
}

run_semgrep() {
  ensure_semgrep_cache_paths || return 1
  local semgrep_bin
  if semgrep_binary_usable && semgrep_bin="$(resolve_semgrep_bin)"; then
    XDG_CACHE_HOME="$SEMGREP_RUNTIME_CACHE_ROOT" \
      SEMGREP_USER_HOME="$SEMGREP_RUNTIME_USER_HOME" \
      SEMGREP_LOG_FILE="$SEMGREP_RUNTIME_LOG_FILE" \
      "$semgrep_bin" "$@"
    return
  fi

  if semgrep_system_binary_usable && semgrep_bin="$(resolve_system_semgrep_bin)"; then
    XDG_CACHE_HOME="$SEMGREP_RUNTIME_CACHE_ROOT" \
      SEMGREP_USER_HOME="$SEMGREP_RUNTIME_USER_HOME" \
      SEMGREP_LOG_FILE="$SEMGREP_RUNTIME_LOG_FILE" \
      "$semgrep_bin" "$@"
    return
  fi

  PYTHONPATH="$SEMGREP_SITE_PACKAGES_DIR${PYTHONPATH:+:$PYTHONPATH}" \
    XDG_CACHE_HOME="$SEMGREP_RUNTIME_CACHE_ROOT" \
    SEMGREP_USER_HOME="$SEMGREP_RUNTIME_USER_HOME" \
    SEMGREP_LOG_FILE="$SEMGREP_RUNTIME_LOG_FILE" \
    "$SEMGREP_BOOTSTRAP_PYTHON" -c 'import sys; from semgrep.console_scripts.entrypoint import main; raise SystemExit(main())' "$@"
}

semgrep_version_usable() {
  local detected_version
  detected_version="$(detect_semgrep_package_version | tr -d "[:space:]")" || return 1
  if [[ "$detected_version" == "$SEMGREP_VERSION" ]]; then
    return 0
  fi
  # Some Python runtimes cannot resolve older Semgrep pins and install a newer
  # compatible release instead. Accept only newer patch releases in the same
  # major.minor package series to avoid cross-series scanner drift.
  local requested_series detected_series
  requested_series="${SEMGREP_VERSION%.*}"
  detected_series="${detected_version%.*}"
  if [[ -z "$requested_series" || -z "$detected_series" ]]; then
    return 1
  fi
  if [[ "$requested_series" != "$detected_series" ]]; then
    return 1
  fi
  local requested_patch detected_patch
  requested_patch="${SEMGREP_VERSION##*.}"
  detected_patch="${detected_version##*.}"
  if [[ ! "$requested_patch" =~ ^[0-9]+$ || ! "$detected_patch" =~ ^[0-9]+$ ]]; then
    return 1
  fi
  (( detected_patch >= requested_patch ))
}

ensure_python_packaging_tools() {
  if [[ -z "${CI:-}" && -z "${CIRCLECI:-}" ]]; then
    return 1
  fi

  if ! command -v apt-get >/dev/null 2>&1; then
    return 1
  fi

  if [[ "$(id -u)" -eq 0 ]]; then
    apt-get update >/dev/null &&
      apt-get install -y python3-pip python3-venv >/dev/null || return 1
    "$SEMGREP_BOOTSTRAP_PYTHON" -m pip --version >/dev/null 2>&1 || return 1
    return 0
  fi

  if command -v sudo >/dev/null 2>&1; then
    sudo apt-get update >/dev/null &&
      sudo apt-get install -y python3-pip python3-venv >/dev/null || return 1
    "$SEMGREP_BOOTSTRAP_PYTHON" -m pip --version >/dev/null 2>&1 || return 1
    return 0
  fi

  return 1
}

install_semgrep_with_venv() {
  ensure_semgrep_cache_paths || return 1
  rm -rf "$SEMGREP_VENV_DIR"
  if ! "$SEMGREP_BOOTSTRAP_PYTHON" -m venv "$SEMGREP_VENV_DIR" >/dev/null 2>&1; then
    return 1
  fi
  if ! "$SEMGREP_PYTHON" -m pip install --quiet --upgrade pip "$SEMGREP_PIP_SPEC"; then
    return 1
  fi
  semgrep_binary_usable && semgrep_version_usable
}

install_semgrep_with_site_packages() {
  ensure_semgrep_cache_paths || return 1
  if ! "$SEMGREP_BOOTSTRAP_PYTHON" -m pip --version >/dev/null 2>&1; then
    return 1
  fi
  rm -rf "$SEMGREP_VENV_DIR"
  rm -f "$SEMGREP_BIN"
  rm -rf "$SEMGREP_SITE_PACKAGES_DIR"
  mkdir -p "$SEMGREP_SITE_PACKAGES_DIR"
  if ! "$SEMGREP_BOOTSTRAP_PYTHON" -m pip install --quiet --upgrade --target "$SEMGREP_SITE_PACKAGES_DIR" "$SEMGREP_PIP_SPEC"; then
    return 1
  fi
  semgrep_site_packages_usable && semgrep_version_usable
}

install_semgrep() {
  if ! ensure_semgrep_cache_paths; then
    echo "Error: python3 or uv-managed Python 3.12 is required to install Semgrep." >&2
    exit 1
  fi

  mkdir -p "$SEMGREP_STATE_ROOT" "$SEMGREP_RUNTIME_CACHE_ROOT" "$SEMGREP_RUNTIME_USER_HOME"
  mkdir -p "$(dirname "$SEMGREP_RUNTIME_LOG_FILE")"
  mkdir -p "$SEMGREP_CACHE_ROOT"

  local legacy_venv_dir="$HOST_CACHE_HOME/coding-harness/semgrep-venv-${SEMGREP_VERSION}-${SEMGREP_PYTHON_CACHE_TAG}"
  if [[ -d "$legacy_venv_dir" ]]; then
    rm -rf "$SEMGREP_VENV_DIR"
    # `cp -a` is GNU-only; `cp -Rp` works on both GNU and BSD/macOS.
    cp -Rp "$legacy_venv_dir" "$SEMGREP_VENV_DIR"
    if semgrep_binary_usable && semgrep_version_usable; then
      return
    fi
    rm -rf "$SEMGREP_VENV_DIR"
  fi

  if install_semgrep_with_venv; then
    return
  fi

  if install_semgrep_with_site_packages; then
    return
  fi

  if ensure_python_packaging_tools; then
    if install_semgrep_with_venv || install_semgrep_with_site_packages; then
      return
    fi
  fi

  echo "Error: unable to install Semgrep ${SEMGREP_VERSION} or newer." >&2
  echo "Tried venv + pip install paths and CI packaging bootstrap." >&2
  exit 1
}

has_semgrep_installation() {
  if semgrep_binary_usable && semgrep_version_usable; then
    return 0
  fi

  if semgrep_site_packages_usable && semgrep_version_usable; then
    return 0
  fi

  if semgrep_system_binary_usable; then
    return 0
  fi

  return 1
}

ensure_semgrep_version() {
  if ! has_semgrep_installation; then
    install_semgrep
  fi

  if ! has_semgrep_installation; then
    echo "Error: semgrep bootstrap did not provision Semgrep ${SEMGREP_VERSION}." >&2
    exit 1
  fi
}
