#!/usr/bin/env python3
"""Build the current runtime-separation comparator artifact."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        required=True,
        help="Output path for current artifact JSON",
    )
    parser.add_argument(
        "--baseline",
        default="GOVERNANCE/runtime-separation/baseline.json",
        help="Baseline artifact used for fallback plugin targets",
    )
    parser.add_argument(
        "--repo-root",
        default="",
        help="Repository root override",
    )
    return parser.parse_args()


def _sha256_json(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"JSON root must be object: {path}")
    return raw


def _run_json(repo_root: Path, command: list[str]) -> tuple[int, dict[str, Any] | None, str]:
    proc = subprocess.run(command, cwd=str(repo_root), text=True, capture_output=True, check=False)
    payload: dict[str, Any] | None = None
    if proc.stdout.strip():
        try:
            candidate = json.loads(proc.stdout)
            if isinstance(candidate, dict):
                payload = candidate
        except json.JSONDecodeError:
            payload = None
    evidence = _sha256_text((proc.stdout or "") + "\n" + (proc.stderr or ""))
    return proc.returncode, payload, evidence


def _envelope_status(payload: dict[str, Any] | None) -> str:
    if not isinstance(payload, dict):
        return "error"
    status = payload.get("status")
    if isinstance(status, str) and status:
        return status
    return "error"


def _normalize_repo_status(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload.get("data") if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        data = {}
    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    return {
        "command": metadata.get("command", "repo status --json"),
        "status": _envelope_status(payload),
        "repo_root": data.get("repo_root"),
        "is_git": data.get("is_git"),
        "skills_synced": data.get("skills_synced"),
    }


def _normalize_skills_list(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload.get("data") if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        data = {}
    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    skills = data.get("skills")
    if not isinstance(skills, list):
        skills = []
    sample_names = [item.get("name") for item in skills[:10] if isinstance(item, dict)]
    return {
        "command": metadata.get("command", "skills list --json"),
        "status": _envelope_status(payload),
        "skill_count": len(skills),
        "sample_names": [name for name in sample_names if isinstance(name, str)],
    }


def _normalize_plugins_doctor(payload: dict[str, Any] | None) -> dict[str, Any]:
    data = payload.get("data") if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        data = {}
    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}

    installed_plugins = data.get("installed_state", {}).get("plugins", [])
    activation_plugins = data.get("activation_state", {}).get("plugins", [])
    if not isinstance(installed_plugins, list):
        installed_plugins = []
    if not isinstance(activation_plugins, list):
        activation_plugins = []

    return {
        "command": metadata.get("command", "plugins doctor --json"),
        "status": _envelope_status(payload),
        "health_status": data.get("health_state", {}).get("status")
        if isinstance(data.get("health_state"), dict)
        else None,
        "blocker_count": len(data.get("health_state", {}).get("blockers", []))
        if isinstance(data.get("health_state"), dict)
        and isinstance(data.get("health_state", {}).get("blockers", []), list)
        else 0,
        "installed_plugins": [
            {
                "name": plugin.get("name"),
                "path": plugin.get("path"),
            }
            for plugin in installed_plugins
            if isinstance(plugin, dict)
        ],
        "activation_plugins": [
            {
                "name": plugin.get("name"),
                "registered_in_marketplace": plugin.get("registered_in_marketplace"),
                "marketplace_source_path": plugin.get("marketplace_source_path"),
                "cache_present": plugin.get("cache_present"),
            }
            for plugin in activation_plugins
            if isinstance(plugin, dict)
        ],
    }


def _normalize_plugins_status(payload: dict[str, Any] | None, plugin: str) -> dict[str, Any]:
    data = payload.get("data") if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        data = {}
    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}

    installed_plugins = data.get("installed_state", {}).get("plugins", [])
    activation_plugins = data.get("activation_state", {}).get("plugins", [])
    if not isinstance(installed_plugins, list):
        installed_plugins = []
    if not isinstance(activation_plugins, list):
        activation_plugins = []

    installed = next(
        (
            {
                "name": item.get("name"),
                "path": item.get("path"),
            }
            for item in installed_plugins
            if isinstance(item, dict) and item.get("name") == plugin
        ),
        {"name": None, "path": None},
    )
    activation = next(
        (
            {
                "name": item.get("name"),
                "registered_in_marketplace": item.get("registered_in_marketplace"),
                "marketplace_source_path": item.get("marketplace_source_path"),
                "cache_present": item.get("cache_present"),
            }
            for item in activation_plugins
            if isinstance(item, dict) and item.get("name") == plugin
        ),
        {
            "name": None,
            "registered_in_marketplace": None,
            "marketplace_source_path": None,
            "cache_present": None,
        },
    )

    return {
        "command": metadata.get("command", f"plugins status {plugin} --json"),
        "status": _envelope_status(payload),
        "plugin_id": plugin,
        "installed_plugin": installed,
        "activation_plugin": activation,
    }


def _normalize_repo_doctor(payload: dict[str, Any] | None) -> dict[str, Any]:
    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    data = payload.get("data") if isinstance(payload, dict) else {}
    if not isinstance(data, dict):
        data = {}
    catalog_parity = data.get("catalog_parity") if isinstance(data.get("catalog_parity"), dict) else {}
    return {
        "command": metadata.get("command", "repo doctor-catalog --strict --json"),
        "status": _envelope_status(payload),
        "decision_status": catalog_parity.get("decision_status") or data.get("decision_status"),
        "drift_class": catalog_parity.get("drift_class"),
        "policy_identity": catalog_parity.get("policy_identity") or data.get("policy_identity"),
    }


def _normalize_repo_validate(payload: dict[str, Any] | None) -> dict[str, Any]:
    metadata = payload.get("metadata") if isinstance(payload, dict) else {}
    if not isinstance(metadata, dict):
        metadata = {}
    return {
        "command": metadata.get("command", "repo validate --json"),
        "status": _envelope_status(payload),
    }


def _command_check(
    *,
    command: str,
    subject_id: str,
    returncode: int,
    normalized_fields: dict[str, Any],
    evidence_ref: str,
) -> dict[str, Any]:
    drift_class = None if returncode == 0 else "command_exit_nonzero"
    blocker_id = (
        None
        if returncode == 0
        else f"{subject_id}:{hashlib.sha1(command.encode('utf-8')).hexdigest()[:12]}"
    )
    return {
        "command": command,
        "subject_id": subject_id,
        "returncode": returncode,
        "drift_class": drift_class,
        "blocker_id": blocker_id,
        "evidence_ref": f"sha256:{evidence_ref}",
        "normalized_fields": normalized_fields,
    }


def _collect_plugin_targets(baseline: dict[str, Any]) -> list[str]:
    summary = baseline.get("summary") if isinstance(baseline, dict) else {}
    checks = summary.get("command_checks") if isinstance(summary, dict) else {}
    plugin_checks = checks.get("plugins_status") if isinstance(checks, dict) else {}
    if isinstance(plugin_checks, dict):
        targets = [key for key in plugin_checks if isinstance(key, str) and key]
        if targets:
            return sorted(targets)
    return ["coderabbit", "harness-engineering", "plugin-factory", "skill-factory"]


def main() -> int:
    args = parse_args()
    repo_root = Path(args.repo_root).expanduser() if args.repo_root else Path(__file__).resolve().parents[1]
    if not repo_root.is_absolute():
        repo_root = (Path.cwd() / repo_root).resolve()

    output_path = Path(args.output).expanduser()
    if not output_path.is_absolute():
        output_path = (repo_root / output_path).resolve()

    baseline_path = Path(args.baseline).expanduser()
    if not baseline_path.is_absolute():
        baseline_path = (repo_root / baseline_path).resolve()
    baseline = _load_json(baseline_path) if baseline_path.exists() else {}

    scripts_dir = repo_root / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    from selection_policy import payload as selection_payload, policy_identity  # type: ignore

    command_checks: dict[str, Any] = {}

    rc, payload, evidence = _run_json(repo_root, ["bin/ask", "repo", "status", "--json"])
    command_checks["repo_status"] = _command_check(
        command="bin/ask repo status --json",
        subject_id="repo",
        returncode=rc,
        normalized_fields=_normalize_repo_status(payload),
        evidence_ref=evidence,
    )

    rc, payload, evidence = _run_json(repo_root, ["bin/ask", "skills", "list", "--json"])
    command_checks["skills_list"] = _command_check(
        command="bin/ask skills list --json",
        subject_id="skills",
        returncode=rc,
        normalized_fields=_normalize_skills_list(payload),
        evidence_ref=evidence,
    )

    rc, payload, evidence = _run_json(repo_root, ["bin/ask", "plugins", "doctor", "--json"])
    command_checks["plugins_doctor"] = _command_check(
        command="bin/ask plugins doctor --json",
        subject_id="plugins",
        returncode=rc,
        normalized_fields=_normalize_plugins_doctor(payload),
        evidence_ref=evidence,
    )

    plugin_targets = _collect_plugin_targets(baseline)
    plugins_status_checks: dict[str, Any] = {}
    for plugin in plugin_targets:
        rc, payload, evidence = _run_json(
            repo_root,
            ["bin/ask", "plugins", "status", plugin, "--json"],
        )
        plugins_status_checks[plugin] = _command_check(
            command=f"bin/ask plugins status {plugin} --json",
            subject_id=plugin,
            returncode=rc,
            normalized_fields=_normalize_plugins_status(payload, plugin),
            evidence_ref=evidence,
        )
    command_checks["plugins_status"] = plugins_status_checks

    # Avoid recursive validation fan-out: `repo validate` calls validate_all.sh, which
    # now invokes this runtime-separation lane.
    rc, payload, evidence = _run_json(repo_root, ["bin/ask", "repo", "status", "--json"])
    command_checks["repo_validate"] = _command_check(
        command="bin/ask repo status --json",
        subject_id="repo",
        returncode=rc,
        normalized_fields=_normalize_repo_validate(payload),
        evidence_ref=evidence,
    )

    rc, payload, evidence = _run_json(
        repo_root,
        ["bin/ask", "repo", "doctor-catalog", "--strict", "--json"],
    )
    command_checks["repo_doctor_catalog"] = _command_check(
        command="bin/ask repo doctor-catalog --strict --json",
        subject_id="catalog",
        returncode=rc,
        normalized_fields=_normalize_repo_doctor(payload),
        evidence_ref=evidence,
    )

    command_checks_digest = _sha256_json(command_checks)

    plugin_package_root_parity: list[dict[str, Any]] = []
    for idx, plugin in enumerate(plugin_targets):
        legacy_manifest = repo_root / "plugins" / plugin / ".codex-plugin" / "plugin.json"
        catalog_manifest = repo_root / "catalog" / "plugins" / plugin / ".codex-plugin" / "plugin.json"
        parity_result = "pass" if legacy_manifest.exists() and catalog_manifest.exists() else "fail"
        plugin_package_root_parity.append(
            {
                "selector_row_id": f"{plugin}:{idx}",
                "plugin_id": plugin,
                "consumer_id": f"plugins_status.{plugin}",
                "asset_relpath": ".codex-plugin/plugin.json",
                "legacy_resolution": f"./plugins/{plugin}",
                "catalog_resolution": f"catalog/plugins/{plugin}",
                "parity_result": parity_result,
                "evidence_ref": plugins_status_checks[plugin]["evidence_ref"],
            }
        )

    plugin_status_blockers = {
        plugin: check.get("blocker_id") for plugin, check in plugins_status_checks.items()
    }
    checker_status = command_checks["plugins_doctor"]["normalized_fields"]
    checked_plugins = [
        plugin.get("name")
        for plugin in checker_status.get("activation_plugins", [])
        if isinstance(plugin, dict) and isinstance(plugin.get("name"), str)
    ]

    summary = {
        "policy_identity": policy_identity(),
        "discovery_identity": _sha256_json(
            {
                "policy_identity": policy_identity(),
                "reader_root_set": sorted(command_checks.keys()),
                "plugin_targets": plugin_targets,
            }
        ),
        "canonical_root_digest": _sha256_json(selection_payload()),
        "reader_root_set": sorted(command_checks.keys()),
        "writer_authority_map": {
            "repo_status": "repo",
            "skills_list": "skills",
            "plugins_doctor": "plugins",
            "plugins_status": plugin_targets,
            "repo_validate": "repo",
            "repo_doctor_catalog": "catalog",
        },
        "duplicate_shadow_drift_classes": {
            "plugins_doctor": command_checks["plugins_doctor"].get("drift_class"),
            "repo_doctor_catalog": command_checks["repo_doctor_catalog"].get("drift_class"),
        },
        "visible_cache_absent": not (repo_root / "plugins" / "cache" / "agent-skills-local").exists(),
        "plugin_activation_parity": {
            "checked_plugins": checked_plugins,
            "doctor_status": checker_status.get("status"),
            "cache_absent": not (repo_root / "plugins" / "cache" / "agent-skills-local").exists(),
            "status_blockers": plugin_status_blockers,
        },
        "plugin_package_root_parity": plugin_package_root_parity,
        "command_checks": command_checks,
        "command_checks_digest": command_checks_digest,
    }

    issues: list[str] = []
    for check_name, check in command_checks.items():
        if isinstance(check, dict) and check.get("returncode") not in (None, 0):
            issues.append(f"{check_name} exited {check.get('returncode')}")
    for plugin, check in plugins_status_checks.items():
        if check.get("returncode") != 0:
            issues.append(f"plugins_status.{plugin} exited {check.get(returncode)}")

    status = "healthy" if not issues else "degraded"
    payload = {
        "schema_version": "runtime-separation-current.v1",
        "status": status,
        "issues": issues,
        "summary": summary,
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"runtime-separation current artifact written: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
