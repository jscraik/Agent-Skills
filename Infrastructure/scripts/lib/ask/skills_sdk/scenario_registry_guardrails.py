from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


REGISTRY_REFERENCE_PATTERNS = (
    "registry://",
    "scenario_registry_id",
    "canonical_scenario_id",
    "shared_scenario_ref",
)
ADAPTATION_RECEIPT_SCHEMA_VERSION = "skills-sdk.scenario-adaptation-receipt.v0"
ADAPTATION_RECEIPT_SCHEMA_URI = (
    "https://agent-skills.local/schemas/skills-sdk/scenario-adaptation-receipt.v0.schema.json"
)
ADAPTATION_RECEIPT_DIR = Path("references/scenario-adaptation-receipts")


def no_direct_registry_use_checks(skill_dir: Path, cases: list[Any]) -> list[dict[str, Any]]:
    """Return scenario-quality checks for governed registry scenario usage."""
    return [
        _check(
            "registry_reference_not_in_skill_entrypoint",
            "blocker" if _skill_md_registry_refs(skill_dir) else "pass",
            "SKILL.md must not load or invoke shared scenario registry references directly.",
            _skill_md_registry_refs(skill_dir),
        ),
        _check(
            "registry_reference_requires_sdk_adaptation_receipt",
            "blocker" if _missing_adaptation_receipt_refs(skill_dir, cases) else "pass",
            "Registry-derived scenarios must be SDK-adapted locally with a scenario adaptation receipt before they count as coverage.",
            _missing_adaptation_receipt_refs(skill_dir, cases),
        ),
    ]


def validate_no_direct_registry_scenario_use(skill_dir: Path) -> dict[str, Any]:
    """Validate a skill package without importing the scenario-quality runner."""
    evals_path = skill_dir / "references" / "evals.yaml"
    cases = _load_evals_cases(evals_path)
    checks = no_direct_registry_use_checks(skill_dir, cases)
    blockers = [check for check in checks if check["status"] == "blocker"]
    return {
        "schema_version": "skills-sdk.no-direct-registry-scenario-use.v0",
        "status": "blocked" if blockers else "pass",
        "skill_path": skill_dir.as_posix(),
        "checks": checks,
        "blockers": blockers,
    }


def _check(check_id: str, status: str, message: str, evidence: list[str] | None = None) -> dict[str, Any]:
    return {"id": check_id, "status": status, "severity": "blocker", "message": message, "evidence": evidence or []}


def _skill_md_registry_refs(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    try:
        text = skill_md.read_text(encoding="utf-8")
    except OSError:
        return []
    return [f"SKILL.md:{pattern}" for pattern in REGISTRY_REFERENCE_PATTERNS if pattern in text]


def _missing_adaptation_receipt_refs(skill_dir: Path, cases: list[Any]) -> list[str]:
    missing: list[str] = []
    for index, case in enumerate(cases):
        if not isinstance(case, dict):
            continue
        case_id = _scenario_id(case, index)
        registry_refs = _case_registry_refs(case)
        if not registry_refs:
            continue
        receipt_path = _adaptation_receipt_path(skill_dir, case_id)
        receipt_error = _adaptation_receipt_error(receipt_path, skill_dir, case, case_id)
        if receipt_error:
            missing.append(f"{case_id}:{receipt_error}:{','.join(registry_refs)}")
    return missing


def _case_registry_refs(case: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    _collect_registry_refs(case, refs, path="")
    return refs


def _collect_registry_refs(value: Any, refs: list[str], *, path: str) -> None:
    if isinstance(value, dict):
        for key, nested in value.items():
            key_path = f"{path}.{key}" if path else str(key)
            if str(key) in {"scenario_registry_id", "canonical_scenario_id", "shared_scenario_ref", "registry_source"}:
                refs.append(key_path)
            _collect_registry_refs(nested, refs, path=key_path)
        return
    if isinstance(value, list):
        for index, nested in enumerate(value):
            _collect_registry_refs(nested, refs, path=f"{path}[{index}]")
        return
    if isinstance(value, str):
        for pattern in REGISTRY_REFERENCE_PATTERNS:
            if pattern in value:
                refs.append(f"{path}:{pattern}" if path else pattern)


def _scenario_id(case: dict[str, Any], index: int) -> str:
    raw = case.get("id")
    return raw if isinstance(raw, str) and raw.strip() else f"case-{index}"


def _adaptation_receipt_path(skill_dir: Path, case_id: str) -> Path:
    return skill_dir / ADAPTATION_RECEIPT_DIR / f"{_safe_filename(case_id)}.json"


def _safe_filename(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", value.strip()).strip("-") or "case"


def _adaptation_receipt_error(receipt_path: Path, skill_dir: Path, case: dict[str, Any], case_id: str) -> str | None:
    if not receipt_path.is_file():
        return f"missing_receipt:{_repo_relative(skill_dir, receipt_path)}"
    try:
        receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return f"unreadable_receipt:{type(exc).__name__}"
    if not isinstance(receipt, dict):
        return "receipt_not_object"
    if receipt.get("schema_version") != ADAPTATION_RECEIPT_SCHEMA_VERSION:
        return "schema_version_mismatch"
    if receipt.get("schema_uri") != ADAPTATION_RECEIPT_SCHEMA_URI:
        return "schema_uri_mismatch"
    if receipt.get("status") != "pass":
        return f"receipt_status:{receipt.get('status')}"
    if receipt.get("target_case_id") != case_id:
        return "target_case_id_mismatch"
    target_skill = receipt.get("target_skill")
    if not isinstance(target_skill, dict) or not _target_skill_matches(target_skill, skill_dir):
        return "target_skill_mismatch"
    criteria_ownership = receipt.get("criteria_ownership")
    if not isinstance(criteria_ownership, dict) or criteria_ownership.get("local_criteria_authoritative") is not True:
        return "local_criteria_not_authoritative"
    registry_source = receipt.get("registry_source")
    if not isinstance(registry_source, dict) or not _registry_source_matches_case(registry_source, case):
        return "registry_source_mismatch"
    return None


def _target_skill_matches(target_skill: dict[str, Any], skill_dir: Path) -> bool:
    expected = skill_dir.as_posix()
    candidates = [
        str(target_skill.get("path") or ""),
        str(target_skill.get("package_path") or ""),
    ]
    return expected in candidates or skill_dir.name in candidates


def _registry_source_matches_case(registry_source: dict[str, Any], case: dict[str, Any]) -> bool:
    source_id = str(registry_source.get("canonical_scenario_id") or registry_source.get("id") or "")
    source_version = str(registry_source.get("version") or "")
    case_source = case.get("registry_source")
    if isinstance(case_source, dict):
        case_id = str(case_source.get("canonical_scenario_id") or case_source.get("id") or "")
        case_version = str(case_source.get("version") or "")
        return bool(source_id and source_id == case_id and (not case_version or source_version == case_version))
    for key in ("scenario_registry_id", "canonical_scenario_id", "shared_scenario_ref"):
        value = case.get(key)
        if isinstance(value, str) and value == source_id:
            return True
    return False


def _repo_relative(base: Path, path: Path) -> str:
    try:
        return path.resolve(strict=False).relative_to(base.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def _load_evals_cases(evals_path: Path) -> list[Any]:
    if not evals_path.is_file():
        return []
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError:
        return _load_minimal_cases(evals_path.read_text(encoding="utf-8"))
    loaded = yaml.safe_load(evals_path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        return []
    cases = loaded.get("cases")
    return cases if isinstance(cases, list) else []


def _load_minimal_cases(text: str) -> list[Any]:
    cases: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("- id:"):
            current = {"id": line.split(":", 1)[1].strip().strip("'\"")}
            cases.append(current)
            continue
        if current is not None and ":" in line:
            key, value = line.split(":", 1)
            current[key.strip()] = value.strip().strip("'\"")
    return cases
