from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
DISPOSABLE_ROOT = ".tmp/agent-skills-artifacts/skills"
OBSOLETE_ROOT = "Infrastructure/artifacts/skills"


def test_skill_quality_workflow_routes_generated_outputs_to_disposable_root() -> None:
    workflow = (ROOT / ".github/workflows/skill-quality.yml").read_text()

    assert f"--reports-root {DISPOSABLE_ROOT}" in workflow
    assert f"--out-json {DISPOSABLE_ROOT}/dashboard.json" in workflow
    assert f"--out-md {DISPOSABLE_ROOT}/dashboard.md" in workflow
    assert f"--reports-root {OBSOLETE_ROOT}" not in workflow
    assert f"--out-json {OBSOLETE_ROOT}/dashboard.json" not in workflow
    assert f"--out-md {OBSOLETE_ROOT}/dashboard.md" not in workflow


def test_skill_quality_guide_matches_disposable_workflow_route() -> None:
    guide = (ROOT / "Docs/skill-graphs/workflows/skill-quality.md").read_text()

    assert f"--reports-root {DISPOSABLE_ROOT}" in guide
    assert f"--out-json {DISPOSABLE_ROOT}/dashboard.json" in guide
    assert f"--out-md {DISPOSABLE_ROOT}/dashboard.md" in guide
    assert f"--reports-root {OBSOLETE_ROOT}" not in guide
    assert f"--out-json {OBSOLETE_ROOT}/dashboard.json" not in guide
    assert f"--out-md {OBSOLETE_ROOT}/dashboard.md" not in guide
