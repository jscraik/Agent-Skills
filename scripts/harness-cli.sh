#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

if ! command -v node >/dev/null 2>&1; then
	echo "Error: node is required to run scripts/harness-cli.sh." >&2
	echo "Install Node.js and retry." >&2
	exit 1
fi

set +e
CLI_PATH="$(
	REPO_ROOT="$REPO_ROOT" node <<'NODE'
const { createRequire } = require("node:module");
const { resolve } = require("node:path");

const repoRoot = process.env.REPO_ROOT;

try {
	const requireFromRepo = createRequire(resolve(repoRoot, "package.json"));
	process.stdout.write(
		requireFromRepo.resolve("@brainwav/coding-harness/dist/cli.js"),
	);
} catch (error) {
	if (
		error &&
		typeof error === "object" &&
		"code" in error &&
		error.code === "MODULE_NOT_FOUND"
	) {
		process.exit(42);
	}

	console.error(error instanceof Error ? error.message : String(error));
	process.exit(43);
}
NODE
)"
resolution_status=$?
set -e

if [[ $resolution_status -eq 42 || -z "$CLI_PATH" ]]; then
	echo "Error: local @brainwav/coding-harness could not be resolved from this repo." >&2
	echo "This is a local install/bootstrap problem, not a harness command failure." >&2
	echo "Repair from the repo root with one of:" >&2
	echo "  npm install" >&2
	echo "  npm install --save-dev @brainwav/coding-harness" >&2
	echo "After the package is installed, rerun:" >&2
	echo "  bash scripts/harness-cli.sh <command>" >&2
	echo "  npm exec harness -- <command>" >&2
	exit 1
fi

if [[ $resolution_status -ne 0 ]]; then
	echo "Error: failed to resolve the local @brainwav/coding-harness CLI entrypoint." >&2
	echo "This indicates a local install/bootstrap problem, not a harness command failure." >&2
	echo "Repair from the repo root with one of:" >&2
	echo "  npm install" >&2
	echo "  npm install --save-dev @brainwav/coding-harness" >&2
	exit 1
fi

exec node "$CLI_PATH" "$@"
