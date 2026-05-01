from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = ROOT / "Plugins/harness-engineering/skills/code_quality_review/he-code-review"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_he_code_review_uses_harness_engineering_naming_only():
    checked = [
        SKILL_DIR / "SKILL.md",
        *sorted((SKILL_DIR / "references").glob("*.md")),
        ROOT / "Infrastructure/references/harness-engineering/he-code-review-doctrine.md",
    ]
    forbidden = ("ClawSweeper", "OpenClaw", "ClawHub", "Projectclawsweeper")

    for path in checked:
        text = read(path)
        for term in forbidden:
            assert term not in text, f"{term} leaked into {path}"


def test_he_code_review_links_deferred_policy_references():
    text = read(SKILL_DIR / "SKILL.md")

    for reference in (
        "review-policy-index.md",
        "he-code-review-doctrine.md",
    ):
        assert reference in text


def test_he_code_review_retains_core_traceability_and_review_rules():
    skill_text = read(SKILL_DIR / "SKILL.md")
    index = read(SKILL_DIR / "references/review-policy-index.md")
    doctrine = read(ROOT / "Infrastructure/references/harness-engineering/he-code-review-doctrine.md")

    assert "Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation" in skill_text
    assert "Do not remove important context for budget trimming" in skill_text
    assert "Review policy index" in skill_text
    assert "Do not close because of title similarity alone" in doctrine
    assert "security/supply-chain pass" in doctrine
    assert "likely owners without blame" in doctrine
    assert "supply-chain" in doctrine
    assert "idempotency key" in doctrine
    assert "Do not recommend or approve a fix before explaining the likely cause" in doctrine
    assert "Root Cause Before Fix Claims" not in index
