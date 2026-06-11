from pathlib import Path
import runpy

impl = Path(__file__).resolve().parents[4] / "scripts" / "skill-builder" / "skill_router_schema.py"
globals().update(runpy.run_path(str(impl)))
