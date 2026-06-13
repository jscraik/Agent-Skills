import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.command_metadata import COMMAND_EXAMPLES, VALID_ACTIONS  # noqa: E402
from ask.skills_sdk.knowledge_ingest import build_knowledge_ingest  # noqa: E402

ASK_PYTHON = shutil.which("python3.14") or shutil.which("python3.12") or sys.executable


def _command_env() -> dict[str, str]:
    env = os.environ.copy()
    temp_base = Path(tempfile.gettempdir()) / "agent-skills-test"
    env.setdefault("XDG_CACHE_HOME", str(temp_base / "xdg-cache"))
    env.setdefault("XDG_STATE_HOME", str(temp_base / "xdg-state"))
    env.setdefault("MISE_CACHE_DIR", str(temp_base / "mise-cache"))
    env.setdefault("UV_CACHE_DIR", str(temp_base / "uv-cache"))
    env.setdefault("MISE_TRUSTED_CONFIG_PATHS", str(REPO_ROOT / ".mise.toml"))
    return env


def _write_skill(repo_root: Path) -> Path:
    skill_dir = repo_root / "Skills" / "agent-ops" / "improve-agent-native"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: improve-agent-native
description: "Audit repo harness readiness."
metadata:
  skill-type: runbook
---

# Improve Agent Native

## When to use

Use for audits.

## Procedure

1. Inspect repo evidence.

## References

- `references/source-context.yaml`
""",
        encoding="utf-8",
    )
    (skill_dir / "references" / "source-context.yaml").write_text(
        yaml.safe_dump(
            {
                "schema_version": 1,
                "skill": "improve-agent-native",
                "references": [
                    {
                        "path": "references/source-context.yaml",
                        "kind": "package_companion",
                    }
                ],
            },
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    return skill_dir


def _write_extraction(root: Path, *, leak: bool = False) -> Path:
    extraction = root / "knowledge-OS" / "exports" / "extractions" / "improve-agent-native"
    refs = extraction / "references"
    capsules = refs / "knowledge-capsules"
    capsules.mkdir(parents=True)
    skill_payload = {
        "skill_id": "improve-agent-native",
        "declared_name": "improve-agent-native",
        "writable_root": "Skills/agent-ops/improve-agent-native",
    }
    plan = {
        "schema_version": "knowledge-os.extraction-plan.v1",
        "skill": skill_payload,
        "upstream_packs": [
            {
                "pack_id": "pack.harness-engineering",
                "snapshot_digest": "sha256:" + "a" * 64,
            }
        ],
    }
    demand = {
        "schema_version": "knowledge-os.knowledge-demand.v1",
        "skill": skill_payload,
        "runtime_dependency_policy": {
            "requires_knowledge_os_at_runtime": False,
            "raw_sources_included": False,
            "local_absolute_paths_required": False,
        },
    }
    manifest = {
        "schema_version": "knowledge-os.knowledge-capsule-manifest.v1",
        "skill": skill_payload,
        "selected_facets": ["pack.harness-engineering:evidence_boundary"],
    }
    (extraction / "extraction-plan.yaml").write_text(yaml.safe_dump(plan, sort_keys=False), encoding="utf-8")
    (extraction / "knowledge-demand.yaml").write_text(yaml.safe_dump(demand, sort_keys=False), encoding="utf-8")
    (refs / "knowledge-demand.yaml").write_text(yaml.safe_dump(demand, sort_keys=False), encoding="utf-8")
    (refs / "knowledge-capsule.manifest.yaml").write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    capsule_text = "# Harness Evidence Boundary\n\nUse evidence before readiness claims.\n"
    if leak:
        capsule_text += "/Users/jamiecraik/dev/knowledge-OS/private-source.md\n"
    (capsules / "harness-evidence-boundary.md").write_text(capsule_text, encoding="utf-8")
    return extraction


class TestSkillsSdkKnowledgeIngest(unittest.TestCase):
    def test_preview_reports_vendored_reference_plan_without_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            extraction = _write_extraction(Path(tmp))

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=False,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "preview")
            self.assertEqual(payload["owner_boundary"]["runtime_dependency"], "vendored_skill_references_only")
            self.assertEqual(len(payload["copied_files"]), 3)
            self.assertFalse((skill_dir / "references" / "knowledge-capsules").exists())

    def test_apply_vendors_references_and_updates_routing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            extraction = _write_extraction(Path(tmp))

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native/SKILL.md",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            self.assertTrue((skill_dir / "references" / "knowledge-demand.yaml").is_file())
            self.assertTrue((skill_dir / "references" / "knowledge-capsules" / "harness-evidence-boundary.md").is_file())
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Do not load all capsules by default", skill_text)
            source_context = yaml.safe_load((skill_dir / "references" / "source-context.yaml").read_text(encoding="utf-8"))
            paths = {entry["path"] for entry in source_context["references"]}
            self.assertIn("references/knowledge-capsule.manifest.yaml", paths)
            self.assertIn("references/knowledge-capsules/", paths)

    def test_local_absolute_path_leak_blocks_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            _write_skill(root)
            extraction = _write_extraction(Path(tmp), leak=True)

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "blocked")
            self.assertIn(
                "references:local_absolute_path_leak:references/knowledge-capsules/harness-evidence-boundary.md",
                payload["findings"],
            )

    def test_cli_requires_preview_or_apply(self) -> None:
        process = subprocess.run(
            [
                ASK_PYTHON,
                "Infrastructure/bin/ask",
                "sdk",
                "knowledge",
                "ingest",
                "--extraction",
                "/tmp/extraction",
                "--skill",
                "Skills/agent-ops/improve-agent-native",
                "--json",
                "--robot",
            ],
            cwd=REPO_ROOT,
            env=_command_env(),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

        self.assertEqual(process.returncode, 2)
        payload = json.loads(process.stdout)
        self.assertEqual(payload["status"], "error")
        self.assertEqual(payload["errors"][0]["code"], "ERR_VALIDATION")
        self.assertIn("exactly one of --preview or --apply", payload["errors"][0]["message"])

    def test_command_metadata_registers_knowledge_route(self) -> None:
        self.assertIn("knowledge", VALID_ACTIONS["sdk"])
        self.assertTrue(
            any(command.startswith("ask sdk knowledge ingest ") for command in COMMAND_EXAMPLES[("sdk", "knowledge")])
        )


if __name__ == "__main__":
    unittest.main()
