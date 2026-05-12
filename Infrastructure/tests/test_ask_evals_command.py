from __future__ import annotations

import sys
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]
ASK_LIB_DIR = REPO_ROOT / "Infrastructure" / "scripts" / "lib"

if str(ASK_LIB_DIR) not in sys.path:
    sys.path.insert(0, str(ASK_LIB_DIR))

from ask.commands import evals  # noqa: E402


def test_smoke_evals_use_codex_spark_without_reasoning_level(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="smoke")

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" in cmd
    assert cmd[cmd.index("--model") + 1] == "gpt-5.3-codex-spark"
    assert "--reasoning" not in cmd
    assert "--reasoning-effort" not in cmd
    assert "--profile" not in cmd
    assert "--codex-arg" in cmd
    assert cmd[cmd.index("--codex-arg") + 1] == "--ignore-user-config"


def test_release_evals_do_not_force_smoke_model(tmp_path: Path) -> None:
    completed = mock.Mock(returncode=0, stdout="{}", stderr="")

    with mock.patch.object(evals.subprocess, "run", return_value=completed) as run:
        result = evals.run_evals(tmp_path, "Plugins/example-skill", mode="release")

    assert result.status == "success"
    cmd = run.call_args.args[0]
    assert "--model" not in cmd
