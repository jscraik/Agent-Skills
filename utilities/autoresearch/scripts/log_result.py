#!/usr/bin/env python3
"""Append one normalized row to an autoresearch results TSV."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

HEADER = (
    "iteration\ttarget\tdecision\tscore\tstatus\tchange_summary\tvalidation_evidence\n"
)


def _sanitize(value: str) -> str:
    """
    Normalises a text field for TSV output by replacing tabs, collapsing line breaks into single spaces, and trimming surrounding whitespace.
    
    Parameters:
        value (str): Input text to normalise.
    
    Returns:
        sanitised (str): The input with tabs replaced by spaces, all line breaks collapsed into single spaces, and leading/trailing whitespace removed.
    """
    return " ".join(value.replace("\t", " ").splitlines()).strip()


def main() -> int:
    """
    Append a single normalized TSV row to an autoresearch run's results.tsv file.
    
    Parameters:
        --run-dir (str): Path to the run directory created by init_run.sh; must be under the repository's artifacts/autoresearch tree.
        --iteration (int): Iteration number to record.
        --target (str): Target identifier; will be sanitized to remove tabs and collapse line breaks.
        --decision (str): One of "keep", "discard", "blocked".
        --score (float): Numeric score; recorded with two decimal places.
        --status (str): One of "pass", "fail", "blocked".
        --change-summary (str): Human-readable summary of changes; will be sanitized.
        --validation-evidence (str): Validation notes or evidence; will be sanitized.
    
    Returns:
        int: Exit code 0 on success.
    
    Raises:
        SystemExit: If run-dir is not under the expected artifacts/autoresearch root, does not exist, is missing required files (results.tsv, journal.md, targets.txt), or if results.tsv does not begin with the expected header.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", required=True, help="Run directory from init_run.sh")
    parser.add_argument("--iteration", required=True, type=int)
    parser.add_argument("--target", required=True)
    parser.add_argument(
        "--decision",
        required=True,
        choices=("keep", "discard", "blocked"),
    )
    parser.add_argument("--score", required=True, type=float)
    parser.add_argument(
        "--status",
        required=True,
        choices=("pass", "fail", "blocked"),
    )
    parser.add_argument("--change-summary", required=True)
    parser.add_argument("--validation-evidence", required=True)
    args = parser.parse_args()

    if args.iteration < 0:
        raise SystemExit("--iteration must be >= 0")
    if not math.isfinite(args.score):
        raise SystemExit("--score must be a finite number")
    if args.score < 0 or args.score > 10:
        raise SystemExit("--score must be between 0 and 10")
    if args.decision == "blocked" and args.status != "blocked":
        raise SystemExit("blocked decision requires --status blocked")
    if args.decision in {"keep", "discard"} and args.status == "blocked":
        raise SystemExit("blocked status requires --decision blocked")

    repo_root = Path(__file__).resolve().parents[3]
    allowed_root = (repo_root / "artifacts" / "autoresearch").resolve()
    run_dir = Path(args.run_dir).resolve()
    if allowed_root not in run_dir.parents:
        raise SystemExit(
            f"run-dir must be under {allowed_root} and created by init_run.sh; got {run_dir}"
        )
    if not run_dir.is_dir():
        raise SystemExit(f"run-dir does not exist: {run_dir}")

    required = ("results.tsv", "journal.md", "targets.txt")
    missing = [name for name in required if not (run_dir / name).exists()]
    if missing:
        raise SystemExit(
            "run-dir is not initialized by init_run.sh; missing: " + ", ".join(missing)
        )

    results_path = run_dir / "results.tsv"
    existing = results_path.read_text(encoding="utf-8")
    if not existing.startswith(HEADER):
        raise SystemExit("results.tsv has unexpected format; initialize via init_run.sh")

    row = "\t".join(
        [
            str(args.iteration),
            _sanitize(args.target),
            args.decision,
            f"{args.score:.2f}",
            args.status,
            _sanitize(args.change_summary),
            _sanitize(args.validation_evidence),
        ]
    )
    with results_path.open("a", encoding="utf-8") as handle:
        handle.write(row + "\n")
    print(str(results_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
