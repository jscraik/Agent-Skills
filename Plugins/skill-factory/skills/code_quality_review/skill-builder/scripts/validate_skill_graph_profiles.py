from pathlib import Path
import runpy
import sys

impl = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "validate_skill_graph_profiles.py"
repo = Path(__file__).resolve().parents[6]

if __name__ == "__main__":
    if not impl.is_file():
        raise FileNotFoundError(f"Implementation not found: {impl}")
    impl_dir = str(impl.parent)
    if impl_dir not in sys.path:
        sys.path.insert(0, impl_dir)
    if "--repo-root" not in sys.argv:
        sys.argv.extend(["--repo-root", str(repo)])
    if "--expected-count" not in sys.argv:
        sys.argv.extend(["--expected-count", "72"])
    runpy.run_path(str(impl), run_name="__main__")
