import subprocess
from pathlib import Path
from ask.envelope import CallResult, ErrorObject

def run_evals(repo_root: Path, path: str, mode: str = "smoke") -> CallResult:
    """Runs evaluation cases for a skill."""
    result = CallResult()

    cmd = [
        "python3", "utilities/skill-builder/scripts/run_skill_evals.py",
        path,
        "--eval-mode", mode
    ]

    try:
        process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True, timeout=300)
        result.data["raw_output"] = process.stdout
        result.data["raw_error"] = process.stderr

        if process.returncode == 0:
            result.status = "success"
        else:
            result.status = "error"
            result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Evaluation run failed."))
    except subprocess.TimeoutExpired as e:
        result.status = "error"
        result.data["raw_output"] = e.stdout if e.stdout else ""
        result.data["raw_error"] = e.stderr if e.stderr else ""
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Evaluation timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run evaluation: {e}"))

    return result

def benchmark_portfolio(repo_root: Path) -> CallResult:
    """Runs the full repository skill benchmark suite."""
    result = CallResult()

    cmd = ["python3", "utilities/skill-builder/scripts/benchmark_skill_portfolio.py"]
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
        result.data["raw_output"] = e.stdout if e.stdout else ""
        result.data["raw_error"] = e.stderr if e.stderr else ""
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

    cmd = ["python3", "utilities/skill-builder/scripts/build_skill_eval_dashboard.py"]
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
        result.data["raw_output"] = e.stdout if e.stdout else ""
        result.data["raw_error"] = e.stderr if e.stderr else ""
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation timed out after 300 seconds."))
    except OSError as e:
        result.status = "error"
        result.data["raw_output"] = ""
        result.data["raw_error"] = str(e)
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message=f"Failed to run dashboard generation: {e}"))

    return result
