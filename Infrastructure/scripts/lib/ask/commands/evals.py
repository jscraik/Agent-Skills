import os
import ast
import json
import subprocess
import shutil
import sys
import tempfile
import hashlib
from pathlib import Path
from ask.envelope import CallResult, ErrorObject


SKILL_BUILDER_SCRIPTS = "Plugins/skill-factory/skills/code_quality_review/skill-builder/scripts"
SMOKE_CASE_TIMEOUT_SECONDS = 600
SMOKE_EVAL_TIMEOUT_SECONDS = 10800
RELEASE_EVAL_TIMEOUT_SECONDS = 21600
SMOKE_EVAL_MODEL = "gpt-5.3-codex-spark"


def _as_text(value, encoding="utf-8") -> str:
    """Convert subprocess output to text, handling bytes/None safely.

    Returns:
        - "" for None
        - Decoded string for bytes (with errors="replace")
        - String as-is for str values
    """
    if value is None:
        return ""
    if isinstance(value, bytes):
        return value.decode(encoding, errors="replace")
    return str(value)

def _tessl_policy() -> dict:
    """Return the repo's Tessl safety contract for eval runs."""
    return {
        "native_tessl_only": True,
        "no_npx": True,
        "no_publish": True,
        "no_registry_upload": True,
        "temp_staged_project_input_only": True,
        "network_permission_required_by_repo": False,
        "project_save_may_use_tessl_service": False,
        "project_save_default": "automatic",
    }


def _copy_if_present(source_root: Path, relative_path: str, target_root: Path) -> list[str]:
    source = source_root / relative_path
    if not source.exists():
        return []
    target = target_root / relative_path
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return [relative_path]


def _parse_tessl_eval_cases(evals_path: Path) -> list[dict[str, str]]:
    if not evals_path.exists():
        return []

    cases: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for raw_line in evals_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if line.startswith("- id:"):
            if current and current.get("id") and current.get("prompt"):
                cases.append(current)
            current = {"id": line.split(":", 1)[1].strip().strip("'\"")}
            continue
        if current is None or not line.startswith("prompt:"):
            continue

        prompt_value = line.split(":", 1)[1].strip()
        try:
            parsed_prompt = ast.literal_eval(prompt_value)
        except (SyntaxError, ValueError):
            parsed_prompt = prompt_value.strip("'\"")
        current["prompt"] = str(parsed_prompt)

    if current and current.get("id") and current.get("prompt"):
        cases.append(current)
    return cases


def _write_tessl_scenarios_from_evals(source_root: Path, staged_root: Path) -> list[str]:
    copied: list[str] = []
    for case in _parse_tessl_eval_cases(source_root / "references" / "evals.yaml"):
        case_id = case["id"].replace("/", "-")
        task_path = staged_root / "scenarios" / case_id / "task.md"
        task_path.parent.mkdir(parents=True, exist_ok=True)
        task_path.write_text(case["prompt"].rstrip() + "\n", encoding="utf-8")
        copied.append(str(task_path.relative_to(staged_root)))
    return copied


def _write_tessl_project_marker(source_root: Path, staged_root: Path) -> list[str]:
    marker_path = staged_root / "tessl.json"
    if marker_path.exists():
        return ["tessl.json"]
    marker_path.write_text(
        json.dumps({"name": source_root.name}, indent=2) + "\n",
        encoding="utf-8",
    )
    return ["tessl.json"]


def _stable_tessl_stage_parent(path: str) -> Path:
    safe_name = path.replace("/", "__").replace(" ", "_")
    digest = hashlib.sha256(path.encode("utf-8")).hexdigest()[:12]
    return Path(tempfile.gettempdir()) / "ask-tessl-evals" / f"{safe_name}-{digest}"


def _stage_tessl_eval_source(repo_root: Path, path: str, temp_root: Path | None = None) -> tuple[Path, list[str]]:
    source_root = (repo_root / path).resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(f"Tessl eval source is not a directory: {path}")

    staged_root = (temp_root / source_root.name) if temp_root else _stable_tessl_stage_parent(path)
    staged_root.mkdir(parents=True, exist_ok=True)
    preserved_marker = staged_root / "tessl.json"
    for child in staged_root.iterdir():
        if child == preserved_marker:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    copied: list[str] = []
    for relative_path in (
        "SKILL.md",
        "references/evals.yaml",
        "references/contract.yaml",
        "references/task-profile.json",
    ):
        copied.extend(_copy_if_present(source_root, relative_path, staged_root))
    copied.extend(_write_tessl_scenarios_from_evals(source_root, staged_root))
    copied.extend(_write_tessl_project_marker(source_root, staged_root))

    if not copied:
        raise FileNotFoundError(f"No Tessl eval staging files found under: {path}")
    return staged_root, copied


def _tessl_project_save_approved(allow_project_save: bool) -> bool:
    env_value = os.environ.get("ASK_TESSL_PROJECT_SAVE_APPROVED", "").strip().lower()
    return allow_project_save or env_value in {"1", "true", "yes", "approved"}


def _run_tessl_eval(repo_root: Path, path: str, *, allow_project_save: bool = True) -> dict:
    """Run the local Tessl eval lane without any registry publish/upload command."""
    tessl_path = shutil.which("tessl")
    command_display = "tessl eval run --json <staged-temp-source>"
    if not tessl_path:
        return {
            "status": "blocked",
            "command": command_display,
            "blocker": "Installed native tessl CLI was not found on PATH.",
            "policy": _tessl_policy(),
        }

    try:
        staged_source, copied_files = _stage_tessl_eval_source(repo_root, path)
        command_display = f"tessl eval run --json {staged_source}"
        if not _tessl_project_save_approved(allow_project_save):
            return {
                "status": "blocked",
                "command": command_display,
                "source_path": path,
                "staged_source": str(staged_source),
                "staged_files": copied_files,
                "raw_output": "",
                "raw_error": "",
                "blocker": (
                    "Tessl eval runs use the local CLI against a temp-staged project input. "
                    "The compatibility approval gate is disabled for this invocation."
                ),
                "approval": {
                    "required": True,
                    "rerun_with": "--allow-tessl-project-save",
                    "env": "ASK_TESSL_PROJECT_SAVE_APPROVED=1",
                },
                "policy": _tessl_policy(),
            }
        cmd = [tessl_path, "eval", "run", "--json", str(staged_source)]
        try:
            process = subprocess.run(cmd, cwd=str(staged_source), capture_output=True, text=True, timeout=600)
        except subprocess.TimeoutExpired as e:
            return {
                "status": "blocked",
                "command": command_display,
                "source_path": path,
                "staged_source": str(staged_source),
                "staged_files": copied_files,
                "raw_output": _as_text(e.stdout),
                "raw_error": _as_text(e.stderr),
                "blocker": "Tessl eval timed out after 600 seconds.",
                "policy": _tessl_policy(),
            }
        except OSError as e:
            return {
                "status": "blocked",
                "command": command_display,
                "source_path": path,
                "staged_source": str(staged_source),
                "staged_files": copied_files,
                "raw_output": "",
                "raw_error": str(e),
                "blocker": f"Failed to run Tessl eval: {e}",
                "policy": _tessl_policy(),
            }

        raw_output = process.stdout
        raw_error = process.stderr
        auth_text = f"{raw_output}\n{raw_error}".lower()
        if process.returncode != 0 and "authenticate with tessl" in auth_text:
            status = "blocked"
            blocker = "Tessl CLI is installed locally, but authentication is required before evals can run."
        elif process.returncode != 0 and "no existing project safely matches this directory" in auth_text:
            status = "blocked"
            blocker = (
                "Tessl CLI is authenticated, but no Tessl project/workspace is linked for the "
                "temp-staged eval directory. Create or link a Tessl project/workspace before rerunning."
            )
        elif process.returncode != 0 and "no tessl project found" in auth_text:
            status = "blocked"
            blocker = "Tessl CLI could not find a tessl.json project marker in the staged eval directory."
        else:
            status = "pass" if process.returncode == 0 else "fail"
            blocker = None

        return {
            "status": status,
            "command": command_display,
            "source_path": path,
            "staged_source": str(staged_source),
            "staged_files": copied_files,
            "exit_code": process.returncode,
            "raw_output": raw_output,
            "raw_error": raw_error,
            "blocker": blocker,
            "policy": _tessl_policy(),
        }
    except OSError as e:
        return {
            "status": "blocked",
            "command": command_display,
            "source_path": path,
            "raw_output": "",
            "raw_error": str(e),
            "blocker": f"Failed to stage Tessl eval source: {e}",
            "policy": _tessl_policy(),
        }


def run_evals(
    repo_root: Path,
    path: str,
    mode: str = "smoke",
    skip_tessl: bool = False,
    allow_tessl_project_save: bool = True,
    model: str | None = None,
    cases: list[str] | None = None,
) -> CallResult:
    """Runs evaluation cases for a skill."""
    result = CallResult()

    cmd = [
        sys.executable, f"{SKILL_BUILDER_SCRIPTS}/run_skill_evals.py",
        path,
        "--eval-mode", mode
    ]
    timeout = RELEASE_EVAL_TIMEOUT_SECONDS if mode == "release" else 300
    if mode == "smoke":
        smoke_model = model or SMOKE_EVAL_MODEL
        cmd.extend([
            "--model",
            smoke_model,
            "--timeout-sec",
            str(SMOKE_CASE_TIMEOUT_SECONDS),
            "--codex-arg",
            "--ignore-user-config",
        ])
        timeout = SMOKE_EVAL_TIMEOUT_SECONDS
    for raw_case in cases or []:
        for case in raw_case.split(","):
            case = case.strip()
            if case:
                cmd.extend(["--case", case])

    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=timeout)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr

        if process.returncode == 0:
            result.status = "success"
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Evaluation run failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = _as_text(e.stdout)
        result.data["raw_error"] = _as_text(e.stderr)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Evaluation timed out after {timeout} seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run evaluation: {e}"))

    if skip_tessl:
        result.data["tessl_eval"] = {
            "status": "skipped",
            "reason": "--skip-tessl",
            "policy": _tessl_policy(),
        }
    else:
        tessl_eval = _run_tessl_eval(repo_root, path, allow_project_save=allow_tessl_project_save)
        result.data["tessl_eval"] = tessl_eval
        if tessl_eval.get("status") != "pass":
            result.status = "error"
            result.errors.append(ErrorObject(
                code="ERR_RUNTIME" if tessl_eval.get("status") == "blocked" else "ERR_VALIDATION",
                message=f"Tessl eval {tessl_eval.get('status')}: {tessl_eval.get('blocker') or 'see data.tessl_eval'}",
            ))

    return result

def benchmark_portfolio(repo_root: Path) -> CallResult:
    """Runs the full repository skill benchmark suite."""
    result = CallResult()

    cmd = [sys.executable, f"{SKILL_BUILDER_SCRIPTS}/benchmark_skill_portfolio.py"]
    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr
        if process.returncode == 0:
            result.status = "success"
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Benchmark suite failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = _as_text(e.stdout)
        result.data["raw_error"] = _as_text(e.stderr)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Benchmark timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run benchmark: {e}"))

    return result

def dashboard_report(repo_root: Path) -> CallResult:
    """Generates the skill evaluation dashboard."""
    result = CallResult()

    cmd = [sys.executable, f"{SKILL_BUILDER_SCRIPTS}/build_skill_eval_dashboard.py"]
    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr
        if process.returncode == 0:
            result.status = "success"
            result.data["message"] = "Dashboard generated successfully."
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = _as_text(e.stdout)
        result.data["raw_error"] = _as_text(e.stderr)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run dashboard generation: {e}"))

    return result
