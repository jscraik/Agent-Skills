#!/usr/bin/env bash
# Local environment preflight (strict)
# Fails fast when required tooling is missing.

set -euo pipefail

prepend_standard_tool_paths() {
	local candidate
	for candidate in \
		"$HOME/.local/share/mise/shims" \
		"$HOME/.local/bin" \
		"/opt/homebrew/bin" \
		"/opt/homebrew/sbin" \
		"/usr/local/bin" \
		"/usr/sbin" \
		"/sbin"; do
		if [[ -d "$candidate" && ":$PATH:" != *":$candidate:"* ]]; then
			PATH="$candidate:$PATH"
		fi
	done
	export PATH
}

prepend_standard_tool_paths

if [[ "${BASH_VERSINFO[0]:-0}" -lt 4 && -z "${CHECK_ENVIRONMENT_REEXECED:-}" ]]; then
	if [[ -x "/opt/homebrew/bin/bash" ]]; then
		export CHECK_ENVIRONMENT_REEXECED=1
		exec "/opt/homebrew/bin/bash" "$0" "$@"
	fi
fi

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)"; then
	:
else
	CANONICAL_SCRIPT_DIR="$(cd -- "$SCRIPT_DIR" && pwd -P)"
	REPO_ROOT="$(cd -- "$CANONICAL_SCRIPT_DIR/../.." && pwd -P)"
fi
CONTRACT_PATH="$REPO_ROOT/harness.contract.json"
	ATTESTATION_PATH="$REPO_ROOT/artifacts/policy/environment-attestation.json"
	MISE_PATH="$REPO_ROOT/.mise.toml"
	CODEX_ENVIRONMENT_PATH="$REPO_ROOT/.codex/environments/environment.toml"
	MAKEFILE_PATH="$REPO_ROOT/Makefile"
	PREK_CONFIG_PATH="$REPO_ROOT/prek.toml"
	PACKAGE_JSON_PATH="$REPO_ROOT/package.json"
	CODESTYLE_PATH="$REPO_ROOT/CODESTYLE.md"
	TOOLING_DOC_PATH="${TOOLING_DOC_PATH:-$HOME/.codex/instructions/tooling.md}"

if [[ ! -f "$CONTRACT_PATH" ]]; then
	echo "Error: missing contract file at $CONTRACT_PATH"
	exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
	echo "Error: required binary 'rg' is not installed or not on PATH"
	exit 1
fi

	if [[ ! -f "$MISE_PATH" ]]; then
		echo "Error: missing mise config at $MISE_PATH"
		exit 1
	fi

	if [[ ! -f "$CODEX_ENVIRONMENT_PATH" ]]; then
		echo "Error: missing Codex environment file at $CODEX_ENVIRONMENT_PATH"
		exit 1
	fi

	if [[ ! -f "$MAKEFILE_PATH" ]]; then
		echo "Error: missing required Makefile at $MAKEFILE_PATH"
		exit 1
	fi

	if [[ ! -f "$PREK_CONFIG_PATH" ]]; then
		echo "Error: missing required prek config at $PREK_CONFIG_PATH"
		exit 1
	fi

	if [[ ! -f "$CODESTYLE_PATH" ]]; then
		echo "Error: missing CODESTYLE contract at $CODESTYLE_PATH"
		exit 1
	fi

	required_support_files=("scripts/codex-preflight.sh" "scripts/codex-preflight-local-memory-legacy.sh" "scripts/codex-learn" "scripts/codex-enforced" "scripts/verify-work.sh" "scripts/validate-codestyle.sh" "scripts/validate-commit-msg.js" "scripts/hooks/pre-commit.sh" "scripts/hooks/commit-msg.sh" "scripts/hooks/pre-push.sh" "scripts/install-prek-hooks.sh" "scripts/prepare-worktree.sh" "scripts/check-staged-secrets.sh" "scripts/check-doc-style.sh" "scripts/check-related-tests.sh" "scripts/check-semgrep-changed.sh" "scripts/semgrep-pre-push.yml" "Infrastructure/scripts/validation-and-linting/git_metadata_preflight.py")
	for support_file in "${required_support_files[@]}"; do
		if [[ ! -f "$REPO_ROOT/${support_file}" ]]; then
			echo "Error: missing required hook support file at $REPO_ROOT/${support_file}"
			exit 1
		fi
	done

if ! command -v mise >/dev/null 2>&1; then
	echo "Error: required binary 'mise' is not installed or not on PATH"
	exit 1
fi

# Bootstrap the full repo-managed environment so hook validation reflects the
# pinned runtime versions and required approval posture, not only the caller
# shell's PATH.
eval "$(mise activate bash)"
export CODEX_APPROVAL_POSTURE="${CODEX_APPROVAL_POSTURE:-require}"

required_mise_tools=("node" "pnpm" "python" "uv" "cargo:prek" "npm:@brainwav/diagram" "npm:@argos-ci/cli" "cosign" "cloudflared" "npm:vitest" "ruff" "pipx:pylint" "npm:eslint" "npm:agent-browser" "npm:agentation" "npm:agentation-mcp" "npm:@mermaid-js/mermaid-cli" "npm:@brainwav/rsearch" "npm:@brainwav/wsearch-cli" "npm:beautiful-mermaid" "npm:markdownlint-cli2" "npm:semver" "npm:wrangler" "semgrep" "trivy" "vale")
for tool in "${required_mise_tools[@]}"; do
	tool_pattern="$(printf '%s' "$tool" | sed 's/[][(){}.^$*+?|\\]/\\&/g')"
	if ! rg -q "^[[:space:]]*(\"${tool_pattern}\"|${tool_pattern})[[:space:]]*=" "$MISE_PATH"; then
		echo "Error: required tool '$tool' is not pinned in $MISE_PATH [tools]"
		echo "Fix: add '$tool = \"<version>\"' to $MISE_PATH."
		exit 1
	fi
done

if [[ -f "$TOOLING_DOC_PATH" ]]; then
	required_tooling_doc_terms=("node" "pnpm" "python" "uv" "make" "rg" "fd" "jq" "prek" "diagram" "mise" "vale" "argos" "cosign" "cloudflared" "vitest" "ruff" "pylint" "eslint" "agent-browser" "agentation-mcp" "mermaid-cli" "markdownlint-cli2" "wrangler" "beautiful-mermaid" "semgrep" "semver" "trivy" "rsearch" "wsearch")
	for term in "${required_tooling_doc_terms[@]}"; do
		if ! rg -qi "(^|[^A-Za-z0-9_-])${term}([^A-Za-z0-9_-]|$)" "$TOOLING_DOC_PATH"; then
			echo "Error: tooling doc missing expected term '$term': $TOOLING_DOC_PATH"
			echo "Fix: update tooling inventory and keep it aligned with $MISE_PATH."
			echo "Interactive flow: run a Codex AskQuestion/request_user_input prompt before applying installs."
			exit 1
		fi
	done
else
	echo "Warning: tooling doc not found at $TOOLING_DOC_PATH; skipping doc sync check."
fi

	required_bins=("pnpm" "node" "jq" "make" "rg" "fd" "python3" "prek" "diagram" "mise" "vale" "argos" "cosign" "cloudflared" "vitest" "ruff" "pylint" "eslint" "agent-browser" "agentation-mcp" "mmdc" "markdownlint-cli2" "wrangler" "beautiful-mermaid" "semgrep" "semver" "trivy" "rsearch" "wsearch")
	for bin in "${required_bins[@]}"; do
		if ! command -v "$bin" >/dev/null 2>&1; then
			echo "Error: required binary '$bin' is not installed or not on PATH"
			exit 1
		fi
	done

	required_codex_actions=("Tools|tool" "Run|run" "Debug|debug" "Test|test" "Prek|test" "Diagram|tool" "Ralph|debug" "Mise|tool" "Vale|debug" "Argos|test" "Cosign|debug" "Cloudflared|run" "Vitest|test" "Ruff|debug" "Pylint|debug" "ESLint|debug" "Agent Browser|tool" "Agentation|tool" "Mermaid CLI|tool" "MarkdownLint|debug" "Wrangler|run" "1Password|tool" "Beautiful Mermaid|tool" "Auth0|tool" "Semgrep|debug" "Semver|tool" "Trivy|debug" "Gitleaks|debug" "Research|tool" "WSearch|tool")
	for action in "${required_codex_actions[@]}"; do
		name="${action%%|*}"
		icon="${action##*|}"
		if ! python3 - "$CODEX_ENVIRONMENT_PATH" "$name" "$icon" <<'PY'
import sys
import tomllib
from pathlib import Path

env_path = Path(sys.argv[1])
required_name = sys.argv[2]
required_icon = sys.argv[3]

data = tomllib.loads(env_path.read_text(encoding="utf-8"))
for action in data.get("actions", []):
    if action.get("name") == required_name and action.get("icon") == required_icon:
        sys.exit(0)
sys.exit(1)
PY
		then
			echo "Error: Codex environment action '$name' is missing or mapped to the wrong icon in $CODEX_ENVIRONMENT_PATH"
			exit 1
		fi
	done

	required_make_targets=("help" "install" "setup" "preflight" "worktree-ready" "verify-work" "codestyle" "hooks" "hooks-pre-commit" "hooks-pre-push" "secrets-staged" "docs-style-changed" "related-tests" "semgrep-changed" "diagrams-check" "lint" "docs-lint" "fmt" "typecheck" "test" "check" "audit" "secrets" "security" "clean" "reset" "ci" "diagrams" "env-check")
	for target in "${required_make_targets[@]}"; do
		if ! rg -q "^${target}:" "$MAKEFILE_PATH"; then
			echo "Error: required Makefile target '$target' is missing from $MAKEFILE_PATH"
			exit 1
		fi
	done

	python3 - "$PREK_CONFIG_PATH" <<'PY'
import sys
import tomllib
from pathlib import Path

prek_config = Path(sys.argv[1])
data = tomllib.loads(prek_config.read_text(encoding="utf-8"))
required_hooks = {
    "pre-commit": "bash scripts/hooks/pre-commit.sh",
    "commit-msg": "bash scripts/hooks/commit-msg.sh",
    "pre-push": "bash scripts/hooks/pre-push.sh",
}
found = {}
for repo in data.get("repos", []):
    for hook in repo.get("hooks", []):
        entry = hook.get("entry")
        for stage in hook.get("stages", []):
            if stage not in found:
                found[stage] = []
            found[stage].append(entry)

for stage, command in required_hooks.items():
    if command not in found.get(stage, []):
        print(
            f"Error: required prek hook '{stage}' is missing or out of date in {prek_config}",
            file=sys.stderr,
        )
        sys.exit(1)
PY

	git_common_dir="$(git -C "$REPO_ROOT" rev-parse --git-common-dir)"
	if [[ "$git_common_dir" = /* ]]; then
		git_hooks_dir="$git_common_dir/hooks"
	else
		git_hooks_dir="$REPO_ROOT/$git_common_dir/hooks"
	fi
	for hook_name in pre-commit commit-msg pre-push; do
		hook_path="$git_hooks_dir/$hook_name"
		if [[ -f "$hook_path" ]] && ! python3 - "$hook_path" <<'PY'
import re
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text(encoding="utf-8")
start = "# agent-skills prek home begin"
end = "# agent-skills prek home end"
if text.count(start) != 1 or text.count(end) != 1:
    raise SystemExit(1)
block = text.split(start, 1)[1].split(end, 1)[0]
commands = [line.strip() for line in block.splitlines() if line.strip() and not line.lstrip().startswith("#")]
root_assignments = [line for line in commands if re.fullmatch(r"export CODEX_HOOK_CACHE_ROOT=.+", line)]
prek_assignments = [line for line in commands if re.fullmatch(r'export PREK_HOME="\$CODEX_HOOK_CACHE_ROOT/prek"', line)]
if len(root_assignments) != 1 or len(prek_assignments) != 1:
    raise SystemExit(1)
if any("$HOME" in line or "~/.cache" in line for line in root_assignments + prek_assignments):
    raise SystemExit(1)
PY
		then
			echo "Error: installed git hook '$hook_name' does not set a sandbox-safe PREK_HOME"
			echo "Fix: run bash scripts/install-prek-hooks.sh"
			exit 1
		fi
	done

	if [[ -f "$PACKAGE_JSON_PATH" ]]; then
		required_package_scripts=("codestyle:validate|bash scripts/validate-codestyle.sh" "secrets:staged|bash scripts/check-staged-secrets.sh" "docs:style:changed|bash scripts/check-doc-style.sh" "test:related|bash scripts/check-related-tests.sh" "semgrep:changed|bash scripts/check-semgrep-changed.sh")
		for script_spec in "${required_package_scripts[@]}"; do
			script_name="${script_spec%%|*}"
			script_command="${script_spec#*|}"
			if ! jq -e --arg script_name "$script_name" --arg script_command "$script_command" '
				(.scripts // {})[$script_name] == $script_command
			' "$PACKAGE_JSON_PATH" >/dev/null; then
				echo "Error: package script '$script_name' is missing or out of date in $PACKAGE_JSON_PATH"
				echo "Fix: run node scripts/setup-git-hooks.js"
				exit 1
			fi
		done

		required_simple_git_hooks=("pre-commit|bash scripts/hooks/pre-commit.sh" "commit-msg|bash scripts/hooks/commit-msg.sh \$1" "pre-push|bash scripts/hooks/pre-push.sh")
		for hook_spec in "${required_simple_git_hooks[@]}"; do
			hook_name="${hook_spec%%|*}"
			hook_command="${hook_spec#*|}"
			if ! jq -e --arg hook_name "$hook_name" --arg hook_command "$hook_command" '
				.["simple-git-hooks"][$hook_name] == $hook_command
			' "$PACKAGE_JSON_PATH" >/dev/null; then
				echo "Error: simple-git-hooks entry '$hook_name' is missing or out of date in $PACKAGE_JSON_PATH"
				echo "Fix: run node scripts/setup-git-hooks.js"
				exit 1
			fi
		done

		has_package_marker() {
			local marker="$1"
			jq -e --arg marker "$marker" '
				((.dependencies // {}) + (.devDependencies // {})) | has($marker)
			' "$PACKAGE_JSON_PATH" >/dev/null
		}

		repo_capabilities=()
		ui_markers=("react" "react-dom" "next" "vite" "tailwindcss" "@storybook/react" "@storybook/react-vite" "@radix-ui/react-slot")
		for marker in "${ui_markers[@]}"; do
			if has_package_marker "$marker"; then
				repo_capabilities+=("ui")
				break
			fi
		done

		chatgpt_apps_sdk_markers=("@openai/chatkit" "@openai/agents" "@openai/agents-realtime")
		for marker in "${chatgpt_apps_sdk_markers[@]}"; do
			if has_package_marker "$marker"; then
				repo_capabilities+=("chatgpt_apps_sdk")
				break
			fi
		done

		has_capability() {
			local wanted="$1"
			for capability in "${repo_capabilities[@]}"; do
				if [[ "$capability" == "$wanted" ]]; then
					return 0
				fi
			done
			return 1
		}

		has_required_package() {
			local pkg="$1"
			local dependency_type="$2"
			case "$dependency_type" in
				dependencies)
					jq -e --arg pkg "$pkg" '(.dependencies // {}) | has($pkg)' "$PACKAGE_JSON_PATH" >/dev/null
					;;
				devDependencies)
					jq -e --arg pkg "$pkg" '(.devDependencies // {}) | has($pkg)' "$PACKAGE_JSON_PATH" >/dev/null
					;;
				either)
					jq -e --arg pkg "$pkg" '((.dependencies // {}) | has($pkg)) or ((.devDependencies // {}) | has($pkg))' "$PACKAGE_JSON_PATH" >/dev/null
					;;
				*)
					return 1
					;;
			esac
		}

		required_package_specs=("@brainwav/design-system-guidance|either|ui,chatgpt_apps_sdk")
		for spec in "${required_package_specs[@]}"; do
			pkg="${spec%%|*}"
			rest="${spec#*|}"
			dependency_type="${rest%%|*}"
			required_caps_csv="${rest#*|}"
			should_apply=0
			IFS=',' read -r -a required_caps <<< "$required_caps_csv"
			for capability in "${required_caps[@]}"; do
				if has_capability "$capability"; then
					should_apply=1
					break
				fi
		done
			if [[ "$should_apply" -eq 1 ]] && ! has_required_package "$pkg" "$dependency_type"; then
				echo "Error: required package '$pkg' is missing from $PACKAGE_JSON_PATH for explicit or detected UI/App SDK capabilities"
				echo "Fix: npm i $pkg"
				exit 1
			fi
		done
	fi

	mkdir -p "$REPO_ROOT/artifacts/policy"

echo "Running harness environment preflight..."

run_check_environment_with_runner() {
	local label="$1"
	shift
	local -a runner=("$@")
	local output=""
	local exit_code=0

	rm -f "$ATTESTATION_PATH"

	echo "Using harness runner: $label"
	set +e
	output="$("${runner[@]}" check-environment \
		--contract "$CONTRACT_PATH" \
		--json \
		--attestation "$ATTESTATION_PATH" 2>&1)"
	exit_code=$?
	set -e

	if [[ -n "$output" ]]; then
		printf '%s\n' "$output"
	fi

	if [[ "$exit_code" -ne 0 ]]; then
		rm -f "$ATTESTATION_PATH"
		echo "Runner failed: $label (exit $exit_code)"
		return 1
	fi

	if [[ ! -f "$ATTESTATION_PATH" ]]; then
		if CHECK_ENVIRONMENT_RUNNER_OUTPUT="$output" python3 - "$ATTESTATION_PATH" <<'PY'
import json
import os
import sys
from pathlib import Path

text = os.environ.get("CHECK_ENVIRONMENT_RUNNER_OUTPUT", "")
decoder = json.JSONDecoder()
for index, char in enumerate(text):
    if char != "{":
        continue
    try:
        obj, end = decoder.raw_decode(text[index:])
    except json.JSONDecodeError:
        continue
    if not isinstance(obj, dict):
        continue
    Path(sys.argv[1]).write_text(json.dumps(obj, sort_keys=True) + "\n", encoding="utf-8")
    raise SystemExit(0)
raise SystemExit(1)
PY
		then
			:
		fi
	fi

	if [[ ! -f "$ATTESTATION_PATH" ]]; then
		echo "Runner produced no attestation output: $label"
		return 1
	fi

	return 0
}

if [[ -f "$REPO_ROOT/src/cli.ts" ]] && command -v pnpm >/dev/null 2>&1 && pnpm --dir "$REPO_ROOT" exec tsx --version >/dev/null 2>&1; then
	if ! run_check_environment_with_runner "repo source CLI (pnpm --dir <repo> exec tsx src/cli.ts)" pnpm --dir "$REPO_ROOT" exec tsx "$REPO_ROOT/src/cli.ts"; then
		echo "Warning: repo source CLI failed; trying the next available runner."
	fi
fi

if [[ ! -f "$ATTESTATION_PATH" && -f "$REPO_ROOT/dist/cli.js" ]] && command -v node >/dev/null 2>&1; then
	if ! run_check_environment_with_runner "repo dist CLI (node dist/cli.js)" node "$REPO_ROOT/dist/cli.js"; then
		echo "Error: repo dist CLI failed to run check-environment successfully."
		exit 1
	fi
elif [[ ! -f "$ATTESTATION_PATH" && -x "$REPO_ROOT/scripts/harness-cli.sh" ]]; then
	if ! run_check_environment_with_runner "repo wrapper (bash scripts/harness-cli.sh)" bash "$REPO_ROOT/scripts/harness-cli.sh"; then
		echo "Error: repo wrapper failed to run check-environment successfully."
		exit 1
	fi
elif [[ ! -f "$ATTESTATION_PATH" ]]; then
	if ! command -v npm >/dev/null 2>&1; then
		echo "Error: npm is required to validate the global harness fallback."
		exit 1
	fi

	if ! npm ls -g --depth=0 @brainwav/coding-harness >/dev/null 2>&1; then
		echo "Error: @brainwav/coding-harness is not installed globally via npm."
		echo "Install globally and retry:"
		echo "  npm i -g @brainwav/coding-harness"
		echo "Private registry auth is required:"
		echo "  - Local shell: export NPM_TOKEN=<token>"
		echo "  - CI (CircleCI): set NPM_TOKEN as a project environment variable in CircleCI project settings"
		exit 1
	fi

	if ! command -v harness >/dev/null 2>&1; then
		echo "Error: global harness binary is not on PATH after npm installation."
		echo "Fix: ensure npm global bin directory is on PATH, then retry."
		exit 1
	fi

	if ! run_check_environment_with_runner "global npm harness ($(command -v harness))" harness; then
		echo "Error: global npm harness failed to run check-environment successfully."
		echo "Reinstall and retry:"
		echo "  npm i -g @brainwav/coding-harness"
		echo "If this is CI (CircleCI), confirm NPM_TOKEN is set as a project environment variable."
		exit 1
	fi
fi

jq -e '.passed == true' "$ATTESTATION_PATH" >/dev/null
echo "Environment check passed (attestation: $ATTESTATION_PATH)"
