import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.repo import DoctorCatalogOptions, doctor_catalog
from ask.catalog_parity import HISTORY_PATH


class TestAskRepoDoctorCatalog(unittest.TestCase):
    def _write_readme(self, repo_root: Path, count: int) -> None:
        """
        Write a README.md at the repository root declaring the repository's Agent Skills count.
        
        Creates or overwrites README.md containing a Markdown heading "Agent Skills" and a line stating the repository has the specified number of skills. The file is written using UTF-8 encoding.
        
        Parameters:
        	repo_root (Path): Repository root directory where README.md will be created.
        	count (int): Number of skills to include in the README text.
        """
        (repo_root / "README.md").write_text(
            f"# Agent Skills\n\nA governed repository of **{count} skills**.\n",
            encoding="utf-8",
        )

    def _write_root_index(self, repo_root: Path, count: int, policy_identity: str = "0123456789abcdef") -> None:
        """
        Write or overwrite the repository root SKILL.md index with summary fields.

        Parameters:
            repo_root (Path): Root directory of the repository where SKILL.md will be written.
            count (int): Number to set for the `total_skills` field in the generated index.
            policy_identity (str): Policy identity stamp to write in the generated index.
        """
        (repo_root / "SKILL.md").write_text(
            (
                "# Agent Skills Index\n\n"
                "## Summary\n"
                f"- `total_skills`: {count}\n"
                f"- `policy_identity`: {policy_identity}\n"
            ),
            encoding="utf-8",
        )

    def test_doctor_catalog_reports_drift_when_counts_mismatch(self) -> None:
        """
        Verifies doctor_catalog reports catalog drift when README and root index skill counts mismatch.
        
        Sets up a temporary repository where README.md claims 10 skills, root SKILL.md reports 12, and discovery returns one skill entry; runs doctor_catalog(repo, strict=False) and asserts the result is an error with a `catalog_parity` report containing `schema_version: "catalog-parity.v1"`, `drift_detected: True`, and `decision_status: "blocked_catalog_parity"`.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            self._write_readme(repo, 10)
            self._write_root_index(repo, 12)
            (repo / "utilities" / "demo").mkdir(parents=True, exist_ok=True)
            (repo / "utilities" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo skill description that is long enough\n---\n",
                encoding="utf-8",
            )

            stub = SimpleNamespace(name="demo", source_dir=repo / "utilities" / "demo")
            with patch("ask.catalog_parity.discover_catalog_entries", return_value=[stub]), patch(
                "ask.catalog_parity.get_policy_identity",
                return_value="0123456789abcdef",
            ):
                result = doctor_catalog(repo, DoctorCatalogOptions(strict=False))
            self.assertEqual(result.status, "error")
            report = result.data["catalog_parity"]
            self.assertEqual(report["schema_version"], "catalog-parity.v1")
            self.assertTrue(report["drift_detected"])
            self.assertEqual(report["decision_status"], "blocked_catalog_parity")

    def test_doctor_catalog_strict_reports_missing_runtime_history(self) -> None:
        """
        Verify that strict catalog parity keeps a fresh repository usable without runtime history.
        
        Sets up a repository with matching README and root SKILL.md counts and a single skill entry, but no local history. The report must remain successful while exposing that history has not been collected.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            self._write_readme(repo, 1)
            self._write_root_index(repo, 1)
            (repo / "utilities" / "demo").mkdir(parents=True, exist_ok=True)
            (repo / "utilities" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo skill description that is long enough\n---\n",
                encoding="utf-8",
            )
            # Matching counts, but no history artifact => strict should block.
            stub = SimpleNamespace(name="demo", source_dir=repo / "utilities" / "demo")
            with patch("ask.catalog_parity.discover_catalog_entries", return_value=[stub]), patch(
                "ask.catalog_parity.get_policy_identity",
                return_value="0123456789abcdef",
            ):
                result = doctor_catalog(repo, DoctorCatalogOptions(strict=True))
            self.assertEqual(result.status, "success")
            report = result.data["catalog_parity"]
            self.assertFalse(report["drift_detected"])
            self.assertEqual(report["history_status"], "not_collected")

    def test_doctor_catalog_reads_runtime_history_in_strict_mode(self) -> None:
        """Strict catalog parity reads the ignored runtime history root."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            self._write_readme(repo, 1)
            self._write_root_index(repo, 1)
            (repo / "utilities" / "demo").mkdir(parents=True, exist_ok=True)
            (repo / "utilities" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo skill description that is long enough\n---\n",
                encoding="utf-8",
            )
            history_path = repo / HISTORY_PATH
            history_path.parent.mkdir(parents=True)
            rows = [
                {"unresolved_ambiguity_rate": 0.1, "no_candidate_rate": 0.1}
                for _ in range(8)
            ]
            history_path.write_text(
                "".join(f"{json.dumps(row)}\n" for row in rows),
                encoding="utf-8",
            )

            stub = SimpleNamespace(name="demo", source_dir=repo / "utilities" / "demo")
            with patch("ask.catalog_parity.discover_catalog_entries", return_value=[stub]), patch(
                "ask.catalog_parity.get_policy_identity",
                return_value="0123456789abcdef",
            ):
                result = doctor_catalog(repo, DoctorCatalogOptions(strict=True))

            self.assertEqual(result.status, "success")
            self.assertFalse(result.data["catalog_parity"]["drift_detected"])


if __name__ == "__main__":
    unittest.main()
