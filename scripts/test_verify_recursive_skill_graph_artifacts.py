#!/usr/bin/env python3
"""Regression tests for recursive skill artifact parity verification."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any, Dict, Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
VERIFY_SCRIPT = REPO_ROOT / "scripts" / "verify_recursive_skill_graph_artifacts.py"


def _write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _write_jsonl(path: Path, rows: Iterable[Dict[str, Any]]) -> None:
    path.write_text("".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8")


class VerifyRecursiveSkillGraphArtifactsTests(unittest.TestCase):
    def _run_verifier(
        self,
        runs_root: Path,
        *,
        strict: bool = False,
        run_state_check: bool = True,
        dry_run: bool = False,
        prune_empty: bool = False,
        waiver_file: Path | None = None,
    ) -> tuple[int, dict]:
        manifest_path = runs_root / "artifact-parity-manifest.json"
        cmd = [
            sys.executable,
            str(VERIFY_SCRIPT),
            "--runs-root",
            str(runs_root),
            "--manifest",
            str(manifest_path),
        ]
        if strict:
            cmd.append("--strict")
        if run_state_check:
            cmd.append("--run-state-check")
        if dry_run:
            cmd.append("--dry-run")
        if prune_empty:
            cmd.append("--prune-empty")
        if waiver_file is not None:
            cmd.extend(["--waiver-file", str(waiver_file)])
        proc = subprocess.run(cmd, cwd=REPO_ROOT, text=True, capture_output=True)
        self.assertIn(proc.returncode, {0, 2, 3})
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        return proc.returncode, manifest

    def _create_run(self, runs_root: Path, run_id: str, *, present: Dict[str, Any]) -> Path:
        run_dir = runs_root / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        for name, content in present.items():
            path = run_dir / name
            if content is None:
                path.parent.mkdir(parents=True, exist_ok=True)
                continue
            if isinstance(content, list):
                _write_jsonl(path, content)
            elif isinstance(content, dict):
                _write_json(path, content)
            elif isinstance(content, str):
                path.write_text(content, encoding="utf-8")
            else:
                raise TypeError(f"unsupported content type for {name}")
        return run_dir

    def _run_obj(
        self,
        *,
        run_id: str,
        terminal_status: str = "passed",
        stop_reason: str = "pass",
        auto_capture_enabled: bool = True,
    ) -> Dict[str, Any]:
        return {
            "schema_version": "1.0",
            "run_id": run_id,
            "profile_id": "ui-ux-creative-coding",
            "terminal_status": terminal_status,
            "stop_reason": stop_reason,
            "prompt_hash": f"hash-{run_id}",
            "scope_skill": "ui-ux-creative-coding",
            "scope_profile": "ui",
            "versions": {
                "rubric_version": "1.0",
                "evaluator_version": "test",
            },
            "counters": {"iterations_completed": 1},
            "runtime_controls": {
                "auto_capture_enabled": auto_capture_enabled,
            },
            "finished_at": "2026-02-26T12:00:00Z",
        }

    def _run_entry(self, manifest: dict, run_dir: Path) -> Dict[str, Any]:
        candidates = [
            entry
            for entry in manifest["runs"]
            if entry["run_dir"] == str(run_dir)
            or (run_dir.is_relative_to(REPO_ROOT) and entry["run_dir"] == str(run_dir.relative_to(REPO_ROOT)))
            or entry["run_dir"].endswith(f"/{run_dir.name}")
            or Path(entry["run_dir"]).name == run_dir.name
        ]
        self.assertTrue(candidates, f"run not found in manifest: {run_dir}")
        return candidates[0]

    def test_parity_classification_counts_for_mixed_runs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()

            self._create_run(
                runs_root,
                "run_compliant",
                present={
                    "run.json": self._run_obj(run_id="run_compliant"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_compliant", "iteration_id": 1},
                    ],
                    "events.jsonl": [
                        {
                            "schema_version": "1.0",
                            "event_id": "evt-1",
                            "ts": "2026-02-26T12:00:00Z",
                            "run_id": "run_compliant",
                            "skill_name": "ui-ux-creative-coding",
                            "task_profile": "ui",
                            "event_type": "run_initialized",
                            "severity": "info",
                            "terminal_status": "passed",
                            "stop_reason": "pass",
                        },
                    ],
                    "promotion_decision.json": {
                        "schema_version": "1.1",
                        "run_id": "run_compliant",
                        "lesson_id": "lesson-compliant",
                        "decision": "candidate",
                    },
                    "capture_record.json": {"schema_version": "1.0"},
                    "evidence_packet.json": {"schema_version": "1.0"},
                    "lesson_candidates.json": {"items": []},
                },
            )

            self._create_run(
                runs_root,
                "run_missing_capture",
                present={
                    "run.json": self._run_obj(run_id="run_missing_capture", auto_capture_enabled=True),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_missing_capture", "iteration_id": 1},
                    ],
                    "events.jsonl": [
                        {
                            "schema_version": "1.0",
                            "event_id": "evt-2",
                            "ts": "2026-02-26T12:01:00Z",
                            "run_id": "run_missing_capture",
                            "skill_name": "ui-ux-creative-coding",
                            "task_profile": "ui",
                            "event_type": "run_initialized",
                            "severity": "info",
                            "terminal_status": "passed",
                            "stop_reason": "pass",
                        },
                    ],
                    "promotion_decision.json": {
                        "schema_version": "1.1",
                        "run_id": "run_missing_capture",
                        "lesson_id": "lesson-missing-capture",
                        "decision": "candidate",
                    },
                },
            )

            self._create_run(
                runs_root,
                "run_off_mode_no_capture",
                present={
                    "run.json": self._run_obj(
                        run_id="run_off_mode_no_capture",
                        auto_capture_enabled=False,
                    ),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_off_mode_no_capture", "iteration_id": 1},
                    ],
                    "events.jsonl": [
                        {
                            "schema_version": "1.0",
                            "event_id": "evt-3",
                            "ts": "2026-02-26T12:02:00Z",
                            "run_id": "run_off_mode_no_capture",
                            "skill_name": "ui-ux-creative-coding",
                            "task_profile": "ui",
                            "event_type": "run_initialized",
                            "severity": "info",
                            "terminal_status": "passed",
                            "stop_reason": "pass",
                        },
                    ],
                    "promotion_decision.json": {
                        "schema_version": "1.1",
                        "run_id": "run_off_mode_no_capture",
                        "lesson_id": "lesson-off-mode-no-capture",
                        "decision": "candidate",
                    },
                },
            )

            self._create_run(
                runs_root,
                "run_legacy_partial",
                present={
                    "run.json": self._run_obj(run_id="run_legacy_partial"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_legacy_partial", "iteration_id": 1},
                    ],
                    "promotion_decision.template.json": {"schema_version": "1.0"},
                },
            )

            self._create_run(runs_root, "run_empty", present={})

            code, manifest = self._run_verifier(runs_root, strict=False)
            self.assertEqual(code, 0)
            self.assertEqual(manifest["counts"]["compliant"], 2)
            self.assertEqual(manifest["counts"]["missing_mandatory"], 1)
            self.assertEqual(manifest["counts"]["legacy_partial"], 1)
            self.assertEqual(manifest["counts"]["empty"], 1)

            self.assertEqual(self._run_entry(manifest, runs_root / "run_compliant")["status"], "compliant")
            self.assertEqual(self._run_entry(manifest, runs_root / "run_missing_capture")["status"], "missing_mandatory")
            self.assertEqual(self._run_entry(manifest, runs_root / "run_off_mode_no_capture")["status"], "compliant")
            self.assertEqual(self._run_entry(manifest, runs_root / "run_legacy_partial")["status"], "legacy_partial")
            self.assertEqual(self._run_entry(manifest, runs_root / "run_empty")["status"], "empty")

    def test_strict_mode_fails_on_non_compliance(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            self._create_run(
                runs_root,
                "run_bad",
                present={
                    "run.json": self._run_obj(run_id="run_bad"),
                },
            )
            code, manifest = self._run_verifier(runs_root, strict=True)
            self.assertEqual(code, 3)
            self.assertEqual(manifest.get("status"), "fail")
            self.assertEqual(self._run_entry(manifest, runs_root / "run_bad")["status"], "missing_mandatory")

    def test_events_jsonl_parse_errors_mark_run_as_non_compliant(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            self._create_run(
                runs_root,
                "run_events_bad",
                present={
                    "run.json": self._run_obj(run_id="run_events_bad"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_events_bad", "iteration_id": 1},
                    ],
                    "events.jsonl": '{"event_type":"run_initialized"}\nnot-json\n{"event_type":"run_completed"}\n',
                    "promotion_decision.json": {
                        "schema_version": "1.1",
                        "run_id": "run_events_bad",
                        "lesson_id": "lesson-events-bad",
                        "decision": "candidate",
                    },
                    "capture_record.json": {"schema_version": "1.0"},
                    "evidence_packet.json": {"schema_version": "1.0"},
                    "lesson_candidates.json": {"items": []},
                },
            )

            code, manifest = self._run_verifier(runs_root, strict=True)
            self.assertEqual(code, 3)
            self.assertEqual(manifest.get("status"), "fail")
            entry = self._run_entry(manifest, runs_root / "run_events_bad")
            self.assertEqual(entry["status"], "missing_mandatory")
            self.assertIn("events.jsonl", entry["missing_files"])
            notes = " | ".join(entry["notes"])
            self.assertIn("events.jsonl line 2 invalid JSON", notes)

    def test_legacy_partial_is_non_compliant_in_strict_mode(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            self._create_run(
                runs_root,
                "run_legacy_partial_strict",
                present={
                    "run.json": self._run_obj(run_id="run_legacy_partial_strict"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_legacy_partial_strict", "iteration_id": 1},
                    ],
                    "promotion_decision.template.json": {"schema_version": "1.0"},
                },
            )
            code, manifest = self._run_verifier(runs_root, strict=True)
            self.assertEqual(code, 3)
            self.assertEqual(manifest.get("status"), "fail")
            self.assertEqual(
                self._run_entry(manifest, runs_root / "run_legacy_partial_strict")["status"],
                "legacy_partial",
            )

    def test_strict_mode_allows_explicit_waiver_for_historical_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            waiver_file = Path(tmpdir) / "waivers.json"
            self._create_run(
                runs_root,
                "run_legacy_partial_waived",
                present={
                    "run.json": self._run_obj(run_id="run_legacy_partial_waived"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_legacy_partial_waived", "iteration_id": 1},
                    ],
                    "promotion_decision.template.json": {"schema_version": "1.0"},
                },
            )
            _write_json(
                waiver_file,
                {
                    "schema_version": "1.0",
                    "waived_runs": [
                        {
                            "waiver_id": "hist-001",
                            "run_dir": "run_legacy_partial_waived",
                            "allowed_statuses": ["legacy_partial"],
                            "reason": "Historical seed artifact predates mandatory capture envelope.",
                            "approved_by": "test",
                            "created_at": "2026-03-11T00:00:00Z",
                        }
                    ],
                },
            )

            code, manifest = self._run_verifier(runs_root, strict=True, waiver_file=waiver_file)
            self.assertEqual(code, 0)
            self.assertEqual(manifest.get("status"), "ok")
            entry = self._run_entry(manifest, runs_root / "run_legacy_partial_waived")
            self.assertEqual(entry["status"], "legacy_partial")
            self.assertEqual(entry["waived"], True)
            self.assertEqual(entry["waiver_id"], "hist-001")

    def test_waiver_applies_to_alias_matches_events_jsonl(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            waiver_file = Path(tmpdir) / "waivers.json"
            self._create_run(
                runs_root,
                "run_missing_events_waived",
                present={
                    "run.json": self._run_obj(run_id="run_missing_events_waived"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_missing_events_waived", "iteration_id": 1},
                    ],
                    "promotion_decision.json": {
                        "schema_version": "1.1",
                        "run_id": "run_missing_events_waived",
                        "lesson_id": "lesson-missing-events",
                        "decision": "candidate",
                    },
                    "capture_record.json": {"schema_version": "1.0"},
                    "evidence_packet.json": {"schema_version": "1.0"},
                    "lesson_candidates.json": {"items": []},
                },
            )
            _write_json(
                waiver_file,
                {
                    "schema_version": "1.0",
                    "waived_runs": [
                        {
                            "waiver_id": "evt-001",
                            "run_dir": "run_missing_events_waived",
                            "allowed_statuses": ["missing_mandatory"],
                            "applies_to": ["event_envelope"],
                            "reason": "events envelope missing for historical run",
                            "approved_by": "test",
                            "created_at": "2026-03-11T00:00:00Z",
                        }
                    ],
                },
            )

            code, manifest = self._run_verifier(runs_root, strict=True, waiver_file=waiver_file)
            self.assertEqual(code, 0)
            self.assertEqual(manifest.get("status"), "ok")
            entry = self._run_entry(manifest, runs_root / "run_missing_events_waived")
            self.assertEqual(entry["status"], "missing_mandatory")
            self.assertEqual(entry["waived"], True)
            self.assertEqual(entry["waiver_id"], "evt-001")

    def test_waiver_applies_to_mismatch_does_not_waive(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            waiver_file = Path(tmpdir) / "waivers.json"
            self._create_run(
                runs_root,
                "run_missing_events_not_waived",
                present={
                    "run.json": self._run_obj(run_id="run_missing_events_not_waived"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_missing_events_not_waived", "iteration_id": 1},
                    ],
                    "promotion_decision.json": {
                        "schema_version": "1.1",
                        "run_id": "run_missing_events_not_waived",
                        "lesson_id": "lesson-missing-events-2",
                        "decision": "candidate",
                    },
                    "capture_record.json": {"schema_version": "1.0"},
                    "evidence_packet.json": {"schema_version": "1.0"},
                    "lesson_candidates.json": {"items": []},
                },
            )
            _write_json(
                waiver_file,
                {
                    "schema_version": "1.0",
                    "waived_runs": [
                        {
                            "waiver_id": "evt-002",
                            "run_dir": "run_missing_events_not_waived",
                            "allowed_statuses": ["missing_mandatory"],
                            "applies_to": ["capture_record.json"],
                            "reason": "scope mismatch should not apply",
                            "approved_by": "test",
                            "created_at": "2026-03-11T00:00:00Z",
                        }
                    ],
                },
            )

            code, manifest = self._run_verifier(runs_root, strict=True, waiver_file=waiver_file)
            self.assertEqual(code, 3)
            self.assertEqual(manifest.get("status"), "fail")
            entry = self._run_entry(manifest, runs_root / "run_missing_events_not_waived")
            self.assertEqual(entry["status"], "missing_mandatory")
            self.assertEqual(entry["waived"], False)

    def test_prune_empty_dry_run_does_not_remove_and_records_candidate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            (runs_root / "run_empty").mkdir()

            code, manifest = self._run_verifier(runs_root, dry_run=True, prune_empty=True)
            self.assertEqual(code, 0)
            self.assertEqual(self._run_entry(manifest, runs_root / "run_empty")["status"], "empty")
            self.assertEqual(manifest["prune_empty"]["enabled"], True)
            self.assertEqual(manifest["prune_empty"]["dry_run"], True)
            self.assertIn(
                next(key for key in manifest["prune_empty"]["actions"] if key.endswith("/run_empty")),
                manifest["prune_empty"]["actions"],
            )
            action_key = next(key for key in manifest["prune_empty"]["actions"] if key.endswith("/run_empty"))
            self.assertEqual(manifest["prune_empty"]["actions"][action_key], "candidate")

            self.assertTrue((runs_root / "run_empty").exists())

    def test_prune_empty_removes_directory_when_not_dry_run(self) -> None:
        with tempfile.TemporaryDirectory(prefix="artifact-parity-") as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            (runs_root / "run_empty").mkdir()

            _, manifest = self._run_verifier(runs_root, prune_empty=True)
            self.assertTrue(
                any(
                    (key.endswith("/run_empty") or key == "run_empty")
                    and value == "removed"
                    for key, value in manifest["prune_empty"]["actions"].items()
                )
            )
            self.assertFalse((runs_root / "run_empty").exists())

    def test_manifest_uses_repo_relative_paths_when_runs_root_is_in_repo(self) -> None:
        artifacts_root = REPO_ROOT / "artifacts"
        artifacts_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="artifact-parity-in-repo-", dir=artifacts_root) as tmpdir:
            runs_root = Path(tmpdir) / "runs"
            runs_root.mkdir()
            run_dir = self._create_run(
                runs_root,
                "run_under_repo",
                present={
                    "run.json": self._run_obj(run_id="run_under_repo"),
                    "iteration_journal.jsonl": [
                        {"run_id": "run_under_repo", "iteration_id": 1},
                    ],
                    "events.jsonl": [
                        {
                            "schema_version": "1.0",
                            "event_id": "evt-1",
                            "ts": "2026-02-26T12:00:00Z",
                            "run_id": "run_under_repo",
                            "skill_name": "ui-ux-creative-coding",
                            "task_profile": "ui",
                            "event_type": "run_initialized",
                            "severity": "info",
                            "terminal_status": "passed",
                            "stop_reason": "pass",
                        },
                    ],
                    "promotion_decision.json": {
                        "schema_version": "1.1",
                        "run_id": "run_under_repo",
                        "lesson_id": "lesson-under-repo",
                        "decision": "candidate",
                    },
                    "capture_record.json": {"schema_version": "1.0"},
                    "evidence_packet.json": {"schema_version": "1.0"},
                    "lesson_candidates.json": {"items": []},
                },
            )
            code, manifest = self._run_verifier(runs_root, strict=False)
            self.assertEqual(code, 0)
            self.assertEqual(manifest["runs_root"], str(runs_root.relative_to(REPO_ROOT)))
            self.assertNotIn(str(Path.home()), manifest["runs_root"])
            self.assertEqual(
                self._run_entry(manifest, run_dir)["run_dir"],
                str(run_dir.relative_to(REPO_ROOT)),
            )


if __name__ == "__main__":
    unittest.main()
