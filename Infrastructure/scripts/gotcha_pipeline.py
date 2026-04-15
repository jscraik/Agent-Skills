#!/usr/bin/env python3
"""Gotcha candidate pipeline with Learnings ingestion and question-gate artifacts."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CANDIDATES = REPO_ROOT / "artifacts" / "gotchas" / "candidates.jsonl"
DEFAULT_PROMOTED = REPO_ROOT / "artifacts" / "gotchas" / "promoted.jsonl"
DEFAULT_QUESTION_PACK = REPO_ROOT / "artifacts" / "gotchas" / "question-pack.json"
DEFAULT_SOURCES = (
    REPO_ROOT / ".harness" / "memory" / "LEARNINGS.md",
    REPO_ROOT / ".harness" / "memory" / "Learnings.md",
)

LEARNING_RE = re.compile(r"^\*\*(\d{4}-\d{2}-\d{2}) \[([^\]]+)\]:\*\* (.+)$")

VALID_STATUS = {"candidate", "promoted", "dismissed"}
VALID_QUESTION_STATE = {"pending", "approved", "rejected", "deferred"}
VALID_DECISION = {"promote", "keep", "dismiss"}


def default_local_only() -> bool:
    raw = os.environ.get("GOTCHA_PIPELINE_LOCAL_ONLY", "1").strip().lower()
    return raw not in {"0", "false", "no", "off"}


def dedupe_sources(sources: list[Path]) -> list[Path]:
    deduped: list[Path] = []
    seen: set[str] = set()
    for source in sources:
        try:
            resolved = source.resolve(strict=False)
        except OSError:
            resolved = source
        key = os.path.normcase(str(resolved))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(source)
    return deduped


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    for idx, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{idx} invalid JSONL: {exc}") from exc
        if not isinstance(obj, dict):
            raise ValueError(f"{path}:{idx} JSONL object must be a map")
        records.append(obj)
    return records


def write_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r, sort_keys=True, ensure_ascii=True) for r in records]
    payload = ("\n".join(lines) + "\n") if lines else ""
    path.write_text(payload, encoding="utf-8")


def stable_id(problem: str, fix: str) -> str:
    normalized = f"{problem.strip().lower()}|{fix.strip().lower()}"
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"gch-{digest}"


def parse_learning_line(line: str) -> tuple[str, str, str, str] | None:
    match = LEARNING_RE.match(line.strip())
    if not match:
        return None
    observed_at, agent, payload = match.groups()
    for sep in ("→", "->"):
        if sep in payload:
            left, right = payload.split(sep, 1)
            problem = left.strip()
            fix = right.strip()
            if not problem or not fix:
                return None
            return observed_at, agent.strip(), problem, fix
    return None


def ingest_sources(
    sources: list[Path],
    existing: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], int, int]:
    sources = dedupe_sources(sources)
    by_id = {str(rec.get("id")): rec for rec in existing if rec.get("id")}
    added = 0
    updated = 0
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()

    for source in sources:
        if not source.exists():
            continue
        for line_no, raw in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            parsed = parse_learning_line(raw)
            if parsed is None:
                continue
            observed_at, agent, problem, fix = parsed
            cid = stable_id(problem, fix)
            source_ref = f"{source}:{line_no}"

            if cid not in by_id:
                by_id[cid] = {
                    "id": cid,
                    "status": "candidate",
                    "question_state": "pending",
                    "source": "learnings",
                    "symptom": problem,
                    "do_instead": fix,
                    "cause": "unknown",
                    "check": "pending",
                    "target_skill": "",
                    "severity": "normal",
                    "first_seen": observed_at,
                    "last_seen": observed_at,
                    "observed_by": [agent],
                    "source_refs": [source_ref],
                    "occurrences": 1,
                    "updated_at": now_iso,
                }
                added += 1
                continue

            rec = by_id[cid]
            source_refs = set(rec.get("source_refs") or [])
            before = len(source_refs)
            source_refs.add(source_ref)
            after = len(source_refs)
            if after > before:
                rec["source_refs"] = sorted(source_refs)
                rec["occurrences"] = after
                updated += 1
            rec["last_seen"] = max(str(rec.get("last_seen", observed_at)), observed_at)
            observed_by = set(rec.get("observed_by") or [])
            observed_by.add(agent)
            rec["observed_by"] = sorted(observed_by)
            rec["updated_at"] = now_iso

    records = sorted(by_id.values(), key=lambda r: str(r.get("id", "")))
    return records, added, updated


def build_question_pack(records: list[dict[str, Any]], limit: int) -> dict[str, Any]:
    pending = [
        rec
        for rec in records
        if rec.get("status") == "candidate" and rec.get("question_state", "pending") == "pending"
    ]
    pending.sort(
        key=lambda r: (
            -int(r.get("occurrences", 1)),
            str(r.get("last_seen", "")),
            str(r.get("id", "")),
        )
    )
    chosen = pending[:limit]

    questions: list[dict[str, Any]] = []
    for idx, rec in enumerate(chosen, start=1):
        cid = str(rec.get("id", "unknown")).replace("-", "_")
        symptom = str(rec.get("symptom", "")).strip()
        do_instead = str(rec.get("do_instead", "")).strip()
        target_skill = str(rec.get("target_skill", "")).strip()
        skill_clause = f" for skill `{target_skill}`" if target_skill else ""
        question_text = (
            f"Promote gotcha candidate{skill_clause}? Symptom: {symptom}. "
            f"Preferred behavior: {do_instead}."
        )

        questions.append(
            {
                "header": f"Gotcha {idx}",
                "id": f"gotcha_{cid}",
                "question": question_text,
                "options": [
                    {
                        "label": "Promote (Recommended)",
                        "description": "Add to promoted gotchas and enforce with eval coverage.",
                    },
                    {
                        "label": "Keep candidate",
                        "description": "Keep collecting evidence before promotion.",
                    },
                    {
                        "label": "Dismiss",
                        "description": "Mark as one-off and stop prompting for this candidate.",
                    },
                ],
            }
        )

    return {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "candidate_count": len(pending),
        "questions": questions,
    }


def validate_records(records: list[dict[str, Any]]) -> list[str]:
    findings: list[str] = []
    seen: set[str] = set()
    required = (
        "id",
        "status",
        "question_state",
        "symptom",
        "do_instead",
        "occurrences",
        "source_refs",
    )
    for idx, rec in enumerate(records, start=1):
        rid = str(rec.get("id", ""))
        if not rid:
            findings.append(f"record#{idx}: missing id")
            continue
        if rid in seen:
            findings.append(f"{rid}: duplicate id")
        seen.add(rid)
        for key in required:
            if key not in rec:
                findings.append(f"{rid}: missing required field `{key}`")
        if rec.get("status") not in VALID_STATUS:
            findings.append(f"{rid}: invalid status `{rec.get('status')}`")
        if rec.get("question_state") not in VALID_QUESTION_STATE:
            findings.append(f"{rid}: invalid question_state `{rec.get('question_state')}`")
        try:
            occ = int(rec.get("occurrences", 0))
        except (TypeError, ValueError):
            findings.append(f"{rid}: occurrences must be an integer")
            occ = 0
        if occ < 1:
            findings.append(f"{rid}: occurrences must be >= 1")
        refs = rec.get("source_refs")
        if not isinstance(refs, list):
            findings.append(f"{rid}: source_refs must be an array")
    return findings


def cmd_ingest(args: argparse.Namespace) -> int:
    sources = [Path(s).expanduser().resolve() for s in args.source]
    existing = load_jsonl(args.candidates)
    merged, added, updated = ingest_sources(sources, existing)
    findings = validate_records(merged)
    if findings:
        print("FAIL gotcha_pipeline ingest validation")
        for finding in findings:
            print(f"- {finding}")
        return 2
    if not args.dry_run:
        write_jsonl(args.candidates, merged)
    print(f"Sources scanned: {len(sources)}")
    print(f"Candidates total: {len(merged)}")
    print(f"Added: {added}")
    print(f"Updated: {updated}")
    print(f"Dry run: {args.dry_run}")
    return 0


def cmd_question_pack(args: argparse.Namespace) -> int:
    records = load_jsonl(args.candidates)
    pack = build_question_pack(records, limit=args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(pack, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    print(f"Question pack written: {args.output}")
    print(f"Questions: {len(pack.get('questions', []))}")
    return 0


def cmd_resolve(args: argparse.Namespace) -> int:
    if args.decision not in VALID_DECISION:
        print(f"invalid decision: {args.decision}", file=sys.stderr)
        return 2
    records = load_jsonl(args.candidates)
    by_id = {str(rec.get("id")): rec for rec in records if rec.get("id")}
    if args.id not in by_id:
        print(f"candidate not found: {args.id}", file=sys.stderr)
        return 2

    rec = by_id[args.id]
    rec["updated_at"] = dt.datetime.now(dt.timezone.utc).isoformat()

    if args.decision == "promote":
        rec["status"] = "promoted"
        rec["question_state"] = "approved"
        if args.skill:
            rec["target_skill"] = args.skill
        if args.cause:
            rec["cause"] = args.cause
        if args.check:
            rec["check"] = args.check
        promoted = load_jsonl(args.promoted)
        promoted_map = {str(r.get("id")): r for r in promoted if r.get("id")}
        promoted_map[args.id] = rec
        write_jsonl(args.promoted, sorted(promoted_map.values(), key=lambda r: str(r.get("id", ""))))
    elif args.decision == "keep":
        rec["status"] = "candidate"
        rec["question_state"] = "deferred"
    elif args.decision == "dismiss":
        rec["status"] = "dismissed"
        rec["question_state"] = "rejected"

    write_jsonl(args.candidates, sorted(by_id.values(), key=lambda r: str(r.get("id", ""))))
    print(f"Updated candidate: {args.id} -> {rec['status']} ({rec['question_state']})")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    if args.local_only:
        print("Mode: local-only")
    else:
        print("Mode: full")

    try:
        records = load_jsonl(args.candidates)
    except PermissionError as exc:
        print("BLOCKED_BY_POLICY gotcha_pipeline validate")
        print(f"- {exc}")
        return 3

    findings = validate_records(records)
    if findings:
        print("FAIL gotcha_pipeline validate")
        for finding in findings:
            print(f"- {finding}")
        return 2
    print("PASS gotcha_pipeline validate")
    print(f"Candidates: {len(records)}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ingest = sub.add_parser("ingest", help="Ingest Learnings entries into gotcha candidates")
    ingest.add_argument(
        "--source",
        action="append",
        default=[str(path) for path in DEFAULT_SOURCES],
        help="Learning source markdown path (repeatable)",
    )
    ingest.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES,
        help="Candidate JSONL output path",
    )
    ingest.add_argument("--dry-run", action="store_true", help="Parse and merge without writing")
    ingest.set_defaults(func=cmd_ingest)

    qpack = sub.add_parser("question-pack", help="Generate request_user_input-compatible question pack")
    qpack.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    qpack.add_argument("--output", type=Path, default=DEFAULT_QUESTION_PACK)
    qpack.add_argument("--limit", type=int, default=3)
    qpack.set_defaults(func=cmd_question_pack)

    resolve = sub.add_parser("resolve", help="Apply a decision to a gotcha candidate")
    resolve.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    resolve.add_argument("--promoted", type=Path, default=DEFAULT_PROMOTED)
    resolve.add_argument("--id", required=True, help="Candidate id (e.g. gch-abc123...)")
    resolve.add_argument("--decision", required=True, choices=sorted(VALID_DECISION))
    resolve.add_argument("--skill", help="Target skill path/name for promoted candidates")
    resolve.add_argument("--cause", help="Root cause summary")
    resolve.add_argument("--check", help="Validation check/assertion text")
    resolve.set_defaults(func=cmd_resolve)

    validate = sub.add_parser("validate", help="Validate candidate store contract")
    validate.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    validate.add_argument(
        "--local-only",
        action=argparse.BooleanOptionalAction,
        default=default_local_only(),
        help="Run only local filesystem contract checks (default: on in this repo env)",
    )
    validate.set_defaults(func=cmd_validate)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        return int(args.func(args))
    except ValueError as exc:
        print(f"FAIL gotcha_pipeline: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
