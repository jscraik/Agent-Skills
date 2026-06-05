from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
from pathlib import Path
from typing import Any


BOOTSTRAP_SCHEMA_VERSION = "ask-bootstrap.v1"
DEFAULT_TIMEOUT_SECONDS = 10
MAX_EXCERPT_CHARS = 1200


def default_repo_root() -> Path:
    return Path(__file__).resolve().parents[4]


def _excerpt(value: str | None, *, limit: int = MAX_EXCERPT_CHARS) -> str:
    text = value or ""
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _is_inside_repo(path: Path, repo_root: Path) -> bool:
    try:
        path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    return True


def _prepend_path_entry(path_value: str | None, entry: Path) -> str:
    entry_text = str(entry)
    existing = path_value or ""
    parts = [part for part in existing.split(os.pathsep) if part]
    if entry_text in parts:
        parts.remove(entry_text)
    return os.pathsep.join([entry_text, *parts])


def _default_runtime_env(repo_root: Path) -> dict[str, str]:
    runtime_env = os.environ.copy()
    runtime_env["PATH"] = _prepend_path_entry(
        runtime_env.get("PATH"),
        repo_root / "bin",
    )
    return runtime_env


def _path_type(path: Path) -> str:
    if path.is_symlink():
        return "symlink"
    if not path.exists():
        return "missing"
    if path.is_file():
        return "regular_file"
    return "other"


def classify_entrypoint(
    repo_root: Path,
    *,
    repair: bool = True,
) -> dict[str, Any]:
    entrypoint = repo_root / "bin" / "ask"
    path_type = _path_type(entrypoint)
    mode_before = None
    mode_after = None
    safe_to_chmod = (
        path_type == "regular_file"
        and not entrypoint.is_symlink()
        and _is_inside_repo(entrypoint, repo_root)
    )
    remediation = "none"

    if path_type == "regular_file":
        mode_before = oct(stat.S_IMODE(entrypoint.stat().st_mode))
        executable = os.access(entrypoint, os.X_OK)
        if executable:
            status = "pass"
            mode_after = mode_before
        elif safe_to_chmod and repair:
            entrypoint.chmod(entrypoint.stat().st_mode | stat.S_IXUSR)
            mode_after = oct(stat.S_IMODE(entrypoint.stat().st_mode))
            status = "repaired" if os.access(entrypoint, os.X_OK) else "fail"
            remediation = "chmod_user_execute"
        else:
            status = "fail"
            remediation = "manual"
            mode_after = mode_before
    else:
        status = "fail"
        remediation = "manual"

    return {
        "status": status,
        "path": "bin/ask",
        "path_type": path_type,
        "safe_to_chmod": safe_to_chmod,
        "mode_before": mode_before,
        "mode_after": mode_after,
        "remediation": remediation,
    }


def _parse_status_json(stdout: str) -> tuple[str | None, str | None]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        return None, None
    if not isinstance(payload, dict):
        return None, None
    status = payload.get("status")
    repo_root = payload.get("data", {}).get("repo_root_resolved")
    return status if isinstance(status, str) else None, repo_root if isinstance(repo_root, str) else None


def _classify_fallback_failure(
    *,
    stdout: str,
    stderr: str,
    timeout: bool = False,
) -> str:
    if timeout:
        return "unknown_unclassified"
    combined = f"{stdout}\n{stderr}"
    dependency_markers = (
        "ModuleNotFoundError",
        "No module named",
        "ImportError",
        "python3: command not found",
        "No such file or directory: 'python3'",
    )
    optional_import_markers = (
        "optional import",
        "optional module",
        "lazy-load",
        "lazy loading",
        "eager optional",
    )
    if any(marker in combined for marker in dependency_markers):
        return "JSC-168"
    if any(marker in combined for marker in optional_import_markers):
        return "JSC-169"
    return "unknown_unclassified"


def run_status_command(
    command: list[str],
    repo_root: Path,
    *,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    env: dict[str, str] | None = None,
) -> dict[str, Any]:
    try:
        process = subprocess.run(
            command,
            cwd=str(repo_root),
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            env=env,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        return {
            "status": "fail",
            "command": command,
            "exit_code": None,
            "used_shell": False,
            "timeout_seconds": timeout_seconds,
            "stdout_json_status": None,
            "repo_root_resolved": None,
            "raw_stdout_excerpt": _excerpt(stdout),
            "raw_stderr_excerpt": _excerpt(stderr),
            "defer_to": _classify_fallback_failure(stdout=stdout, stderr=stderr, timeout=True),
            "failure_reason": "timeout",
        }
    except OSError as exc:
        stderr = str(exc)
        return {
            "status": "fail",
            "command": command,
            "exit_code": None,
            "used_shell": False,
            "timeout_seconds": timeout_seconds,
            "stdout_json_status": None,
            "repo_root_resolved": None,
            "raw_stdout_excerpt": "",
            "raw_stderr_excerpt": _excerpt(stderr),
            "defer_to": _classify_fallback_failure(stdout="", stderr=stderr),
            "failure_reason": type(exc).__name__,
        }

    json_status, observed_repo_root = _parse_status_json(process.stdout)
    passed = process.returncode == 0 and json_status == "success"
    return {
        "status": "pass" if passed else "fail",
        "command": command,
        "exit_code": process.returncode,
        "used_shell": False,
        "timeout_seconds": timeout_seconds,
        "stdout_json_status": json_status,
        "repo_root_resolved": observed_repo_root,
        "raw_stdout_excerpt": _excerpt(process.stdout),
        "raw_stderr_excerpt": _excerpt(process.stderr),
        "defer_to": None if passed else _classify_fallback_failure(stdout=process.stdout, stderr=process.stderr),
    }


def resolve_ask_on_path(env: dict[str, str] | None = None) -> dict[str, Any]:
    if env is None:
        path_value = os.environ.get("PATH")
    elif "PATH" in env:
        path_value = env.get("PATH")
    else:
        # Honor isolated call-sites that intentionally omit PATH.
        path_value = ""
    resolved = shutil.which("ask", path=path_value)
    return {
        "status": "pass" if resolved else "warn",
        "command": "ask",
        "resolution_method": "shutil.which",
        "resolved_path": str(Path(resolved).resolve()) if resolved else None,
    }


def _path_matches_repo_entrypoint(resolved_path: str | None, repo_root: Path) -> bool:
    if not resolved_path:
        return False
    expected = repo_root / "bin" / "ask"
    try:
        return Path(resolved_path).resolve() == expected.resolve()
    except OSError:
        return False


def run_bootstrap_checks(
    repo_root: Path | None = None,
    *,
    repair: bool = True,
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS,
    env: dict[str, str] | None = None,
    python_executable: str = "python3",
) -> dict[str, Any]:
    resolved_repo_root = (repo_root or default_repo_root()).resolve()
    runtime_env = env if env is not None else _default_runtime_env(resolved_repo_root)

    entrypoint = classify_entrypoint(resolved_repo_root, repair=repair)
    fallback = run_status_command(
        [python_executable, "bin/ask", "repo", "status", "--json"],
        resolved_repo_root,
        timeout_seconds=timeout_seconds,
        env=runtime_env,
    )
    fallback["canonical_command"] = ["python3", "bin/ask", "repo", "status", "--json"]

    path_discovery = resolve_ask_on_path(runtime_env)
    shim = {
        "status": "skipped",
        "command": ["ask", "repo", "status", "--json"],
        "exit_code": None,
        "used_shell": False,
        "timeout_seconds": None,
        "repo_identity_status": "skipped",
        "observed_repo_root": None,
    }
    resolved_path = path_discovery.get("resolved_path")
    if resolved_path:
        shim_result = run_status_command(
            ["ask", "repo", "status", "--json"],
            resolved_repo_root,
            timeout_seconds=timeout_seconds,
            env=runtime_env,
        )
        command_provenance_matches = _path_matches_repo_entrypoint(
            resolved_path if isinstance(resolved_path, str) else None,
            resolved_repo_root,
        )
        observed_repo_root = shim_result.get("repo_root_resolved")
        repo_identity_matches = observed_repo_root == str(resolved_repo_root)
        shim = {
            "status": "pass" if shim_result["status"] == "pass" and command_provenance_matches and repo_identity_matches else "fail",
            "command": ["ask", "repo", "status", "--json"],
            "exit_code": shim_result.get("exit_code"),
            "used_shell": False,
            "timeout_seconds": timeout_seconds,
            "repo_identity_status": "pass" if command_provenance_matches and repo_identity_matches else "fail",
            "observed_repo_root": observed_repo_root,
            "raw_stdout_excerpt": shim_result.get("raw_stdout_excerpt", ""),
            "raw_stderr_excerpt": shim_result.get("raw_stderr_excerpt", ""),
        }

    manual_remediation = []
    applied_remediation = []
    if entrypoint["remediation"] == "chmod_user_execute":
        applied_remediation.append("chmod_bin_ask")
    if entrypoint["status"] == "fail":
        manual_remediation.append("inspect_bin_ask")
    if fallback["status"] == "fail":
        manual_remediation.append("use_python_fallback")
    if path_discovery["status"] == "warn":
        manual_remediation.append("add_repo_bin_to_path")
    elif shim["status"] == "fail":
        manual_remediation.append("fix_ask_path_shim_identity")

    status = "success"
    if entrypoint["status"] == "fail" or fallback["status"] == "fail":
        status = "error"
    elif path_discovery["status"] == "warn" or shim["status"] in {"fail", "skipped"}:
        status = "warning"

    return {
        "schema_version": BOOTSTRAP_SCHEMA_VERSION,
        "status": status,
        "repo_root": str(resolved_repo_root),
        "checks": {
            "entrypoint_executable": entrypoint,
            "fallback_command": fallback,
            "path_discovery": path_discovery,
            "shim_smoke": shim,
        },
        "remediation": {
            "applied": applied_remediation,
            "manual": manual_remediation,
        },
    }


def main(argv: list[str] | None = None) -> int:
    args = argv if argv is not None else sys.argv[1:]
    json_mode = "--json" in args
    no_repair = "--no-repair" in args
    proof = run_bootstrap_checks(repair=not no_repair)
    if json_mode:
        print(json.dumps(proof, indent=2))
    else:
        print(f"Ask bootstrap: {proof['status']}")
        print(f"Repo root: {proof['repo_root']}")
        print(f"Entrypoint: {proof['checks']['entrypoint_executable']['status']}")
        print(f"Fallback: {proof['checks']['fallback_command']['status']}")
        print(f"PATH discovery: {proof['checks']['path_discovery']['status']}")
    return 0 if proof["status"] in {"success", "warning"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
