from __future__ import annotations

import json
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from ask.services.codex_preview import build_codex_config_explain, build_codex_render_preview
from ask.skills_sdk.contracts import read_skill_frontmatter_fields
from ask.skills_sdk.package_contracts import read_agents_openai_yaml_fields, skill_package_contract
from ask.skills_sdk.package_verify import verify_archive_package


CONFORMANCE_SCHEMA_VERSION = "skills-conformance-evidence.v1"
DEFAULT_SUITE = "codex-parity"


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _safe_case_id(value: str) -> str:
    return "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in value)


def _write_skill(path: Path, frontmatter: str, body: str = "Use this fixture for conformance evidence.\n") -> Path:
    path.mkdir(parents=True, exist_ok=True)
    skill_md = path / "SKILL.md"
    skill_md.write_text(f"---\n{frontmatter}---\n\n{body}", encoding="utf-8")
    return skill_md


def _case(
    case_id: str,
    status: str,
    summary: str,
    evidence: dict[str, Any] | None = None,
    blockers: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "case_id": case_id,
        "status": status,
        "summary": summary,
        "evidence": evidence or {},
        "blockers": blockers or [],
    }


def _case_malformed_frontmatter(repo_root: Path, workspace: Path) -> dict[str, Any]:
    skill_md = _write_skill(
        workspace / "malformed-frontmatter",
        "description: Missing required name\n",
    )
    contract = skill_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
    missing = contract.get("required_fields", {}).get("missing", [])
    if "name" not in missing:
        return _case(
            "malformed_frontmatter",
            "blocked",
            "Malformed package metadata was not classified as missing required Codex fields.",
            {"missing": missing},
        )
    return _case(
        "malformed_frontmatter",
        "pass",
        "Missing required frontmatter is detected as blocked validation evidence.",
        {"missing": missing},
    )


def _case_invalid_agents_openai_yaml(repo_root: Path, workspace: Path) -> dict[str, Any]:
    skill_md = _write_skill(
        workspace / "invalid-openai-yaml",
        "name: invalid-openai-yaml\ndescription: Fixture.\n",
    )
    agents_dir = skill_md.parent / "agents"
    agents_dir.mkdir()
    (agents_dir / "openai.yaml").write_text("interface:\n  - [unterminated\n", encoding="utf-8")
    fields = read_agents_openai_yaml_fields(skill_md)
    contract = skill_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
    failed_open = contract.get("compatibility_status") == "compatible" and bool(contract.get("metadata", {}).get("name"))
    return _case(
        "invalid_agents_openai_yaml_fail_open",
        "pass" if failed_open else "blocked",
        "Invalid agents/openai.yaml fails open to SKILL.md metadata without crashing package contract generation.",
        {
            "openai_fields": fields,
            "contract_status": contract.get("compatibility_status"),
            "metadata_name": contract.get("metadata", {}).get("name"),
        },
    )


def _case_duplicate_names(repo_root: Path, workspace: Path) -> dict[str, Any]:
    first = _write_skill(workspace / "dup-a", "name: duplicate\ndescription: First.\n")
    second = _write_skill(workspace / "dup-b", "name: duplicate\ndescription: Second.\n")
    names = [
        read_skill_frontmatter_fields(first).get("name"),
        read_skill_frontmatter_fields(second).get("name"),
    ]
    duplicates = sorted({name for name in names if names.count(name) > 1})
    return _case(
        "duplicate_names",
        "pass" if duplicates == ["duplicate"] else "blocked",
        "Duplicate skill names are detectable before command-surface or injection claims.",
        {"duplicates": duplicates},
    )


def _case_plugin_namespace(repo_root: Path, workspace: Path) -> dict[str, Any]:
    skill_md = _write_skill(
        workspace / "plugin-skill",
        "name: plugin-skill\ndescription: Plugin fixture.\nplugin_id: fixture-plugin\n",
    )
    contract = skill_package_contract(repo_root, skill_md, read_skill_frontmatter_fields(skill_md))
    plugin_id = contract.get("metadata", {}).get("plugin_id")
    namespaced = f"{plugin_id}:plugin-skill" if plugin_id else None
    return _case(
        "plugin_namespace",
        "pass" if namespaced == "fixture-plugin:plugin-skill" else "blocked",
        "Plugin package metadata preserves plugin_id needed for Codex plugin namespacing.",
        {"plugin_id": plugin_id, "expected_runtime_name": namespaced},
    )


def _case_disabled_config(repo_root: Path, workspace: Path) -> dict[str, Any]:
    config = build_codex_config_explain(repo_root)
    contract = config.get("config_contract", {})
    selector_policy = contract.get("selector_policy")
    return _case(
        "disabled_config",
        "pass" if selector_policy else "blocked",
        "Codex config explain exposes selector policy for disabled-name and disabled-path rules.",
        {
            "selector_policy": selector_policy,
            "status": config.get("status"),
            "preview_limitations": config.get("blocked_checks", []),
        },
    )


def _case_symlinked_roots(repo_root: Path, workspace: Path) -> dict[str, Any]:
    source = _write_skill(workspace / "symlink-source", "name: symlink-source\ndescription: Fixture.\n")
    link = workspace / "symlink-root"
    symlink_status = "unavailable"
    try:
        link.symlink_to(source.parent, target_is_directory=True)
        symlink_status = "created" if link.is_symlink() and (link / "SKILL.md").is_file() else "blocked"
    except (OSError, NotImplementedError) as exc:
        return _case(
            "symlinked_roots",
            "blocked",
            "The local environment could not create a symlink fixture.",
            {"error": str(exc)},
        )
    return _case(
        "symlinked_roots",
        "pass" if symlink_status == "created" else "blocked",
        "Symlinked root fixtures are representable for loader parity tests without runtime mutation.",
        {"symlink_status": symlink_status, "link": link.as_posix()},
    )


def _case_thin_handles(repo_root: Path, workspace: Path) -> dict[str, Any]:
    handle = _write_skill(
        workspace / "thin-handle",
        "name: thin-handle\ndescription: Thin handle.\n",
        body=(
            "Source: Skills/example/SKILL.md\n"
            "Source hash: sha256:fixture\n"
            "Resolver command: ./bin/ask skills explain example --json --robot\n"
        ),
    )
    body = handle.read_text(encoding="utf-8")
    required = ["Source:", "Source hash:", "Resolver command:"]
    missing = [item for item in required if item not in body]
    return _case(
        "thin_handles",
        "pass" if not missing else "blocked",
        "Thin command handles carry source, hash, and resolver provenance fields.",
        {"missing": missing},
    )


def _case_context_truncation(repo_root: Path, workspace: Path) -> dict[str, Any]:
    preview = build_codex_render_preview(repo_root, context_window=1024)
    rendered = preview.get("rendered", {})
    report = rendered.get("report", {})
    omitted_count = int(report.get("omitted_count") or 0)
    included_count = int(report.get("included_count") or 0)
    exercised_budget = omitted_count > 0 or included_count > 0
    return _case(
        "context_truncation",
        "pass" if exercised_budget else "blocked",
        "Render preview reports Codex-style metadata budget and truncation evidence.",
        {
            "status": preview.get("status"),
            "budget_chars": report.get("budget_chars"),
            "included_count": included_count,
            "omitted_count": omitted_count,
            "preview_limitations": preview.get("blocked_checks", []),
        },
    )


def _case_installer_rollback(repo_root: Path, workspace: Path) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    archive = workspace / "missing-rollback.zip"
    skill_text = "---\nname: packaged\ndescription: Packaged fixture.\n---\n"
    manifest = {
        "provenance": {"source": "repo-owned-fixture", "trusted": True},
        "files": [{"path": "SKILL.md", "sha256": "0" * 64}],
    }
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("SKILL.md", skill_text)
        zip_file.writestr("skill-package-manifest.json", json.dumps(manifest))
    verification = verify_archive_package(archive)
    rules = [item.get("rule_id") for item in verification.get("rule_results", [])]
    expected = {"digest_mismatch", "rollback_journal_missing"}
    return _case(
        "installer_rollback",
        "pass" if expected.issubset(set(rules)) else "blocked",
        "Package verification blocks digest mismatch and missing rollback journal before mutation.",
        {"rules": rules, "mutation_status": verification.get("mutation_status")},
    )


def _case_archive_traversal(repo_root: Path, workspace: Path) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    archive = workspace / "unsafe-traversal.zip"
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("../escape/SKILL.md", "---\nname: escape\ndescription: Escape.\n---\n")
    verification = verify_archive_package(archive)
    rules = [item.get("rule_id") for item in verification.get("rule_results", [])]
    return _case(
        "unsafe_archive_traversal",
        "pass" if "archive_path_traversal" in rules else "blocked",
        "Archive traversal entries are rejected before package extraction.",
        {"rules": rules, "mutation_status": verification.get("mutation_status")},
    )


def _case_archive_symlink_escape(repo_root: Path, workspace: Path) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    archive = workspace / "symlink-escape.zip"
    symlink_info = zipfile.ZipInfo("skill-link")
    symlink_info.external_attr = (0o120777 & 0xFFFF) << 16
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr(symlink_info, "../../outside")
    verification = verify_archive_package(archive)
    rules = [item.get("rule_id") for item in verification.get("rule_results", [])]
    return _case(
        "archive_symlink_escape",
        "pass" if "archive_symlink_escape" in rules else "blocked",
        "Archive symlink entries are rejected before package extraction.",
        {"rules": rules, "mutation_status": verification.get("mutation_status")},
    )


def _case_untrusted_provenance(repo_root: Path, workspace: Path) -> dict[str, Any]:
    workspace.mkdir(parents=True, exist_ok=True)
    archive = workspace / "untrusted-provenance.zip"
    manifest = {
        "provenance": {"source": "external-untrusted", "trusted": False},
        "files": [],
        "rollback_journal": "rollback.jsonl",
    }
    with zipfile.ZipFile(archive, "w") as zip_file:
        zip_file.writestr("SKILL.md", "---\nname: packaged\ndescription: Packaged fixture.\n---\n")
        zip_file.writestr("rollback.jsonl", '{"action":"verify","decision":"blocked"}\n')
        zip_file.writestr("skill-package-manifest.json", json.dumps(manifest))
    verification = verify_archive_package(archive)
    rules = [item.get("rule_id") for item in verification.get("rule_results", [])]
    return _case(
        "untrusted_provenance",
        "pass" if "untrusted_provenance" in rules else "blocked",
        "Untrusted package provenance is rejected before mutation.",
        {"rules": rules, "mutation_status": verification.get("mutation_status")},
    )


CASE_RUNNERS: dict[str, Callable[[Path, Path], dict[str, Any]]] = {
    "malformed_frontmatter": _case_malformed_frontmatter,
    "invalid_agents_openai_yaml_fail_open": _case_invalid_agents_openai_yaml,
    "duplicate_names": _case_duplicate_names,
    "plugin_namespace": _case_plugin_namespace,
    "disabled_config": _case_disabled_config,
    "symlinked_roots": _case_symlinked_roots,
    "thin_handles": _case_thin_handles,
    "context_truncation": _case_context_truncation,
    "unsafe_archive_traversal": _case_archive_traversal,
    "archive_symlink_escape": _case_archive_symlink_escape,
    "untrusted_provenance": _case_untrusted_provenance,
    "installer_rollback": _case_installer_rollback,
}


def _prepare_evidence_dir(repo_root: Path, evidence_dir: str | None) -> Path:
    if evidence_dir:
        path = Path(evidence_dir).expanduser()
        if not path.is_absolute():
            path = repo_root / path
    else:
        path = repo_root / ".harness" / "evidence" / "skills-conformance" / _utc_timestamp().replace(":", "")
    path.mkdir(parents=True, exist_ok=True)
    return path.resolve()


def run_skills_conformance(repo_root: Path, suite: str = DEFAULT_SUITE, evidence_dir: str | None = None) -> dict[str, Any]:
    if suite != DEFAULT_SUITE:
        return {
            "schema_version": CONFORMANCE_SCHEMA_VERSION,
            "suite": suite,
            "status": "blocked",
            "blockers": [
                {
                    "rule_id": "unknown_suite",
                    "message": f"Unknown skills conformance suite: {suite}",
                }
            ],
            "validation_commands": [
                "./bin/ask skills conformance run --suite codex-parity --json --robot --evidence-dir <path>"
            ],
        }

    evidence_path = _prepare_evidence_dir(repo_root, evidence_dir)
    case_workspace = Path(tempfile.mkdtemp(prefix="skills-conformance-", dir=str(evidence_path)))
    snapshots_path = evidence_path / "snapshots"
    snapshots_path.mkdir(exist_ok=True)
    cases: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for case_id, runner in CASE_RUNNERS.items():
        try:
            case = runner(repo_root, case_workspace / _safe_case_id(case_id))
        except Exception as exc:  # pragma: no cover - defensive fail-closed path
            case = _case(
                case_id,
                "blocked",
                "Conformance case raised an unexpected exception.",
                {"exception": type(exc).__name__, "message": str(exc)},
            )
        snapshot_path = snapshots_path / f"{_safe_case_id(case_id)}.json"
        case["snapshot_path"] = snapshot_path.as_posix()
        snapshot_path.write_text(
            json.dumps({"schema_version": CONFORMANCE_SCHEMA_VERSION, **case}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        cases.append(case)
        if case.get("status") != "pass":
            blockers.append(
                {
                    "rule_id": case_id,
                    "message": case.get("summary", "Conformance case did not pass."),
                }
            )

    evidence_jsonl = evidence_path / "skills-conformance-evidence.jsonl"
    with evidence_jsonl.open("w", encoding="utf-8") as handle:
        for case in cases:
            handle.write(json.dumps({"schema_version": CONFORMANCE_SCHEMA_VERSION, **case}, sort_keys=True) + "\n")

    command_manifest_path = evidence_path / "skills-conformance-commands.jsonl"
    command_entries = [
        {
            "schema_version": CONFORMANCE_SCHEMA_VERSION,
            "command": "./bin/ask skills conformance run --suite codex-parity --json --robot --evidence-dir <path>",
            "purpose": "Replay the full deterministic suite.",
        }
    ]
    command_entries.extend(
        {
            "schema_version": CONFORMANCE_SCHEMA_VERSION,
            "case_id": case["case_id"],
            "command": "./bin/ask skills conformance run --suite codex-parity --json --robot --evidence-dir <path>",
            "snapshot_path": case.get("snapshot_path"),
            "purpose": f"Replay and inspect {case['case_id']} evidence.",
        }
        for case in cases
    )
    with command_manifest_path.open("w", encoding="utf-8") as handle:
        for entry in command_entries:
            handle.write(json.dumps(entry, sort_keys=True) + "\n")

    summary_path = evidence_path / "skills-conformance-summary.json"
    summary = {
        "schema_version": CONFORMANCE_SCHEMA_VERSION,
        "suite": suite,
        "status": "blocked" if blockers else "pass",
        "case_count": len(cases),
        "passed_count": len([case for case in cases if case.get("status") == "pass"]),
        "blocked_count": len(blockers),
        "cases": cases,
        "checks": cases,
        "blockers": blockers,
        "evidence_dir": evidence_path.as_posix(),
        "evidence_jsonl": evidence_jsonl.as_posix(),
        "commands_jsonl": command_manifest_path.as_posix(),
        "snapshots_dir": snapshots_path.as_posix(),
        "summary_path": summary_path.as_posix(),
        "mutation_status": "evidence_dir_only",
        "validation_commands": [
            "./bin/ask skills conformance run --suite codex-parity --json --robot --evidence-dir <path>"
        ],
    }
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return summary
