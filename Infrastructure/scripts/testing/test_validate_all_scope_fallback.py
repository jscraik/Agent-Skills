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
