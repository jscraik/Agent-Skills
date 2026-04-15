import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

import bootstrap_doc_qa


class BootstrapDocQaSymlinkTests(unittest.TestCase):
    def test_validate_repo_write_target_allows_repo_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_root = Path(tmpdir)
            target = repo_root / "brand" / "README.md"
            # Should not raise
            bootstrap_doc_qa.validate_repo_write_target(target, repo_root)

    def test_validate_repo_write_target_rejects_symlink_escape(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo_root = root / "repo"
            outside = root / "outside"
            repo_root.mkdir()
            outside.mkdir()
            (repo_root / ".vale").symlink_to(outside)

            target = repo_root / ".vale" / "styles" / "Docs" / "HeadingPunctuation.yml"
            with self.assertRaises(ValueError):
                bootstrap_doc_qa.validate_repo_write_target(target, repo_root)

    def test_validate_repo_write_target_rejects_direct_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            repo_root = root / "repo"
            repo_root.mkdir()
            target = repo_root / "README.md"
            target.write_text("original", encoding="utf-8")
            link = repo_root / "README-link.md"
            link.symlink_to(target)

            with self.assertRaises(ValueError):
                bootstrap_doc_qa.validate_repo_write_target(link, repo_root)


if __name__ == "__main__":
    unittest.main()
