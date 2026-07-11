from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from Infrastructure.scripts.testing.test_validate_all_runtime_separation import FakeRepo


def test_changed_files_scope_miss_falls_back_to_required_baseline() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        proc = repo.run("--persistent", "--changed-files", "Infrastructure/scripts/bootstrap-ask.sh")

        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert (
            "Changed-files scope classification missed all known buckets; falling back to baseline required validation"
            in proc.stdout
        )
        rows = repo.check_results()
        required_rows = [row for row in rows if row["mode"] == "required"]
        assert required_rows, "expected required checks to be recorded"
        assert any(
            row["outcome"] == "pass" for row in required_rows
        ), "expected at least one required check to execute instead of every check being blocked"

        rows = repo.check_results()
        required_rows = [row for row in rows if row["mode"] == "required"]
        assert required_rows, "expected required checks to be recorded"
        assert any(
            row["outcome"] == "pass" for row in required_rows
        ), "expected at least one required check to execute instead of every check being blocked"


def test_changed_files_from_scope_miss_falls_back_to_required_baseline() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_files = repo.root / "changed-files.txt"
        changed_files.write_text("Infrastructure/scripts/bootstrap-ask.sh\n", encoding="utf-8")

        proc = repo.run("--persistent", "--changed-files-from", str(changed_files))

        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert (
            "Changed-files scope classification missed all known buckets; falling back to baseline required validation"
            in proc.stdout
        )


def test_lint_changed_skill_metadata_runs_no_command_handles() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "Skills/agent-ops/autofix/agents/openai.yaml"

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode == 0, proc.stdout + proc.stderr
        rows = repo.check_results()
        by_slug = {row["slug"]: row for row in rows}
        assert by_slug["no-command-handles"]["outcome"] == "pass"


def test_lint_changed_python_files_run_ask_cli_modularity() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "Infrastructure/scripts/lib/ask/commands/skills_impl.py"

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "Changed-files scope classification missed all known buckets" not in proc.stdout
        rows = repo.check_results()
        by_slug = {row["slug"]: row for row in rows}
        assert by_slug["ask-cli-modularity"]["outcome"] == "pass"

        args = repo.recorded_args_for("Infrastructure/scripts/verify_ask_cli_modularity.py")
        assert args is not None
        assert "--changed-files" in args
        assert changed_file in args


def test_lint_changed_python_files_run_program_design() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "Infrastructure/scripts/lib/ask/commands/skills_impl.py"

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode == 0, proc.stdout + proc.stderr
        rows = repo.check_results()
        by_slug = {row["slug"]: row for row in rows}
        assert by_slug["program-design"]["outcome"] == "pass"

        args = repo.recorded_args_for("Infrastructure/scripts/validation-and-linting/verify_program_design.py")
        assert args is not None
        assert "--changed-files" in args
        assert changed_file in args
