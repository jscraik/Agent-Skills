from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
SKILL_DIR = ROOT / "Plugins/harness-engineering/skills/he-code-review"
SHARED_REVIEW_REFERENCES = ROOT / "Plugins/harness-engineering/references/skills/he-code-review"


def read(path: Path) -> str:
    """
    Read and return the text contents of the file at the given filesystem path using UTF-8 decoding.
    
    Parameters:
    	path (Path): Filesystem path of the file to read.
    
    Returns:
    	The file's text decoded using UTF-8.
    """
    return path.read_text(encoding="utf-8")


def test_he_code_review_uses_harness_engineering_naming_only():
    """
    Verify that specific skill and doctrine markdown files do not contain disallowed legacy or competitor names.
    
    Checks SKILL.md, every Markdown file under the skill's references directory, and the infrastructure doctrine file for any occurrence of a predefined set of forbidden terms; raises an AssertionError identifying the offending term and file path if a forbidden term is found.
    """
    checked = [
        SKILL_DIR / "SKILL.md",
        *sorted((SKILL_DIR / "references").glob("*.md")),
        ROOT / "Infrastructure/references/harness-engineering/he-code-review-doctrine.md",
    ]
    forbidden = ("ClawSweeper", "OpenClaw", "ClawHub", "Projectclawsweeper", "Claude", "Haiku", "Sonnet")

    for path in checked:
        text = read(path)
        lower_text = text.lower()
        for term in forbidden:
            assert term.lower() not in lower_text, f"{term} leaked into {path}"


def test_he_code_review_links_deferred_policy_references():
    """
    Check that SKILL.md contains required deferred policy reference identifiers.
    
    Asserts that "review-policy-index.md" and "he-code-review-doctrine.md" appear in the SKILL.md file within the he-code-review skill directory. Raises AssertionError if any required reference is missing.
    """
    text = read(SKILL_DIR / "SKILL.md")

    for reference in (
        "review-policy-index.md",
        "he-code-review-doctrine.md",
    ):
        assert reference in text


def test_he_code_review_retains_core_traceability_and_review_rules():
    skill_text = read(SKILL_DIR / "SKILL.md")
    index = read(SHARED_REVIEW_REFERENCES / "review-policy-index.md")
    doctrine = read(ROOT / "Infrastructure/references/harness-engineering/he-code-review-doctrine.md")

    assert "Linear issue -> spec/source acceptance IDs -> plan units -> PR evidence -> validation" in skill_text
    assert "Apply the context-disposition policy" in skill_text
    assert "Review policy index" in skill_text
    assert "Do not close because of title similarity alone" in doctrine
    assert "security/supply-chain pass" in doctrine
    assert "likely owners without blame" in doctrine
    assert "supply-chain" in doctrine
    assert "idempotency key" in doctrine
    assert "codex_review.findings[]" in doctrine
    assert "overall_correctness" in doctrine
    assert "Multi-Lens Review And False-Positive Filter" in doctrine
    assert "Confidence Ladder" in doctrine
    assert "overall_confidence_score: 0.96" in doctrine
    assert "evidence_ladder" in skill_text
    assert "Confidence Calibration" in index
    assert "Cap at `0.90`" in index
    assert "Codex-compatible findings must be tight" in skill_text
    assert "Review Lenses" in index
    assert "Codex-compatible review" in index
    assert "Do not recommend or approve a fix before explaining the likely cause" in doctrine
    assert "Root Cause Before Fix Claims" not in index
