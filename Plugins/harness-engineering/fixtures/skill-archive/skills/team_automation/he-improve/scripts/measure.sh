#!/bin/bash

# Measurement runner for he-improve optimization loops.
#
# Usage: measure.sh <command> <timeout_seconds> [working_directory] [KEY=VALUE ...]
#
# Trust contract:
# - Set HE_IMPROVE_COMMAND_PROVENANCE to describe the approved command source.
# - Command must be executable/argv style (no shell metacharacter pipelines/chains).

set -euo pipefail

COMMAND="${1:?Error: command argument required}"
TIMEOUT="${2:?Error: timeout_seconds argument required}"
shift 2

WORKDIR="."
if [[ $# -gt 0 ]] && [[ "$1" != *=* ]]; then
  WORKDIR="$1"
  shift
fi

for arg in "$@"; do
  if [[ "$arg" == *=* ]]; then
    export "$arg"
  fi
done

PROVENANCE="${HE_IMPROVE_COMMAND_PROVENANCE:-}"
if [[ -z "$PROVENANCE" ]]; then
  echo "Error: HE_IMPROVE_COMMAND_PROVENANCE is required before executing measurement commands." >&2
  exit 2
fi

if [[ "$COMMAND" == *$'\n'* ]] || [[ "$COMMAND" == *$'\r'* ]]; then
  echo "Error: measurement command contains unsupported newline characters." >&2
  exit 2
fi

if [[ "$COMMAND" =~ [\;\&\|\<\>\`\$\(\)\{\}] ]]; then
  echo "Error: complex shell metacharacters are not allowed in measurement commands." >&2
  echo "Provide a direct executable invocation without shell pipelines or command chaining." >&2
  exit 2
fi

cd "$WORKDIR" || {
  echo "Error: cannot cd to $WORKDIR" >&2
  exit 1
}

# run_with_timeout runs $COMMAND with a wall-clock timeout of $TIMEOUT seconds and propagates the command's exit status.
# 
# Uses an embedded Python3 helper to spawn the command in a new process session, wait up to $TIMEOUT seconds, and on timeout send SIGTERM to the command's process group then SIGKILL if it does not exit; on timeout the function exits with status 124. If the command tokenizes to an empty argv the helper exits with 2. If python3 is unavailable the function prints an error and exits with 1.
run_with_timeout() {
  if command -v python3 >/dev/null 2>&1; then
    python3 - "$TIMEOUT" "$COMMAND" <<'PY'
import os
import shlex
import signal
import subprocess
import sys

timeout_seconds = int(sys.argv[1])
command = sys.argv[2].strip()
argv = shlex.split(command)
if not argv:
    print("Error: command argument resolved to empty argv", file=sys.stderr)
    sys.exit(2)

proc = subprocess.Popen(argv, start_new_session=True)

try:
    sys.exit(proc.wait(timeout=timeout_seconds))
except subprocess.TimeoutExpired:
    os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        os.killpg(proc.pid, signal.SIGKILL)
        proc.wait()
    sys.exit(124)
PY
    return
  fi

  echo "Error: no supported execution backend available (python3 required)." >&2
  exit 1
}

run_with_timeout
