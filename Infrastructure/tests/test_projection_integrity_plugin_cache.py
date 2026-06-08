import importlib.util
import sys
import tempfile
from pathlib import Path
from unittest import TestCase


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


class ProjectionIntegrityPluginCacheTests(TestCase):
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
            (canonical / "SKILL.md").write_text("# Plugin Builder\n", encoding="utf-8")
            (duplicate / "SKILL.md").write_text("# Duplicate Plugin Builder\n", encoding="utf-8")

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
