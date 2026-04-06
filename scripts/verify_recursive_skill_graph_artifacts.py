#!/usr/bin/env python3
"""Verify recursive skill-graph run artifacts and classify parity compliance."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

RUNNER = "artifacts/skill-graphs/runs"

REQUIRED_BASE_FILES: Set[str] = {
    "run.json",
    "iteration_journal.jsonl",
    "events.jsonl",
    "promotion_decision.json",
}
REQUIRED_CAPTURE_FILES: Set[str] = {
    "capture_record.json",
    "evidence_packet.json",
    "lesson_candidates.json",
}
REQUIRED_OPTIONAL_BLOCKER_FILES: Dict[str, Set[str]] = {
    "run_rollforward_blocked": {"run_blocker.json", "rollback_recommendation.json"},
    "run_rollback_required": {"run_blocker.json", "rollback_recommendation.json"},
    "kill_switch_activated": {"run_blocker.json", "rollback_recommendation.json"},
    "evaluator_conflict": {"run_blocker.json"},
}
DEFAULT_MANIFEST = "artifacts/skill-graphs/pilot/artifact-parity-manifest.json"
DEFAULT_WAIVER_FILE = "artifacts/skill-graphs/pilot/artifact-parity-waivers.json"

LEGACY_RUN_FILE_SETS = {
    frozenset({"run.json", "iteration_journal.jsonl"}),
    frozenset({"run.json", "iteration_journal.jsonl", "promotion_decision.template.json"}),
    frozenset({"run.json", "promotion_decision.template.json"}),
    frozenset({"run.json", "events.jsonl"}),
}

PARSER_STATUSES = {"passed", "failed", "escalated", "aborted"}
STOP_REASONS = {"pass", "budget_exhausted", "escalated", "aborted", "policy_failed", "evaluator_conflict", "dependency_missing"}


@dataclass
class ArtifactStatus:
    status: str
    terminal_status: Optional[str]
    stop_reason: Optional[str]
    blocker_code: Optional[str]
    event_blocker_codes: Set[str]
    auto_capture_enabled: Optional[bool]
    required: List[str]
    missing: List[str]
    present: List[str]
    notes: List[str]
    run_dir: Path
    promotion_state: Optional[str]

    @property
    def run_dir_relative(self) -> str:
        try:
            return str(self.run_dir.relative_to(Path.cwd()))
        except ValueError:
            return str(self.run_dir)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Verify recursive skill-graph artifact parity")
    p.add_argument(
        "--runs-root",
        default="artifacts/skill-graphs/runs",
        help="Root directory containing run_* artifacts",
    )
    p.add_argument(
        "--run-dir",
        action="append",
        default=[],
        help="Optional explicit run directory path(s); if set, ignore --runs-root scan",
    )
    p.add_argument(
        "--manifest",
        default=DEFAULT_MANIFEST,
        help="Output manifest JSON path",
    )
    p.add_argument(
        "--waiver-file",
        default=DEFAULT_WAIVER_FILE,
        help="Optional JSON file listing explicit waivers for historical non-compliant runs",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned parity actions without deleting any directories",
    )
    p.add_argument(
        "--prune-empty",
        action="store_true",
        help="Remove empty run directories identified during scan",
    )
    p.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any run is non-compliant",
    )
    p.add_argument(
        "--exit-on-parse-error",
        action="store_true",
        help="Treat manifest emission as failed when JSON manifests cannot be parsed",
    )
    p.add_argument(
        "--run-state-check",
        action="store_true",
        help="Emit per-run control-state check summary in manifest",
    )
    p.add_argument(
        "--quiet",
        action="store_true",
        help="Only output summary counts, not full run details",
    )
    return p.parse_args()


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(obj, dict):
        return obj
    return None


def safe_bool(value: Any, default: bool = True) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _collect_event_blockers(rows: List[Dict[str, Any]]) -> Set[str]:
    blockers: Set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            continue
        if str(row.get("event_type", "")).strip().lower() == "run_blocked":
            code = str(row.get("blocker_code", "")).strip()
            if code:
                blockers.add(code)
    return blockers


def load_events(path: Path) -> Tuple[List[Dict[str, Any]], List[str]]:
    if not path.exists():
        return [], []
    rows: List[Dict[str, Any]] = []
    errors: List[str] = []
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except Exception as exc:
            errors.append(f"events.jsonl line {line_no} invalid JSON: {exc}")
            continue
        if isinstance(row, dict):
            rows.append(row)
        else:
            errors.append(f"events.jsonl line {line_no} must be an object")
    return rows, errors


def is_empty_run_dir(run_dir: Path) -> bool:
    return not any(run_dir.iterdir()) if run_dir.exists() else False


def read_promotion_state(run_dir: Path) -> Optional[str]:
    decision = load_json(run_dir / "promotion_decision.json")
    if not decision:
        return None
    state = str(decision.get("decision", "")).strip().lower()
    return state or None


def classify_run_dir(run_dir: Path) -> ArtifactStatus:
    artifact_files = {p.name for p in run_dir.glob("*") if p.is_file()}

    if not artifact_files:
        return ArtifactStatus(
            status="empty",
            terminal_status=None,
            stop_reason=None,
            blocker_code=None,
            event_blocker_codes=set(),
            auto_capture_enabled=None,
            required=sorted(REQUIRED_BASE_FILES),
            missing=sorted(REQUIRED_BASE_FILES),
            present=[],
            notes=["run directory has no files"],
            run_dir=run_dir,
            promotion_state=None,
        )

    run_obj = load_json(run_dir / "run.json")
    if not run_obj:
        if artifact_files in LEGACY_RUN_FILE_SETS:
            missing = sorted(REQUIRED_BASE_FILES - artifact_files)
            return ArtifactStatus(
                status="legacy_partial",
                terminal_status=None,
                stop_reason=None,
                blocker_code=None,
                event_blocker_codes=set(),
                auto_capture_enabled=None,
                required=sorted(REQUIRED_BASE_FILES),
                missing=missing,
                present=sorted(artifact_files),
                notes=["run.json is missing or unreadable; historical partial layout"],
                run_dir=run_dir,
                promotion_state=read_promotion_state(run_dir),
            )

        missing = sorted(REQUIRED_BASE_FILES - artifact_files)
        return ArtifactStatus(
            status="missing_mandatory",
            terminal_status=None,
            stop_reason=None,
            blocker_code=None,
            event_blocker_codes=set(),
            auto_capture_enabled=None,
            required=sorted(REQUIRED_BASE_FILES),
            missing=missing,
            present=sorted(artifact_files),
            notes=["run.json is missing or unreadable"],
            run_dir=run_dir,
            promotion_state=read_promotion_state(run_dir),
        )

    terminal_status = str(run_obj.get("terminal_status", "")).strip() or None
    if terminal_status and terminal_status not in PARSER_STATUSES:
        terminal_status = str(run_obj.get("terminal_status")).strip() or None
    stop_reason = str(run_obj.get("stop_reason", "")).strip() or None
    if stop_reason and stop_reason not in STOP_REASONS:
        stop_reason = str(run_obj.get("stop_reason", "")).strip() or None

    control_obj = run_obj.get("runtime_controls")
    if not isinstance(control_obj, dict):
        control_obj = {}
    auto_capture_enabled = safe_bool(control_obj.get("auto_capture_enabled"), default=True)

    events_rows, event_parse_errors = load_events(run_dir / "events.jsonl")
    event_blocker_codes = _collect_event_blockers(events_rows)

    blocker_obj = run_obj.get("run_blocker")
    blocker_code = None
    if isinstance(blocker_obj, dict):
        candidate = str(blocker_obj.get("code", "")).strip()
        blocker_code = candidate or None

    required = set(REQUIRED_BASE_FILES)
    if not auto_capture_enabled:
        required = set(REQUIRED_BASE_FILES)
    else:
        required.update(REQUIRED_CAPTURE_FILES)

    if blocker_code:
        required.update(REQUIRED_OPTIONAL_BLOCKER_FILES.get(blocker_code, set()))

    notes: List[str] = []
    notes.extend([f"terminal_status={terminal_status}"] if terminal_status else [])
    notes.extend([f"stop_reason={stop_reason}"] if stop_reason else [])
    if blocker_code:
        notes.append(f"blocker_code={blocker_code}")

    # legacy signature check for incomplete historical layouts
    if artifact_files in LEGACY_RUN_FILE_SETS:
        status = "legacy_partial"
    else:
        status = "compliant"

    missing = sorted(required - artifact_files)

    # Terminal state control semantics (blocked runs expect blocker artifacts)
    if terminal_status == "failed" and stop_reason in {"policy_failed", "dependency_missing"} and not blocker_code:
        required.add("run_blocker.json")
        missing = sorted(required - artifact_files)

    if event_parse_errors:
        notes.extend(event_parse_errors)
        status = "missing_mandatory"
        if "events.jsonl" not in missing:
            missing.append("events.jsonl")

    if status != "legacy_partial" and not missing:
        # Additional event consistency checks when the event stream exists.
        if not (run_dir / "events.jsonl").exists():
            missing = sorted(REQUIRED_BASE_FILES - artifact_files)
            status = "missing_mandatory"
        if terminal_status == "failed" and stop_reason == "dependency_missing" and "run_rollback_required" not in event_blocker_codes and not blocker_code:
            notes.append("terminal_state dependency_missing requires run_blocked event blocker_code=run_rollback_required")
            missing.append("run_blocker.json")
        if terminal_status == "escalated" and stop_reason == "evaluator_conflict" and "evaluator_conflict" not in event_blocker_codes:
            notes.append("terminal_state escalated/evaluator_conflict should emit run_blocked/evaluator_conflict")

    if missing:
        if status == "compliant":
            status = "missing_mandatory"
    return ArtifactStatus(
        status=status,
        terminal_status=terminal_status,
        stop_reason=stop_reason,
        blocker_code=blocker_code,
        event_blocker_codes=event_blocker_codes,
        auto_capture_enabled=auto_capture_enabled,
        required=sorted(required),
        missing=sorted(set(missing)),
        present=sorted(artifact_files),
        notes=notes,
        run_dir=run_dir,
        promotion_state=read_promotion_state(run_dir),
    )


def scan_run_dirs(explicit: Sequence[str], runs_root: str) -> List[Path]:
    if explicit:
        return [Path(item).resolve() for item in explicit]
    root = Path(runs_root).resolve()
    if not root.exists():
        return []
    return sorted(p for p in root.glob("run_*") if p.is_dir())


def summarize_audits(audits: Sequence[ArtifactStatus]) -> Dict[str, Any]:
    counts: Dict[str, int] = {
        "compliant": 0,
        "missing_mandatory": 0,
        "legacy_partial": 0,
        "empty": 0,
    }
    for audit in audits:
        counts[audit.status] = counts.get(audit.status, 0) + 1
    return {
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "runs_root": str((Path(audits[0].run_dir).parent.relative_to(Path.cwd())) if audits else Path("artifacts/skill-graphs/runs")),
        "counts": counts,
        "total_runs": len(audits),
        "run_status_counts": counts,
        "compliance_rate": round((counts["compliant"] / len(audits)) * 100.0, 3) if audits else 0.0,
    }


def load_waivers(path: Path) -> Dict[str, Dict[str, Any]]:
    payload = load_json(path)
    if not payload:
        return {}
    rows = payload.get("waived_runs")
    if not isinstance(rows, list):
        return {}

    waivers: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        if not isinstance(row, dict):
            continue
        run_dir = str(row.get("run_dir", "")).strip()
        if not run_dir:
            continue
        waivers[run_dir] = row
    return waivers


def resolve_waiver(audit: ArtifactStatus, waivers: Dict[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    candidates = [audit.run_dir_relative, str(audit.run_dir), audit.run_dir.name]
    for key in candidates:
        waiver = waivers.get(key)
        if not waiver:
            continue
        allowed = waiver.get("allowed_statuses")
        if isinstance(allowed, list) and allowed:
            allowed_values = {str(item).strip() for item in allowed}
            if audit.status not in allowed_values:
                continue
        return waiver
    return None


def make_manifest(
    audits: Sequence[ArtifactStatus],
    run_state_check: bool,
    waivers: Dict[str, Dict[str, Any]],
) -> Dict[str, Any]:
    summary = summarize_audits(audits)
    summary["waived_non_compliant"] = 0
    runs_payload: List[Dict[str, Any]] = []
    for audit in audits:
        waiver = resolve_waiver(audit, waivers)
        waived = audit.status != "compliant" and waiver is not None
        if waived:
            summary["waived_non_compliant"] += 1
        entry: Dict[str, Any] = {
            "run_dir": audit.run_dir_relative,
            "status": audit.status,
            "waived": waived,
            "required_files": audit.required,
            "missing_files": audit.missing,
            "present_files": audit.present,
            "promotion_state": audit.promotion_state,
            "auto_capture_enabled": audit.auto_capture_enabled,
            "terminal_status": audit.terminal_status,
            "stop_reason": audit.stop_reason,
            "blocker_code": audit.blocker_code,
            "notes": audit.notes,
        }
        if waived:
            entry["waiver_reason"] = waiver.get("reason")
            entry["waiver_id"] = waiver.get("waiver_id")
            entry["waiver_approved_by"] = waiver.get("approved_by")
            entry["waiver_created_at"] = waiver.get("created_at")
        if run_state_check:
            entry["event_blocker_codes"] = sorted(audit.event_blocker_codes)
        runs_payload.append(entry)
    summary["runs"] = runs_payload
    return summary


def _manifest_without_generated_at(payload: Dict[str, Any]) -> Dict[str, Any]:
    snapshot = dict(payload)
    snapshot.pop("generated_at", None)
    return snapshot


def _stabilize_generated_at(manifest: Dict[str, Any], manifest_path: Path) -> Dict[str, Any]:
    """Keep generated_at stable when no substantive manifest fields changed."""
    if not manifest_path.exists():
        return manifest
    try:
        existing = json.loads(manifest_path.read_text(encoding="utf-8"))
    except Exception:
        return manifest
    if _manifest_without_generated_at(existing) == _manifest_without_generated_at(manifest):
        previous_generated_at = existing.get("generated_at")
        if isinstance(previous_generated_at, str) and previous_generated_at:
            manifest["generated_at"] = previous_generated_at
    return manifest


def run_prune_empty(audits: Sequence[ArtifactStatus], dry_run: bool) -> Dict[str, Any]:
    removals: Dict[str, Any] = {}
    for audit in audits:
        if audit.status != "empty":
            continue
        if is_empty_run_dir(audit.run_dir):
            removals[audit.run_dir_relative] = "candidate"
            if not dry_run:
                try:
                    audit.run_dir.rmdir()
                    removals[audit.run_dir_relative] = "removed"
                except Exception:
                    removals[audit.run_dir_relative] = "failed"
    return removals


def main() -> int:
    args = parse_args()
    run_dirs = scan_run_dirs(args.run_dir, args.runs_root)
    waivers = load_waivers(Path(args.waiver_file))

    audits = [classify_run_dir(run_dir) for run_dir in run_dirs]
    removals = run_prune_empty(audits, dry_run=args.dry_run) if args.prune_empty else {}

    manifest_path = Path(args.manifest)
    if removals:
        for audit in audits:
            state = removals.get(audit.run_dir_relative)
            if state:
                audit.notes.append(f"prune_empty={state}")

    manifest = make_manifest(audits, run_state_check=args.run_state_check, waivers=waivers)
    manifest["prune_empty"] = {
        "enabled": bool(args.prune_empty),
        "dry_run": bool(args.dry_run),
        "actions": removals,
    }
    manifest["waiver_file"] = args.waiver_file if waivers else None

    if args.strict:
        # In strict mode, waived non-compliant runs are acceptable
        def _is_strict_compliant(audit: ArtifactStatus) -> bool:
            if audit.status == "compliant":
                return True
            return resolve_waiver(audit, waivers) is not None

        manifest["status"] = (
            "ok"
            if all(_is_strict_compliant(audit) for audit in audits)
            else "fail"
        )
    else:
        # Derive status from actual compliance counts
        compliant_count = counts.get("compliant", 0)
        total = len(audits)
        manifest["status"] = "ok" if (total > 0 and compliant_count == total) else "non_compliant"

    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = _stabilize_generated_at(manifest, manifest_path)
    rendered_manifest = json.dumps(manifest, indent=2) + "\n"
    try:
        if manifest_path.exists():
            existing_text = manifest_path.read_text(encoding="utf-8")
            if existing_text == rendered_manifest:
                if args.quiet:
                    output = {k: v for k, v in manifest.items() if k != "runs"}
                    print(json.dumps(output, indent=2))
                else:
                    print(json.dumps(manifest, indent=2))
                if args.strict and any(
                    audit.status != "compliant" and resolve_waiver(audit, waivers) is None
                    for audit in audits
                ):
                    return 3
                return 0
        manifest_path.write_text(rendered_manifest, encoding="utf-8")
    except Exception as exc:
        if args.exit_on_parse_error:
            print(f"failed to write manifest: {exc}", file=sys.stderr)
            return 2
        raise

    if args.strict:
        non_compliant = [
            audit for audit in audits
            if audit.status != "compliant" and resolve_waiver(audit, waivers) is None
        ]
        if non_compliant:
            if args.quiet:
                print(json.dumps({k: v for k, v in manifest.items() if k != "runs"}, indent=2))
            else:
                print(
                    json.dumps(
                        make_manifest(audits, run_state_check=args.run_state_check, waivers=waivers),
                        indent=2,
                    )
                )
            return 3

    if args.quiet:
        # Only output summary, not full run details
        output = {k: v for k, v in manifest.items() if k != "runs"}
        print(json.dumps(output, indent=2))
    else:
        print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
