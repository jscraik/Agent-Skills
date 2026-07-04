#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from json import JSONDecodeError
from pathlib import Path
from typing import Any


REQUIRED_KEYS = {
    "schema_version",
    "review_status",
    "risk_summary",
    "required_followups",
    "evidence_digest_seen",
    "reviewer_model_boundary",
}

DIGEST_RE = re.compile(r"sha256:[0-9a-fA-F]+")
FENCED_JSON_RE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)
ANSI_RE = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")


def _extract_json(raw: str) -> dict[str, Any]:
    stripped = ANSI_RE.sub("", raw).strip()
    stripped = "".join(
        char
        for char in stripped
        if char in "\n\r\t" or 32 <= ord(char) < 127
    )
    fenced_matches = FENCED_JSON_RE.findall(stripped)
    if fenced_matches:
        body = fenced_matches[-1].strip()
    elif stripped.startswith("```"):
        body = stripped.split("\n", 1)[1] if "\n" in stripped else ""
        body = body.rsplit("```", 1)[0].strip()
    else:
        body = stripped
    payload = json.loads(body, strict=False)
    if not isinstance(payload, dict):
        raise ValueError("review output must be a JSON object")
    return payload


def validate_review(path: Path, *, expected_digest: str | None = None) -> dict[str, Any]:
    try:
        payload = _extract_json(path.read_text(encoding="utf-8"))
    except (JSONDecodeError, ValueError) as exc:
        return {
            "schema_version": "skills-sdk.oss-security-review-extraction.v0",
            "status": "blocked",
            "blockers": [f"review output is not valid JSON: {exc}"],
            "review": None,
        }
    missing = sorted(REQUIRED_KEYS - set(payload))
    status = "pass"
    blockers: list[str] = []
    if missing:
        status = "blocked"
        blockers.append(f"missing required key(s): {', '.join(missing)}")
    expected = expected_digest.strip() if expected_digest else None
    observed = str(payload.get("evidence_digest_seen", "")).strip()
    expected_match = DIGEST_RE.search(expected) if expected else None
    observed_match = DIGEST_RE.search(observed)
    expected_canonical = expected_match.group(0).lower() if expected_match else expected
    observed_canonical = observed_match.group(0).lower() if observed_match else observed
    digest_matches = (
        not expected_canonical
        or observed_canonical == expected_canonical
        or str(observed_canonical) in str(expected_canonical)
        or str(expected_canonical) in str(observed_canonical)
    )
    if not digest_matches:
        status = "blocked"
        blockers.append(
            "evidence_digest_seen does not match expected digest "
            f"(expected={expected!r}, observed={observed!r}, "
            f"expected_canonical={expected_canonical!r}, observed_canonical={observed_canonical!r}, "
            f"digest_matches={digest_matches!r})"
        )
    review_status = str(payload.get("review_status", "")).strip().lower()
    if not any(
        review_status == accepted or review_status.startswith(f"{accepted}:")
        for accepted in ("pass", "warn", "fail", "blocked")
    ):
        status = "blocked"
        blockers.append("review_status is outside the accepted vocabulary")
    return {
        "schema_version": "skills-sdk.oss-security-review-extraction.v0",
        "status": status,
        "blockers": blockers,
        "review": payload,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Extract and validate oss-security receipt-review JSON.")
    parser.add_argument("path", type=Path)
    parser.add_argument("--expected-digest")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = validate_review(args.path, expected_digest=args.expected_digest)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(result["status"])
    return 0 if result["status"] == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
