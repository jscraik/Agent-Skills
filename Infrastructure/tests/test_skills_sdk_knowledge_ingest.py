import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lib"))

from ask.command_metadata import COMMAND_EXAMPLES, VALID_ACTIONS  # noqa: E402
from ask.commands import evals as eval_commands  # noqa: E402
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


def _write_skill(repo_root: Path, *, workflow_heading: str = "Procedure", source_context: bool = True) -> Path:
    skill_dir = repo_root / "Skills" / "agent-ops" / "improve-agent-native"
    (skill_dir / "references").mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: improve-agent-native
description: "Audit repo harness readiness."
metadata:
  skill-type: runbook
---

# Improve Agent Native

## When to use

Use for audits.

## {workflow_heading}

1. Inspect repo evidence.

## References

- `references/source-context.yaml`
""",
        encoding="utf-8",
    )
    if source_context:
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


def _write_extraction(
    root: Path,
    *,
    leak: bool = False,
    vendored_demand_override: Optional[dict] = None,
    include_evals: bool = False,
    eval_files: str = "both",
) -> Path:
    extraction = root / "knowledge-OS" / "exports" / "extractions" / "improve-agent-native"
    refs = extraction / "references"
    capsules = refs / "knowledge-capsules"
    capsules.mkdir(parents=True)
    skill_payload = _extraction_skill_payload()
    plan = _extraction_plan(skill_payload)
    demand = _extraction_demand(skill_payload)
    manifest = _extraction_manifest(skill_payload)
    if include_evals:
        manifest["selected_asset_ids"] = ["eval.harness.local-pass-ci-unknown"]
    _write_yaml(extraction / "extraction-plan.yaml", plan)
    _write_yaml(extraction / "knowledge-demand.yaml", demand)
    vendored_demand = vendored_demand_override or demand
    _write_yaml(refs / "knowledge-demand.yaml", vendored_demand)
    _write_yaml(refs / "knowledge-capsule.manifest.yaml", manifest)
    (refs / "knowledge-capsule-routing.md").write_text(
        "# Knowledge Capsule Routing\n\n"
        "- `references/knowledge-capsules/harness-evidence-boundary.md` - Evidence boundary\n",
        encoding="utf-8",
    )
    capsule_text = "# Harness Evidence Boundary\n\nUse evidence before readiness claims.\n"
    if leak:
        capsule_text += "/Users/jamiecraik/dev/knowledge-OS/private-source.md\n"
    (capsules / "harness-evidence-boundary.md").write_text(capsule_text, encoding="utf-8")
    if include_evals and eval_files in {"both", "scenarios"}:
        (refs / "eval-scenarios.json").write_text(
            json.dumps(
                [
                    {
                        "id": "eval.harness.local-pass-ci-unknown",
                        "type": "eval-scenario",
                        "title": "Local Pass Does Not Prove CI",
                        "payload": {
                            "given": "Local validation passed but remote CI is unchecked.",
                            "should": "Report local pass and CI unknown as separate claims.",
                            "expected_failure": "Claiming merge readiness from local checks alone.",
                            "reproduce_with": "references/evals/eval.harness.local-pass-ci-unknown.md",
                        },
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    if include_evals and eval_files in {"both", "fixtures"}:
        evals = refs / "evals"
        evals.mkdir()
        (evals / "eval.harness.local-pass-ci-unknown.md").write_text(
            "# Local Pass Does Not Prove CI\n\nKeep CI and local validation as separate proof lanes.\n",
            encoding="utf-8",
        )
    return extraction


def _extraction_skill_payload() -> dict[str, str]:
    return {
        "skill_id": "improve-agent-native",
        "declared_name": "improve-agent-native",
        "writable_root": "Skills/agent-ops/improve-agent-native",
    }


def _extraction_plan(skill_payload: dict[str, str]) -> dict[str, object]:
    return {
        "schema_version": "knowledge-os.extraction-plan.v1",
        "skill": skill_payload,
        "upstream_packs": [{"pack_id": "pack.harness-engineering", "snapshot_digest": "sha256:" + "a" * 64}],
    }


def _extraction_demand(skill_payload: dict[str, str]) -> dict[str, object]:
    return {
        "schema_version": "knowledge-os.knowledge-demand.v1",
        "skill": skill_payload,
        "runtime_dependency_policy": {
            "requires_knowledge_os_at_runtime": False,
            "raw_sources_included": False,
            "local_absolute_paths_required": False,
        },
    }


def _extraction_manifest(skill_payload: dict[str, str]) -> dict[str, object]:
    return {
        "schema_version": "knowledge-os.knowledge-capsule-manifest.v1",
        "skill": skill_payload,
        "selected_facets": ["pack.harness-engineering:evidence_boundary"],
        "upstream_pack": {"pack_id": "pack.harness-engineering", "snapshot_digest": "sha256:" + "a" * 64},
        "capsules": [
            {
                "facet_id": "evidence_boundary",
                "target_path": "references/knowledge-capsules/harness-evidence-boundary.md",
            }
        ],
    }


def _write_yaml(path: Path, payload: dict[str, object]) -> None:
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def _write_skill_gate(repo_root: Path) -> Path:
    gate = repo_root / "Plugins" / "skill-factory" / "scripts" / "skill-builder" / "skill_gate.py"
    gate.parent.mkdir(parents=True)
    gate.write_text(
        "import sys\nprint('gate ok')\nraise SystemExit(0)\n",
        encoding="utf-8",
    )
    return gate


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
            copied_sources = {item["source"] for item in payload["copied_files"]}
            self.assertIn("references/knowledge-capsule-routing.md", copied_sources)
            self.assertEqual(len(payload["copied_files"]), 4)
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
            capsule_routing = skill_dir / "references" / "knowledge-capsule-routing.md"
            self.assertTrue(capsule_routing.is_file())
            capsule_routing_text = capsule_routing.read_text(encoding="utf-8")
            self.assertIn("references/knowledge-capsules/harness-evidence-boundary.md", capsule_routing_text)
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("Do not load all capsules by default", skill_text)
            self.assertIn("references/knowledge-capsule-routing.md", skill_text)
            self.assertNotIn("references/eval-scenarios.json", skill_text)
            self.assertNotIn("references/evals/", skill_text)
            source_context = yaml.safe_load((skill_dir / "references" / "source-context.yaml").read_text(encoding="utf-8"))
            paths = {entry["path"] for entry in source_context["references"]}
            self.assertIn("references/knowledge-capsule.manifest.yaml", paths)
            self.assertIn("references/knowledge-capsules/", paths)
            self.assertNotIn("references/eval-scenarios.json", paths)
            self.assertNotIn("references/evals/", paths)
            self.assertNotIn(
                "KnowledgeOS-selected eval scenarios must be wired through references/evals.yaml before Tessl proof",
                source_context.get("allowed_claims", []),
            )

    def test_apply_preserves_explicit_zero_capsule_asset_count(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            extraction = _write_extraction(Path(tmp))
            manifest_path = extraction / "references" / "knowledge-capsule.manifest.yaml"
            manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
            manifest["selected_asset_ids"] = ["asset.one", "asset.two"]
            manifest["capsules"][0]["asset_ids"] = []
            _write_yaml(manifest_path, manifest)

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native/SKILL.md",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            capsule_routing = skill_dir / "references" / "knowledge-capsule-routing.md"
            capsule_routing_text = capsule_routing.read_text(encoding="utf-8")
            self.assertIn("selected_asset_count: 0", capsule_routing_text)

    def test_apply_vendors_knowledge_eval_scenarios_and_fixtures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            extraction = _write_extraction(Path(tmp), include_evals=True)

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native/SKILL.md",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            copied = {item["source"] for item in payload["copied_files"]}
            self.assertIn("references/eval-scenarios.json", copied)
            self.assertIn("references/evals/eval.harness.local-pass-ci-unknown.md", copied)
            scenarios = json.loads((skill_dir / "references" / "eval-scenarios.json").read_text(encoding="utf-8"))
            self.assertEqual(scenarios[0]["id"], "eval.harness.local-pass-ci-unknown")
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("references/eval-scenarios.json", skill_text)
            self.assertIn("references/evals/", skill_text)
            source_context = yaml.safe_load((skill_dir / "references" / "source-context.yaml").read_text(encoding="utf-8"))
            paths = {entry["path"] for entry in source_context["references"]}
            self.assertIn("references/eval-scenarios.json", paths)
            self.assertIn("references/evals/", paths)
            self.assertIn(
                "KnowledgeOS-selected eval scenarios must be wired through references/evals.yaml before Tessl proof",
                source_context.get("allowed_claims", []),
            )

    def test_apply_routes_eval_scenarios_only_when_scenario_json_is_copied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            extraction = _write_extraction(Path(tmp), include_evals=True, eval_files="scenarios")

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native/SKILL.md",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("references/eval-scenarios.json", skill_text)
            self.assertNotIn("references/evals/", skill_text)
            source_context = yaml.safe_load((skill_dir / "references" / "source-context.yaml").read_text(encoding="utf-8"))
            paths = {entry["path"] for entry in source_context["references"]}
            self.assertIn("references/eval-scenarios.json", paths)
            self.assertNotIn("references/evals/", paths)
            self.assertNotIn(
                "KnowledgeOS-selected eval scenarios must be wired through references/evals.yaml before Tessl proof",
                source_context.get("allowed_claims", []),
            )

    def test_apply_routes_eval_fixtures_only_when_fixture_files_are_copied(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            extraction = _write_extraction(Path(tmp), include_evals=True, eval_files="fixtures")

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native/SKILL.md",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("references/eval-scenarios.json", skill_text)
            self.assertIn("references/evals/", skill_text)
            source_context = yaml.safe_load((skill_dir / "references" / "source-context.yaml").read_text(encoding="utf-8"))
            paths = {entry["path"] for entry in source_context["references"]}
            self.assertNotIn("references/eval-scenarios.json", paths)
            self.assertIn("references/evals/", paths)
            self.assertNotIn(
                "KnowledgeOS-selected eval scenarios must be wired through references/evals.yaml before Tessl proof",
                source_context.get("allowed_claims", []),
            )

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

    def test_invalid_utf8_reference_blocks_apply_with_finding(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            _write_skill(root)
            extraction = _write_extraction(Path(tmp))
            bad_reference = extraction / "references" / "knowledge-capsules" / "invalid-utf8.md"
            bad_reference.write_bytes(b"\xff\xfe\x00")

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "blocked")
            self.assertIn(
                "references:invalid_utf8:references/knowledge-capsules/invalid-utf8.md",
                payload["findings"],
            )

    def test_duplicate_eval_scenario_ids_block_apply(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            _write_skill(root)
            extraction = _write_extraction(Path(tmp), include_evals=True)
            scenarios_path = extraction / "references" / "eval-scenarios.json"
            scenarios = json.loads(scenarios_path.read_text(encoding="utf-8"))
            scenarios.append(dict(scenarios[0]))
            scenarios_path.write_text(json.dumps(scenarios, indent=2) + "\n", encoding="utf-8")

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "blocked")
            self.assertIn(
                "references:invalid_eval_scenarios_json:references/eval-scenarios.json:1:duplicate_eval_id:eval.harness.local-pass-ci-unknown",
                payload["findings"],
            )

    def test_vendored_demand_policy_is_validated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            _write_skill(root)
            bad_vendored_demand = {
                "schema_version": "knowledge-os.knowledge-demand.v1",
                "skill": {
                    "skill_id": "improve-agent-native",
                    "declared_name": "improve-agent-native",
                    "writable_root": "Skills/agent-ops/improve-agent-native",
                },
                "runtime_dependency_policy": {
                    "requires_knowledge_os_at_runtime": True,
                    "raw_sources_included": False,
                    "local_absolute_paths_required": False,
                },
            }
            extraction = _write_extraction(Path(tmp), vendored_demand_override=bad_vendored_demand)

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "blocked")
            self.assertIn(
                "references/knowledge-demand:requires_knowledge_os_at_runtime_not_false",
                payload["findings"],
            )
            self.assertIn("references/knowledge-demand:differs_from_root_knowledge-demand", payload["findings"])

    def test_preflight_resolves_canonical_plugins_skill_gate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            _write_skill(root)
            _write_skill_gate(root)
            extraction = _write_extraction(Path(tmp))

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=False,
                preflight_security=True,
            )

            self.assertEqual(payload["status"], "preview")
            self.assertEqual(payload["staged_preflight"]["status"], "pass")

    def test_apply_adds_routing_under_workflow_heading(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root, workflow_heading="Workflow")
            extraction = _write_extraction(Path(tmp))

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("## Workflow", skill_text)
            self.assertIn("Do not load all capsules by default", skill_text)

    def test_apply_creates_source_context_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root, source_context=False)
            extraction = _write_extraction(Path(tmp))

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            source_context = yaml.safe_load((skill_dir / "references" / "source-context.yaml").read_text(encoding="utf-8"))
            paths = {entry["path"] for entry in source_context["references"]}
            self.assertIn("references/knowledge-capsule.manifest.yaml", paths)

    @unittest.skipIf(not hasattr(os, "symlink"), "symlink support required")
    def test_apply_skips_symlinked_extraction_references(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "agent-skills"
            root.mkdir()
            skill_dir = _write_skill(root)
            extraction = _write_extraction(Path(tmp))
            outside = Path(tmp) / "outside-secret.md"
            outside.write_text("private source", encoding="utf-8")
            os.symlink(outside, extraction / "references" / "knowledge-capsules" / "outside-secret.md")

            payload = build_knowledge_ingest(
                root,
                extraction=str(extraction),
                skill="Skills/agent-ops/improve-agent-native",
                apply=True,
                preflight_security=False,
            )

            self.assertEqual(payload["status"], "applied")
            self.assertFalse((skill_dir / "references" / "knowledge-capsules" / "outside-secret.md").exists())

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

    def test_current_improve_agent_native_knowledge_evals_are_wired_to_tessl_source(self) -> None:
        skill_dir = REPO_ROOT / "Skills" / "agent-ops" / "improve-agent-native"
        manifest = yaml.safe_load((skill_dir / "references" / "knowledge-capsule.manifest.yaml").read_text(encoding="utf-8"))
        selected_eval_ids = {
            asset_id
            for asset_id in manifest.get("selected_asset_ids", [])
            if isinstance(asset_id, str) and asset_id.startswith("eval.")
        }
        evals = yaml.safe_load((skill_dir / "references" / "evals.yaml").read_text(encoding="utf-8"))
        tessl_case_ids = {case["id"] for case in evals.get("cases", [])}
        tessl_case_fixtures = {
            case.get("knowledge_pack", {}).get("fixture")
            for case in evals.get("cases", [])
            if isinstance(case.get("knowledge_pack"), dict)
        }
        scenario_payload = json.loads((skill_dir / "references" / "eval-scenarios.json").read_text(encoding="utf-8"))
        scenario_ids = {scenario["id"] for scenario in scenario_payload}
        fixture_paths = {
            f"references/evals/{asset_id}.md"
            for asset_id in selected_eval_ids
        }

        self.assertTrue(selected_eval_ids)
        self.assertEqual(set(), selected_eval_ids - scenario_ids)
        self.assertEqual(set(), selected_eval_ids - tessl_case_ids)
        self.assertEqual(set(), fixture_paths - tessl_case_fixtures)
        for fixture_path in fixture_paths:
            self.assertTrue((skill_dir / fixture_path).is_file(), fixture_path)

    def test_current_improve_agent_native_evals_are_behavioral_not_keyword_only(self) -> None:
        evals_path = REPO_ROOT / "Skills" / "agent-ops" / "improve-agent-native" / "references" / "evals.yaml"
        cases = eval_commands._parse_tessl_eval_cases(evals_path)
        findings = eval_commands._tessl_eval_quality_findings(cases)

        self.assertTrue(cases)
        self.assertEqual([], findings)


if __name__ == "__main__":
    unittest.main()
