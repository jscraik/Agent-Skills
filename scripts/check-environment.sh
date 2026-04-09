#!/usr/bin/env bash
# Local environment preflight (strict)
# Fails fast when required tooling is missing.

set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"
CONTRACT_PATH="$REPO_ROOT/harness.contract.json"
ATTESTATION_PATH="$REPO_ROOT/artifacts/policy/environment-attestation.json"
MISE_PATH="$REPO_ROOT/.mise.toml"
CODEX_ENVIRONMENT_PATH="$REPO_ROOT/.codex/environments/environment.toml"
MAKEFILE_PATH="$REPO_ROOT/Makefile"
PREK_CONFIG_PATH="$REPO_ROOT/prek.toml"
PACKAGE_JSON_PATH="$REPO_ROOT/package.json"
TOOLING_CONTRACT_PATH="${TOOLING_CONTRACT_PATH:-$REPO_ROOT/docs/agents/tooling.contract.json}"
TOOLING_DOC_PATH="${TOOLING_DOC_PATH:-$REPO_ROOT/docs/agents/tooling.md}"

if [[ ! -f "$CONTRACT_PATH" ]]; then
	echo "Error: missing contract file at $CONTRACT_PATH"
	exit 1
fi

if ! command -v rg >/dev/null 2>&1; then
	echo "Error: required binary 'rg' is not installed or not on PATH"
	exit 1
fi

if ! command -v jq >/dev/null 2>&1; then
	echo "Error: required binary 'jq' is not installed or not on PATH"
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

if [[ ! -f "$TOOLING_CONTRACT_PATH" ]]; then
	echo "Error: missing tooling contract at $TOOLING_CONTRACT_PATH"
	exit 1
fi

if ! jq -e '
	(.required_mise_tools | type == "array") and
	(.required_bins | type == "array") and
	(.required_codex_actions | type == "array")
' "$TOOLING_CONTRACT_PATH" >/dev/null; then
	echo "Error: invalid tooling contract schema at $TOOLING_CONTRACT_PATH"
	echo "Fix: required arrays are required_mise_tools, required_bins, and required_codex_actions."
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

required_support_files=("scripts/codex-preflight.sh" "scripts/check-staged-secrets.sh" "scripts/check-doc-style.sh" "scripts/check-related-tests.sh" "scripts/check-semgrep-changed.sh" "scripts/semgrep-pre-push.yml")
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
export CLAUDE_APPROVAL_POSTURE="${CLAUDE_APPROVAL_POSTURE:-require}"

required_mise_tools=()
while IFS= read -r tool; do
	required_mise_tools+=("$tool")
done < <(jq -r '.required_mise_tools[]' "$TOOLING_CONTRACT_PATH")

required_bins=()
while IFS= read -r bin; do
	required_bins+=("$bin")
done < <(jq -r '.required_bins[]' "$TOOLING_CONTRACT_PATH")

required_codex_actions=()
while IFS= read -r action; do
	required_codex_actions+=("$action")
done < <(jq -r '.required_codex_actions[] | "\(.name)|\(.icon)"' "$TOOLING_CONTRACT_PATH")

for tool in "${required_mise_tools[@]}"; do
	if ! rg -Fq "\"${tool}\" = " "$MISE_PATH" && ! rg -Fq "${tool} = " "$MISE_PATH"; then
		echo "Error: required tool '$tool' is not pinned in $MISE_PATH [tools]"
		echo "Fix: add '$tool = \"<version>\"' to $MISE_PATH."
		exit 1
	fi
done

if [[ -f "$TOOLING_DOC_PATH" ]]; then
	for tool in "${required_mise_tools[@]}"; do
		if ! rg -Fq "\`${tool}\`" "$TOOLING_DOC_PATH"; then
			echo "Error: tooling doc missing required mise tool '${tool}': $TOOLING_DOC_PATH"
			echo "Fix: regenerate docs/agents/tooling.md from $TOOLING_CONTRACT_PATH."
			exit 1
		fi
	done

	for bin in "${required_bins[@]}"; do
		if ! rg -Fq "\`${bin}\`" "$TOOLING_DOC_PATH"; then
			echo "Error: tooling doc missing required binary '${bin}': $TOOLING_DOC_PATH"
			echo "Fix: regenerate docs/agents/tooling.md from $TOOLING_CONTRACT_PATH."
			exit 1
		fi
	done

	for action in "${required_codex_actions[@]}"; do
		name="${action%%|*}"
		icon="${action##*|}"
		if ! rg -Fq "| \`${name}\` | \`${icon}\` |" "$TOOLING_DOC_PATH"; then
			echo "Error: tooling doc missing required Codex action '${name}|${icon}': $TOOLING_DOC_PATH"
			echo "Fix: regenerate docs/agents/tooling.md from $TOOLING_CONTRACT_PATH."
			exit 1
		fi
	done
else
	echo "Warning: tooling doc not found at $TOOLING_DOC_PATH; skipping doc sync check."
fi

for bin in "${required_bins[@]}"; do
	if ! command -v "$bin" >/dev/null 2>&1; then
		echo "Error: required binary '$bin' is not installed or not on PATH"
		exit 1
	fi
done

for action in "${required_codex_actions[@]}"; do
	name="${action%%|*}"
	icon="${action##*|}"
	if ! awk -v name="$name" -v icon="$icon" '
		prev == "name = \"" name "\"" && $0 == "icon = \"" icon "\"" { found = 1 }
		{ prev = $0 }
		END { exit found ? 0 : 1 }
	' "$CODEX_ENVIRONMENT_PATH"; then
		echo "Error: Codex environment action '$name' is missing or mapped to the wrong icon in $CODEX_ENVIRONMENT_PATH"
		exit 1
	fi
done

	required_make_targets=("help" "install" "setup" "preflight" "hooks" "hooks-pre-commit" "hooks-commit-msg" "hooks-pre-push" "secrets-staged" "docs-style-changed" "related-tests" "semgrep-changed" "diagrams-check" "lint" "docs-lint" "fmt" "typecheck" "test" "check" "audit" "secrets" "security" "clean" "reset" "ci" "diagrams" "env-check")
	for target in "${required_make_targets[@]}"; do
		if ! rg -q "^${target}:" "$MAKEFILE_PATH"; then
			echo "Error: required Makefile target '$target' is missing from $MAKEFILE_PATH"
			exit 1
		fi
	done

	python3 - "$PREK_CONFIG_PATH" <<'PY'
import sys
import tomllib

path = sys.argv[1]
with open(path, "rb") as fh:
    data = tomllib.load(fh)

if data.get("default_install_hook_types") != ["pre-commit", "commit-msg", "pre-push"]:
    raise SystemExit(f"Error: default_install_hook_types must be canonical in {path}")

hooks = {}
for repo in data.get("repos", []):
    if repo.get("repo") != "local":
        continue
    for hook in repo.get("hooks", []):
        hook_id = hook.get("id")
        if hook_id:
            hooks[hook_id] = hook

expected = {
    "hooks-pre-commit": {
        "entry": "make hooks-pre-commit",
        "stages": ["pre-commit"],
    },
    "hooks-commit-msg": {
        "entry": 'bash -lc \'make hooks-commit-msg HOOK_COMMIT_MSG_FILE="$1"\' --',
        "stages": ["commit-msg"],
    },
    "hooks-pre-push": {
        "entry": "make hooks-pre-push",
        "stages": ["pre-push"],
    },
}

for hook_id, contract in expected.items():
    hook = hooks.get(hook_id)
    if not hook:
        raise SystemExit(f"Error: required prek hook '{hook_id}' is missing in {path}")
    if hook.get("entry") != contract["entry"]:
        raise SystemExit(f"Error: required prek hook '{hook_id}' has the wrong entry in {path}")
    if hook.get("stages") != contract["stages"]:
        raise SystemExit(f"Error: required prek hook '{hook_id}' has the wrong stages in {path}")
PY

	if [[ -f "$REPO_ROOT/.pre-commit-config.yaml" ]]; then
		echo "Error: legacy .pre-commit-config.yaml must be removed from $REPO_ROOT" >&2
		echo "Fix: keep prek.toml as the single source of truth for git hooks." >&2
		exit 1
	fi

	if [[ -f "$PACKAGE_JSON_PATH" ]]; then
		required_package_scripts=("secrets:staged|bash scripts/check-staged-secrets.sh" "docs:style:changed|bash scripts/check-doc-style.sh" "test:related|bash scripts/check-related-tests.sh" "semgrep:changed|bash scripts/check-semgrep-changed.sh")
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

		if jq -e 'has("simple-git-hooks") or ((.devDependencies // {}) | has("simple-git-hooks"))' "$PACKAGE_JSON_PATH" >/dev/null; then
			echo "Error: legacy simple-git-hooks metadata must be removed from $PACKAGE_JSON_PATH"
			echo "Fix: run node scripts/setup-git-hooks.js"
			exit 1
		fi

		has_package_marker() {
			local marker="$1"
			jq -e --arg marker "$marker" '
				((.dependencies // {}) + (.devDependencies // {})) | has($marker)
			' "$PACKAGE_JSON_PATH" >/dev/null
		}

		repo_capabilities=()
		explicit_capabilities=()
		for capability in "${explicit_capabilities[@]}"; do
			[[ -n "$capability" ]] || continue
			repo_capabilities+=("$capability")
		done
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
		echo "Runner failed: $label (exit $exit_code)"
		return 1
	fi

	if [[ ! -f "$ATTESTATION_PATH" ]]; then
		local json_line
		json_line="$(printf '%s\n' "$output" | awk '/^\{/{line=$0} END{if(line!="") print line}')"
		if [[ -n "$json_line" ]]; then
			printf '%s\n' "$json_line" > "$ATTESTATION_PATH"
		fi
	fi

	if [[ ! -f "$ATTESTATION_PATH" ]]; then
		echo "Runner produced no attestation output: $label"
		return 1
	fi

	return 0
}

runner_succeeded=0

if [[ -n "${CODING_HARNESS_CLI_PATH:-}" ]]; then
	if [[ -f "${CODING_HARNESS_CLI_PATH}" ]]; then
		if run_check_environment_with_runner "CODING_HARNESS_CLI_PATH" node "${CODING_HARNESS_CLI_PATH}"; then
			runner_succeeded=1
		fi
	elif command -v "${CODING_HARNESS_CLI_PATH}" >/dev/null 2>&1; then
		if run_check_environment_with_runner "CODING_HARNESS_CLI_PATH command" "${CODING_HARNESS_CLI_PATH}"; then
			runner_succeeded=1
		fi
	else
		echo "Warning: CODING_HARNESS_CLI_PATH is set but not usable: ${CODING_HARNESS_CLI_PATH}"
	fi
fi

if [[ "$runner_succeeded" -eq 0 ]] && command -v harness >/dev/null 2>&1; then
	if run_check_environment_with_runner "PATH harness ($(command -v harness))" harness; then
		runner_succeeded=1
	fi
fi

if [[ "$runner_succeeded" -eq 0 ]] && [[ -x /opt/homebrew/bin/harness ]]; then
	if run_check_environment_with_runner "Homebrew harness (/opt/homebrew/bin/harness)" /opt/homebrew/bin/harness; then
		runner_succeeded=1
	fi
fi

if [[ "$runner_succeeded" -eq 0 ]] && [[ -f "$HOME/dev/coding-harness/dist/cli.js" ]]; then
	if run_check_environment_with_runner "local coding-harness dist ($HOME/dev/coding-harness/dist/cli.js)" node "$HOME/dev/coding-harness/dist/cli.js"; then
		runner_succeeded=1
	fi
fi

if [[ "$runner_succeeded" -eq 0 ]] && [[ -x "$REPO_ROOT/dist/cli.js" ]]; then
	if run_check_environment_with_runner "repo dist CLI ($REPO_ROOT/dist/cli.js)" node "$REPO_ROOT/dist/cli.js"; then
		runner_succeeded=1
	fi
fi

if [[ "$runner_succeeded" -eq 0 ]] && [[ -f "$REPO_ROOT/src/cli.ts" ]]; then
	if run_check_environment_with_runner "repo source CLI ($REPO_ROOT/src/cli.ts)" pnpm exec tsx "$REPO_ROOT/src/cli.ts"; then
		runner_succeeded=1
	fi
fi

if [[ "$runner_succeeded" -eq 0 ]]; then
	echo "Error: unable to run harness check-environment with a compatible CLI."
	echo "Install or provide a compatible harness CLI, then retry."
	echo "Options:"
	echo "  1) Install globally (recommended for skills/config repos):"
	echo "     npm i -g @brainwav/coding-harness"
	echo "     Requires auth for the private package:"
	echo "     - Local shell: export NPM_TOKEN=<token>"
	echo "     - GitHub Actions: add repository secret NPM_TOKEN and map it to workflow env"
	echo '       env: NPM_TOKEN: ${{ secrets.NPM_TOKEN }}'
	echo "  2) Point to a known-good local CLI build:"
	echo "     export CODING_HARNESS_CLI_PATH=\"$HOME/dev/coding-harness/dist/cli.js\""
	echo "  3) Use any compatible harness binary on PATH."
	exit 1
fi

jq -e '.passed == true' "$ATTESTATION_PATH" >/dev/null
echo "Environment check passed (attestation: $ATTESTATION_PATH)"
