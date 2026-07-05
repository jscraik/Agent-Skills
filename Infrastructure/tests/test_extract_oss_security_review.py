from __future__ import annotations

import importlib.util
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "scripts"
    / "validation-and-linting"
    / "extract_oss_security_review.py"
)
SPEC = importlib.util.spec_from_file_location("extract_oss_security_review", MODULE_PATH)
assert SPEC is not None
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def write_review(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "review.txt"
    path.write_text(body, encoding="utf-8")
    return path


def valid_review(status: str = "pass") -> str:
    return f'''{{
  "schema_version": "skills-sdk.oss-security-review-input.v0",
  "review_status": "{status}",
  "risk_summary": "reviewed deterministic receipt",
  "required_followups": [],
  "evidence_digest_seen": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "reviewer_model_boundary": "static receipt review only"
}}'''


def test_validates_plain_json_with_expected_digest(tmp_path: Path) -> None:
    result = MODULE.validate_review(
        write_review(tmp_path, valid_review()),
        expected_digest="sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )

    assert result["status"] == "pass"
    assert result["blockers"] == []


def test_extracts_last_fenced_json_after_model_thinking(tmp_path: Path) -> None:
    review = "Thinking...\nnoise\n```json\n" + valid_review("FAIL: CRITICAL") + "\n```\n"

    result = MODULE.validate_review(
        write_review(tmp_path, review),
        expected_digest="sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )

    assert result["status"] == "pass"
    assert result["review"]["review_status"] == "FAIL: CRITICAL"


def test_blocks_digest_mismatch(tmp_path: Path) -> None:
    result = MODULE.validate_review(
        write_review(tmp_path, valid_review()),
        expected_digest="sha256:bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb",
    )

    assert result["status"] == "blocked"
    assert "evidence_digest_seen does not match expected digest" in result["blockers"][0]


def test_blocks_truncated_digest_prefix(tmp_path: Path) -> None:
    truncated = valid_review().replace(
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
        "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )

    result = MODULE.validate_review(
        write_review(tmp_path, truncated),
        expected_digest="sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
    )

    assert result["status"] == "blocked"
    assert "evidence_digest_seen does not match expected digest" in result["blockers"][0]


def test_blocks_unknown_review_status(tmp_path: Path) -> None:
    result = MODULE.validate_review(write_review(tmp_path, valid_review("maybe")))

    assert result["status"] == "blocked"
    assert result["blockers"] == ["review_status is outside the accepted vocabulary"]


def test_blocks_empty_summary_and_boundary(tmp_path: Path) -> None:
    review = '''{
  "schema_version": "skills-sdk.oss-security-review-input.v0",
  "review_status": "pass",
  "risk_summary": "",
  "required_followups": [],
  "evidence_digest_seen": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "reviewer_model_boundary": ""
}'''

    result = MODULE.validate_review(write_review(tmp_path, review))

    assert result["status"] == "blocked"
    assert "risk_summary must be a non-empty string" in result["blockers"]
    assert "reviewer_model_boundary must be a non-empty string" in result["blockers"]


def test_blocks_non_string_summary_and_boundary(tmp_path: Path) -> None:
    review = '''{
  "schema_version": "skills-sdk.oss-security-review-input.v0",
  "review_status": "pass",
  "risk_summary": 123,
  "required_followups": [],
  "evidence_digest_seen": "sha256:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "reviewer_model_boundary": true
}'''

    result = MODULE.validate_review(write_review(tmp_path, review))

    assert result["status"] == "blocked"
    assert "risk_summary must be a non-empty string" in result["blockers"]
    assert "reviewer_model_boundary must be a non-empty string" in result["blockers"]


def test_preserves_unicode_review_text(tmp_path: Path) -> None:
    review = valid_review().replace("reviewed deterministic receipt", "reviewed caf\u00e9 receipt")

    result = MODULE.validate_review(write_review(tmp_path, review))

    assert result["status"] == "pass"
    assert result["review"]["risk_summary"] == "reviewed caf\u00e9 receipt"
