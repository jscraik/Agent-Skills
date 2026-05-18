from __future__ import annotations
# pyright: reportMissingImports=false

import json
import os
import stat
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "testing"))

from ask.bootstrap import (  # noqa: E402
    classify_entrypoint,
    run_bootstrap_checks,
    run_status_command,
)
from validation_and_linting_import import load_docs_validator  # noqa: E402


def _write_executable(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def _make_minimal_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    (repo / "bin").mkdir(parents=True)
    (repo / ".git").mkdir()
    ask = repo / "bin" / "ask"
    _write_executable(
        ask,
        "#!/usr/bin/env python3\n"
        "import json\n"
        "import pathlib\n"
        "print(json.dumps({'status':'success','data':{'repo_root_resolved':str(pathlib.Path.cwd().resolve())}}))\n",
    )
    return repo


def test_non_executable_entrypoint_is_repaired_in_temp_root(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path)
    entrypoint = repo / "bin" / "ask"
    entrypoint.chmod(entrypoint.stat().st_mode & ~stat.S_IXUSR)

    result = classify_entrypoint(repo, repair=True)

    assert result["status"] == "repaired"
    assert result["path_type"] == "regular_file"
    assert result["safe_to_chmod"] is True
    assert os.access(entrypoint, os.X_OK)


def test_symlink_entrypoint_is_not_chmodded(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    target = tmp_path / "outside-ask"
    (repo / "bin").mkdir(parents=True)
    target.write_text("#!/usr/bin/env python3\n", encoding="utf-8")
    target.chmod(stat.S_IRUSR | stat.S_IWUSR)
    (repo / "bin" / "ask").symlink_to(target)

    result = classify_entrypoint(repo, repair=True)

    assert result["status"] == "fail"
    assert result["path_type"] == "symlink"
    assert result["safe_to_chmod"] is False
    assert not os.access(target, os.X_OK)


def test_pathless_shell_preserves_python_but_omits_ask(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path)
    env = {"PATH": str(Path(sys.executable).parent)}

    result = run_bootstrap_checks(repo, env=env, python_executable=sys.executable)

    assert result["checks"]["fallback_command"]["status"] == "pass"
    assert result["checks"]["fallback_command"]["command"][0] == sys.executable
    assert result["checks"]["fallback_command"]["canonical_command"][0] == "python3"
    assert result["checks"]["path_discovery"]["status"] == "warn"
    assert result["status"] == "warning"


def test_empty_env_does_not_fall_back_to_process_path(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path)

    result = run_bootstrap_checks(repo, env={}, python_executable=sys.executable)

    assert result["checks"]["fallback_command"]["status"] == "pass"
    assert result["checks"]["path_discovery"]["status"] == "warn"
    assert result["checks"]["path_discovery"]["resolved_path"] is None
    assert result["checks"]["shim_smoke"]["status"] == "skipped"


def test_wrong_global_shim_fails_even_with_forged_repo_root(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path)
    shim_dir = tmp_path / "shim"
    shim_dir.mkdir()
    _write_executable(
        shim_dir / "ask",
        "#!/usr/bin/env python3\n"
        "import json\n"
        f"print(json.dumps({{'status':'success','data':{{'repo_root_resolved':{str(repo.resolve())!r}}}}}))\n",
    )
    env = {"PATH": f"{shim_dir}{os.pathsep}{Path(sys.executable).parent}"}

    result = run_bootstrap_checks(repo, env=env, python_executable=sys.executable)

    assert result["checks"]["shim_smoke"]["status"] == "fail"
    assert result["checks"]["shim_smoke"]["repo_identity_status"] == "fail"


def test_unknown_fallback_failure_blocks_closure(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path)
    result = run_status_command(
        [sys.executable, "-c", "import sys; print('mystery'); sys.exit(7)"],
        repo,
        timeout_seconds=5,
    )

    assert result["status"] == "fail"
    assert result["defer_to"] == "unknown_unclassified"


def test_non_object_json_fallback_is_classified_as_failure(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path)
    result = run_status_command(
        [sys.executable, "-c", "print('[]')"],
        repo,
        timeout_seconds=5,
    )

    assert result["status"] == "fail"
    assert result["stdout_json_status"] is None
    assert result["repo_root_resolved"] is None


def test_hanging_command_records_timeout(tmp_path: Path) -> None:
    repo = _make_minimal_repo(tmp_path)
    result = run_status_command(
        [sys.executable, "-c", "import time; time.sleep(2)"],
        repo,
        timeout_seconds=1,
    )

    assert result["status"] == "fail"
    assert result["failure_reason"] == "timeout"
    assert result["defer_to"] == "unknown_unclassified"


def test_live_bootstrap_json_contract() -> None:
    process = subprocess.run(
        ["bash", "scripts/bootstrap-ask.sh", "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    payload = json.loads(process.stdout)

    assert process.returncode == 0
    assert payload["schema_version"] == "ask-bootstrap.v1"
    assert payload["checks"]["fallback_command"]["used_shell"] is False
    assert payload["checks"]["entrypoint_executable"]["path"] == "bin/ask"


def test_docs_validator_accepts_normative_docs() -> None:
    validator = load_docs_validator()

    assert validator.validate_docs(REPO_ROOT) == []
