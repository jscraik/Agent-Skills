#!/usr/bin/env python3
"""Human review gate for skill genome loop candidates.

Candidates are written to pending-candidates.jsonl by the genome loop.
This script allows human operators to review and approve/reject them.

Usage:
  python3 scripts/review_candidates.py               # Interactive review
  python3 scripts/review_candidates.py --list        # List pending
  python3 scripts/review_candidates.py --approve ID  # Approve specific candidate
  python3 scripts/review_candidates.py --reject ID   # Reject specific candidate
  python3 scripts/review_candidates.py --approve-all # Approve all pending
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Configuration
PENDING_PATH = Path("artifacts/skill-graphs/telemetry/pending-candidates.jsonl")
CANDIDATES_PATH = Path("artifacts/skill-graphs/telemetry/candidates.jsonl")
REJECTED_PATH = Path("artifacts/skill-graphs/telemetry/rejected-candidates.jsonl")


def load_pending() -> List[Dict[str, Any]]:
    """Load all pending candidates."""
    if not PENDING_PATH.exists():
        return []

    candidates = []
    for line in PENDING_PATH.read_text(encoding="utf-8").splitlines():
        if line.strip():
            try:
                candidates.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return candidates


def save_pending(candidates: List[Dict[str, Any]]) -> None:
    """Save remaining pending candidates."""
    PENDING_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(PENDING_PATH, "w", encoding="utf-8") as f:
        for c in candidates:
            f.write(json.dumps(c, sort_keys=True) + "\n")


def append_to_file(path: Path, candidate: Dict[str, Any], extra_fields: Optional[Dict[str, Any]] = None) -> None:
    """Append candidate to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {**candidate}
    if extra_fields:
        record.update(extra_fields)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def format_candidate(c: Dict[str, Any], idx: int) -> str:
    """Format candidate for display."""
    lines = [
        f"\n[{idx}] Candidate: {c.get('candidate_id', 'unknown')}",
        f"    Skill: {c.get('skill_path', 'unknown')}",
        f"    Score: {c.get('composite_score', 0):.2f}",
        f"    Windows: {c.get('window_count', 0)}",
        f"    Reason: {c.get('decision_reason', 'unknown')}",
        f"    Created: {c.get('created_at', 'unknown')}",
    ]
    return "\n".join(lines)


def interactive_review() -> int:
    """Interactive review of pending candidates."""
    candidates = load_pending()

    if not candidates:
        print("No pending candidates to review.")
        return 0

    print(f"=== Pending Candidates ({len(candidates)}) ===")

    for i, c in enumerate(candidates):
        print(format_candidate(c, i + 1))

    print("\n" + "=" * 50)
    print("Commands: a=approve, r=reject, s=skip, q=quit, A=approve-all, R=reject-all")
    print("=" * 50)

    approved: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    remaining: List[Dict[str, Any]] = []

    for i, c in enumerate(candidates):
        while True:
            choice = input(f"\n[{i + 1}/{len(candidates)}] Approve {c.get('candidate_id', '?')}? [a/r/s/q/A/R]: ").strip()

            if choice == "a":
                approved.append(c)
                print("  ✓ Approved")
                break
            elif choice == "r":
                rejected.append(c)
                print("  ✗ Rejected")
                break
            elif choice == "s":
                remaining.append(c)
                print("  → Skipped (will remain pending)")
                break
            elif choice == "q":
                remaining.extend(candidates[i:])
                print(f"  Quitting. {len(remaining)} candidates will remain pending.")
                # Save remaining and exit
                save_pending(remaining)
                print(f"\nSummary: {len(approved)} approved, {len(rejected)} rejected, {len(remaining)} pending")
                return 0
            elif choice == "A":
                # Approve all remaining
                approved.append(c)
                approved.extend(candidates[i + 1:])
                remaining = []
                print(f"  ✓ Approved all remaining ({len(candidates) - i})")
                # Process and exit
                for a in approved:
                    append_to_file(CANDIDATES_PATH, a, {
                        "reviewed_at": datetime.now(timezone.utc).isoformat(),
                        "review_status": "approved",
                    })
                for r in rejected:
                    append_to_file(REJECTED_PATH, r, {
                        "reviewed_at": datetime.now(timezone.utc).isoformat(),
                        "review_status": "rejected",
                    })
                save_pending(remaining)
                print(f"\nSummary: {len(approved)} approved, {len(rejected)} rejected, {len(remaining)} pending")
                return 0
            elif choice == "R":
                # Reject all remaining
                rejected.append(c)
                rejected.extend(candidates[i + 1:])
                remaining = []
                print(f"  ✗ Rejected all remaining ({len(candidates) - i})")
                # Process and exit
                for a in approved:
                    append_to_file(CANDIDATES_PATH, a, {
                        "reviewed_at": datetime.now(timezone.utc).isoformat(),
                        "review_status": "approved",
                    })
                for r in rejected:
                    append_to_file(REJECTED_PATH, r, {
                        "reviewed_at": datetime.now(timezone.utc).isoformat(),
                        "review_status": "rejected",
                    })
                save_pending(remaining)
                print(f"\nSummary: {len(approved)} approved, {len(rejected)} rejected, {len(remaining)} pending")
                return 0
            else:
                print("  Invalid choice. Use: a/r/s/q/A/R")

    # Write approved and rejected
    now = datetime.now(timezone.utc).isoformat()

    for a in approved:
        append_to_file(CANDIDATES_PATH, a, {
            "reviewed_at": now,
            "review_status": "approved",
        })

    for r in rejected:
        append_to_file(REJECTED_PATH, r, {
            "reviewed_at": now,
            "review_status": "rejected",
        })

    # Save remaining (skipped) back to pending
    save_pending(remaining)

    print(f"\nSummary: {len(approved)} approved, {len(rejected)} rejected, {len(remaining)} pending")
    return 0


def list_pending() -> int:
    """List all pending candidates."""
    candidates = load_pending()

    if not candidates:
        print("No pending candidates.")
        return 0

    print(f"=== Pending Candidates ({len(candidates)}) ===\n")

    for i, c in enumerate(candidates):
        print(format_candidate(c, i + 1))

    print(f"\nTotal: {len(candidates)} pending")
    return 0


def approve_candidate(candidate_id: str) -> int:
    """Approve a specific candidate by ID."""
    candidates = load_pending()

    for i, c in enumerate(candidates):
        if c.get("candidate_id") == candidate_id:
            approved = candidates.pop(i)
            append_to_file(CANDIDATES_PATH, approved, {
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "review_status": "approved",
            })
            save_pending(candidates)
            print(f"✓ Approved candidate: {candidate_id}")
            return 0

    print(f"✗ Candidate not found: {candidate_id}")
    return 1


def reject_candidate(candidate_id: str) -> int:
    """Reject a specific candidate by ID."""
    candidates = load_pending()

    for i, c in enumerate(candidates):
        if c.get("candidate_id") == candidate_id:
            rejected = candidates.pop(i)
            append_to_file(REJECTED_PATH, rejected, {
                "reviewed_at": datetime.now(timezone.utc).isoformat(),
                "review_status": "rejected",
            })
            save_pending(candidates)
            print(f"✗ Rejected candidate: {candidate_id}")
            return 0

    print(f"✗ Candidate not found: {candidate_id}")
    return 1


def approve_all() -> int:
    """Approve all pending candidates."""
    candidates = load_pending()

    if not candidates:
        print("No pending candidates to approve.")
        return 0

    now = datetime.now(timezone.utc).isoformat()

    for c in candidates:
        append_to_file(CANDIDATES_PATH, c, {
            "reviewed_at": now,
            "review_status": "approved",
        })

    # Clear pending
    save_pending([])

    print(f"✓ Approved {len(candidates)} candidates")
    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Review pending skill genome candidates")
    parser.add_argument("--list", action="store_true", help="List pending candidates")
    parser.add_argument("--approve", metavar="ID", help="Approve candidate by ID")
    parser.add_argument("--reject", metavar="ID", help="Reject candidate by ID")
    parser.add_argument("--approve-all", action="store_true", help="Approve all pending candidates")

    args = parser.parse_args()

    if args.list:
        return list_pending()
    elif args.approve:
        return approve_candidate(args.approve)
    elif args.reject:
        return reject_candidate(args.reject)
    elif args.approve_all:
        return approve_all()
    else:
        return interactive_review()


if __name__ == "__main__":
    raise SystemExit(main())
