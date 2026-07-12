from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path


VALIDATOR_DIR = Path(__file__).resolve().parents[1] / "scripts" / "validation-and-linting"
if str(VALIDATOR_DIR) not in sys.path:
    sys.path.insert(0, str(VALIDATOR_DIR))

import validate_repo_layout  # noqa: E402
import generate_repo_layout_caller_inventory  # noqa: E402


def _write_config(path: Path) -> None:
    source = Path(__file__).resolve().parents[1] / "config" / "repo-layout.v1.json"
    path.write_text(source.read_text(encoding="utf-8"), encoding="utf-8")


def _minimal_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "Infrastructure" / "config").mkdir(parents=True)
    _write_config(root / "Infrastructure" / "config" / "repo-layout.v1.json")
    for dirname in (".agents", ".harness", "Infrastructure", "Skills"):
        (root / dirname).mkdir(exist_ok=True)
    (root / "README.md").write_text("repo\n", encoding="utf-8")
    return root


def test_current_repository_layout_policy_passes_without_unknown_symlinks() -> None:
    root = Path(__file__).resolve().parents[2]
    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    assert report["summary"]["blocking_count"] == 0


def test_tracked_phase_zero_roots_have_explicit_classifications() -> None:
    root = Path(__file__).resolve().parents[2]
    config = json.loads(
        (root / "Infrastructure" / "config" / "repo-layout.v1.json").read_text(
            encoding="utf-8"
        )
    )
    entries = validate_repo_layout._iter_layout_entries(config)

    assert {
        path: entries[path]["section"]
        for path in ("AI", "codestyle", "codex", "coding-policy.json", "contracts")
    } == {
        "AI": "supporting_reference",
        "codestyle": "root_governance",
        "codex": "repo_automation",
        "coding-policy.json": "repo_automation",
        "contracts": "repo_automation",
    }
    assert "*" not in entries


def test_runtime_projection_symlink_blocks_copy_only_install_contract(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / ".agents" / "skills").mkdir(parents=True)
    os.symlink("../../Skills/agent-ops/testing", root / ".agents" / "skills" / "testing")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    symlink_findings = [
        finding for finding in report["findings"] if finding["path"] == ".agents/skills/testing"
    ]
    assert symlink_findings
    assert symlink_findings[0]["code"] == "symlink_forbidden"
    assert symlink_findings[0]["classification"] == "legacy_runtime_projection"


def test_unknown_symlink_blocks_layout_validation(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    os.symlink("Infrastructure", root / "mystery-link")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(finding["code"] == "unknown_symlink" for finding in report["findings"])


def test_known_swift_build_output_symlinks_are_ignored(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    output_root = root / "Prototypes" / "improve-agent-native-menubar" / "dist"
    for rel_path in (
        "swiftpm-build-nodebug/debug",
        "swiftpm-build/debug",
    ):
        link = output_root / rel_path
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink("arm64-apple-macosx/debug", link)

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    ignored_paths = {
        finding["path"]
        for finding in report["findings"]
        if finding["code"] == "symlink_ignored"
    }
    assert ignored_paths == {
        "Prototypes/improve-agent-native-menubar/dist/swiftpm-build-nodebug/debug",
        "Prototypes/improve-agent-native-menubar/dist/swiftpm-build/debug",
    }


def test_swift_output_policy_rejects_source_target_at_allowlisted_path(
    tmp_path: Path,
) -> None:
    root = _minimal_repo(tmp_path)
    link = (
        root
        / "Prototypes"
        / "improve-agent-native-menubar"
        / "dist"
        / "swiftpm-build"
        / "debug"
    )
    link.parent.mkdir(parents=True, exist_ok=True)
    os.symlink("../../../../Sources/secret-source", link)

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(
        finding["code"] == "unknown_symlink"
        and finding["path"]
        == "Prototypes/improve-agent-native-menubar/dist/swiftpm-build/debug"
        for finding in report["findings"]
    )


def test_swift_output_policy_does_not_mask_other_ignored_or_source_symlinks(
    tmp_path: Path,
) -> None:
    root = _minimal_repo(tmp_path)
    prototype = root / "Prototypes" / "improve-agent-native-menubar"
    for rel_path in ("dist/other/debug", "Sources/debug"):
        link = prototype / rel_path
        link.parent.mkdir(parents=True, exist_ok=True)
        os.symlink("/private/tmp/unowned-link", link)

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    unknown_paths = {
        finding["path"]
        for finding in report["findings"]
        if finding["code"] == "unknown_symlink"
    }
    assert unknown_paths == {
        "Prototypes/improve-agent-native-menubar/dist/other/debug",
        "Prototypes/improve-agent-native-menubar/Sources/debug",
    }


def test_capitalized_plugin_internal_alias_is_allowed(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    alias_dir = root / "Plugins" / "skill-factory" / "skills"
    alias_dir.mkdir(parents=True)
    os.symlink("../../../Skills/agent-ops/testing", alias_dir / "skill-refactor")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    alias_findings = [
        finding
        for finding in report["findings"]
        if finding["path"] == "Plugins/skill-factory/skills/skill-refactor"
    ]
    assert alias_findings
    assert alias_findings[0]["classification"] == "compatibility_alias"


def test_capitalized_browser_use_runtime_link_is_allowed(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "Plugins").mkdir(exist_ok=True)
    os.symlink(
        "/Applications/Codex.app/Contents/Resources/plugins/openai-bundled/plugins/browser-use",
        root / "Plugins" / "browser-use",
    )

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    browser_findings = [
        finding for finding in report["findings"] if finding["path"] == "Plugins/browser-use"
    ]
    assert browser_findings
    assert browser_findings[0]["classification"] == "external_runtime_link"


def test_in_repo_foundry_root_blocks_external_foundry_contract(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "foundry" / "skills").mkdir(parents=True)

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(
        finding["code"] == "forbidden_top_level_root" and finding["path"] == "foundry"
        for finding in report["findings"]
    )


def test_untracked_in_repo_foundry_root_blocks_in_git_worktree(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    subprocess.run(["git", "init", "--quiet", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "Infrastructure", "README.md"], check=True)
    (root / "foundry" / "skills").mkdir(parents=True)

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(
        finding["code"] == "forbidden_top_level_root" and finding["path"] == "foundry"
        for finding in report["findings"]
    )


def test_in_repo_skills_sdk_root_is_legacy_until_repository_extraction(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "skills-sdk" / "brand").mkdir(parents=True)

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    assert any(
        finding["code"] == "legacy_layout_path"
        and finding["path"] == "skills-sdk"
        and finding["classification"] == "skills_sdk"
        for finding in report["findings"]
    )


def test_root_infrastructure_alias_is_deprecated_warning(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    os.symlink("Infrastructure/scripts", root / "scripts")

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    script_findings = [finding for finding in report["findings"] if finding["path"] == "scripts"]
    assert script_findings
    assert script_findings[0]["status"] == "warning"
    assert script_findings[0]["severity"] == "warning"
    assert script_findings[0]["classification"] == "compatibility_alias"
    assert report["status"] == "pass"


def test_unknown_top_level_directory_blocks(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "random-new-root").mkdir()

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(
        finding["code"] == "top_level_unclassified"
        and finding["path"] == "random-new-root"
        for finding in report["findings"]
    )


def test_root_brand_directory_blocks_after_skills_sdk_brand_migration(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "brand").mkdir()

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "fail"
    assert any(
        finding["code"] == "top_level_unclassified" and finding["path"] == "brand"
        for finding in report["findings"]
    )


def test_prototypes_root_is_classified_as_evidence_control(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    (root / "Prototypes" / "improve-agent-native-menubar").mkdir(parents=True)
    (root / "Prototypes" / "improve-agent-native-menubar" / "README.md").write_text(
        "Prototype workbench.\n",
        encoding="utf-8",
    )

    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert report["status"] == "pass"
    assert not any(
        finding["code"] == "top_level_unclassified" and finding["path"] == "Prototypes"
        for finding in report["findings"]
    )


def test_json_report_is_serializable(tmp_path: Path) -> None:
    root = _minimal_repo(tmp_path)
    report = validate_repo_layout.validate_repo_layout(
        root, root / "Infrastructure" / "config" / "repo-layout.v1.json"
    )

    assert json.loads(json.dumps(report))["schema_version"] == "repo-layout-validation.v1"


def test_caller_inventory_classifies_legacy_root_references(
    tmp_path: Path, monkeypatch
) -> None:
    root = _minimal_repo(tmp_path)
    (root / "Infrastructure" / "scripts" / "lib" / "ask").mkdir(parents=True)
    (root / ".github" / "workflows").mkdir(parents=True)
    (root / "Docs" / "reference").mkdir(parents=True)
    files = {
        "Infrastructure/scripts/lib/ask/commands.py": (
            'command = "./bin/ask skills package verify Skills/agent-ops/testing"\n'
        ),
        ".github/workflows/ci.yml": "run: bash Infrastructure/scripts/validate_all.sh\n",
        "Docs/reference/example.md": "See Plugins/skill-factory and docs-policy.json.\n",
    }
    for rel_path, content in files.items():
        path = root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    monkeypatch.setattr(
        generate_repo_layout_caller_inventory,
        "_tracked_files",
        lambda _root: sorted(files),
    )

    report = generate_repo_layout_caller_inventory.generate_inventory(root)

    assert report["schema_version"] == "repo-layout-caller-inventory.v1"
    assert report["summary"]["root_counts"]["Skills/"] == 1
    assert report["summary"]["root_counts"]["Infrastructure/"] == 1
    assert report["summary"]["root_counts"]["Plugins/"] == 1
    assert report["summary"]["root_counts"]["docs-policy.json"] == 1
    assert report["summary"]["category_counts"]["ask_cli_route"] >= 1
    assert report["summary"]["category_counts"]["ci_workflow"] >= 1
    assert report["summary"]["category_counts"]["docs_reference_link"] >= 1


def test_caller_inventory_scans_nested_extensionless_scripts(
    tmp_path: Path, monkeypatch
) -> None:
    root = _minimal_repo(tmp_path)
    rel_path = "Infrastructure/bin/ask"
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("exec ./bin/ask skills package verify Skills/agent-ops/testing\n", encoding="utf-8")
    monkeypatch.setattr(generate_repo_layout_caller_inventory, "_tracked_files", lambda _root: [rel_path])

    report = generate_repo_layout_caller_inventory.generate_inventory(root)

    assert report["summary"]["scanned_files"] == 1
    assert report["summary"]["root_counts"]["Skills/"] == 1
    assert report["summary"]["category_counts"]["ask_cli_route"] >= 1


def test_caller_inventory_uses_portable_root_marker(
    tmp_path: Path, monkeypatch
) -> None:
    rel_path = "README.md"
    roots = [tmp_path / "first-worktree", tmp_path / "second-worktree"]
    for root in roots:
        root.mkdir()
        (root / rel_path).write_text("Use Skills/agent-ops/testing.\n", encoding="utf-8")

    monkeypatch.setattr(
        generate_repo_layout_caller_inventory,
        "_tracked_files",
        lambda _root: [rel_path],
    )

    reports = [
        generate_repo_layout_caller_inventory.generate_inventory(root) for root in roots
    ]

    assert reports[0]["repo_root"] == "."
    assert reports[0] == reports[1]


def test_actionable_caller_inventory_excludes_generated_inputs_before_scanning(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    source_path = "README.md"
    generated_path = ".harness/refactors/root-layout/caller-inventory.current.json"
    (root / source_path).write_text("Use Skills/agent-ops/testing.\n", encoding="utf-8")
    artifact = root / generated_path
    artifact.parent.mkdir(parents=True)
    artifact.write_text("Historical Skills/agent-ops/testing reference.\n", encoding="utf-8")

    monkeypatch.setattr(
        generate_repo_layout_caller_inventory,
        "_tracked_files",
        lambda _root: [source_path, generated_path],
    )

    report = generate_repo_layout_caller_inventory.generate_inventory(
        root, actionable_only=True
    )

    assert report["mode"] == "actionable_only"
    assert report["summary"]["scanned_files"] == 1
    assert report["summary"]["root_counts"] == {"Skills/": 1}
    assert [item["path"] for item in report["occurrences"]] == [source_path]


def test_actionable_inventory_keeps_generated_command_callers(
    tmp_path: Path, monkeypatch
) -> None:
    root = _minimal_repo(tmp_path)
    rel_path = "Infrastructure/scripts/run-migration.py"
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "cmd = 'python3 Infrastructure/scripts/generate_skillset_manifests.py --write'\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(generate_repo_layout_caller_inventory, "_tracked_files", lambda _root: [rel_path])

    report = generate_repo_layout_caller_inventory.generate_inventory(root)
    actionable = generate_repo_layout_caller_inventory.filter_actionable(report)

    assert report["summary"]["root_counts"]["Infrastructure/"] == 1
    assert actionable["summary"]["root_counts"]["Infrastructure/"] == 1
    assert "generated_artifact_input" not in actionable["occurrences"][0]["categories"]


def test_actionable_inventory_filters_generated_occurrences_in_source_files(
    tmp_path: Path, monkeypatch
) -> None:
    root = _minimal_repo(tmp_path)
    rel_path = "README.md"
    path = root / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "Use Skills/agent-ops/testing.\n"
        "Historical .harness/evidence/receipt.json mentions Skills/agent-ops/testing.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(generate_repo_layout_caller_inventory, "_tracked_files", lambda _root: [rel_path])

    report = generate_repo_layout_caller_inventory.generate_inventory(root, actionable_only=True)

    assert [item["line"] for item in report["occurrences"]] == [1]


def test_caller_inventory_markdown_summary_is_written(tmp_path: Path, monkeypatch) -> None:
    root = _minimal_repo(tmp_path)
    rel_path = "README.md"
    (root / rel_path).write_text("Use scripts/check.sh for old entrypoints.\n", encoding="utf-8")
    monkeypatch.setattr(
        generate_repo_layout_caller_inventory,
        "_tracked_files",
        lambda _root: [rel_path],
    )

    report = generate_repo_layout_caller_inventory.generate_inventory(root)
    output = tmp_path / "inventory.md"
    generate_repo_layout_caller_inventory.write_markdown(report, output)

    text = output.read_text(encoding="utf-8")
    assert "Repo Layout Caller Inventory" in text
    assert "scripts" in text
    assert "Migration Use" in text
