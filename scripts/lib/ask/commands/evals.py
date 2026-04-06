import os
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
    
    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    
    result.data["raw_output"] = process.stdout
    result.data["raw_error"] = process.stderr
    
    if process.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_VALIDATION", message="Evaluation run failed."))
        
    return result

def benchmark_portfolio(repo_root: Path) -> CallResult:
    """Runs the full repository skill benchmark suite."""
    result = CallResult()
    
    cmd = ["python3", "utilities/skill-builder/scripts/benchmark_skill_portfolio.py"]
    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    
    result.data["raw_output"] = process.stdout
    if process.returncode == 0:
        result.status = "success"
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Benchmark suite failed."))
        
    return result

def dashboard_report(repo_root: Path) -> CallResult:
    """Generates the skill evaluation dashboard."""
    result = CallResult()
    
    cmd = ["python3", "utilities/skill-builder/scripts/build_skill_eval_dashboard.py"]
    process = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
    
    if process.returncode == 0:
        result.status = "success"
        result.data["message"] = "Dashboard generated successfully."
    else:
        result.status = "error"
        result.errors.append(ErrorObject(code="ERR_RUNTIME", message="Dashboard generation failed."))
        
    return result
