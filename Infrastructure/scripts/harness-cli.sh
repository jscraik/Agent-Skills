#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT_FALLBACK="$(cd -- "$SCRIPT_DIR/.." && pwd)"
SUPPORTED_VERSION="0.15.3"
FALLBACK_PACKAGE="@brainwav/coding-harness@$SUPPORTED_VERSION"
if REPO_ROOT="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel 2>/dev/null)"; then
	:
else
	REPO_ROOT="${REPO_ROOT_FALLBACK}"
fi

if [[ "${1:-}" == "plan-gate" ]]; then
	has_max_age=0
	normalized_args=()
	for arg in "$@"; do
		if [[ "$arg" == "--max-age" ]]; then
			has_max_age=1
			normalized_args+=("$arg")
		elif [[ "$arg" == --max-age=* ]]; then
			has_max_age=1
			normalized_args+=("--max-age" "${arg#--max-age=}")
		else
			normalized_args+=("$arg")
		fi
	done
	set -- "${normalized_args[@]}"
	if [[ "$has_max_age" -eq 0 ]]; then
		set -- "$@" --max-age "${HARNESS_PLAN_GATE_MAX_AGE_DAYS:-3650}"
	fi
fi

if ! command -v node >/dev/null 2>&1; then
	echo "Error: node is required to run scripts/harness-cli.sh." >&2
	echo "Install Node.js and retry." >&2
	exit 1
fi

set +e
CLI_PATH="$(
	HARNESS_SUPPORTED_VERSION="$SUPPORTED_VERSION" REPO_ROOT="$REPO_ROOT" node -e '
const { createRequire } = require("node:module");
const { readFileSync, realpathSync } = require("node:fs");
const { isAbsolute, relative, resolve } = require("node:path");

const repoRoot = process.env.REPO_ROOT;
const supportedVersion = process.env.HARNESS_SUPPORTED_VERSION;

try {
	const requireFromRepo = createRequire(resolve(repoRoot, "package.json"));
	const packageJsonPath = requireFromRepo.resolve("@brainwav/coding-harness/package.json");
	const cliPath = requireFromRepo.resolve("@brainwav/coding-harness/dist/cli.js");
	const expectedPackageRoot = resolve(
		repoRoot,
		"node_modules/@brainwav/coding-harness",
	);
	const isWithin = (root, candidate) => {
		const pathFromRoot = relative(root, candidate);
		return pathFromRoot !== ".." && !pathFromRoot.startsWith("../") && !isAbsolute(pathFromRoot);
	};
	if (!isWithin(expectedPackageRoot, resolve(packageJsonPath)) || !isWithin(expectedPackageRoot, resolve(cliPath))) {
		console.error("Resolved local @brainwav/coding-harness is outside the approved repo-local dependency boundary.");
		process.exit(45);
	}
	const realPackageRoot = realpathSync(expectedPackageRoot);
	const realPackageJsonPath = realpathSync(packageJsonPath);
	const realCliPath = realpathSync(cliPath);
	if (
		!isWithin(realPackageRoot, realPackageJsonPath) ||
		!isWithin(realPackageRoot, realCliPath) ||
		relative(realPackageRoot, realPackageJsonPath) !== "package.json" ||
		relative(realPackageRoot, realCliPath) !== "dist/cli.js"
	) {
		console.error("Resolved local Harness metadata and CLI do not share the approved package root.");
		process.exit(45);
	}
	const packageMetadata = JSON.parse(readFileSync(packageJsonPath, "utf8"));
	if (
		packageMetadata.name !== "@brainwav/coding-harness" ||
		packageMetadata.version !== supportedVersion
	) {
		console.error(
			`Unsupported local Harness identity ${String(packageMetadata.name)}@${String(packageMetadata.version)}; expected @brainwav/coding-harness@${supportedVersion}.`,
		);
		process.exit(44);
	}
	process.stdout.write(cliPath);
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
'
)"
resolution_status=$?
set -e

if [[ $resolution_status -eq 42 || $resolution_status -eq 44 ]]; then
	if [[ "${HARNESS_CLI_ALLOW_NPM_EXEC:-}" == "1" ]]; then
		if ! command -v npm >/dev/null 2>&1; then
			echo "Error: npm is required for HARNESS_CLI_ALLOW_NPM_EXEC fallback." >&2
			exit 1
		fi
		exec npm exec --yes --package "$FALLBACK_PACKAGE" -- harness "$@"
	fi

	if [[ $resolution_status -eq 44 ]]; then
		echo "Error: the resolved local @brainwav/coding-harness does not match $SUPPORTED_VERSION." >&2
	else
		echo "Error: local @brainwav/coding-harness@$SUPPORTED_VERSION could not be resolved from this repo." >&2
	fi
	echo "This is a local install/bootstrap problem, not a harness command failure." >&2
	echo "Refusing to run an ambient harness executable because its version is not verified." >&2
	echo "For a deliberate one-off pinned runner, rerun with:" >&2
	echo "  HARNESS_CLI_ALLOW_NPM_EXEC=1 bash scripts/harness-cli.sh <command>" >&2
	echo "A consuming package repository may instead install @brainwav/coding-harness@$SUPPORTED_VERSION locally." >&2
	echo "After a verified repo-local install, rerun:" >&2
	echo "  bash scripts/harness-cli.sh <command>" >&2
	exit 1
fi

if [[ $resolution_status -eq 45 ]]; then
	echo "Error: the resolved local Harness package is outside the approved repo-local boundary." >&2
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

if [[ -z "$CLI_PATH" ]]; then
	echo "Error: local @brainwav/coding-harness resolver returned an empty CLI path." >&2
	echo "This indicates a local install/bootstrap problem, not a harness command failure." >&2
	echo "Repair from the repo root with one of:" >&2
	echo "  npm install" >&2
	echo "  npm install --save-dev @brainwav/coding-harness" >&2
	exit 1
fi

exec node "$CLI_PATH" "$@"
