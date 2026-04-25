import hashlib
import json
import os
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


def _declared_metrics(config: dict[str, Any]) -> set[str]:
    constraints = config.get("constraints") or {}
    if not isinstance(constraints, dict):
        raise ValueError("Workout constraints must be a mapping")
    declared = constraints.get("metrics") or config.get("metrics") or []
    if not isinstance(declared, list) or not all(isinstance(item, str) and item.strip() for item in declared):
        raise ValueError("Workout constraints.metrics must be a list of non-empty metric names")
    return {item.strip() for item in declared}


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
    yaml_error: BaseException | None = None
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text)
    except ImportError as exc:
        loaded = {}
        yaml_error = exc
    except yaml.YAMLError as exc:
        loaded = {}
        yaml_error = exc

    if yaml_error is not None:
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
            raise ValueError(f"Unable to parse {path}: {yaml_error or 'empty mapping'}") from yaml_error
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def _resolve_inside(base_dir: Path, relative_path: str, *, label: str) -> Path:
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


def _empty_score() -> dict[str, Any]:
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
    target = telemetry_dir / "amendments" / state / f"{_safe_filename(workout_id)}-{int(time.time())}.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(proposal, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def _score_attempts(attempts: list[dict[str, Any]]) -> dict[str, Any]:
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
                "Workout constraints.metrics must exactly match "
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
        "promotion_eligible": score["pass_rate"] > 0 and context_tokens <= max_skill_context_tokens,
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
    max_context_tokens = int(
        scorecard.get("limits", {}).get("max_skill_context_tokens", DEFAULT_MAX_SKILL_CONTEXT_TOKENS)
        if isinstance(scorecard.get("limits"), dict)
        else DEFAULT_MAX_SKILL_CONTEXT_TOKENS
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
    if if_better and not scorecard.get("promotion_eligible"):
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
