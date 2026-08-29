from __future__ import annotations

import subprocess
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


def test_persistent_validation_keeps_parity_manifest_in_run_directory() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))

        proc = repo.run("--persistent", "--changed-files", "Infrastructure/scripts/bootstrap-ask.sh")

        assert proc.returncode == 0, proc.stdout + proc.stderr
        args = repo.recorded_args_for("Infrastructure/scripts/verify_recursive_skill_graph_artifacts.py")
        assert args is not None
        manifest_index = args.index("--manifest") + 1
        manifest_path = args[manifest_index]
        assert manifest_path.startswith(".tmp/agent-skills-artifacts/validation/")
        assert manifest_path.endswith("/artifact-parity-manifest.json")
        assert manifest_path != ".harness/evidence/skill-graphs/pilot/artifact-parity-manifest.json"


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


def test_handoff_evidence_uses_skills_sdk_scope_without_baseline_fallback() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = ".harness/evidence/handoff/improve-agent-native/current/oss-local.json"

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "Changed-files scope classification missed all known buckets" not in proc.stdout
        rows = repo.check_results()
        by_slug = {row["slug"]: row for row in rows}
        assert by_slug["skills-sdk-typed-artifacts"]["outcome"] == "pass"


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


def test_staged_source_forwards_only_to_program_design() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        proc = repo.run(
            "--persistent",
            "--scope",
            "lint",
            "--staged-source",
            "--changed-files",
            "Infrastructure/scripts/lib/ask/commands/skills_impl.py",
        )

        assert proc.returncode == 0, proc.stdout + proc.stderr
        program_design_args = repo.recorded_args_for(
            "Infrastructure/scripts/validation-and-linting/verify_program_design.py"
        )
        assert program_design_args is not None
        assert "--staged-source" in program_design_args


def test_lint_changed_python_shebang_entrypoint_runs_program_design() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "Plugins/example/scripts/run"
        entrypoint = repo.root / changed_file
        entrypoint.parent.mkdir(parents=True, exist_ok=True)
        entrypoint.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode == 0, proc.stdout + proc.stderr
        rows = repo.check_results()
        by_slug = {row["slug"]: row for row in rows}
        assert by_slug["program-design"]["outcome"] == "pass"
        args = repo.recorded_args_for("Infrastructure/scripts/validation-and-linting/verify_program_design.py")
        assert args is not None
        assert "--changed-files" in args
        assert changed_file in args


def test_blob_sources_keep_large_python_shebang_matches() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "Plugins/example/scripts/run"
        entrypoint = repo.root / changed_file
        entrypoint.parent.mkdir(parents=True, exist_ok=True)
        entrypoint.write_bytes(b"#!/usr/bin/env python3\n" + b"x" * (8 * 1024 * 1024))
        subprocess.run(["git", "init", "-q"], cwd=repo.root, check=True)
        subprocess.run(["git", "add", changed_file], cwd=repo.root, check=True)
        subprocess.run(
            ["git", "-c", "user.name=Probe", "-c", "user.email=probe@example.com", "-c", "commit.gpgsign=false", "commit", "-qm", "probe"],
            cwd=repo.root,
            check=True,
        )
        entrypoint.write_text("not a Python entrypoint\n", encoding="utf-8")

        for source_mode in ("--staged-source", "--head-source"):
            proc = repo.run("--persistent", "--scope", "lint", source_mode, "--changed-files", changed_file)
            assert proc.returncode == 0, proc.stdout + proc.stderr
            assert repo.recorded_args_for(
                "Infrastructure/scripts/validation-and-linting/verify_program_design.py"
            ) is not None


def test_lint_changed_binary_file_emits_no_null_byte_warning() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "Skills/example/assets/font.woff2"
        binary = repo.root / changed_file
        binary.parent.mkdir(parents=True, exist_ok=True)
        binary.write_bytes(b"wOF2\x00binary-font-data")

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "ignored null byte in input" not in proc.stderr


def test_changed_non_regular_source_fails_closed() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "Plugins/example/scripts/run"
        (repo.root / changed_file).mkdir(parents=True)

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode != 0
        assert f"changed source is not a regular file: {changed_file}" in proc.stderr


def test_lint_changed_unscanned_python_wrapper_falls_back_to_required_baseline() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        changed_file = "bin/ask"
        entrypoint = repo.root / changed_file
        entrypoint.parent.mkdir(parents=True, exist_ok=True)
        entrypoint.write_text("#!/usr/bin/env python3\n", encoding="utf-8")

        proc = repo.run("--persistent", "--scope", "lint", "--changed-files", changed_file)

        assert proc.returncode == 0, proc.stdout + proc.stderr
        assert "Changed-files scope classification missed all known buckets" in proc.stdout


def test_head_source_probes_extensionless_shebang_from_head() -> None:
    with TemporaryDirectory() as tmpdir:
        repo = FakeRepo(Path(tmpdir))
        impl_text = (repo.root / "Infrastructure/scripts/validate_all_impl.sh").read_text(encoding="utf-8")
        assert 'git show "HEAD:$changed_file"' in impl_text
