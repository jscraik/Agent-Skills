#!/usr/bin/env python3
"""Receipt-level checks for Skills SDK release ratchets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


FACTORY_GATE_REQUIRED_FIELDS = {
    "user_outcome",
    "copied_assumption",
    "smallest_effective_mechanism",
    "artifact_decision",
    "proof_needed",
}
FACTORY_GATE_DECISIONS = {
    "BUILD",
    "BUILD_SKILL",
    "BUILD_PLUGIN",
    "IMPROVE_EXISTING",
    "DOCS_ONLY",
    "DO_NOT_BUILD",
}
REQUIRED_GATE_CHAIN = (
    "sdk_start",
    "strict_audit",
    "package_verify",
    "security_risk_modes",
    "scenario_quality",
    "scorer_quality",
    "scorer_calibration",
    "oss_local",
    "oss_cloud",
    "tessl_local_proof",
    "tessl_dry_run",
    "handoff_readiness",
)
SECURITY_RISK_KEYS = (
    "prompt_injection",
    "unsafe_command_escalation",
    "secret_redaction",
    "external_url_trust",
    "local_path_leakage",
    "permission_profile",
    "mcp_tool_side_effects",
)
PLUGIN_SHAPE_REQUIRED = (
    ".tessl-plugin/plugin.json",
    "tessl.json",
    "README.md",
    "skills",
    "references",
)


def build_receipt_findings(
    root: Path,
    skill_dir: Path,
    refs: Path,
    expected_case_ids: list[str],
    contract_command_text: str,
    target_gate: str | None = None,
) -> list[dict[str, Any]]:
    """Return release receipt findings for the candidate package."""
    evidence_dir = root / ".harness" / "evidence" / "handoff" / skill_dir.name
    factory_gate = root / ".harness" / "evidence" / "factory-gates" / skill_dir.name / "factory-gate.json"
    checks = [
        _check_factory_gate(root, factory_gate),
        _check_reference_routing(root, skill_dir / "SKILL.md", refs),
        _check_no_carried_advisories(root, evidence_dir, target_gate),
        _check_gate_chain(root, evidence_dir, target_gate),
    ]
    if _gate_reached("package_verify", target_gate):
        checks.append(_check_plugin_shape(root, evidence_dir))
    if _gate_reached("security_risk_modes", target_gate):
        checks.append(_check_security(root, evidence_dir, contract_command_text))
    if _gate_reached("scenario_quality", target_gate):
        checks.append(_check_scenario_set(root, evidence_dir, refs, expected_case_ids))
    if _gate_reached("oss_local", target_gate):
        checks.append(_check_repair_loop(root, evidence_dir))
    return checks


def _required_gate_chain(target_gate: str | None = None) -> tuple[str, ...]:
    if target_gate is None:
        return REQUIRED_GATE_CHAIN
    if target_gate not in REQUIRED_GATE_CHAIN:
        raise ValueError(f"unknown target gate: {target_gate}")
    return REQUIRED_GATE_CHAIN[: REQUIRED_GATE_CHAIN.index(target_gate) + 1]


def _gate_reached(gate_id: str, target_gate: str | None) -> bool:
    return gate_id in _required_gate_chain(target_gate)


def _finding(code: str, status: str, message: str, evidence: dict[str, Any]) -> dict[str, Any]:
    return {"code": code, "status": status, "message": message, "evidence": evidence}


def _rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _load_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    if not path.is_file():
        return None, "missing"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not isinstance(payload, dict):
        return None, "json_root_not_object"
    return payload, None


def _blank(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"", "todo", "tbd", "unknown", "n/a"}
    if isinstance(value, list):
        return not value
    return False


def _json_path_list(payload: dict[str, Any], *keys: str) -> list[str]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, list):
            return [str(item) for item in value if str(item)]
    return []


def _json_refs(payload: Any, key_names: set[str], path: str = "") -> list[str]:
    refs: list[str] = []
    if isinstance(payload, dict):
        for key, value in payload.items():
            child_path = f"{path}.{key}" if path else key
            if key in key_names and isinstance(value, list) and value:
                refs.append(child_path)
            refs.extend(_json_refs(value, key_names, child_path))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            refs.extend(_json_refs(item, key_names, f"{path}[{index}]"))
    return refs


def _has_carried_advisories(payload: dict[str, Any]) -> list[str]:
    accepted = payload.get("accepted_exceptions")
    accepted_paths: set[str] = set()
    if isinstance(accepted, list):
        accepted_paths = {str(item["path"]) for item in accepted if isinstance(item, dict) and isinstance(item.get("path"), str)}
    return [path for path in _json_refs(payload, {"advisories", "warnings"}) if path not in accepted_paths]


def _release_ratchet_exception_paths(evidence_dir: Path, check: str) -> set[str]:
    payload, _error = _load_json(evidence_dir / "release-ratchet-exceptions.json")
    if payload is None:
        return set()
    entries = payload.get("accepted_exceptions")
    if not isinstance(entries, list):
        return set()
    paths: set[str] = set()
    for entry in entries:
        if (
            isinstance(entry, dict)
            and entry.get("check") == check
            and isinstance(entry.get("path"), str)
            and entry["path"].strip()
        ):
            paths.add(entry["path"].strip())
    return paths


def _check_factory_gate(root: Path, path: Path) -> dict[str, Any]:
    payload, error = _load_json(path)
    if payload is None:
        return _finding("factory_gate_receipt", "fail", "Factory work must record a factory-gate/v1 receipt.", {"path": _rel(path, root), "error": error})
    missing = sorted(field for field in FACTORY_GATE_REQUIRED_FIELDS if _blank(payload.get(field)))
    decision = str(payload.get("artifact_decision", "")).strip()
    invalid_decision = bool(decision and decision not in FACTORY_GATE_DECISIONS)
    return _finding(
        "factory_gate_receipt",
        "pass" if not missing and not invalid_decision else "fail",
        "Factory decisions must prove outcome, rejected assumption, mechanism, decision, and proof.",
        {"path": _rel(path, root), "missing": missing, "artifact_decision": decision, "invalid_decision": invalid_decision},
    )


def _check_reference_routing(root: Path, skill_md: Path, refs: Path) -> dict[str, Any]:
    skill_text = skill_md.read_text(encoding="utf-8") if skill_md.is_file() else ""
    route_text = _routing_text(refs)
    unrouted = [_rel(path, root) for path in sorted(refs.rglob("*.md")) if _unrouted_reference(path, skill_md.parent, skill_text, route_text)]
    return _finding(
        "reference_routing_completeness",
        "pass" if not unrouted else "fail",
        "Every Markdown reference must be discoverable through entrypoint, contract, capsule routing, task profile, or evals.",
        {"unrouted_references": unrouted[:20]},
    )


def _routing_text(refs: Path) -> str:
    routed = (refs / "contract.yaml", refs / "knowledge-capsule-routing.md", refs / "evals.yaml", refs / "task-profile.json")
    return "\n".join(path.read_text(encoding="utf-8") for path in routed if path.is_file())


def _unrouted_reference(path: Path, skill_dir: Path, skill_text: str, route_text: str) -> bool:
    if "/examples/" in path.as_posix():
        return False
    rel = _rel(path, skill_dir)
    name = path.name
    return rel not in skill_text and rel not in route_text and name not in skill_text and name not in route_text


def _check_scenario_set(root: Path, evidence_dir: Path, refs: Path, expected: list[str]) -> dict[str, Any]:
    path = evidence_dir / "scenario-sources.json"
    payload, error = _load_json(path)
    if payload is None:
        return _finding("scenario_set_parity", "fail", "OSS and Tessl lanes must use the same explained scenario set.", {"path": _rel(path, root), "error": error, "expected_count": len(expected)})
    mismatches = _scenario_receipt_mismatches(payload, expected)
    exclusions = payload.get("exclusions")
    unexplained = [item for item in exclusions if isinstance(item, dict) and _blank(item.get("reason"))] if isinstance(exclusions, list) else []
    source_ids = sorted(_json_path_list(payload, "scenario_ids", "case_ids"))
    status = "pass" if source_ids == expected and not mismatches and not unexplained else "fail"
    return _finding("scenario_set_parity", status, "Scenario IDs must stay aligned across canonical evals, staged sources, OSS, and Tessl.", {"path": _rel(path, root), "expected_ids": expected, "source_ids": source_ids, "receipt_mismatches": mismatches[:20], "unexplained_exclusions": unexplained[:20]})


def _scenario_receipt_mismatches(payload: dict[str, Any], expected: list[str]) -> list[dict[str, Any]]:
    receipts = payload.get("receipts")
    if not isinstance(receipts, list):
        return []
    return [
        {"lane": str(receipt.get("lane") or "unknown"), "scenario_ids": sorted(_json_path_list(receipt, "scenario_ids", "case_ids"))}
        for receipt in receipts
        if isinstance(receipt, dict) and sorted(_json_path_list(receipt, "scenario_ids", "case_ids")) != expected
    ]


def _check_security(root: Path, evidence_dir: Path, contract_command_text: str) -> dict[str, Any]:
    path = evidence_dir / "security-risk-modes.json"
    payload, error = _load_json(path)
    if payload is None:
        return _finding("security_package_gate", "fail", "Security risk-mode preview receipt is required before OSS/Tessl movement.", {"path": _rel(path, root), "error": error, "contract_mentions_security": "sdk security risk-modes" in contract_command_text})
    risk_modes = payload.get("risk_modes")
    missing = sorted(set(SECURITY_RISK_KEYS) - (set(risk_modes) if isinstance(risk_modes, dict) else set()))
    flags = _security_flags(payload, missing)
    return _finding("security_package_gate", "pass" if all(flags.values()) else "fail", "Security proof must cover prompt injection, risky commands, secrets, URLs, paths, permissions, and side effects.", {"path": _rel(path, root), **flags, "missing_modes": missing, "carried_advisories": _has_carried_advisories(payload)[:20]})


def _security_flags(payload: dict[str, Any], missing: list[str]) -> dict[str, bool]:
    return {
        "status_ok": str(payload.get("status", "")).lower() in {"pass", "success"},
        "preview_ok": payload.get("preview") is True or "--preview" in str(payload.get("command", "")),
        "modes_ok": not missing,
        "advisories_ok": not _has_carried_advisories(payload),
    }


def _check_plugin_shape(root: Path, evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "plugin-shape.json"
    payload, error = _load_json(path)
    if payload is None:
        return _finding("plugin_shape_parity", "fail", "OpenAI/Codex and Tessl plugin shape parity must be recorded.", {"path": _rel(path, root), "error": error})
    missing = _missing_plugin_shape(payload)
    flags = _plugin_flags(payload)
    return _finding("plugin_shape_parity", "pass" if all(flags.values()) and not missing else "fail", "Package movement must preserve OpenAI/Codex and Tessl private plugin boundaries.", {"path": _rel(path, root), "missing": missing, **flags})


def _missing_plugin_shape(payload: dict[str, Any]) -> list[str]:
    if str(payload.get("target_kind") or "") == "standalone_skill":
        return []
    files = set(_json_path_list(payload, "files", "staged_files"))
    return sorted(item for item in PLUGIN_SHAPE_REQUIRED if not any(path == item or path.startswith(item + "/") for path in files))


def _plugin_flags(payload: dict[str, Any]) -> dict[str, bool]:
    target_kind = str(payload.get("target_kind") or "")
    return {
        "openai_ok": payload.get("openai_skill_shape") in {"pass", True},
        "tessl_ok": payload.get("tessl_plugin_shape") in {"pass", True, "not_applicable"},
        "private_ok": payload.get("private") is True or target_kind == "standalone_skill",
        "workspace_ok": payload.get("workspace") in {"jscraik", None},
    }


RECEIPT_STEM_GATES = {
    "security-risk-modes": "security_risk_modes",
    "scenario-sources": "scenario_quality",
    "repair-loop": "oss_local",
}


def _check_no_carried_advisories(root: Path, evidence_dir: Path, target_gate: str | None = None) -> dict[str, Any]:
    carried = []
    ignored = []
    accepted = _release_ratchet_exception_paths(evidence_dir, "no_carried_advisories")
    required_gates = set(_required_gate_chain(target_gate))
    for path in sorted(evidence_dir.glob("*.json")) if evidence_dir.is_dir() else []:
        # Skip receipts for gates beyond the target gate
        if target_gate is not None:
            gate_id = RECEIPT_STEM_GATES.get(path.stem, path.stem)
            if gate_id in REQUIRED_GATE_CHAIN and gate_id not in required_gates:
                continue
        payload, error = _load_json(path)
        if payload is None:
            item = f"{_rel(path, root)}:{error}"
            if item in accepted:
                ignored.append(item)
            else:
                carried.append(item)
            continue
        for advisory_path in _has_carried_advisories(payload):
            item = f"{_rel(path, root)}:{advisory_path}"
            if item in accepted:
                ignored.append(item)
            else:
                carried.append(item)
    return _finding(
        "no_carried_advisories",
        "pass" if not carried else "fail",
        "Promotion gates must repair advisories or record accepted exceptions.",
        {"handoff_dir": _rel(evidence_dir, root), "carried": carried[:20], "ignored_legacy": ignored[:20]},
    )


def _check_gate_chain(root: Path, evidence_dir: Path, target_gate: str | None = None) -> dict[str, Any]:
    path = evidence_dir / "gate-chain.json"
    payload, error = _load_json(path)
    if payload is None:
        return _finding("ordered_gate_chain", "fail", "Release movement requires a current ordered gate-chain receipt.", {"path": _rel(path, root), "error": error})
    gates = payload.get("gates")
    if not isinstance(gates, list):
        return _finding("ordered_gate_chain", "fail", "Gate-chain receipt must contain a gates list.", {"path": _rel(path, root)})
    required = _required_gate_chain(target_gate)
    evidence = _gate_chain_evidence(root, evidence_dir, gates, required, target_gate)
    status = "pass" if all(not evidence[key] for key in ("missing_gates", "bad_status", "missing_receipts", "missing_claim_boundaries", "carried_advisories")) and evidence["order_ok"] else "fail"
    return _finding("ordered_gate_chain", status, "Gate receipts must exist, pass in order, and carry claim-boundary evidence.", {"path": _rel(path, root), **evidence})


def _gate_chain_evidence(root: Path, evidence_dir: Path, gates: list[Any], required: tuple[str, ...], target_gate: str | None) -> dict[str, Any]:
    gate_ids = [str(gate.get("id")) for gate in gates if isinstance(gate, dict)]
    required_gate_set = set(required)
    scoped_gates = [
        gate
        for gate in gates
        if isinstance(gate, dict) and str(gate.get("id")) in required_gate_set
    ]
    receipt_errors = [_gate_receipt_error(root, evidence_dir, gate) for gate in scoped_gates]
    return {
        "target_gate": target_gate or REQUIRED_GATE_CHAIN[-1],
        "required_gate_count": len(required),
        "missing_gates": _missing_required_gates(gate_ids, required),
        "extra_future_gates": _extra_future_gates(gate_ids, required),
        "order_ok": [gate for gate in gate_ids if gate in required_gate_set] == list(required),
        "bad_status": _bad_gate_statuses(scoped_gates),
        "missing_receipts": _missing_gate_receipts(receipt_errors),
        "missing_claim_boundaries": _missing_claim_boundaries(scoped_gates),
        "carried_advisories": _gate_carried_advisories(receipt_errors),
    }


def _missing_required_gates(gate_ids: list[str], required: tuple[str, ...]) -> list[str]:
    return [gate for gate in required if gate not in gate_ids]


def _extra_future_gates(gate_ids: list[str], required: tuple[str, ...]) -> list[str]:
    return [gate for gate in gate_ids if gate in REQUIRED_GATE_CHAIN and gate not in required]


def _bad_gate_statuses(gates: list[Any]) -> list[str]:
    return [str(gate.get("id")) for gate in gates if isinstance(gate, dict) and gate.get("status") != "pass"]


def _missing_gate_receipts(receipt_errors: list[dict[str, Any]]) -> list[str]:
    return [item["gate_id"] for item in receipt_errors if item["missing_receipt"]]


def _missing_claim_boundaries(gates: list[Any]) -> list[str]:
    missing: list[str] = []
    for gate in gates:
        if isinstance(gate, dict) and (_blank(gate.get("what_this_proves")) or _blank(gate.get("what_this_does_not_prove"))):
            missing.append(str(gate.get("id")))
    return missing


def _gate_carried_advisories(receipt_errors: list[dict[str, Any]]) -> list[str]:
    return [item for error in receipt_errors for item in error["carried_advisories"]][:20]


def _gate_receipt_error(root: Path, _evidence_dir: Path, gate: dict[str, Any]) -> dict[str, Any]:
    gate_id = str(gate.get("id"))
    receipt_path = _receipt_path(root, gate.get("receipt_path"))
    payload = _load_json(receipt_path)[0] if receipt_path is not None and receipt_path.is_file() else None
    carried = [f"{gate_id}:{item}" for item in _has_carried_advisories(payload)] if payload else []
    return {"gate_id": gate_id, "missing_receipt": receipt_path is None or not receipt_path.is_file(), "carried_advisories": carried}


def _receipt_path(root: Path, value: Any) -> Path | None:
    if not isinstance(value, str) or not value.strip():
        return None
    path = Path(value)
    if path.is_absolute():
        candidate = path
    else:
        candidate = root / path
    try:
        resolved = candidate.resolve()
        resolved.relative_to(root.resolve())
    except (OSError, ValueError):
        return None
    return candidate


def _check_repair_loop(root: Path, evidence_dir: Path) -> dict[str, Any]:
    path = evidence_dir / "repair-loop.json"
    payload, error = _load_json(path)
    if payload is None:
        return _finding("repair_loop_monotonicity", "fail", "Repair loops must record fixed, regressed, unchanged, and classified cases.", {"path": _rel(path, root), "error": error})
    regressions = _unclassified_regressions(payload)
    return _finding("repair_loop_monotonicity", "pass" if not regressions else "fail", "Repair loops must classify regressions before later gate movement.", {"path": _rel(path, root), "unclassified_regressions": regressions[:20]})


def _unclassified_regressions(payload: dict[str, Any]) -> list[dict[str, Any]]:
    attempts = payload.get("attempts")
    if not isinstance(attempts, list):
        return []
    regressions: list[dict[str, Any]] = []
    for attempt in attempts:
        cases = attempt.get("regressed_cases") if isinstance(attempt, dict) else None
        if not isinstance(cases, list):
            continue
        regressions.extend(
            {"attempt": attempt.get("id"), "case": case}
            for case in cases
            if not isinstance(case, dict) or _blank(case.get("classification"))
        )
    return regressions
