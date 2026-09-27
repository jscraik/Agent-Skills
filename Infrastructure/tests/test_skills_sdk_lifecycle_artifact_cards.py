from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
LIFECYCLE_HTML = REPO_ROOT / "artifacts" / "skills-sdk-user-lifecycle-one-page.html"


def test_retired_lifecycle_keeps_doctrine_inside_historical_disclosure() -> None:
    html = LIFECYCLE_HTML.read_text(encoding="utf-8")

    _, historical = html.split('<details id="retired-lifecycle">', 1)
    assert "Self improving" in historical
    assert "Product doctrine" in historical
