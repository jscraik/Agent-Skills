#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
RULESET_PATH="$REPO_ROOT/scripts/semgrep-pre-push.yml"
SEMGREP_VERSION="1.153.1"
SEMGREP_CACHE_ROOT="${XDG_CACHE_HOME:-$HOME/.cache}/coding-harness"
SEMGREP_VENV_DIR="${SEMGREP_CACHE_ROOT}/semgrep-venv-${SEMGREP_VERSION}"
SEMGREP_BIN="$SEMGREP_VENV_DIR/bin/semgrep"
SEMGREP_PYTHON="$SEMGREP_VENV_DIR/bin/python"
cd "$REPO_ROOT"

install_semgrep() {
	mkdir -p "$SEMGREP_CACHE_ROOT"
	python3 -m venv "$SEMGREP_VENV_DIR"
	"$SEMGREP_PYTHON" -m pip install --quiet --upgrade pip "semgrep==$SEMGREP_VERSION"
}

ensure_semgrep_version() {
	if [[ ! -x "$SEMGREP_BIN" ]]; then
		install_semgrep
		return
	fi

	local detected_version
	detected_version="$("$SEMGREP_BIN" --version 2>/dev/null | tr -d '[:space:]')"
	if [[ "$detected_version" != "$SEMGREP_VERSION" ]]; then
		install_semgrep
	fi
}

if [[ ! -f "$RULESET_PATH" ]]; then
	echo "Error: missing Semgrep ruleset at $RULESET_PATH"
	exit 1
fi

ensure_semgrep_version

base_ref=""
if git rev-parse --verify '@{upstream}' >/dev/null 2>&1; then
	base_ref="$(git merge-base HEAD '@{upstream}')"
else
	for candidate in origin/main origin/master main master; do
		if git rev-parse --verify "$candidate" >/dev/null 2>&1; then
			base_ref="$(git merge-base HEAD "$candidate")"
			break
		fi
	done
fi

if [[ -z "$base_ref" ]]; then
	if git rev-parse --verify HEAD^ >/dev/null 2>&1; then
		base_ref="HEAD^"
	else
		echo "No comparison base available for Semgrep changed-file scan."
		exit 0
	fi
fi

changed_sources=()
while IFS= read -r -d "" path; do
	[[ -n "$path" ]] || continue
	if [[ "$path" =~ ^src/.*\.(ts|tsx|js|jsx|mts|cts)$ ]] && \
		[[ ! "$path" =~ \.d\.ts$ ]] && \
		[[ ! "$path" =~ \.(test|spec)\.(ts|tsx|js|jsx|mts|cts)$ ]]; then
		changed_sources+=("$path")
	fi
done < <(git diff --name-only --diff-filter=ACMR -z "$base_ref"...HEAD --)

if [[ ${#changed_sources[@]} -eq 0 ]]; then
	echo "No changed src/** implementation files detected for Semgrep."
	exit 0
fi

"$SEMGREP_BIN" scan \
	--config "$RULESET_PATH" \
	--disable-version-check \
	--error \
	--jobs 1 \
	"${changed_sources[@]}"
