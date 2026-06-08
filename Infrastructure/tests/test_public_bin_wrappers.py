import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest import mock


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_wrapper(name: str, path: Path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    if spec is None:
        raise AssertionError(f"could not load spec for {path}")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class TestPublicBinWrappers(unittest.TestCase):
    def test_ask_uses_current_python_when_it_satisfies_repo_contract(self) -> None:
        wrapper = _load_wrapper("ask_wrapper_current_python", REPO_ROOT / "bin/ask")

        with (
            mock.patch.object(wrapper.sys, "version_info", (3, 12, 0)),
            mock.patch.object(wrapper.os, "execv", side_effect=RuntimeError("exec called")) as execv,
            self.assertRaisesRegex(RuntimeError, "exec called"),
        ):
            wrapper._exec_target(REPO_ROOT, REPO_ROOT / "Infrastructure/bin/ask", ["repo", "status"])

        execv.assert_called_once_with(
            sys.executable,
            [sys.executable, str(REPO_ROOT / "Infrastructure/bin/ask"), "repo", "status"],
        )

    def test_ask_trampolines_through_uv_when_ambient_python_is_too_old(self) -> None:
        wrapper = _load_wrapper("ask_wrapper_uv_trampoline", REPO_ROOT / "bin/ask")

        with (
            mock.patch.object(wrapper.sys, "version_info", (3, 9, 6)),
            mock.patch.object(wrapper, "_uv_executable", return_value="/opt/homebrew/bin/uv"),
            mock.patch.object(wrapper.os, "execv", side_effect=RuntimeError("exec called")) as execv,
            self.assertRaisesRegex(RuntimeError, "exec called"),
        ):
            wrapper._exec_target(REPO_ROOT, REPO_ROOT / "Infrastructure/bin/ask", ["sdk", "status"])

        execv.assert_called_once_with(
            "/opt/homebrew/bin/uv",
            [
                "/opt/homebrew/bin/uv",
                "run",
                "--project",
                str(REPO_ROOT / "Infrastructure"),
                "--python",
                "3.12",
                "python",
                str(REPO_ROOT / "Infrastructure/bin/ask"),
                "sdk",
                "status",
            ],
        )

    def test_skills_sdk_wrapper_preserves_sdk_facade_under_uv_trampoline(self) -> None:
        wrapper = _load_wrapper("skills_sdk_wrapper_uv_trampoline", REPO_ROOT / "bin/skills-sdk")

        with (
            mock.patch.object(wrapper.sys, "version_info", (3, 9, 6)),
            mock.patch.object(wrapper, "_uv_executable", return_value="/opt/homebrew/bin/uv"),
            mock.patch.object(wrapper.os, "execv", side_effect=RuntimeError("exec called")) as execv,
            self.assertRaisesRegex(RuntimeError, "exec called"),
        ):
            wrapper._exec_target(REPO_ROOT, REPO_ROOT / "Infrastructure/bin/ask", ["status"])

        execv.assert_called_once_with(
            "/opt/homebrew/bin/uv",
            [
                "/opt/homebrew/bin/uv",
                "run",
                "--project",
                str(REPO_ROOT / "Infrastructure"),
                "--python",
                "3.12",
                "python",
                str(REPO_ROOT / "Infrastructure/bin/ask"),
                "sdk",
                "status",
            ],
        )

    def test_wrapper_fails_actionably_when_old_python_has_no_uv(self) -> None:
        wrapper = _load_wrapper("ask_wrapper_missing_uv", REPO_ROOT / "bin/ask")

        with (
            mock.patch.object(wrapper.sys, "version_info", (3, 9, 6)),
            mock.patch.object(wrapper, "_uv_executable", return_value=None),
            self.assertRaises(SystemExit) as raised,
        ):
            wrapper._exec_target(REPO_ROOT, REPO_ROOT / "Infrastructure/bin/ask", ["repo", "status"])

        self.assertEqual(raised.exception.code, 127)

    def test_ask_ignores_non_executable_fallback_uv_candidates(self) -> None:
        wrapper = _load_wrapper("ask_wrapper_non_executable_uv", REPO_ROOT / "bin/ask")

        with (
            mock.patch.object(wrapper.shutil, "which", return_value=None),
            mock.patch.object(wrapper, "_is_executable_file", return_value=False) as executable_check,
        ):
            self.assertIsNone(wrapper._uv_executable())

        executable_check.assert_has_calls(
            [mock.call("/opt/homebrew/bin/uv"), mock.call("/usr/local/bin/uv")]
        )

    def test_skills_sdk_ignores_non_executable_fallback_uv_candidates(self) -> None:
        wrapper = _load_wrapper("skills_sdk_wrapper_non_executable_uv", REPO_ROOT / "bin/skills-sdk")

        with (
            mock.patch.object(wrapper.shutil, "which", return_value=None),
            mock.patch.object(wrapper, "_is_executable_file", return_value=False) as executable_check,
        ):
            self.assertIsNone(wrapper._uv_executable())

        executable_check.assert_has_calls(
            [mock.call("/opt/homebrew/bin/uv"), mock.call("/usr/local/bin/uv")]
        )


if __name__ == "__main__":
    unittest.main()
