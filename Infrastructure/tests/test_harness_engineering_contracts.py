import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PLUGIN_ROOT = REPO_ROOT / "Plugins" / "harness-engineering"


def test_lifecycle_tracer_covers_main_stages() -> None:
    tracer = PLUGIN_ROOT / "references" / "lifecycle-tracer-evals.yaml"
    text = tracer.read_text(encoding="utf-8")

    for stage in [
        "he-brainstorm",
        "he-spec",
        "he-plan",
        "he-work",
        "he-fix-bugs",
        "he-improve",
        "he-code-review",
        "he-phase-work",
        "he-reconcile",
        "he-reinforce",
        "he-eval-report",
        "he-strategy",
        "he-reframe",
        "he-linear-plan",
    ]:
        assert f"stage: {stage}" in text
        assert f"expected_route: {stage}" in text

    assert re.search(
        r"(?s)he-compound has been removed.*?expected_route:\s*he-reinforce",
        text,
    )


def test_deferred_context_index_stays_router_with_preserved_context() -> None:
    index = PLUGIN_ROOT / "references" / "deferred-context-index.md"
    text = index.read_text(encoding="utf-8")

    assert "references/goal-continuity.md" in text
    assert "references/artifact-classification-and-traceability.md" in text
    assert "## Preserved Entry Point Lines" in text
    assert "Return schema_version when structured." not in text


def test_pragmatic_contract_is_wired_to_review_surfaces() -> None:
    pragmatic = "pragmatic-programmer-review-contract.md"
    strategy = PLUGIN_ROOT / "skills" / "he-strategy" / "SKILL.md"
    code_review = PLUGIN_ROOT / "skills" / "he-code-review" / "SKILL.md"

    assert pragmatic in strategy.read_text(encoding="utf-8")
    assert pragmatic in code_review.read_text(encoding="utf-8")
