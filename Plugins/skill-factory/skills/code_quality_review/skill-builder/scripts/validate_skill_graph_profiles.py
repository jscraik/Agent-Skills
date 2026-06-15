from pathlib import Path
import runpy
import sys

impl = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "validate_skill_graph_profiles.py"
repo = Path(__file__).resolve().parents[6]

if __name__ == "__main__":
    sys.path.insert(0, str(impl.parent))
    if "--repo-root" not in sys.argv:
        sys.argv.extend(["--repo-root", str(repo)])
    if "--expected-count" not in sys.argv:
        sys.argv.extend(["--expected-count", "73"])
    runpy.run_path(str(impl), run_name="__main__")
