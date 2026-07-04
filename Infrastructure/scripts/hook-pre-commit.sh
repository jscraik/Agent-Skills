#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

unset_git_context_env() {
	local git_env_name
	while IFS= read -r git_env_name; do
		[[ -n "$git_env_name" ]] && unset "$git_env_name"
	done < <(compgen -v GIT_)
}

package_script_exists() {
	local script_name="$1"
	bash ./scripts/run-package-command.sh node -e 'const fs = require("node:fs"); const script = process.argv[1]; const pkg = JSON.parse(fs.readFileSync("package.json", "utf8")); process.exit(pkg.scripts && Object.prototype.hasOwnProperty.call(pkg.scripts, script) ? 0 : 1);' "$script_name"
}

run_optional_package_script() {
	local script_name="$1"
	shift
	if package_script_exists "$script_name"; then
		"$@"
	else
		echo "Skipping optional package script ${script_name}; package.json does not define it."
	fi
}

bash ./scripts/check-hook-critical-config-sync.sh
make codestyle-parity
unset_git_context_env
bash ./scripts/validate-codestyle.sh --fast
bash ./scripts/run-package-command.sh npm run lint
bash ./scripts/run-package-command.sh npm run docs:lint
bash ./scripts/run-package-command.sh npm run typecheck
bash ./scripts/run-package-command.sh npm run quality:docstrings
bash ./scripts/run-package-command.sh npm run quality:size
run_optional_package_script "quality:behavior-tests" bash ./scripts/run-package-command.sh npm run quality:behavior-tests
run_optional_package_script "quality:git-env-sanitizer" bash ./scripts/run-package-command.sh npm run quality:git-env-sanitizer
run_optional_package_script "harness:audit-tracking" bash ./scripts/run-package-command.sh npm run harness:audit-tracking
make secrets-staged
make docs-style-changed
make related-tests-staged
