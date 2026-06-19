from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR_PATH = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "validation-and-linting"
    / "validate_skills_sdk_typed_artifacts.py"
)


def _load_validator() -> ModuleType:
    spec = importlib.util.spec_from_file_location("validate_skills_sdk_typed_artifacts", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load Skills SDK typed artifact validator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TestSkillsSdkRootPackageBoundary(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = _load_validator()

    def _scratch_repo(self) -> TemporaryDirectory[str]:
        tempdir = TemporaryDirectory()
        repo_root = Path(tempdir.name)
        (repo_root / "Infrastructure").mkdir()
        (repo_root / "Infrastructure" / "pyproject.toml").write_text("[project]\nname='test'\n", encoding="utf-8")
        (repo_root / "Infrastructure" / "uv.lock").write_text("version = 1\n", encoding="utf-8")
        return tempdir

    def test_infrastructure_manifest_and_lockfile_are_allowed(self) -> None:
        with self._scratch_repo() as tmpdir:
            check = self.validator.validate_root_package_boundary(Path(tmpdir))

        self.assertEqual(check.status, "pass")
        self.assertEqual(check.issues, ())

    def test_forbidden_root_package_manifests_fail_in_scratch_repo(self) -> None:
        for filename in self.validator.FORBIDDEN_ROOT_PACKAGE_FILES:
            with self.subTest(filename=filename):
                with self._scratch_repo() as tmpdir:
                    repo_root = Path(tmpdir)
                    (repo_root / filename).write_text("{}", encoding="utf-8")
                    check = self.validator.validate_root_package_boundary(repo_root)

                self.assertEqual(check.status, "fail")
                self.assertEqual(check.issues[0].path, filename)
                self.assertEqual(check.issues[0].code, "skills_sdk_root_package_manager_forbidden")

    def test_empty_root_package_lock_stub_fails_in_scratch_repo(self) -> None:
        with self._scratch_repo() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "package-lock.json").write_text(
                """{
  "name": "agent-skills",
  "lockfileVersion": 3,
  "requires": true,
  "packages": {}
}
""",
                encoding="utf-8",
            )
            check = self.validator.validate_root_package_boundary(repo_root)

        self.assertEqual(check.status, "fail")
        self.assertEqual(check.issues[0].path, "package-lock.json")
        self.assertEqual(check.issues[0].code, "skills_sdk_root_package_manager_forbidden")

    def test_missing_infrastructure_lockfile_fails_without_touching_live_repo(self) -> None:
        with self._scratch_repo() as tmpdir:
            repo_root = Path(tmpdir)
            (repo_root / "Infrastructure" / "uv.lock").unlink()
            check = self.validator.validate_root_package_boundary(repo_root)

        self.assertEqual(check.status, "fail")
        self.assertEqual(check.issues[0].path, "Infrastructure/uv.lock")


if __name__ == "__main__":
    unittest.main()
