import importlib.util
import sys
import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[2]
PROJECTION_INTEGRITY_PATH = (
    REPO_ROOT
    / "Infrastructure"
    / "scripts"
    / "lifecycle-and-sync"
    / "projection_integrity_impl.py"
)
spec = importlib.util.spec_from_file_location("projection_integrity_impl_test", PROJECTION_INTEGRITY_PATH)
assert spec and spec.loader
projection_integrity_impl = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = projection_integrity_impl
spec.loader.exec_module(projection_integrity_impl)

HEADER_TOKEN = projection_integrity_impl.HEADER_TOKEN
MirrorProjection = projection_integrity_impl.MirrorProjection
sync_mirror = projection_integrity_impl.sync_mirror
verify_mirror = projection_integrity_impl.verify_mirror
prune_nested_duplicates = projection_integrity_impl._prune_nested_duplicate_skill_identities


class ProjectionIntegrityPluginCacheTests(TestCase):
    def test_sync_mirror_preserves_python_sync_monkeypatch_seam(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-monkeypatch-sync-") as tmp:
            repo_root = Path(tmp) / "repo"
            (repo_root / "source").mkdir(parents=True)
            mirror = MirrorProjection(
                name="compatibility-sync",
                source_path="source",
                projection_path="projection",
                tags=("compatibility",),
            )
            with (
                patch.object(projection_integrity_impl.shutil, "which", return_value=None),
                patch.object(
                    projection_integrity_impl,
                    "_sync_mirror_python",
                    return_value=(17, 23),
                ) as patched_sync,
            ):
                result = sync_mirror(repo_root, mirror)

            patched_sync.assert_called_once()
            self.assertEqual(result["sync_engine"], "python")
            self.assertEqual(result["changed_files"], 17)
            self.assertEqual(result["deleted_files"], 23)

    def test_sync_mirror_preserves_duplicate_prune_monkeypatch_seam(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-monkeypatch-prune-") as tmp:
            repo_root = Path(tmp) / "repo"
            skill = repo_root / "plugin" / "skills" / "demo"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text("---\nname: demo\n---\n", encoding="utf-8")
            mirror = MirrorProjection(
                name="compatibility-prune",
                source_path="plugin",
                projection_path="projection",
                tags=("compatibility",),
                plugin_cache_package=True,
            )
            with patch.object(
                projection_integrity_impl,
                "_prune_nested_duplicate_skill_identities",
                return_value=(["patched-prune"], 7),
            ) as patched_prune:
                result = sync_mirror(repo_root, mirror)

            patched_prune.assert_called_once_with(repo_root / "projection" / "skills")
            self.assertEqual(result["deleted_files"], 7)
            self.assertIn("patched-prune", result["logs"])

    def test_plugin_cache_projection_uses_runtime_package_transform(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-plugin-cache-") as tmp:
            repo_root = Path(tmp) / "repo"
            plugin_root = repo_root / "Plugins" / "plugin-factory"
            canonical = plugin_root / "skills" / "plugin-builder"
            duplicate = plugin_root / "skills" / "code_quality_review" / "plugin-builder"
            canonical.mkdir(parents=True)
            duplicate.mkdir(parents=True)
            (plugin_root / ".codex-plugin").mkdir(parents=True)
            (plugin_root / ".codex-plugin" / "plugin.json").write_text(
                '{"name":"plugin-factory","skills":"./skills/"}',
                encoding="utf-8",
            )
            skill_text = "---\nname: plugin-builder\ndescription: Build plugins.\n---\n# Plugin Builder\n"
            (canonical / "SKILL.md").write_text(skill_text, encoding="utf-8")
            (duplicate / "SKILL.md").write_text(skill_text, encoding="utf-8")

            spec = MirrorProjection(
                name="cache-plugin-factory",
                source_path="Plugins/plugin-factory",
                projection_path=".agents/plugins-runtime/cache/agent-skills-local/plugin-factory",
                tags=("plugin-caches",),
                follow_symlinks=True,
                replace_before_sync=True,
                excluded_dir_names=("fixtures",),
                plugin_cache_package=True,
            )

            sync_result = sync_mirror(repo_root, spec)
            projection_root = repo_root / spec.projection_path

            self.assertEqual(sync_result["status"], "synced")
            self.assertTrue((projection_root / "skills" / "plugin-builder" / "SKILL.md").is_file())
            self.assertFalse((projection_root / "skills" / "code_quality_review" / "plugin-builder").exists())
            self.assertNotIn(
                HEADER_TOKEN,
                (projection_root / "skills" / "plugin-builder" / "SKILL.md").read_text(encoding="utf-8"),
            )
            self.assertEqual("pass", verify_mirror(repo_root, spec)["status"])

    def test_same_basename_distinct_identity_and_content_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-plugin-cache-distinct-") as tmp:
            repo_root = Path(tmp) / "repo"
            plugin_root = repo_root / "Plugins" / "plugin-factory"
            direct = plugin_root / "skills" / "router"
            nested = plugin_root / "skills" / "team" / "router"
            direct.mkdir(parents=True)
            nested.mkdir(parents=True)
            (plugin_root / ".codex-plugin").mkdir(parents=True)
            (plugin_root / ".codex-plugin" / "plugin.json").write_text('{"name":"plugin-factory","skills":"./skills/"}', encoding="utf-8")
            (direct / "SKILL.md").write_text("---\nname: direct-router\ndescription: Direct.\n---\n", encoding="utf-8")
            (nested / "SKILL.md").write_text("---\nname: team-router-distinct\ndescription: Team.\n---\n", encoding="utf-8")
            projection = ".agents/plugins-runtime/cache/agent-skills-local/plugin-factory"
            mirror = MirrorProjection(name="cache-plugin-factory", source_path="Plugins/plugin-factory", projection_path=projection, tags=("plugin-caches",), follow_symlinks=True, replace_before_sync=True, excluded_dir_names=("fixtures",), plugin_cache_package=True)

            sync_mirror(repo_root, mirror)

            self.assertTrue((repo_root / projection / "skills" / "router" / "SKILL.md").is_file())
            self.assertTrue((repo_root / projection / "skills" / "team" / "router" / "SKILL.md").is_file())
            self.assertEqual("pass", verify_mirror(repo_root, mirror)["status"])

    def test_same_identity_with_distinct_reference_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-plugin-reference-") as tmp:
            skills = Path(tmp) / "skills"
            direct = skills / "router"
            nested = skills / "team" / "router"
            for package in (direct, nested):
                (package / "references").mkdir(parents=True)
                (package / "SKILL.md").write_text("---\nname: router\ndescription: Route.\n---\n", encoding="utf-8")
            (direct / "references" / "contract.md").write_text("direct\n", encoding="utf-8")
            (nested / "references" / "contract.md").write_text("nested\n", encoding="utf-8")

            _, deleted = prune_nested_duplicates(skills)

            self.assertEqual(deleted, 0)
            self.assertTrue(nested.is_dir())

    def test_same_identity_with_distinct_symlink_target_is_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-plugin-symlink-") as tmp:
            skills = Path(tmp) / "skills"
            direct = skills / "router"
            nested = skills / "team" / "router"
            for package in (direct, nested):
                package.mkdir(parents=True)
                (package / "SKILL.md").write_text("---\nname: router\ndescription: Route.\n---\n", encoding="utf-8")
            (direct / "reference-link").symlink_to("references/direct.md")
            (nested / "reference-link").symlink_to("references/nested.md")

            _, deleted = prune_nested_duplicates(skills)

            self.assertEqual(deleted, 0)
            self.assertTrue((nested / "reference-link").is_symlink())

    def test_sync_blocks_unsafe_package_symlinks_without_projection(self) -> None:
        cases = ("outside-directory", "outside-file", "absolute", "parent-escape", "broken")
        for case in cases:
            with self.subTest(case=case), tempfile.TemporaryDirectory(prefix=f"projection-plugin-{case}-") as tmp:
                repo_root = Path(tmp) / "repo"
                plugin = repo_root / "Plugins" / "demo"
                package = plugin / "skills" / "router"
                outside = repo_root / "outside"
                package.mkdir(parents=True)
                outside.mkdir(parents=True)
                (plugin / ".codex-plugin").mkdir(parents=True)
                (plugin / ".codex-plugin" / "plugin.json").write_text('{"name":"demo","skills":"./skills/"}', encoding="utf-8")
                (package / "SKILL.md").write_text("---\nname: router\ndescription: Route.\n---\n", encoding="utf-8")
                outside_file = outside / "SECRET"
                outside_file.write_text("must-not-copy\n", encoding="utf-8")
                link = package / "unsafe-link"
                if case == "outside-directory":
                    link.symlink_to(outside, target_is_directory=True)
                elif case == "outside-file":
                    link.symlink_to(outside_file)
                elif case == "absolute":
                    link.symlink_to(outside_file.resolve())
                elif case == "parent-escape":
                    link.symlink_to("../../../../outside/SECRET")
                else:
                    link.symlink_to("references/missing.md")
                projection = ".agents/plugins-runtime/cache/demo"
                mirror = MirrorProjection(name="cache-demo", source_path="Plugins/demo", projection_path=projection, tags=("plugin-caches",), follow_symlinks=True, replace_before_sync=True, plugin_cache_package=True)

                result = sync_mirror(repo_root, mirror)

                self.assertEqual(result["status"], "error")
                self.assertEqual(result["reason"], "unsafe_plugin_package_symlink")
                self.assertEqual(result["changed_files"], 0)
                self.assertFalse((repo_root / projection).exists())
                self.assertTrue(result["unsafe_symlinks"])

    def test_sync_preserves_valid_contained_symlink(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-plugin-contained-link-") as tmp:
            repo_root = Path(tmp) / "repo"
            plugin = repo_root / "Plugins" / "demo"
            package = plugin / "skills" / "router"
            references = package / "references"
            references.mkdir(parents=True)
            (plugin / ".codex-plugin").mkdir(parents=True)
            (plugin / ".codex-plugin" / "plugin.json").write_text('{"name":"demo","skills":"./skills/"}', encoding="utf-8")
            (package / "SKILL.md").write_text("---\nname: router\ndescription: Route.\n---\n", encoding="utf-8")
            (references / "contract.md").write_text("contained\n", encoding="utf-8")
            (package / "contract-link").symlink_to("references/contract.md")
            projection = ".agents/plugins-runtime/cache/demo"
            mirror = MirrorProjection(name="cache-demo", source_path="Plugins/demo", projection_path=projection, tags=("plugin-caches",), follow_symlinks=True, replace_before_sync=True, plugin_cache_package=True)

            result = sync_mirror(repo_root, mirror)
            projected = repo_root / projection / "skills" / "router" / "contract-link"

            self.assertEqual(result["status"], "synced")
            self.assertTrue(projected.is_symlink())
            self.assertEqual(projected.readlink().as_posix(), "references/contract.md")

    def test_same_bytes_with_distinct_executable_bits_are_preserved(self) -> None:
        with tempfile.TemporaryDirectory(prefix="projection-plugin-mode-") as tmp:
            skills = Path(tmp) / "skills"
            direct = skills / "runner"
            nested = skills / "team" / "runner"
            for package in (direct, nested):
                package.mkdir(parents=True)
                (package / "SKILL.md").write_text("---\nname: runner\ndescription: Run.\n---\n", encoding="utf-8")
                (package / "run.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            (direct / "run.sh").chmod(0o644)
            (nested / "run.sh").chmod(0o755)

            _, deleted = prune_nested_duplicates(skills)

            self.assertEqual(deleted, 0)
            self.assertTrue(nested.is_dir())
