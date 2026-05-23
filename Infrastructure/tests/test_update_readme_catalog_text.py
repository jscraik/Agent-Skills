import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "Infrastructure" / "scripts" / "lifecycle-and-sync"))

from update_readme_catalog_text import (  # noqa: E402
    CURRENT_AGENT_SKILLS_KIT_SENTENCE,
    refresh_readme_catalog_text,
)


class TestUpdateReadmeCatalogText(unittest.TestCase):
    def test_preserves_current_intro_and_updates_catalog_count(self) -> None:
        content = (
            "# Agent Skills\n\n"
            f"{CURRENT_AGENT_SKILLS_KIT_SENTENCE}\n\n"
            "This repository currently exposes **24 skills** in the default catalog.\n"
        )

        refreshed = refresh_readme_catalog_text(content, 25)

        self.assertEqual(refreshed.count(CURRENT_AGENT_SKILLS_KIT_SENTENCE), 1)
        self.assertIn("This repository currently exposes **25 skills** in the default catalog", refreshed)

    def test_normalizes_wrapped_current_intro(self) -> None:
        content = (
            "# Agent Skills\n\n"
            "A governed **Agent Skills Kit** repository for Codex and AI coding agents.\n"
            "Author skills once, validate quality, expose `$` command handles, and sync\n"
            "routed skills and plugins into runtime projections through the `ask` CLI.\n\n"
            "Body.\n"
        )

        refreshed = refresh_readme_catalog_text(content, 25)

        self.assertIn(f"# Agent Skills\n\n{CURRENT_AGENT_SKILLS_KIT_SENTENCE}\n\nBody.", refreshed)

    def test_normalizes_legacy_intro(self) -> None:
        content = (
            "# Agent Skills\n\n"
            "A governed repository of **skills** for AI coding agents. Built around "
            "the **Agent Skills Kit (`ask`)** CLI.\n\n"
            "Body.\n"
        )

        refreshed = refresh_readme_catalog_text(content, 25)

        self.assertIn(f"# Agent Skills\n\n{CURRENT_AGENT_SKILLS_KIT_SENTENCE}\n\nBody.", refreshed)

    def test_collapses_duplicate_current_intro(self) -> None:
        content = (
            "# Agent Skills\n\n"
            f"{CURRENT_AGENT_SKILLS_KIT_SENTENCE}\n\n"
            "A governed **Agent Skills Kit** repository for Codex and AI coding agents.\n"
            "Author skills once, validate quality, expose `$` command handles, and sync\n"
            "routed skills and plugins into runtime projections through the `ask` CLI.\n\n"
            "Body.\n"
        )

        refreshed = refresh_readme_catalog_text(content, 25)

        self.assertEqual(refreshed.count(CURRENT_AGENT_SKILLS_KIT_SENTENCE), 1)
        self.assertIn(f"{CURRENT_AGENT_SKILLS_KIT_SENTENCE}\n\nBody.", refreshed)

    def test_inserts_intro_when_only_heading_is_known(self) -> None:
        content = "# Agent Skills\n\nBody.\n"

        refreshed = refresh_readme_catalog_text(content, 25)

        self.assertIn(f"# Agent Skills\n\n{CURRENT_AGENT_SKILLS_KIT_SENTENCE}\n\nBody.", refreshed)

    def test_raises_when_heading_is_missing(self) -> None:
        with self.assertRaises(ValueError):
            refresh_readme_catalog_text("Body only.\n", 25)


if __name__ == "__main__":
    unittest.main()
