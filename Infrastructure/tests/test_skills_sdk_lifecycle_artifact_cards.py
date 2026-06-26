from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_HTML = REPO_ROOT / "artifacts" / "skills-sdk-user-lifecycle-one-page.html"


def test_lifecycle_artifact_names_self_improving_doctrine_card() -> None:
    html = LIFECYCLE_HTML.read_text(encoding="utf-8")

    assert "Self Improving" in html
