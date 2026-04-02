#!/usr/bin/env bash
#
# codex-enforced
# Wraps codex with repo-local preflight enforcement and scoped failure learning.
#

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
PREFLIGHT_SCRIPT="${SCRIPT_DIR}/codex-preflight.sh"
LEARN_SCRIPT="${SCRIPT_DIR}/codex-learn"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

usage() {
	echo "Usage: codex-enforced [options] <prompt>"
	echo ""
	echo "Runs repo-local preflight before executing codex."
	echo ""
	echo "Options:"
	echo "  --skip-preflight    Skip preflight (not recommended)"
	echo "  --preflight-only    Run preflight and exit"
	echo "  --learn-only        Run preflight, record outcome, exit"
	echo "  --help              Show this help"
	echo ""
	echo "All other options passed to codex."
}

if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
	usage
	exit 0
fi

SKIP_PREFLIGHT=false
PREFLIGHT_ONLY=false
LEARN_ONLY=false
NEW_ARGS=()

for arg in "$@"; do
	case "${arg}" in
		--skip-preflight)
			SKIP_PREFLIGHT=true
			;;
		--preflight-only)
			PREFLIGHT_ONLY=true
			;;
		--learn-only)
			LEARN_ONLY=true
			;;
		*)
			NEW_ARGS+=("${arg}")
			;;
	esac
done

PREFLIGHT_STATUS=0
if [[ "${SKIP_PREFLIGHT}" == true ]]; then
	echo -e "${YELLOW}WARNING: Skipping preflight (not recommended)${NC}"
else
	echo "Running preflight checks..."
	echo ""

	if [[ ! -x "${PREFLIGHT_SCRIPT}" ]]; then
		echo -e "${RED}ERROR: Preflight script not found: ${PREFLIGHT_SCRIPT}${NC}"
		exit 1
	fi

	if ! "${PREFLIGHT_SCRIPT}"; then
		PREFLIGHT_STATUS=1
		echo ""
		echo -e "${RED}PREFLIGHT FAILED${NC}"
		echo ""

		if [[ -x "${LEARN_SCRIPT}" ]]; then
			echo -e "${BLUE}Recording failure for analysis...${NC}"
			"${LEARN_SCRIPT}" --scope repo record "preflight_failure" "Preflight checks failed" || true
			echo ""
			echo "Run './scripts/codex-learn analyze' to see scoped override suggestions."
		fi

		echo ""
		echo "Fix the issues above before running codex."
		echo ""
		echo "To bypass (not recommended):"
		echo "  ./scripts/codex-enforced --skip-preflight <your prompt>"
		exit 1
	fi

	echo ""
	echo -e "${GREEN}Preflight passed. Proceeding to codex...${NC}"
	echo ""
fi

if [[ "${PREFLIGHT_ONLY}" == true ]]; then
	exit "${PREFLIGHT_STATUS}"
fi

if [[ "${LEARN_ONLY}" == true ]]; then
	echo "Preflight recorded. Exiting."
	exit 0
fi

CODEX_STATUS=0
codex "${NEW_ARGS[@]}" || CODEX_STATUS=$?

if (( CODEX_STATUS != 0 )) && [[ -x "${LEARN_SCRIPT}" ]]; then
	echo ""
	echo -e "${YELLOW}Session ended with errors. Recording for analysis...${NC}"
	"${LEARN_SCRIPT}" --scope repo record "codex_exit_${CODEX_STATUS}" "Codex exited with code ${CODEX_STATUS}" || true
fi

exit "${CODEX_STATUS}"
