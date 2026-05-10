import json
import os
import shutil
from pathlib import Path
from typing import Any


import json
import os
import shutil
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def load_local_marketplace(repo_root: Path) -> tuple[Path, list[dict[str, Any]]]:
    """Load local plugin entries from the repository marketplace manifest."""
    marketplace_path = repo_root / "Plugins" / "marketplace.json"
    if not marketplace_path.is_file():
        raise FileNotFoundError(f"Local marketplace manifest missing: {marketplace_path}")

    payload = json.loads(marketplace_path.read_text(encoding="utf-8"))
    raw_plugins = payload.get("plugins", [])
    if not isinstance(raw_plugins, list):
        raise ValueError("Plugins/marketplace.json must contain a top-level 'plugins' list.")

    entries: list[dict[str, Any]] = []
    for item in raw_plugins:
        if not isinstance(item, dict):
            logger.warning("Skipping non-dict marketplace entry: %r", item)
            continue
        name = item.get("name")
        source = item.get("source", {})
        if not isinstance(name, str) or not isinstance(source, dict):
            logger.warning("Skipping malformed marketplace entry (invalid name or source): %r", item)
            continue
        if source.get("source") != "local":
            continue
        path = source.get("path")
        if not isinstance(path, str):
            logger.warning("Skipping local plugin '%s' with non-string path: %r", name, source)
            continue
        entries.append({"name": name, "path": path})
    return marketplace_path, entries


def copy_directory_contents(source_dir: Path, target_dir: Path) -> None:
    """Replace target_dir contents with source_dir first-level entries."""
    target_dir.mkdir(parents=True, exist_ok=True)
    for child in list(target_dir.iterdir()):
        if child.is_symlink() or child.is_file():
            child.unlink()
        else:
            shutil.rmtree(child)

    for child in source_dir.iterdir():
        destination = target_dir / child.name
        if child.is_symlink():
            destination.symlink_to(os.readlink(child), target_is_directory=child.is_dir())
        elif child.is_dir():
            shutil.copytree(child, destination, symlinks=True)
        else:
            shutil.copy2(child, destination)


def materialize_first_level_skill_aliases(plugin_root: Path) -> None:
    """Replace first-level symlinked skill aliases with real directory copies."""
    skills_root = plugin_root / "skills"
    if not skills_root.is_dir():
        return

    hidden_entries = {
        "agents",
        "assets",
        "examples",
        "fixtures",
        "infrastructure_ops",
        "references",
        "rules",
        "scaffolding_templates",
        "scripts",
        "shared",
        "team_automation",
        "templates",
        "code_quality_review",
    }
    for child in skills_root.iterdir():
        if child.name.startswith("_") or child.name in hidden_entries or not child.is_symlink():
            continue
        resolved = child.resolve(strict=True)
        if not resolved.is_dir():
            continue
        child.unlink()
        shutil.copytree(resolved, child, symlinks=True)
