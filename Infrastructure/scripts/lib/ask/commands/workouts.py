import hashlib
import json
import os
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


def add_workouts_parser(subparsers: Any, global_parser: Any) -> None:
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
    result.errors.append(ErrorObject(
        code="ERR_VALIDATION",
        message=f"{action_msg} for topic 'workouts'",
        fix_suggestion="Valid actions: list, run, score, promote",
    ))
    return result


def _timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_id(value: str) -> str:
    return value.strip().strip("/").replace("\\", "/")


def _safe_filename(value: str) -> str:
    return _safe_id(value).replace("/", "__")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    digest.update(path.read_bytes())
    return digest.hexdigest()


def _timeout_text(value: bytes | str | None) -> str:
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _timed_out_process(exc: subprocess.TimeoutExpired) -> subprocess.CompletedProcess[str]:
    stderr = _timeout_text(exc.stderr)
    timeout_note = f"Command timed out after {exc.timeout} seconds"
    if stderr:
        stderr = f"{stderr}\n{timeout_note}"
    else:
        stderr = timeout_note
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
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text) or {}
    except Exception as exc:
        loaded = {}
        current_key: Optional[str] = None
        for raw_line in text.splitlines():
            if not raw_line.strip() or raw_line.lstrip().startswith("#"):
                continue
            indent = len(raw_line) - len(raw_line.lstrip(" "))
            line = raw_line.strip()
            if indent == 0 and ":" in line:
                key, value = line.split(":", 1)
                current_key = key.strip()
                value = value.strip().strip("\"'")
                loaded[current_key] = value if value else []
            elif current_key and line.startswith("- "):
                if not isinstance(loaded.get(current_key), list):
                    loaded[current_key] = []
                loaded[current_key].append(line[2:].strip().strip("\"'"))
        if not loaded:
            raise ValueError(f"Unable to parse {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def _workout_dir(repo_root: Path, workout_id: str) -> Path:
    safe = _safe_id(workout_id)
    if not safe or safe.startswith("../") or "/../" in safe or safe == "..":
        raise ValueError("Workout id must be a relative .workouts path")
    return repo_root / WORKOUTS_DIRNAME / safe


def _load_workout(repo_root: Path, workout_id: str) -> tuple[Path, dict[str, Any]]:
    directory = _workout_dir(repo_root, workout_id)
    config_path = directory / "workout.yaml"
    if not config_path.is_file():
        raise FileNotFoundError(f"Workout not found: {workout_id}")
    config = _load_structured_file(config_path)
    config.setdefault("workout_path", _safe_id(workout_id))
    config.setdefault("id", _safe_id(workout_id))
    return directory, config


def _telemetry_dir(repo_root: Path) -> Path:
    override = os.environ.get("SKILL_TELEMETRY_DIR", "").strip()
    return Path(override) if override else repo_root / TELEMETRY_DIRNAME


def _append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, sort_keys=True) + "\n")


def _estimate_context_tokens(repo_root: Path, source_path: str) -> int:
    if not source_path:
        return 0
    target = repo_root / source_path
    if not target.is_file():
        return 0
    words = len([word for word in target.read_text(encoding="utf-8", errors="ignore").split() if word.strip()])
    return (words * 4 + 2) // 3


def _score_attempts(attempts: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(attempts)
    successes = sum(1 for attempt in attempts if attempt.get("outcome") == "success")
    failures = total - successes
    wall_clock = sum(float(attempt.get("wall_clock_seconds") or 0) for attempt in attempts)
    return {
        "attempts": total,
        "successes": successes,
        "failures": failures,
        "pass_rate": round(successes / total, 4) if total else 0,
        "flake_rate": 1 if successes and failures else 0,
        "wall_clock_seconds": round(wall_clock, 4),
    }


def list_workouts(repo_root: Path) -> CallResult:
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
    return result


def run_workout(repo_root: Path, workout_id: str, *, attempts: int = 1) -> CallResult:
    result = CallResult()
    try:
        directory, config = _load_workout(repo_root, workout_id)
    except (FileNotFoundError, ValueError) as exc:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message=str(exc)))
        return result

    bounded_attempts = max(1, min(int(attempts), int(config.get("max_attempts", 5))))
    seed_path = directory / str(config.get("seed", "seed.sh"))
    verify_path = directory / str(config.get("verify", "verify.py"))
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
    target_source = str(config.get("target_source_path") or "")
    context_tokens = _estimate_context_tokens(repo_root, target_source)
    attempt_results: list[dict[str, Any]] = []

    for attempt_no in range(1, bounded_attempts + 1):
        verifier_hash_before = _sha256(verify_path)
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
        verifier_hash_after = _sha256(verify_path)
        outcome = "success" if seed.returncode == 0 and verify.returncode == 0 and verifier_hash_before == verifier_hash_after else "failure"
        failure_type: Optional[str] = None
        if verifier_hash_before != verifier_hash_after:
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
            "estimated_skill_context_tokens": context_tokens,
        },
        "promotion_eligible": score["pass_rate"] > 0 and context_tokens <= int(config.get("max_skill_context_tokens", 1500)),
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
    result = CallResult()
    scorecard_path = _telemetry_dir(repo_root) / "scorecards" / f"{_safe_filename(workout_id)}.json"
    if not scorecard_path.is_file():
        result.status = "error"
        result.errors.append(ErrorObject(
            code="ERR_VALIDATION",
            message=f"No scorecard found for workout {workout_id}.",
            fix_suggestion=f"Run `bin/ask workouts run {workout_id}` first.",
        ))
        return result
    result.status = "success"
    result.data["scorecard"] = json.loads(scorecard_path.read_text(encoding="utf-8"))
    result.data["scorecard_path"] = scorecard_path.relative_to(repo_root).as_posix() if scorecard_path.is_relative_to(repo_root) else str(scorecard_path)
    return result


def promote_workout(repo_root: Path, workout_id: str, *, if_better: bool = False, dry_run: bool = False) -> CallResult:
    score = score_workout(repo_root, workout_id)
    if score.status != "success":
        return score

    result = CallResult()
    scorecard = score.data["scorecard"]
    import shlex
    
    target_source = str(scorecard.get("target_source_path") or "")
    target_path = repo_root / target_source if target_source else None
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
    if if_better and not scorecard.get("promotion_eligible"):
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Scorecard is not promotion eligible."))
        result.data["scorecard"] = scorecard
        result.data["rollback_validation"] = rollback_validation
        return result

    promotion = {
        "schema_version": "skill-workout-promotion.v1",
        "timestamp": _timestamp(),
        "workout": _safe_id(workout_id),
        "scorecard_run_id": scorecard.get("run_id"),
        "target_source_path": target_source,
        "score_after": scorecard.get("metrics", {}),
        "rollback_command": rollback_command,
        "dry_run": dry_run,
    }
    if not dry_run:
        target = _telemetry_dir(repo_root) / "amendments" / "accepted" / f"{_safe_filename(workout_id)}-{int(time.time())}.json"
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(promotion, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        promotion["promotion_path"] = target.relative_to(repo_root).as_posix() if target.is_relative_to(repo_root) else str(target)

    result.status = "success"
    result.data["scorecard"] = scorecard
    result.data["rollback_validation"] = rollback_validation
    result.data["promotion"] = promotion
    return result
