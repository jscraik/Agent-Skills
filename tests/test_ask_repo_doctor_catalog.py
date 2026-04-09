import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "scripts" / "lib"))
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from ask.commands.repo import doctor_catalog


class TestAskRepoDoctorCatalog(unittest.TestCase):
    def _write_readme(self, repo_root: Path, count: int) -> None:
        (repo_root / "README.md").write_text(
            f"# Agent Skills\n\nA governed repository of **{count} skills**.\n",
            encoding="utf-8",
        )

    def _write_root_index(self, repo_root: Path, count: int) -> None:
        (repo_root / "SKILL.md").write_text(
            f"# Agent Skills Index\n\n## Summary\n- `total_skills`: {count}\n",
            encoding="utf-8",
        )

    def test_doctor_catalog_reports_drift_when_counts_mismatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir)
            self._write_readme(repo, 10)
            self._write_root_index(repo, 12)
            (repo / "utilities" / "demo").mkdir(parents=True, exist_ok=True)
            (repo / "utilities" / "demo" / "SKILL.md").write_text(
                "---\nname: demo\ndescription: demo skill description that is long enough\n---\n",
                encoding="utf-8",
            )

            with patch("ask.catalog_parity.discover_skill_entries", return_value=[object()]):
                result = doctor_catalog(repo, strict=False)
            self.assertEqual(result.status, "error")
            report = result.data["catalog_parity"]
            self.assertEqual(report["schema_version"], "catalog-parity.v1")
            self.assertTrue(report["drift_detected"])
            self.assertEqual(report["decision_status"], "blocked_catalog_parity")

    def test_doctor_catalog_strict_blocks_on_insufficient_history(self) -> None:
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
            with patch("ask.catalog_parity.discover_skill_entries", return_value=[object()]):
                result = doctor_catalog(repo, strict=True)
            self.assertEqual(result.status, "error")
            report = result.data["catalog_parity"]
            self.assertEqual(report["drift_class"], "trend_insufficient_history")
            self.assertEqual(report["blocking_reason"], "insufficient_history")


if __name__ == "__main__":
    unittest.main()
