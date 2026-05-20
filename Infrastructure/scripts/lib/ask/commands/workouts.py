from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from ask.envelope import CallResult, ErrorObject


WORKOUTS_DIRNAME = ".workouts"
TELEMETRY_DIRNAME = ".skill-telemetry"
DEFAULT_MAX_SKILL_CONTEXT_TOKENS = 1500
EXPECTED_DECLARED_METRICS = {
    "success",
    "wall_clock_seconds",
    "tool_steps",
    "retries",
    "flake_rate",
    "estimated_skill_context_tokens",
}


def add_workouts_parser(subparsers: Any, global_parser: Any) -> None:
    """
    Register the `workouts` CLI command group and its subcommands on the provided subparsers object.

    Adds a top-level "workouts" parser with subcommands:
    - list: no extra args, lists available workouts
    - run <workout_id> [--attempts N]: executes a workout with an optional attempts bound
    - score <workout_id>: shows the latest scorecard for a workout
    - promote <workout_id> [--if-better] [--dry-run]: validates or records a promotion

    Parameters:
        subparsers (Any): The argparse subparsers object returned by ArgumentParser.add_subparsers().
        global_parser (Any): An ArgumentParser instance whose arguments should be inherited by the workouts subparsers.
    """
    workouts_parser = subparsers.add_parser("workouts", help="Skill workout sessions", parents=[global_parser])
    workouts_subparsers = workouts_parser.add_subparsers(dest="action")
    workouts_subparsers.add_parser("list", help="List available skill workouts", parents=[global_parser])
    run_parser = workouts_subparsers.add_parser("run", help="Run a skill workout", parents=[global_parser])
    run_parser.add_argument("workout_id", help="Workout id, for example agent-ops/verification-before-completion")
    run_parser.add_argument("--attempts", type=int, default=1, help="Attempt count, bounded by workout config")
    score_parser = workouts_subparsers.add_parser("score", help="Show latest workout scorecard", parents=[global_parser])
    score_parser.add_argument("workout_id", help="Workout id")
    promote_parser = workouts_subparsers.add_parser("promote", help="Validate or record workout promotion", parents=[global_parser])
    promote_parser.add_argument("workout_id", help="Workout id")
    promote_parser.add_argument("--if-better", action="store_true", help="Require a promotion-eligible scorecard")
    promote_parser.add_argument("--dry-run", action="store_true", help="Validate rollback and promotion gates without writing")


def dispatch_workouts(repo_root: Path, args: Any) -> CallResult:
    """
    Dispatches 'workouts' subcommands to their corresponding handlers.

    Parameters:
        repo_root (Path): Repository root directory used for resolving workout and telemetry paths.
        args (Any): Parsed command-line arguments object that must include `action` and, depending on action,
            `workout_id`, `attempts`, `if_better`, and `dry_run` as applicable.

    Returns:
        CallResult: The result produced by the selected handler (`list_workouts`, `run_workout`,
        `score_workout`, or `promote_workout`). If `args.action` is missing or not one of the valid
        actions, returns a `CallResult` with `status` set to `"error"` and a validation error indicating
        valid actions: `list`, `run`, `score`, `promote`.
    """
    if args.action == "list":
        return list_workouts(repo_root)
    if args.action == "run":
        return run_workout(repo_root, args.workout_id, attempts=args.attempts)
    if args.action == "score":
        return score_workout(repo_root, args.workout_id)
    if args.action == "promote":
        return promote_workout(repo_root, args.workout_id, if_better=args.if_better, dry_run=args.dry_run)

    result = CallResult()
    action_msg = f"unknown action '{args.action}'" if args.action else "missing action"
    result.status = "error"
    result.data["validation_commands"] = [_workouts_validation_command("list")]
    result.errors.append(ErrorObject(
        code="ERR_VALIDATION",
        message=f"{action_msg} for topic 'workouts'",
        fix_suggestion="Valid actions: list, run, score, promote",
    ))
    return result


def render_workouts_human(args: Any, result: CallResult) -> None:
    """Print a compact human summary for workout command results."""
    print(f"✅ Workout {args.action}: {result.status}")
    if args.action == "list":
        print(f"Workouts: {result.data.get('count', 0)}")
        for workout in result.data.get("workouts", []):
            print(f"  - {workout.get('id')} ({workout.get('path')})")
    elif args.action == "run":
        print(f"Workout: {result.data.get('workout', args.workout_id)}")
        print(f"Run id: {result.data.get('run_id')}")
        print(f"Scorecard: {result.data.get('scorecard_path')}")
    elif args.action == "score":
        print(f"Scorecard: {result.data.get('scorecard_path')}")
    elif args.action == "promote":
        promotion = result.data.get("promotion", {})
        print(f"Promotion state: {promotion.get('state', 'unknown')}")
    commands = result.data.get("validation_commands") or []
    if commands:
        print(f"Validation: {commands[0]}")


def _timestamp() -> str:
    """
    Produce an ISO-8601 UTC timestamp with second precision and a trailing "Z".

    Returns:
        timestamp (str): Current UTC time formatted as an ISO-8601 string (e.g. "2026-04-25T12:34:56Z").
    """
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str) -> str:
    """
    Normalize an identifier string by trimming whitespace, removing leading/trailing slashes, and converting backslashes to forward slashes.

    Parameters:
        value (str): Input identifier to normalize.

    Returns:
        str: The normalized identifier.
    """
    return value.strip().strip("/").replace("\\", "/")


def _safe_filename(value: str) -> str:
    """
    Produce a filename-safe representation of an identifier or path.

    Converts the input string into a safe filename by trimming and normalizing path separators, then replacing each forward slash with two underscores.

    Parameters:
        value (str): Identifier or path to sanitize.

    Returns:
        filename (str): Filename-safe string derived from `value`.
    """
    return _safe_id(value).replace("/", "__")


def _workouts_validation_command(
    action: str,
    workout_id: str | None = None,
    *,
    attempts: int | None = None,
    if_better: bool = False,
    dry_run: bool = False,
) -> str:
    parts = ["./bin/ask", "workouts", action]
    if workout_id:
        parts.append(_safe_id(workout_id))
    if attempts is not None and attempts != 1:
        parts.extend(["--attempts", str(attempts)])
    if if_better:
        parts.append("--if-better")
    if dry_run:
        parts.append("--dry-run")
    parts.extend(["--json", "--robot"])
    return " ".join(shlex.quote(part) for part in parts)


def _sha256(path: Path) -> str:
    """
    Compute the SHA-256 digest of a file's contents and return it as a hex string.

    Parameters:
        path (Path): Path to the file whose bytes will be hashed.

    Returns:
        hex_digest (str): Hex-encoded SHA-256 digest of the file contents.
    """
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _declared_metrics(config: dict[str, Any]) -> set[str]:
    """
    Extracts and validates the set of metric names declared in a workout configuration.

    Parameters:
        config (dict[str, Any]): The workout configuration mapping, typically loaded from the workout manifest.

    Returns:
        set[str]: A set of metric names (trimmed strings) declared by the workout.

    Raises:
        ValueError: If `config["constraints"]` exists but is not a mapping, or if the declared metrics are not a list of non-empty strings.
    """
    constraints = config.get("constraints") or {}
    if not isinstance(constraints, dict):
        raise ValueError("Workout constraints must be a mapping")
    declared = constraints.get("metrics") or config.get("metrics") or []
    if not isinstance(declared, list) or not all(isinstance(item, str) and item.strip() for item in declared):
        raise ValueError("Workout metrics must be a list of non-empty metric names")
    return {item.strip() for item in declared}


def _timeout_text(value: bytes | str | None) -> str:
    """
    Normalize a bytes/string/None process output into a UTF-8 string safe for display.

    Parameters:
        value (bytes | str | None): The raw output value; may be bytes, a string, or None.

    Returns:
        str: Decoded UTF-8 string when `value` is bytes (invalid sequences replaced), the original string when `value` is a str, or an empty string when `value` is None.
    """
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _timed_out_process(exc: subprocess.TimeoutExpired) -> subprocess.CompletedProcess[str]:
    """
    Create a CompletedProcess representing a subprocess that timed out.

    Parameters:
        exc (subprocess.TimeoutExpired): The TimeoutExpired exception raised by subprocess.run() / subprocess.Popen that contains the original command, timeout value, and any captured stdout/stderr.

    Returns:
        subprocess.CompletedProcess[str]: A CompletedProcess with returncode 124, `args` set from `exc.cmd`, `stdout` populated from the original stdout (converted to text), and `stderr` containing the original stderr text followed by a "Command timed out after N seconds" note.
    """
    stderr = _timeout_text(exc.stderr)
    timeout_note = f"Command timed out after {exc.timeout} seconds"
    stderr = f"{stderr}\n{timeout_note}" if stderr else timeout_note
    return subprocess.CompletedProcess(
        args=exc.cmd,
        returncode=124,
        stdout=_timeout_text(exc.stdout),
        stderr=stderr,
    )


def _run_workout_command(command: list[str], *, repo_root: Path, env: dict[str, str]) -> tuple[subprocess.CompletedProcess[str], bool]:
    # Workout scripts (seed.sh under .workouts/) are trusted repository content.
    # Path-traversal checks elsewhere prevent escaping the workouts directory,
    # so executing these scripts is considered safe. We intentionally pass check=False
    # to handle non-zero exit codes ourselves rather than raising CalledProcessError.
    """
    Run a trusted workout command in the repository root with a 60-second timeout.

    Parameters:
        repo_root (Path): Directory to use as the process working directory.
        env (dict[str, str]): Environment variables to pass to the subprocess.

    Returns:
        (process, timed_out): `process` is a CompletedProcess capturing stdout, stderr, and the exit code; `timed_out` is `True` when the command exceeded the 60-second timeout, `False` otherwise.
    """
    try:
        process = subprocess.run(
            command,
            cwd=str(repo_root),
            env=env,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return _timed_out_process(exc), True
    return process, False


def _load_structured_file(path: Path) -> dict[str, Any]:
    """
    Load a file containing JSON or YAML and return its top-level mapping.

    Attempts to parse the file as JSON first. If JSON parsing fails it will try to parse as YAML using PyYAML when available. If YAML is not available or parsing fails, a limited line/indentation-based fallback parser is applied that supports simple mappings and lists. The function guarantees the returned value is a dict.

    Parameters:
        path (Path): Path to the input file to read and parse.

    Returns:
        dict[str, Any]: The parsed top-level mapping from the file.

    Raises:
        ValueError: If the file cannot be parsed into a mapping or if the parsed top-level value is not a mapping.
    """
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
    except ImportError:
        # When PyYAML is unavailable, reject YAML-specific syntax that the
        # fallback parser cannot safely validate (flow sequences/objects),
        # but do not reject brackets that appear inside quoted scalars.
        def _has_unquoted_bracket(s: str) -> bool:
            in_single = False
            in_double = False
            escaped = False
            for ch in s:
                if escaped:
                    escaped = False
                    continue
                if ch == "\\":
                    escaped = True
                    continue
                if ch == '"' and not in_single:
                    in_double = not in_double
                    continue
                if ch == "'" and not in_double:
                    in_single = not in_single
                    continue
                if ch in "[{" and not in_single and not in_double:
                    return True
            return False

        if _has_unquoted_bracket(text):
            raise ValueError(
                f"Invalid YAML in {path}: flow syntax detected but PyYAML is not available"
            )
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML in {path}: {exc}") from exc

    if "loaded" not in locals():
        loaded = {}
        current_key: Optional[str] = None
        current_nested_key: Optional[str] = None
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            line = raw_line.strip()
            if indent == 0 and ":" in line:
                key, value = line.split(":", 1)
                current_key = key.strip()
                current_nested_key = None
                value = value.strip().strip("\"'")
                loaded[current_key] = value if value else {}
            elif indent == 2 and current_key and ":" in line and isinstance(loaded.get(current_key), dict):
                key, value = line.split(":", 1)
                current_nested_key = key.strip()
                value = value.strip().strip("\"'")
                loaded[current_key][current_nested_key] = value if value else []
            elif current_key and line.startswith("- "):
                item = line[2:].strip().strip("\"'")
                if current_nested_key and isinstance(loaded.get(current_key), dict):
                    nested_value = loaded[current_key].setdefault(current_nested_key, [])
                    if not isinstance(nested_value, list):
                        loaded[current_key][current_nested_key] = []
                    loaded[current_key][current_nested_key].append(item)
                    continue
                if not isinstance(loaded.get(current_key), list):
                    loaded[current_key] = []
                loaded[current_key].append(item)
        if not loaded:
            raise ValueError(f"Unable to parse {path}: empty mapping")
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def _int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _resolve_inside(base_dir: Path, relative_path: str, *, label: str) -> Path:
    """
    Resolve a relative path against a base directory and ensure the resolved path is contained within that base.

    Parameters:
        base_dir (Path): The base directory to resolve against.
        relative_path (str): A non-empty, relative file-system path (must not be absolute).
        label (str): Human-readable label used in error messages to identify the path being resolved.

    Returns:
        Path: The absolute, resolved target path (guaranteed to be inside `base_dir`).

    Raises:
        ValueError: If `relative_path` is empty or absolute, or if the resolved target is not located within `base_dir`.
    """
    if not relative_path or Path(relative_path).is_absolute():
        raise ValueError(f"Workout {label} must be a relative path")
    base_resolved = base_dir.resolve()
    target = (base_dir / relative_path).resolve()
    try:
        target.relative_to(base_resolved)
    except ValueError as exc:
        raise ValueError(f"Workout {label} must stay inside {base_dir}") from exc
    return target


def _resolve_repo_path(repo_root: Path, relative_path: str, *, label: str) -> Path:
    """
    Resolve a repository-relative path under `repo_root` and ensure it does not escape the repository.

    Parameters:
        repo_root (Path): Repository root directory.
        relative_path (str): A non-empty path relative to the repository root.
        label (str): Human-readable label used in error messages for this path.

    Returns:
        Path: The resolved absolute path within `repo_root`.

    Raises:
        ValueError: If `relative_path` is empty or absolute, or if the resolved path is outside `repo_root`.
    """
    if not relative_path or Path(relative_path).is_absolute():
        raise ValueError(f"Workout {label} must be a relative repository path")
    repo_resolved = repo_root.resolve()
    target = (repo_root / relative_path).resolve()
    try:
        target.relative_to(repo_resolved)
    except ValueError as exc:
        raise ValueError(f"Workout {label} must stay inside {repo_root}") from exc
    return target


def _workout_dir(repo_root: Path, workout_id: str) -> Path:
    """
    Resolve the filesystem path for a workout directory inside the repository.

    Parameters:
        repo_root (Path): The repository root directory.
        workout_id (str): The workout identifier; it will be normalized. Must be a non-empty relative id that does not perform upward traversal.

    Returns:
        Path: The path repo_root/.workouts/<safe_workout_id>.

    Raises:
        ValueError: If the normalized workout id is empty, equals "..", or attempts directory traversal.
    """
    safe = _safe_id(workout_id)
    if not safe:
        raise ValueError("Workout id must be a relative .workouts path")
    try:
        return _resolve_inside(repo_root / WORKOUTS_DIRNAME, safe, label="id")
    except ValueError as exc:
        raise ValueError("Workout id must be a relative .workouts path") from exc


def _load_workout(repo_root: Path, workout_id: str) -> tuple[Path, dict[str, Any]]:
    """
    Load a workout's directory and configuration from the repository.

    Parameters:
        repo_root (Path): Path to the repository root containing the .workouts directory.
        workout_id (str): Identifier of the workout to load.

    Returns:
        (tuple[Path, dict[str, Any]]): A tuple where the first element is the workout directory Path
        and the second is the workout configuration dict. The configuration will include
        `workout_path` and `id` fields set to a sanitized form of `workout_id` if they were absent.

    Raises:
        FileNotFoundError: If the workout's `workout.yaml` file does not exist.
    """
    directory = _workout_dir(repo_root, workout_id)
    config_path = directory / "workout.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Workout not found: {workout_id}")
    config = _load_structured_file(config_path)
    config.setdefault("workout_path", _safe_id(workout_id))
    config.setdefault("id", _safe_id(workout_id))
    return directory, config


def _telemetry_dir(repo_root: Path) -> Path:
    """
    Resolve the directory used for storing skill telemetry.

    Parameters:
        repo_root (Path): Repository root to use when no environment override is provided.

    Returns:
        Path: The telemetry directory path — `SKILL_TELEMETRY_DIR` environment variable is used if set to a non-empty value (after trimming); otherwise returns `repo_root/.skill-telemetry`.
    """
    override = os.environ.get("SKILL_TELEMETRY_DIR", "").strip()
    return Path(override) if override else repo_root / TELEMETRY_DIRNAME


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    """
    Append a JSON-serialized object as a single newline-delimited record to a file, creating parent directories as needed.

    Parameters:
        path (Path): Path to the JSONL file to append to; parent directories will be created.
        payload (dict[str, Any]): Mapping to serialize as a single JSON object on its own line.

    Details:
        Serialization uses json.dumps(..., sort_keys=True) with UTF-8 encoding and a trailing newline.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _estimate_context_tokens(repo_root: Path, source_path: str) -> int:
    """
    Estimate the number of skill-context tokens required by a source file.

    Parameters:
        repo_root (Path): Repository root directory used to resolve `source_path`.
        source_path (str): Repository-relative path to the source file. If empty or the file does not exist, the function treats it as absent.

    Returns:
        int: Estimated token count derived from the file's word count (returns 0 when `source_path` is empty or the file is missing).
    """
    if not source_path:
        return 0
    target = repo_root / source_path
    if not target.is_file():
        return 0
    words = len([word for word in target.read_text(encoding="utf-8", errors="ignore").split() if word.strip()])
    return (words * 4 + 2) // 3


def _empty_score() -> dict[str, Any]:
    """
    Create a score dictionary initialized with zeroed aggregate fields for workout attempts and metrics.

    Returns:
        dict: A mapping containing the following keys initialized to 0:
            - "attempts": total number of attempts
            - "successes": number of successful attempts
            - "failures": number of failed attempts
            - "pass_rate": pass rate (0..1)
            - "flake_rate": 1 if both successes and failures occurred, otherwise 0
            - "wall_clock_seconds": total wall-clock time in seconds
            - "tool_steps": total tool-invocation steps
            - "retries": total retries across attempts
            - "estimated_skill_context_tokens": estimated token usage for the target source
    """
    return {
        "attempts": 0,
        "successes": 0,
        "failures": 0,
        "pass_rate": 0,
        "flake_rate": 0,
        "wall_clock_seconds": 0,
        "tool_steps": 0,
        "retries": 0,
        "estimated_skill_context_tokens": 0,
    }


def _latest_accepted_amendment(telemetry_dir: Path, workout_id: str) -> dict[str, Any] | None:
    """
    Finds the most recent accepted amendment JSON for a workout.

    Searches telemetry_dir/amendments/accepted for files named "<safe_workout_id>-*.json",
    parses them as JSON, and returns the last file (by filename sort) whose content is a JSON object.

    Parameters:
        telemetry_dir (Path): Base telemetry directory.
        workout_id (str): Workout identifier (will be converted to a safe filename form).

    Returns:
        dict[str, Any] | None: The parsed amendment object if found and valid, otherwise `None`.
    """
    accepted_dir = telemetry_dir / "amendments" / "accepted"
    if not accepted_dir.is_dir():
        return None
    candidates = sorted(accepted_dir.glob(f"{_safe_filename(workout_id)}-*.json"))
    for candidate in reversed(candidates):
        try:
            payload = json.loads(candidate.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _record_amendment(telemetry_dir: Path, state: str, workout_id: str, proposal: dict[str, Any]) -> Path:
    """
    Write the given amendment proposal as a JSON file under the telemetry amendments directory and return its path.

    The file is written to: <telemetry_dir>/amendments/<state>/<safe-workout-id>-<unix-timestamp>.json.
    Parent directories are created if needed; the JSON is pretty-printed with sorted keys and ends with a newline.

    Parameters:
        telemetry_dir (Path): Base telemetry directory.
        state (str): Amendment state subdirectory name (e.g., "proposed", "accepted", "rejected").
        workout_id (str): Workout identifier used to form a safe filename.
        proposal (dict[str, Any]): Amendment payload to serialize as JSON.

    Returns:
        Path: The path to the written JSON file.
    """
    target = telemetry_dir / "amendments" / state / f"{_safe_filename(workout_id)}-{time.time_ns()}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _score_attempts(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Compute aggregate statistics for a sequence of workout attempts.

    Parameters:
        attempts (list[dict[str, Any]]): List of attempt records where each record may contain
            keys like "outcome" (string, e.g. "success"), "wall_clock_seconds" (numeric),
            and "tool_steps" (integer).

    Returns:
        dict[str, Any]: Aggregated metrics with keys:
            - "attempts": total number of attempts.
            - "successes": count of attempts with outcome == "success".
            - "failures": count of non-success attempts.
            - "pass_rate": fraction of attempts that succeeded, rounded to 4 decimals (0 if none).
            - "flake_rate": 1 if there are both successes and failures, 0 otherwise.
            - "wall_clock_seconds": total wall-clock seconds summed and rounded to 4 decimals.
            - "tool_steps": sum of tool step counts across attempts.
            - "retries": max(0, attempts - 1).
    """
    total = len(attempts)
    successes = sum(1 for attempt in attempts if attempt.get("outcome") == "success")
    failures = total - successes
    wall_clock = sum(float(attempt.get("wall_clock_seconds") or 0) for attempt in attempts)
    tool_steps = sum(int(attempt.get("tool_steps") or 0) for attempt in attempts)
    return {
        "attempts": total,
        "successes": successes,
        "failures": failures,
        "pass_rate": round(successes / total, 4) if total else 0,
        "flake_rate": 1 if successes and failures else 0,
        "wall_clock_seconds": round(wall_clock, 4),
        "tool_steps": tool_steps,
        "retries": max(0, total - 1),
    }


def list_workouts(repo_root: Path) -> CallResult:
    """
    List available workouts from the repository's workouts directory.

    Scans the repository for workout configuration files and returns a summary list describing each discovered workout and its status.

    Returns:
        result (CallResult): A CallResult with `status="success"` and `data` containing:
            - `workouts` (list[dict]): One entry per discovered `workout.yaml` with keys:
                - `id` (str): Workout id derived from the path under the workouts directory.
                - `path` (str): Repo-relative path to the `workout.yaml`.
                - `status` (str): `"ready"` when the config loaded successfully or `"invalid"` when parsing failed.
                - `error` (str, optional): Error message present only when `status` is `"invalid"`.
                - `target_skill_set` (optional): Copied from the config when present.
                - `target_module` (optional): Copied from the config when present.
                - `level` (optional): Copied from the config when present.
            - `count` (int): Number of entries in `workouts`.
    """
    result = CallResult()
    workouts = []
    root = repo_root / WORKOUTS_DIRNAME
    if root.is_dir():
        for config_path in sorted(root.rglob("workout.yaml")):
            workout_id = config_path.parent.relative_to(root).as_posix()
            try:
                config = _load_structured_file(config_path)
            except ValueError as exc:
                workouts.append({
                    "id": workout_id,
                    "path": config_path.relative_to(repo_root).as_posix(),
                    "status": "invalid",
                    "error": str(exc),
                })
                continue
            workouts.append({
                "id": workout_id,
                "path": config_path.relative_to(repo_root).as_posix(),
                "status": "ready",
                "target_skill_set": config.get("target_skill_set"),
                "target_module": config.get("target_module"),
                "level": config.get("level"),
            })
    result.status = "success"
    result.data["workouts"] = workouts
    result.data["count"] = len(workouts)
    result.data["validation_commands"] = [_workouts_validation_command("list")]
    return result


def run_workout(repo_root: Path, workout_id: str, *, attempts: int = 1) -> CallResult:
    """
    Run a workout by executing its seed and verifier tools and produce a scorecard with telemetry.

    Runs up to `attempts` executions of the workout's configured seed and verifier inside the repository, records per-attempt telemetry, aggregates attempt results into a scorecard, writes telemetry/scorecard files under the telemetry directory, and returns a summary CallResult.

    Parameters:
        attempts (int): Desired number of attempts to execute; the actual number will be bounded by the workout's `max_attempts` configuration.

    Returns:
        CallResult: Result object with:
            - status: `"success"` if all attempts succeeded, `"error"` otherwise.
            - data: includes `run_id` (str), `workout` (str), `attempts` (list of per-attempt payloads), `scorecard` (dict), and `scorecard_path` (str).
            - errors: populated with `ErrorObject` entries on validation failures or if one or more attempts fail.
    """
    result = CallResult()
    result.data["validation_commands"] = [
        _workouts_validation_command("run", workout_id, attempts=attempts)
    ]
    try:
        directory, config = _load_workout(repo_root, workout_id)
    except (FileNotFoundError, ValueError) as exc:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(exc)))
        return result

    try:
        max_attempts = int(config.get("max_attempts", 5))
        requested_attempts = int(attempts)
        max_skill_context_tokens = int(config.get("max_skill_context_tokens", 1500))
        if max_attempts < 1 or requested_attempts < 1:
            raise ValueError
        if max_skill_context_tokens < 1:
            raise ValueError
        bounded_attempts = min(requested_attempts, max_attempts)
        seed_path = _resolve_inside(directory, str(config.get("seed", "seed.sh")), label="seed")
        verify_path = _resolve_inside(directory, str(config.get("verify", "verify.py")), label="verify")
        declared_metrics = _declared_metrics(config)
        if declared_metrics and declared_metrics != EXPECTED_DECLARED_METRICS:
            raise ValueError(
                "Workout metrics must exactly match "
                f"{', '.join(sorted(EXPECTED_DECLARED_METRICS))}"
            )
        target_source = str(config.get("target_source_path") or "")
        if target_source:
            _resolve_repo_path(repo_root, target_source, label="target_source_path")
    except (TypeError, ValueError) as exc:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Invalid workout configuration: {exc}",
            fix_suggestion="Use positive integer attempts/max_attempts and relative seed/verify paths inside the workout directory.",
        ))
        return result
    if not seed_path.is_file() or not verify_path.is_file():
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Workout seed.sh and verify.py must both exist.",
            fix_suggestion=f"Check {directory.relative_to(repo_root).as_posix()}",
        ))
        return result

    telemetry_dir = _telemetry_dir(repo_root)
    run_id = f"{_safe_filename(workout_id)}-{int(time.time())}"
    context_tokens = _estimate_context_tokens(repo_root, target_source)
    attempt_results: list[dict[str, Any]] = []

    for attempt_no in range(1, bounded_attempts + 1):
        verifier_hash_failed = False
        try:
            verifier_hash_before: Optional[str] = _sha256(verify_path)
        except OSError:
            verifier_hash_before = None
            verifier_hash_failed = True
        with tempfile.TemporaryDirectory(prefix="skill-workout-") as state_dir:
            start = time.monotonic()
            env = {
                **os.environ,
                "WORKOUT_STATE_DIR": state_dir,
                "WORKOUT_ID": str(config.get("id", workout_id)),
                "WORKOUT_ATTEMPT": str(attempt_no),
            }
            seed, seed_timed_out = _run_workout_command(["bash", str(seed_path)], repo_root=repo_root, env=env)
            if seed_timed_out:
                verify = subprocess.CompletedProcess(
                    args=[sys.executable, str(verify_path)],
                    returncode=124,
                    stdout="",
                    stderr="Verifier skipped because seed timed out.",
                )
                verify_timed_out = False
            else:
                verify, verify_timed_out = _run_workout_command([sys.executable, str(verify_path)], repo_root=repo_root, env=env)
            elapsed = time.monotonic() - start
        try:
            verifier_hash_after: Optional[str] = _sha256(verify_path)
        except OSError:
            verifier_hash_after = None
            verifier_hash_failed = True
        outcome = (
            "success"
            if not verifier_hash_failed
            and seed.returncode == 0
            and verify.returncode == 0
            and verifier_hash_before == verifier_hash_after
            else "failure"
        )
        failure_type: Optional[str] = None
        if verifier_hash_failed or verifier_hash_before != verifier_hash_after:
            failure_type = "contract_violation"
        elif seed_timed_out or verify_timed_out:
            failure_type = "timeout"
        elif seed.returncode != 0 or verify.returncode != 0:
            failure_type = "tool_error"
        attempt_payload = {
            "timestamp": _timestamp(),
            "run_id": run_id,
            "workout": _safe_id(workout_id),
            "attempt": attempt_no,
            "projection_mode": config.get("projection_mode", "rooted"),
            "root_skill_set": config.get("target_skill_set"),
            "selected_module": config.get("target_module"),
            "level": config.get("level"),
            "outcome": outcome,
            "failure_type": failure_type,
            "seed_exit_code": seed.returncode,
            "verify_exit_code": verify.returncode,
            "wall_clock_seconds": round(elapsed, 4),
            "tool_steps": 1 if seed_timed_out else 2,
            "retries": max(0, attempt_no - 1),
            "context_budget": {
                "modules_loaded": 1,
                "estimated_skill_context_tokens": context_tokens,
            },
        }
        attempt_results.append(attempt_payload)
        _append_jsonl(telemetry_dir / "runs.jsonl", attempt_payload)
        _append_jsonl(telemetry_dir / "workout-results.jsonl", attempt_payload)

    score = _score_attempts(attempt_results)
    scorecard = {
        "schema_version": "skill-workout-scorecard.v1",
        "timestamp": _timestamp(),
        "run_id": run_id,
        "workout": _safe_id(workout_id),
        "target_skill_set": config.get("target_skill_set"),
        "target_module": config.get("target_module"),
        "target_source_path": target_source,
        "metrics": {
            **score,
            "success": score["failures"] == 0,
            "estimated_skill_context_tokens": context_tokens,
        },
        "limits": {
            "max_skill_context_tokens": max_skill_context_tokens,
        },
        "promotion_eligible": score["failures"] == 0
        and score["pass_rate"] > 0
        and context_tokens <= max_skill_context_tokens,
    }
    scorecard_path = telemetry_dir / "scorecards" / f"{_safe_filename(workout_id)}.json"
    scorecard_path.parent.mkdir(parents=True, exist_ok=True)
    scorecard_path.write_text(json.dumps(scorecard, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    result.status = "success" if score["failures"] == 0 else "error"
    if result.status == "error":
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="One or more workout attempts failed."))
    result.data["run_id"] = run_id
    result.data["workout"] = _safe_id(workout_id)
    result.data["attempts"] = attempt_results
    result.data["scorecard"] = scorecard
    result.data["scorecard_path"] = scorecard_path.relative_to(repo_root).as_posix() if scorecard_path.is_relative_to(repo_root) else str(scorecard_path)
    return result


def score_workout(repo_root: Path, workout_id: str) -> CallResult:
    """
    Load the saved scorecard for a given workout and return a CallResult describing success or failure.

    On success, `result.status` is "success" and `result.data` contains:
    - `scorecard`: the parsed scorecard dictionary.
    - `scorecard_path`: repository-relative path (when under `repo_root`) or absolute path.

    If no scorecard file is found, `result.status` is "error" and `result.errors` contains a validation error suggesting to run the workout. If the scorecard file cannot be read or parsed, `result.status` is "error", `result.errors` contains a validation error, and `result.data` includes `scorecard_path` and `parse_error` with the underlying exception text.

    Returns:
        CallResult: Result object populated as described above.
    """
    result = CallResult()
    result.data["validation_commands"] = [_workouts_validation_command("score", workout_id)]
    scorecard_path = _telemetry_dir(repo_root) / "scorecards" / f"{_safe_filename(workout_id)}.json"
    if not scorecard_path.is_file():
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"No scorecard found for workout {workout_id}.",
            fix_suggestion=f"Run `bin/ask workouts run {workout_id}` first.",
        ))
        return result
    try:
        scorecard = json.loads(scorecard_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"Scorecard for {workout_id} is corrupted or malformed.",
            fix_suggestion=f"Re-run `bin/ask workouts run {workout_id}` to regenerate {scorecard_path}.",
        ))
        result.data["scorecard_path"] = (
            scorecard_path.relative_to(repo_root).as_posix()
            if scorecard_path.is_relative_to(repo_root)
            else str(scorecard_path)
        )
        result.data["parse_error"] = str(exc)
        return result
    result.status = "success"
    result.data["scorecard"] = scorecard
    result.data["scorecard_path"] = scorecard_path.relative_to(repo_root).as_posix() if scorecard_path.is_relative_to(repo_root) else str(scorecard_path)
    return result


def promote_workout(repo_root: Path, workout_id: str, *, if_better: bool = False, dry_run: bool = False) -> CallResult:
    """
    Create and optionally record a promotion amendment for a workout based on its latest scorecard.

    Parameters:
        repo_root (Path): Repository root directory used to resolve paths and store telemetry.
        workout_id (str): Identifier of the workout to promote.
        if_better (bool): When True, require the new pass rate to be strictly greater than the previously accepted pass rate for promotion to proceed.
        dry_run (bool): When True, validate promotion and produce a proposal without recording an accepted amendment.

    Returns:
        CallResult: Result object containing:
            - On success: status "success" with `data` including `scorecard`, `rollback_validation`, and the `promotion` amendment (and `promotion.promotion_path` when recorded).
            - On rejection or validation failure: status "error" with `errors` describing the problem, `data` including `scorecard`, `rollback_validation`, and the `promotion` object (state "rejected" when applicable).

    Notes:
        - The function validates a rollback dry-run (ensuring a quoted git rollback command and that the target file exists) and checks context token budget and pass-rate improvement (when `if_better` is set).
        - If recording is allowed (not `dry_run`) and the promotion is accepted or rejected, an amendment JSON is written into the telemetry amendments directory and its path is included in the returned `promotion`.
    """
    score = score_workout(repo_root, workout_id)
    if score.status != "success":
        score.data["validation_commands"] = [
            _workouts_validation_command("promote", workout_id, if_better=if_better, dry_run=dry_run)
        ]
        return score

    result = CallResult()
    result.data["validation_commands"] = [
        _workouts_validation_command("promote", workout_id, if_better=if_better, dry_run=dry_run)
    ]
    scorecard = score.data["scorecard"]
    telemetry_dir = _telemetry_dir(repo_root)
    target_source = str(scorecard.get("target_source_path") or "")
    target_path = None
    if target_source:
        try:
            target_path = _resolve_repo_path(repo_root, target_source, label="target_source_path")
        except ValueError as exc:
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_VALIDATION",
                message=str(exc),
                fix_suggestion="Use a relative target_source_path inside the repository.",
            ))
            return result
    rollback_command = f"git checkout -- {shlex.quote(target_source)}" if target_source else ""
    rollback_validation = {
        "status": "pass" if target_path and target_path.is_file() and rollback_command else "fail",
        "rollback_command": rollback_command,
        "target_exists": bool(target_path and target_path.is_file()),
        "dry_run": True,
    }
    if rollback_validation["status"] != "pass":
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Rollback dry-run validation failed."))
        result.data["rollback_validation"] = rollback_validation
        return result

    target_hash = _sha256(target_path) if target_path and target_path.is_file() else ""
    latest_accepted = _latest_accepted_amendment(telemetry_dir, workout_id)
    score_before = (
        latest_accepted.get("score_after", {})
        if latest_accepted and isinstance(latest_accepted.get("score_after"), dict)
        else _empty_score()
    )
    score_after = scorecard.get("metrics", {})
    max_context_tokens = _int_or_default(
        scorecard.get("limits", {}).get("max_skill_context_tokens", DEFAULT_MAX_SKILL_CONTEXT_TOKENS)
        if isinstance(scorecard.get("limits"), dict)
        else DEFAULT_MAX_SKILL_CONTEXT_TOKENS,
        DEFAULT_MAX_SKILL_CONTEXT_TOKENS,
    )
    context_tokens = int(score_after.get("estimated_skill_context_tokens") or 0)
    pass_rate_before = float(score_before.get("pass_rate") or 0)
    pass_rate_after = float(score_after.get("pass_rate") or 0)
    budget_ok = context_tokens <= max_context_tokens
    improvement_ok = pass_rate_after > pass_rate_before or not if_better
    rejection_reasons: list[str] = []
    if if_better and not improvement_ok:
        rejection_reasons.append("pass_rate_not_improved")
    if not budget_ok:
        rejection_reasons.append("context_budget_exceeded")
    if not scorecard.get("promotion_eligible"):
        rejection_reasons.append("scorecard_not_promotion_eligible")

    promotion = {
        "schema_version": "skill-workout-amendment.v1",
        "timestamp": _timestamp(),
        "state": "proposed" if dry_run else "accepted",
        "workout": _safe_id(workout_id),
        "scorecard_run_id": scorecard.get("run_id"),
        "target_source_path": target_source,
        "previous_hash": target_hash,
        "new_hash": target_hash,
        "current_version": target_hash,
        "score_before": score_before,
        "score_after": score_after,
        "rationale": "Workout promotion proposal generated from latest scorecard evidence.",
        "evidence": [
            score.data.get("scorecard_path", ""),
            f"{TELEMETRY_DIRNAME}/workout-results.jsonl",
        ],
        "rollback_command": rollback_command,
        "rollback_validation": rollback_validation,
        "context_budget": {
            "estimated_skill_context_tokens": context_tokens,
            "max_skill_context_tokens": max_context_tokens,
            "status": "pass" if budget_ok else "fail",
        },
        "rejection_reasons": rejection_reasons,
        "dry_run": dry_run,
    }
    if rejection_reasons:
        promotion["state"] = "rejected"
        if not dry_run:
            target = _record_amendment(telemetry_dir, "rejected", workout_id, promotion)
            promotion["promotion_path"] = target.relative_to(repo_root).as_posix() if target.is_relative_to(repo_root) else str(target)
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message="Workout amendment proposal rejected.",
            fix_suggestion="Inspect promotion.rejection_reasons and rerun the workout after a smaller patch.",
        ))
        result.data["scorecard"] = scorecard
        result.data["rollback_validation"] = rollback_validation
        result.data["promotion"] = promotion
        return result

    if not dry_run:
        target = _record_amendment(telemetry_dir, "accepted", workout_id, promotion)
        promotion["promotion_path"] = target.relative_to(repo_root).as_posix() if target.is_relative_to(repo_root) else str(target)

    result.status = "success"
    result.data["scorecard"] = scorecard
    result.data["rollback_validation"] = rollback_validation
    result.data["promotion"] = promotion
    return result
