#!/usr/bin/env python3
"""Skill Genome Loop - nightly draft PR candidate generator.

Architecture:
  - Single script (~200 LOC max)
  - Sequential function calls (no stage abstraction)
  - Append-only JSONL output

Usage:
  python3 scripts/run_skill_genome_loop.py [--runs-root PATH] [--dry-run]

P1 FIXES:
  - Kill-switch check at startup (abort if kill-switch.txt exists)
  - Rollout mode check at startup (off/observe_only/active)
  - Fail-closed redaction (candidates with redaction_passed=False are filtered)
  - Comprehensive SECRET_PATTERNS from validate_recursive_promotion.py + JWTs + IPs
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Set

# Configuration
CANDIDATES_PATH = Path("artifacts/skill-graphs/telemetry/candidates.jsonl")
RUNS_ROOT = Path("artifacts/skill-graphs/runs")
CONTROLS_ROOT = Path("artifacts/skill-graphs/controls")
STATS_PATH = Path("artifacts/skill-graphs/telemetry/skill-genome-processing-stats.json")
WATERMARK_PATH = Path("artifacts/skill-graphs/telemetry/.genome-watermark")

MIN_CONFIDENCE = 0.82
MIN_WINDOWS = 2
MAX_CANDIDATES = 10
SCHEMA_VERSION = "1.0"

# Control file paths
KILL_SWITCH_PATH = CONTROLS_ROOT / "kill-switch.txt"
ROLLBACK_REQUIRED_PATH = CONTROLS_ROOT / "rollback-required.txt"
ROLLOUT_MODE_PATH = CONTROLS_ROOT / "rollout-mode.txt"

# Allowlist fields for candidate emission (privacy-first)
ALLOWLIST_FIELDS: Set[str] = {
    "schema_version",
    "skill_path",
    "proposed_change_type",
    "composite_score",
    "window_id",
    "decision_reason",
    "candidate_id",
    "window_count",
    "redaction_passed",
    "created_at",
}

# Comprehensive secret patterns (P1 FIX: expanded from validate_recursive_promotion.py:62-69)
SECRET_PATTERNS: List[re.Pattern] = [
    re.compile(r"sk-[A-Za-z0-9]{20,}"),  # OpenAI keys
    re.compile(r"ghp_[A-Za-z0-9]{30,}"),  # GitHub PATs
    re.compile(r"xox[baprs]-[A-Za-z0-9-]{20,}"),  # Slack tokens
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),  # SSH keys
    re.compile(r"(?i)aws_access_key_id\s*[:=]\s*[A-Z0-9]{16,}"),  # AWS keys
    re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{8,}"
    ),  # Generic secrets
    re.compile(r"eyJ[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*\.[A-Za-z0-9_-]*"),  # JWTs (P1 FIX)
    re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"),  # IP addresses (P1 FIX)
]

PII_PATTERNS: List[re.Pattern] = [
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # Email
    re.compile(r"/Users/[^/]+|/home/[^/]+"),  # Home paths
    re.compile(r"[A-Z]{2}\d{6}"),  # Passport numbers (simplified)
]

# Required artifact files for valid runs
# MVP: Only require run.json minimum (other artifacts optional)
REQUIRED_RUN_FILES: Set[str] = {"run.json"}


def log(message: str) -> None:
    """Structured logging for audit trail."""
    timestamp = datetime.now(timezone.utc).isoformat()
    print(f"[{timestamp}] {message}")


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    p = argparse.ArgumentParser(description="Skill Genome Loop - draft PR candidate generator")
    p.add_argument(
        "--runs-root",
        default=str(RUNS_ROOT),
        help="Root directory containing run_* artifacts",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Run in dry-run mode (no writes)",
    )
    p.add_argument(
        "--force-mode",
        choices=["off", "observe_only", "active"],
        help="Override rollout mode from control file",
    )
    return p.parse_args()


# --- Control file helpers (P1 FIX: explicit control checks) ---


def read_rollout_mode(path: Path, default: str = "observe_only") -> str:
    """Read rollout mode from control file with validation."""
    if not path.exists():
        return default
    mode = path.read_text(encoding="utf-8").strip().lower()
    valid_modes = {"off", "observe_only", "active"}
    return mode if mode in valid_modes else default


def is_kill_switch_activated(path: Path) -> bool:
    """Check if kill-switch control file content indicates active state.

    P1 FIX: Parse file content with fail-closed semantics.
    - Empty/blank files are treated as ACTIVE (fail-closed for    - Only falsy values explicitly deactivate
    - This matches operator behavior (touch .../kill-switch.txt)
    and existing parser in recursive_skill_loop.py.
    """
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8").strip().lower()
    # P1 FIX: Empty/unknown content is treated as ACTIVE (fail-closed)
    # Only explicit falsy values deactivate
    return content not in {"off", "false", "0", "no", "inactive"}


def is_rollback_required(path: Path) -> bool:
    """Check if rollback-required control file content indicates active state.

    P1 FIX: Parse file content with fail-closed semantics.
    - Empty/blank files are treated as ACTIVE (fail-closed)
    - Only falsy values explicitly deactivate
    - This matches the documented control posture and existing parser behavior.
    """
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8").strip().lower()
    # P1 FIX: Empty/unknown content is treated as ACTIVE (fail-closed)
    # Only explicit falsy values deactivate
    return content not in {"off", "false", "0", "no", "inactive"}


# --- Artifact loading ---


def load_json(path: Path) -> Optional[Dict[str, Any]]:
    """Load JSON file with graceful error handling."""
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    if isinstance(obj, dict):
        return obj
    return None


def discover_runs(runs_root: Path, since_watermark: Optional[str] = None) -> List[Path]:
    """Discover all run directories with required artifacts.

    P1 FIX: Filter runs by watermark to avoid reprocessing historical artifacts.
    Only returns runs with started_at timestamp after the watermark.
    """
    runs = []
    if not runs_root.exists():
        return runs

    for run_dir in sorted(runs_root.iterdir()):
        if not run_dir.is_dir() or not run_dir.name.startswith("run_"):
            continue

        # Check required files exist
        missing = [f for f in REQUIRED_RUN_FILES if not (run_dir / f).exists()]
        if missing:
            continue

        # P1 FIX: Filter by watermark if provided
        if since_watermark:
            run_json = load_json(run_dir / "run.json") or {}
            started_at = run_json.get("started_at", "")
            if started_at and started_at <= since_watermark:
                continue

        runs.append(run_dir)

    return runs


def read_watermark() -> Optional[str]:
    """Read last processed timestamp watermark."""
    if not WATERMARK_PATH.exists():
        return None
    return WATERMARK_PATH.read_text(encoding="utf-8").strip() or None


def write_watermark(timestamp: str) -> None:
    """Write processing watermark."""
    WATERMARK_PATH.parent.mkdir(parents=True, exist_ok=True)
    WATERMARK_PATH.write_text(timestamp, encoding="utf-8")


def load_run_artifacts(run_dir: Path) -> Dict[str, Any]:
    """Load all artifacts for a single run."""
    run_json = load_json(run_dir / "run.json") or {}
    events = []

    events_path = run_dir / "events.jsonl"
    if events_path.exists():
        for line in events_path.read_text(encoding="utf-8").splitlines():
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    promotion = load_json(run_dir / "promotion_decision.json") or {}

    return {
        "run_dir": run_dir,
        "run": run_json,
        "events": events,
        "promotion": promotion,
    }


# --- Signal computation ---


def compute_routing_confusion(artifacts: List[Dict[str, Any]]) -> Dict[str, float]:
    """Compute routing confusion score per skill path.

    Higher score = more routing issues detected.
    """
    skill_counts: Dict[str, Dict[str, int]] = {}

    for artifact in artifacts:
        run = artifact.get("run", {})
        skill_path = run.get("scope_skill", "unknown")
        terminal = run.get("terminal_status", "")
        stop_reason = run.get("stop_reason", "")

        if skill_path not in skill_counts:
            skill_counts[skill_path] = {"total": 0, "issues": 0}

        skill_counts[skill_path]["total"] += 1

        # Count as issue if failed or had policy issues
        if terminal == "failed" or stop_reason in {"policy_failed", "evaluator_conflict"}:
            skill_counts[skill_path]["issues"] += 1

    # Convert to confusion scores
    confusion: Dict[str, float] = {}
    for skill, counts in skill_counts.items():
        if counts["total"] > 0:
            confusion[skill] = counts["issues"] / counts["total"]

    return confusion


def compute_composite_score(
    confusion_score: float,
    artifact: Dict[str, Any],
) -> float:
    """Compute composite confidence score for a candidate.

    Simplified from existing multi-factor model in recursive_skill_loop.py:292-356.
    """
    run = artifact.get("run", {})

    # Base: routing confusion (weight: 0.40)
    confusion_signal = confusion_score

    # Terminal status signal (weight: 0.30)
    terminal_signal = 1.0 if run.get("terminal_status") == "passed" else 0.5

    # Evidence completeness (weight: 0.30)
    events = artifact.get("events", [])
    evidence_signal = min(1.0, len(events) / 10.0) if events else 0.0

    # Weighted composite
    score = (
        confusion_signal * 0.40
        + terminal_signal * 0.30
        + evidence_signal * 0.30
    )

    return round(score, 3)


def current_window() -> str:
    """Get current week window ID (YYYY-WNN format)."""
    now = datetime.now(timezone.utc)
    iso_cal = now.isocalendar()
    return f"{iso_cal[0]}-W{iso_cal[1]:02d}"


def get_window_count(skill_path: str, artifacts: List[Dict[str, Any]]) -> int:
    """Count unique windows where this skill had activity."""
    windows: Set[str] = set()

    for artifact in artifacts:
        run = artifact.get("run", {})
        if run.get("scope_skill") == skill_path:
            created = run.get("started_at", "")
            if created:
                try:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    iso_cal = dt.isocalendar()
                    windows.add(f"{iso_cal[0]}-W{iso_cal[1]:02d}")
                except ValueError:
                    continue

    return len(windows)


# --- Candidate generation ---


def generate_candidate_id(skill_path: str, window_id: str, change_type: str) -> str:
    """Generate deterministic candidate ID for deduplication."""
    key = f"{skill_path}|{window_id}|{change_type}"
    return hashlib.sha256(key.encode()).hexdigest()[:16]


def build_candidates(
    signals: Dict[str, float],
    artifacts: List[Dict[str, Any]],
    all_artifacts: Optional[List[Dict[str, Any]]] = None,
) -> List[Dict[str, Any]]:
    """Build candidate change proposals with deterministic IDs.

    P1 FIX: all_artifacts provides historical context for window_count,
    ensuring the MIN_WINDOWS >= 2 gate works correctly with incremental processing.
    """
    candidates = []
    window_id = current_window()
    # P1 FIX: Use all_artifacts for window_count if provided
    window_count_artifacts = all_artifacts if all_artifacts is not None else artifacts

    for skill_path, confusion_score in signals.items():
        # Only consider skills with meaningful confusion
        if confusion_score < 0.2:
            continue

        # Find representative artifact for this skill
        skill_artifacts = [
            a for a in artifacts
            if a.get("run", {}).get("scope_skill") == skill_path
        ]
        if not skill_artifacts:
            continue

        representative = skill_artifacts[0]
        composite_score = compute_composite_score(confusion_score, representative)
        # P1 FIX: Use all_artifacts for window_count (historical context)
        window_count = get_window_count(skill_path, window_count_artifacts)

        # Determine change type based on signals
        change_type = "trigger_rule_review"
        decision_reason = f"Routing confusion detected ({confusion_score:.1%})"

        candidate_id = generate_candidate_id(skill_path, window_id, change_type)

        candidates.append({
            "schema_version": SCHEMA_VERSION,
            "skill_path": skill_path,
            "proposed_change_type": change_type,
            "composite_score": composite_score,
            "window_id": window_id,
            "decision_reason": decision_reason,
            "candidate_id": candidate_id,
            "window_count": window_count,
            "created_at": datetime.now(timezone.utc).isoformat(),
        })

    return candidates


def is_high_confidence(candidate: Dict[str, Any]) -> bool:
    """Single composite gate check for MVP."""
    return (
        candidate.get("composite_score", 0) >= MIN_CONFIDENCE
        and candidate.get("window_count", 0) >= MIN_WINDOWS
    )


# --- Redaction (P1 FIX: fail-closed) ---


def verify_no_pii(data: Any) -> bool:
    """Fail-closed PII verification - return False if any pattern matches."""
    if isinstance(data, str):
        for pattern in SECRET_PATTERNS + PII_PATTERNS:
            if pattern.search(data):
                return False
    elif isinstance(data, dict):
        return all(verify_no_pii(v) for v in data.values())
    elif isinstance(data, list):
        return all(verify_no_pii(item) for item in data)
    return True


def redact_candidate(candidate: Dict[str, Any]) -> Dict[str, Any]:
    """Apply allowlist filtering and verify no PII."""
    filtered = {k: v for k, v in candidate.items() if k in ALLOWLIST_FIELDS}
    filtered["redaction_passed"] = verify_no_pii(filtered)
    return filtered


# --- Atomic writes ---


@contextmanager
def atomic_write(path: Path) -> Iterator[Path]:
    """Write file atomically via temp file + rename."""
    temp_path = path.with_suffix(path.suffix + ".tmp")
    try:
        yield temp_path
        temp_path.rename(path)  # Atomic on POSIX
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise


def write_processing_stats(
    candidates_raw: int,
    candidates_high_conf: int,
    candidates_emitted: int,
    emitted: int = 0,
    runs_processed: int = 0,  # P2 FIX: Actually track runs
) -> None:
    """Write processing stats for observability."""
    stats = {
        "window_id": current_window(),
        "processing_timestamp": datetime.now(timezone.utc).isoformat(),
        "runs_processed": runs_processed,  # P2 FIX: Now tracked properly
        "candidates_raw": candidates_raw,
        "candidates_high_confidence": candidates_high_conf,
        "candidates_emitted": candidates_emitted,
        "candidates_written": emitted,
    }

    STATS_PATH.parent.mkdir(parents=True, exist_ok=True)

    with atomic_write(STATS_PATH) as temp_path:
        temp_path.write_text(json.dumps(stats, indent=2), encoding="utf-8")


def append_candidates(candidates: List[Dict[str, Any]]) -> int:
    """Append candidates to JSONL file atomically with deduplication.

    P1 FIX: Deduplicate by candidate_id before appending to prevent
    duplicate records when rerunning on the same artifact set.
    """
    if not candidates:
        return 0

    CANDIDATES_PATH.parent.mkdir(parents=True, exist_ok=True)

    # P1 FIX: Read existing candidate IDs for deduplication
    existing_ids: Set[str] = set()
    if CANDIDATES_PATH.exists():
        for line in CANDIDATES_PATH.read_text(encoding="utf-8").splitlines():
            try:
                existing = json.loads(line)
                existing_ids.add(existing.get("candidate_id", ""))
            except json.JSONDecodeError:
                continue

    # Filter out duplicates
    new_candidates = [
        c for c in candidates
        if c.get("candidate_id") not in existing_ids
    ]

    if not new_candidates:
        return 0

    with open(CANDIDATES_PATH, "a", encoding="utf-8") as f:
        for c in new_candidates:
            f.write(json.dumps(c, sort_keys=True) + "\n")

    return len(new_candidates)


# --- Main entry point ---


def main() -> int:
    """Main entry point for skill genome loop."""
    args = parse_args()
    runs_root = Path(args.runs_root)

    # P1 FIX: Check kill-switch FIRST
    if is_kill_switch_activated(KILL_SWITCH_PATH):
        log("Kill-switch activated; aborting candidate generation")
        return 1

    # P2 FIX: Check rollback-required (control hierarchy: rollback > rollout)
    if is_rollback_required(ROLLBACK_REQUIRED_PATH):
        log("Rollback required; blocking candidate emission")
        return 1

    # P1 FIX: Check rollout mode
    rollout_mode = (
        args.force_mode
        if args.force_mode
        else read_rollout_mode(ROLLOUT_MODE_PATH, default="observe_only")
    )

    if rollout_mode == "off":
        log("Rollout mode is off; skipping candidate generation")
        return 0

    log(f"Starting skill genome loop (mode={rollout_mode})")

    # P1 FIX: Read watermark for incremental processing
    watermark = read_watermark()
    if watermark:
        log(f"Processing runs since watermark: {watermark}")

    # Load artifacts
    runs = discover_runs(runs_root, since_watermark=watermark)
    log(f"Discovered {len(runs)} valid runs")

    artifacts = [load_run_artifacts(r) for r in runs]

    # P1 FIX: Load ALL artifacts for window_count (historical context)
    # This ensures the MIN_WINDOWS >= 2 gate works correctly with incremental processing
    all_runs = discover_runs(runs_root, since_watermark=None)  # No filter
    all_artifacts = [load_run_artifacts(r) for r in all_runs]
    log(f"Loaded {len(all_artifacts)} total artifacts for window_count computation")

    # Compute signals
    signals = compute_routing_confusion(artifacts)
    log(f"Computed routing confusion for {len(signals)} skills")

    # Build candidates
    # P1 FIX: Pass all_artifacts for window_count (historical context)
    candidates = build_candidates(signals, artifacts, all_artifacts=all_artifacts)
    log(f"Generated {len(candidates)} raw candidates")

    # Apply confidence gate
    high_conf = [c for c in candidates if is_high_confidence(c)]
    log(f"High-confidence candidates: {len(high_conf)}")

    # Apply redaction (P1 FIX: fail-closed)
    redacted = [redact_candidate(c) for c in high_conf]
    passed_redaction = [c for c in redacted if c.get("redaction_passed") is True]
    capped = passed_redaction[:MAX_CANDIDATES]

    log(f"Candidates passing redaction: {len(passed_redaction)}, capped: {len(capped)}")

    # Handle modes
    # P2 FIX: Check dry_run FIRST to prevent any writes in dry-run mode
    if args.dry_run:
        log(f"DRY_RUN: Would write {len(capped)} candidates (no stats written)")
        return 0

    if rollout_mode == "observe_only":
        log(f"OBSERVE_ONLY: Would emit {len(capped)} candidates")
        write_processing_stats(
            len(candidates),
            len(high_conf),
            len(capped),
            emitted=0,
            runs_processed=len(runs),  # P2 FIX
        )
        return 0

    # Write candidates
    emitted = append_candidates(capped)
    log(f"Emitted {emitted} candidates to {CANDIDATES_PATH}")

    # P1 FIX: Use max started_at from processed runs as watermark (not wall-clock time)
    # This prevents dropping late-arriving artifacts that started before this job
    # but were written after it finished
    max_started_at = None
    for artifact in artifacts:
        started_at = artifact.get("run", {}).get("started_at", "")
        if started_at:
            if max_started_at is None or started_at > max_started_at:
                max_started_at = started_at

    if max_started_at:
        write_watermark(max_started_at)
        log(f"Updated watermark to: {max_started_at}")
    write_processing_stats(
        len(candidates),
        len(high_conf),
        len(capped),
        emitted=emitted,
        runs_processed=len(runs),  # P2 FIX
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
