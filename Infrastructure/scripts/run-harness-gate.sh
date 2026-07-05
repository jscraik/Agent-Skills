#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd)"

if [[ $# -eq 0 ]]; then
	echo "Usage: bash scripts/run-harness-gate.sh <harness-subcommand> [args...]" >&2
	exit 2
fi

run_with_process_storm_guard() {
	if ! command -v python3 >/dev/null 2>&1; then
		exec "$@"
	fi

	HARNESS_GATE_CWD="$REPO_ROOT" python3 - "$@" <<'PY'
import os
import signal
import subprocess
import sys
import time

FORBIDDEN_NEEDLES = (
    "npm view @openai/codex versions time --json",
    "npm view @openai/codex dist-tags --json",
)

cmd = sys.argv[1:]
proc = subprocess.Popen(cmd, cwd=os.environ["HARNESS_GATE_CWD"], start_new_session=True)


def process_snapshot():
    output = subprocess.check_output(["ps", "-axo", "pid=,ppid=,command="], text=True)
    parents = {}
    commands = {}
    for raw in output.splitlines():
        raw = raw.strip()
        if not raw:
            continue
        try:
            pid_raw, ppid_raw, command = raw.split(None, 2)
        except ValueError:
            continue
        pid = int(pid_raw)
        parents[pid] = int(ppid_raw)
        commands[pid] = command
    return parents, commands


def descendants(root_pid, parents):
    found = {root_pid}
    changed = True
    while changed:
        changed = False
        for pid, ppid in parents.items():
            if ppid in found and pid not in found:
                found.add(pid)
                changed = True
    return found


def stop_group():
    for sig in (signal.SIGTERM, signal.SIGKILL):
        try:
            os.killpg(proc.pid, sig)
        except ProcessLookupError:
            return
        time.sleep(1)


while True:
    status = proc.poll()
    if status is not None:
        raise SystemExit(status)

    try:
        parents, commands = process_snapshot()
    except (OSError, subprocess.SubprocessError):
        time.sleep(1)
        continue
    branch = descendants(proc.pid, parents)
    matches = [
        (pid, commands.get(pid, ""))
        for pid in sorted(branch)
        if any(needle in commands.get(pid, "") for needle in FORBIDDEN_NEEDLES)
    ]
    if matches:
        stop_group()
        print(
            "Error: harness gate spawned Codex npm metadata lookups; stopped process branch to prevent a local process storm.",
            file=sys.stderr,
        )
        for pid, command in matches[:10]:
            print(f"blocked_process pid={pid} command={command}", file=sys.stderr)
        raise SystemExit(124)

    time.sleep(1)
PY
}

is_harness_source_repo() {
	[[ -f "$REPO_ROOT/src/cli.ts" ]] || return 1
	[[ -f "$REPO_ROOT/package.json" ]] || return 1
	command -v node >/dev/null 2>&1 || return 1

	node -e '
		const { readFileSync } = require("node:fs");
		const packageJson = JSON.parse(readFileSync(process.argv[1], "utf8"));
		process.exit(packageJson.name === "@brainwav/coding-harness" ? 0 : 1);
	' "$REPO_ROOT/package.json" >/dev/null 2>&1
}

if is_harness_source_repo; then
	if ! command -v node >/dev/null 2>&1; then
		echo "Error: source checkout detected but node is unavailable; refusing fallback to avoid stale harness binaries." >&2
		exit 1
	fi
	cd "$REPO_ROOT"
	if ! node --import tsx --eval "" >/dev/null 2>&1; then
		echo "Error: source checkout detected but tsx cannot be resolved from $REPO_ROOT; run the repository install first." >&2
		exit 1
	fi
	run_with_process_storm_guard node --import tsx "$REPO_ROOT/src/cli.ts" "$@"
	exit "$?"
fi

if [[ -f "$REPO_ROOT/dist/cli.js" ]] && command -v node >/dev/null 2>&1; then
	run_with_process_storm_guard node "$REPO_ROOT/dist/cli.js" "$@"
	exit "$?"
fi

if [[ -f "$REPO_ROOT/scripts/harness-cli.sh" && -r "$REPO_ROOT/scripts/harness-cli.sh" ]]; then
	wrapper_exit=0
	bash "$REPO_ROOT/scripts/harness-cli.sh" "$@" || wrapper_exit=$?
	if [[ "$wrapper_exit" -eq 0 ]]; then
		exit 0
	fi
	if [[ "$wrapper_exit" -eq 126 || "$wrapper_exit" -eq 127 ]]; then
		echo "Warning: scripts/harness-cli.sh unavailable (exit $wrapper_exit); attempting fallback runners." >&2
	else
		exit "$wrapper_exit"
	fi
fi

if command -v mise >/dev/null 2>&1; then
	MISE_RESOLVED="$(mise which harness 2>/dev/null || true)"
	if [[ -n "$MISE_RESOLVED" && -x "$MISE_RESOLVED" ]]; then
		run_with_process_storm_guard "$MISE_RESOLVED" "$@"
		exit "$?"
	fi
fi

if command -v harness >/dev/null 2>&1; then
	run_with_process_storm_guard harness "$@"
	exit "$?"
fi

echo "Error: unable to resolve a harness runner for this repository." >&2
echo "Install dependencies with:" >&2
echo "  npm install" >&2
echo "or run with a local harness install via:" >&2
echo "  npm exec harness -- <command>" >&2
exit 1
