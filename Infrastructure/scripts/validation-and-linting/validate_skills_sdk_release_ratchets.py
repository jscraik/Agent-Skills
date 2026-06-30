#!/usr/bin/env python3
"""Validate Skills SDK release ratchets for a candidate skill package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[3]
SCRIPT_DIR = Path(__file__).resolve().parent
ASK_LIB = ROOT / "Infrastructure" / "scripts" / "lib"
if str(ASK_LIB) not in sys.path:
    sys.path.insert(0, str(ASK_LIB))
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from ask.skills_sdk.package_contracts import (  # noqa: E402
    _scenario_cases_from_reference,
    read_structured_reference,
)

from skills_sdk_release_receipts import REQUIRED_GATE_CHAIN, build_receipt_findings  # noqa: E402


CENTRAL_RUBRIC = Path("Infrastructure/config/skills-sdk/gold-standard-rubric.v1.json")
PATTERN_REPORT = Path(".harness/reports/skills-sdk-ratchet-patterns.json")
STEERING_LEDGER = Path(".harness/quality/steering-uptake.md")
REQUIRED_CRITERIA = {
    "construction_structure_steering_pruning",
    "domain_artifact_classification",
    "trigger_boundary",
    "reference_invocation",
    "progressive_disclosure",
    "scenario_evidence_quality",
    "evidence_lane_separation",
}
PACKAGE_ONLY_REFERENCES = {
    "references/source-context.yaml",
    "references/source-provenance.md",
    "references/knowledge-capsule.manifest.yaml",
    "references/knowledge-demand.yaml",
}
REQUIRED_CONTRACT_COMMANDS = (
    "skills package verify",
    "sdk eval scenario-quality",
    "sdk security risk-modes",
)
REQUIRED_PATTERN_IDS = {
    "central-rubric-drift",
    "knowledgeos-reference-shape-drift",
    "reference-heading-invocation-drift",
    "yaml-parser-parity-drift",
    "reference-boundary-drift",
    "tessl-lane-overclaim",
    "skill-factory-pipeline-drift",
    "security-lane-gap",
    "advisory-carry-forward",
    "stale-runtime-handle",
}


@dataclass
class Finding:
    code: str
    status: str
    message: str
    evidence: dict[str, Any]


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _json(path: Path) -> Any:
    return json.loads(_read(path))


def _structured(path: Path) -> dict[str, Any]:
    loaded, error = read_structured_reference(path)
    if error is not None or not isinstance(loaded, dict):
        raise ValueError(error or "structured reference must be a mapping")
    return loaded


def _skill_paths(root: Path, target: str) -> tuple[Path, Path, Path]:
    raw = root / target
    skill_dir = raw if raw.is_dir() else raw.parent
    skill_md = raw if raw.name == "SKILL.md" else skill_dir / "SKILL.md"
    refs = skill_dir / "references"
    return skill_dir, skill_md, refs


def _case_ids_from_refs(refs: Path) -> list[str]:
    evals = refs / "evals.yaml"
    loaded, _error = read_structured_reference(evals)
    cases = _scenario_cases_from_reference(evals, loaded if isinstance(loaded, dict) else {})
    return [str(case.get("id")) for case in cases if isinstance(case, dict) and case.get("id")]


def markdown_title(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def markdown_reference_heading_weak(path: Path, text: str) -> bool:
    title = markdown_title(text)
    if not title:
        return True
    expected_words = [word for word in path.stem.replace("-", " ").split() if len(word) > 2]
    title_lower = title.lower()
    if title_lower in {"details", "overview", "notes", "reference", "provenance", "routing"}:
        return True
    return not all(word.lower() in title_lower for word in expected_words[:3])


def _check_central_rubric(root: Path) -> Finding:
    path = root / CENTRAL_RUBRIC
    if not path.is_file():
        return Finding("central_rubric_missing", "fail", "Central Skills SDK gold rubric is missing.", {"path": str(CENTRAL_RUBRIC)})
    try:
        payload = _json(path)
    except (OSError, ValueError) as exc:
        return Finding("central_rubric_unparseable", "fail", "Central Skills SDK gold rubric must be JSON.", {"path": str(CENTRAL_RUBRIC), "error": str(exc)})
    criteria = payload.get("quality_criteria")
    missing = sorted(REQUIRED_CRITERIA - set(criteria if isinstance(criteria, dict) else []))
    status = "pass" if not missing and payload.get("rubric_id") == "skills-sdk.gold-standard.v1" else "fail"
    return Finding(
        "central_rubric_profile",
        status,
        "Central Skills SDK gold rubric must expose the shared release criteria.",
        {"path": str(CENTRAL_RUBRIC), "rubric_id": payload.get("rubric_id"), "missing_criteria": missing},
    )


def _check_contract_rubric(root: Path, refs: Path) -> Finding:
    contract_path = refs / "contract.yaml"
    if not contract_path.is_file():
        return Finding("contract_missing", "fail", "Skill package must declare references/contract.yaml.", {"path": _rel(contract_path, root)})
    try:
        contract = _structured(contract_path)
    except ValueError as exc:
        return Finding("contract_unparseable", "fail", "references/contract.yaml must be parseable.", {"path": _rel(contract_path, root), "error": str(exc)})
    profile = contract.get("rubric_profile") or contract.get("rubric_profiles")
    local_criteria = contract.get("quality_criteria")
    local_keys = set(local_criteria) if isinstance(local_criteria, dict) else set()
    duplicated = sorted(REQUIRED_CRITERIA & local_keys)
    missing_profile = profile != "skills-sdk.gold-standard.v1"
    status = "pass" if not missing_profile and not duplicated else "fail"
    return Finding(
        "contract_rubric_profile",
        status,
        "Skill contracts should select the central gold rubric and avoid duplicating global criteria locally.",
        {"path": _rel(contract_path, root), "rubric_profile": profile, "duplicated_global_criteria": duplicated},
    )


def _check_reference_boundary(root: Path, skill_md: Path, refs: Path) -> Finding:
    text = _read(skill_md) if skill_md.is_file() else ""
    contract_text = _read(refs / "contract.yaml") if (refs / "contract.yaml").is_file() else ""
    mentioned_in_skill = sorted(ref for ref in PACKAGE_ONLY_REFERENCES if ref in text)
    existing_package_refs = sorted(ref for ref in PACKAGE_ONLY_REFERENCES if (skill_md.parent / ref).exists())
    missing_contract_routes = sorted(ref for ref in existing_package_refs if ref not in contract_text and Path(ref).name not in contract_text)
    status = "pass" if not mentioned_in_skill and not missing_contract_routes else "fail"
    return Finding(
        "reference_boundary",
        status,
        "Package-management references should be routed by package contracts, not always-loaded SKILL.md progressive disclosure.",
        {
            "skill": _rel(skill_md, root),
            "mentioned_in_skill": mentioned_in_skill,
            "missing_contract_routes": missing_contract_routes,
        },
    )


def _check_knowledgeos_reference_shape(root: Path, refs: Path) -> Finding:
    manifest_path = refs / "knowledge-capsule.manifest.yaml"
    if not manifest_path.is_file():
        return Finding(
            "knowledgeos_reference_shape",
            "pass",
            "Skills without a KnowledgeOS capsule manifest have no KnowledgeOS reference shape to validate.",
            {"path": _rel(manifest_path, root), "manifest_declared": False},
        )
    try:
        manifest = _structured(manifest_path)
    except ValueError as exc:
        return Finding(
            "knowledgeos_reference_shape",
            "fail",
            "KnowledgeOS capsule manifest must be parseable before release movement.",
            {"path": _rel(manifest_path, root), "error": str(exc)},
        )
    capsule_paths = _knowledge_capsule_paths(manifest)
    legacy_paths = [path for path in capsule_paths if path.startswith("references/knowledge-capsules/")]
    legacy_allowed, storage_justification = _legacy_capsule_subdirectory_allowed(manifest)
    missing_files = _missing_capsule_files(refs, capsule_paths)
    missing_routing = _missing_capsule_routing(refs, capsule_paths)
    status = "pass" if not missing_files and not missing_routing and (not legacy_paths or legacy_allowed) else "fail"
    return Finding(
        "knowledgeos_reference_shape",
        status,
        "KnowledgeOS exports must vendor capsule bodies as top-level references/*.md by default; legacy subdirectories need manifest justification.",
        {
            "path": _rel(manifest_path, root),
            "capsule_paths": capsule_paths,
            "legacy_capsule_paths": legacy_paths,
            "legacy_subdirectory_allowed": legacy_allowed,
            "legacy_subdirectory_justification_present": bool(storage_justification),
            "missing_files": missing_files,
            "missing_routing": missing_routing,
        },
    )


def _check_reference_heading_invocation(root: Path, refs: Path) -> Finding:
    if not refs.is_dir():
        return Finding(
            "reference_heading_invocation",
            "fail",
            "Skill package references directory is required before release movement.",
            {"path": _rel(refs, root)},
        )
    weak: list[dict[str, Any]] = []
    checked = 0
    for candidate in sorted(refs.rglob("*.md")):
        if not candidate.is_file():
            continue
        checked += 1
        rel_path = _rel(candidate, root)
        try:
            text = candidate.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            weak.append({"path": rel_path, "title": "", "reason": str(exc)})
            continue
        if markdown_reference_heading_weak(candidate, text):
            weak.append(
                {
                    "path": rel_path,
                    "title": markdown_title(text),
                    "reason": "missing_generic_or_filename_misaligned_h1",
                }
            )
    return Finding(
        "reference_heading_invocation",
        "pass" if not weak else "fail",
        "Markdown references and vendored KnowledgeOS capsule bodies must have specific filename-aligned H1 headings.",
        {"references_dir": _rel(refs, root), "checked_markdown_count": checked, "weak_headings": weak[:20]},
    )


def _knowledge_capsule_paths(manifest: dict[str, Any]) -> list[str]:
    capsules = manifest.get("capsules")
    if not isinstance(capsules, list):
        return []
    paths: list[str] = []
    for capsule in capsules:
        if isinstance(capsule, dict) and isinstance(capsule.get("target_path"), str):
            path = capsule["target_path"].strip()
            if path:
                paths.append(path)
    return paths


def _legacy_capsule_subdirectory_allowed(manifest: dict[str, Any]) -> tuple[bool, str]:
    storage = manifest.get("capsule_storage")
    if not isinstance(storage, dict):
        return False, ""
    justification = str(storage.get("justification") or "").strip()
    allowed = storage.get("allow_legacy_subdirectory") is True and bool(justification)
    return allowed, justification


def _missing_capsule_files(refs: Path, capsule_paths: list[str]) -> list[str]:
    return sorted(
        path
        for path in capsule_paths
        if path.startswith("references/") and not (refs.parent / path).is_file()
    )


def _missing_capsule_routing(refs: Path, capsule_paths: list[str]) -> list[str]:
    routing_path = refs / "knowledge-capsule-routing.md"
    routing_text = _read(routing_path) if routing_path.is_file() else ""
    return sorted(path for path in capsule_paths if path not in routing_text)


def _check_tessl_lane_naming(root: Path, skill_dir: Path) -> Finding:
    handoff_dir = root / ".harness" / "evidence" / "handoff" / skill_dir.name
    receipts = sorted(handoff_dir.glob("tessl*.json")) if handoff_dir.is_dir() else []
    missing: list[str] = []
    for receipt in receipts:
        try:
            payload = _json(receipt)
        except (OSError, ValueError):
            missing.append(_rel(receipt, root))
            continue
        lane = payload.get("tessl_lane") or payload.get("lane") or payload.get("tessl", {}).get("lane")
        if lane not in {"review", "dry_run", "live_eval", "score_receipt", "local_proof"}:
            missing.append(_rel(receipt, root))
    status = "pass" if not missing else "fail"
    return Finding(
        "tessl_lane_naming",
        status,
        "Tessl artifacts must name their lane so review, dry-run, live eval, and score receipts cannot be conflated.",
        {"handoff_dir": _rel(handoff_dir, root), "receipt_count": len(receipts), "missing_lane": missing},
    )


def _check_scenario_parser_parity(root: Path, refs: Path) -> Finding:
    evals = refs / "evals.yaml"
    if not evals.is_file():
        return Finding("scenario_evals_missing", "fail", "references/evals.yaml is required before SDK eval handoff.", {"path": _rel(evals, root)})
    text = _read(evals)
    loaded, error = read_structured_reference(evals)
    fallback_cases = _scenario_cases_from_reference(evals, loaded if isinstance(loaded, dict) else {})
    case_text = _case_section_text(text)
    id_count, deterministic_count, alias_lines = _scenario_text_counts(text, case_text)
    missing_fields = _scenario_missing_fields(fallback_cases)
    status = (
        "pass"
        if error is None
        and id_count == len(fallback_cases)
        and deterministic_count == id_count
        and not alias_lines
        and not missing_fields
        else "fail"
    )
    return Finding(
        "scenario_parser_parity",
        status,
        "Scenario YAML must parse to the same case set under SDK fallback parsing and avoid alias-dependent deterministic checks.",
        {
            "path": _rel(evals, root),
            "structured_error": error,
            "text_id_count": id_count,
            "fallback_case_count": len(fallback_cases),
            "deterministic_checks_count": deterministic_count,
            "alias_lines": alias_lines,
            "missing_fields": missing_fields[:20],
        },
    )


def _scenario_text_counts(text: str, case_text: str) -> tuple[int, int, list[str]]:
    id_count = len(re.findall(r"(?m)^\s*-\s+id\s*:", case_text))
    deterministic_count = len(re.findall(r"(?m)^\s+deterministic_checks\s*:", case_text))
    alias_lines = [line.strip() for line in text.splitlines() if "deterministic_checks:" in line and "*" in line]
    return id_count, deterministic_count, alias_lines


def _scenario_missing_fields(cases: list[Any]) -> list[dict[str, Any]]:
    missing_fields: list[dict[str, Any]] = []
    required = ("id", "category", "task", "given", "should", "acceptance")
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            missing_fields.append({"index": index, "missing": ["mapping"]})
            continue
        missing = [field for field in required if not case.get(field)]
        if missing:
            missing_fields.append({"id": case.get("id", f"case[{index}]"), "missing": missing})
    return missing_fields


def _check_skill_factory_pipeline(root: Path, refs: Path, contract: dict[str, Any] | None) -> Finding:
    if contract is None:
        return Finding(
            "skill_factory_pipeline_commands",
            "fail",
            "Skill Factory pipeline check skipped due to missing or unparseable contract.",
            {"path": _rel(refs / "contract.yaml", root)},
        )
    commands = contract.get("commands")
    command_text = "\n".join(str(item) for item in commands) if isinstance(commands, list) else ""
    missing = [needle for needle in REQUIRED_CONTRACT_COMMANDS if needle not in command_text]
    status = "pass" if not missing else "fail"
    return Finding(
        "skill_factory_pipeline_commands",
        status,
        "Skill Factory-created or hardened skills must advertise the same Skills SDK package, scenario, and security gates.",
        {"path": _rel(refs / "contract.yaml", root), "missing_command_fragments": missing},
    )


def _check_security_lane(root: Path, refs: Path, contract: dict[str, Any] | None) -> Finding:
    if contract is None:
        return Finding(
            "security_risk_mode_lane",
            "fail",
            "Security lane check skipped due to missing or unparseable contract.",
            {"path": _rel(refs / "contract.yaml", root)},
        )
    commands = contract.get("commands")
    command_text = "\n".join(str(item) for item in commands) if isinstance(commands, list) else ""
    has_security_preview = "sdk security risk-modes" in command_text and "--preview" in command_text
    return Finding(
        "security_risk_mode_lane",
        "pass" if has_security_preview else "fail",
        "Skills SDK release candidates must include the non-mutating security risk-mode preview before Tessl movement.",
        {"path": _rel(refs / "contract.yaml", root), "has_security_preview": has_security_preview},
    )


def _check_advisory_policy(root: Path, refs: Path) -> Finding:
    evals = refs / "evals.yaml"
    text = _read(evals)
    case_text = _case_section_text(text)
    deterministic_count = len(re.findall(r"(?m)^\s+deterministic_checks\s*:", case_text))
    id_count = len(re.findall(r"(?m)^\s*-\s+id\s*:", case_text))
    weak: list[dict[str, Any]] = []
    for block in _case_blocks(case_text):
        match = re.search(r"(?m)^-\s+id\s*:\s*(\S+)", block)
        case_id = match.group(1) if match else "unknown"
        release = bool(re.search(r"(?m)^\s*-\s+release\s*$", block))
        acceptance_count = len(re.findall(r"(?m)^\s+-\s+type\s*:", block))
        if release and acceptance_count < 2:
            weak.append({"id": case_id, "reason": "release_acceptance_lt_2"})
    if deterministic_count != id_count:
        weak.append({"id": "scenario_set", "reason": "deterministic_checks_count_mismatch"})
    return Finding(
        "advisory_carry_forward_policy",
        "pass" if not weak else "fail",
        "Scenario warnings should be repaired before the next phase; release cases need executable acceptance and deterministic checks.",
        {"path": _rel(evals, root), "weak_cases": weak[:20]},
    )


def _case_section_text(text: str) -> str:
    """Return only the top-level cases section from an evals.yaml file."""
    lines = text.splitlines()
    collected: list[str] = []
    in_cases = False
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip(" "))
        if not in_cases:
            if indent == 0 and stripped == "cases:":
                in_cases = True
            continue
        if indent == 0 and stripped and not stripped.startswith("- ") and stripped != "cases:":
            break
        collected.append(line)
    return "\n".join(collected)


def _case_blocks(case_text: str) -> list[str]:
    """Split a cases section into raw case blocks."""
    blocks: list[str] = []
    current: list[str] = []
    for line in case_text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("- id:") and current:
            blocks.append("\n".join(current))
            current = []
        if line.strip():
            current.append(line)
    if current:
        blocks.append("\n".join(current))
    return blocks


def _check_session_pattern_uptake(root: Path) -> Finding:
    report = root / PATTERN_REPORT
    ledger = root / STEERING_LEDGER
    if not report.is_file():
        return Finding("session_pattern_report_missing", "fail", "Session/memory pattern report is required for this ratchet pass.", {"path": str(PATTERN_REPORT)})
    try:
        payload = _json(report)
    except (OSError, ValueError) as exc:
        return Finding("session_pattern_report_unparseable", "fail", "Session/memory pattern report must be JSON.", {"path": str(PATTERN_REPORT), "error": str(exc)})
    patterns = payload.get("patterns")
    ids = {str(item.get("id")) for item in patterns if isinstance(item, dict)} if isinstance(patterns, list) else set()
    missing = sorted(REQUIRED_PATTERN_IDS - ids)
    ledger_text = _read(ledger) if ledger.is_file() else ""
    stale_recorded = "stale" in ledger_text.lower() and "wait" in ledger_text.lower()
    status = "pass" if not missing and stale_recorded else "fail"
    return Finding(
        "session_memory_pattern_uptake",
        status,
        "Recurring session, memory, and session-collector patterns must be recorded before the pipeline moves on.",
        {"path": str(PATTERN_REPORT), "missing_pattern_ids": missing, "stale_wait_recorded": stale_recorded},
    )


def _receipt_checks(root: Path, skill_dir: Path, refs: Path, contract: dict[str, Any] | None, target_gate: str | None) -> list[Finding]:
    """Build receipt-level release ratchet findings."""
    if contract is None:
        return []
    commands = contract.get("commands")
    command_text = "\n".join(str(item) for item in commands) if isinstance(commands, list) else ""
    return [
        Finding(**finding)
        for finding in build_receipt_findings(
            root,
            skill_dir,
            refs,
            sorted(_case_ids_from_refs(refs)),
            command_text,
            target_gate,
        )
    ]


def validate(root: Path, target: str, target_gate: str | None = None) -> dict[str, Any]:
    skill_dir, skill_md, refs = _skill_paths(root, target)
    contract = None
    with suppress(ValueError):
        contract = _structured(refs / "contract.yaml")
    # contract_missing or contract_unparseable will be returned by _check_contract_rubric
    receipt_checks = _receipt_checks(root, skill_dir, refs, contract, target_gate)
    checks = [
        _check_central_rubric(root),
        _check_contract_rubric(root, refs),
        _check_reference_boundary(root, skill_md, refs),
        _check_knowledgeos_reference_shape(root, refs),
        _check_reference_heading_invocation(root, refs),
        _check_tessl_lane_naming(root, skill_dir),
        _check_scenario_parser_parity(root, refs),
        _check_skill_factory_pipeline(root, refs, contract),
        _check_security_lane(root, refs, contract),
        _check_advisory_policy(root, refs),
        _check_session_pattern_uptake(root),
        *receipt_checks,
    ]
    findings = [check.__dict__ for check in checks]
    status = "pass" if all(check.status == "pass" for check in checks) else "fail"
    return {
        "schema_version": "skills-sdk-release-ratchet-validation/v1",
        "status": status,
        "target": target,
        "target_gate": target_gate or REQUIRED_GATE_CHAIN[-1],
        "skill_path": _rel(skill_md, root),
        "checks": findings,
        "finding_count": sum(1 for check in checks if check.status != "pass"),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", help="Repo-relative skill directory or SKILL.md path")
    parser.add_argument("--repo-root", default=str(ROOT), help="Repository root")
    parser.add_argument(
        "--target-gate",
        choices=REQUIRED_GATE_CHAIN,
        help="Validate receipts only through this sequential SDK gate. Defaults to the full release chain.",
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)
    payload = validate(Path(args.repo_root).resolve(), args.target, args.target_gate)
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"status={payload['status']} finding_count={payload['finding_count']}")
    return 0 if payload["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
