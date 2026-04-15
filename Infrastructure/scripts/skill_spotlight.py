#!/usr/bin/env python3
"""Generate skill spotlight for daily health report.

Picks a skill that needs attention based on:
- Recent failed promotions
- High confusion signals
- Not modified recently
"""
import json
import random
from pathlib import Path
from datetime import datetime, timezone

RUNS_ROOT = Path("Infrastructure/artifacts/skill-graphs/runs")
TELEMETRY_ROOT = Path("Infrastructure/artifacts/skill-graphs/telemetry")
SKILLS_ROOT = Path("skills")

def get_skill_mod_time(skill_name: str) -> str:
    """Get last modified time of a skill."""
    skill_path = SKILLS_ROOT / skill_name / "SKILL.md"
    if skill_path.exists():
        mtime = skill_path.stat().st_mtime
        dt = datetime.fromtimestamp(mtime, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d")
    return "unknown"

def analyze_failures() -> dict:
    """Analyze failure patterns from runs."""
    skill_failures = {}

    if not RUNS_ROOT.exists():
        return skill_failures

    for run_dir in RUNS_ROOT.iterdir():
        if not run_dir.is_dir() or not run_dir.name.startswith("run_"):
            continue

        run_json = run_dir / "run.json"
        if not run_json.exists():
            continue

        try:
            data = json.loads(run_json.read_text())
            skill = data.get("scope_skill", "unknown")
            status = data.get("terminal_status", "")
            stop_reason = data.get("stop_reason", "")

            if status == "failed" or stop_reason in {"policy_failed", "evaluator_conflict"}:
                if skill not in skill_failures:
                    skill_failures[skill] = {"count": 0, "reasons": []}
                skill_failures[skill]["count"] += 1
                skill_failures[skill]["reasons"].append(stop_reason)
        except:
            continue

    return skill_failures

def pick_spotlight() -> dict:
    """Pick a skill to spotlight."""
    failures = analyze_failures()

    if failures:
        # Pick skill with most failures
        skill = max(failures.keys(), key=lambda s: failures[s]["count"])
        return {
            "skill": skill,
            "signal": f"{failures[skill]['count']} failed run(s)",
            "reasons": list(set(failures[skill]["reasons"])),
            "action": "Review trigger phrases and confidence thresholds"
        }

    # Fallback: pick a random skill that hasn't been modified recently
    skills = [d.name for d in SKILLS_ROOT.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
    if skills:
        skill = random.choice(skills)
        return {
            "skill": skill,
            "signal": "Random spotlight - no failures detected",
            "reasons": [],
            "action": "Review and validate skill documentation"
        }

    return {"skill": "none", "signal": "No skills found", "reasons": [], "action": "N/A"}

def main():
    spotlight = pick_spotlight()
    mod_time = get_skill_mod_time(spotlight["skill"])

    print(f"## Skill Spotlight (Auto-Generated)")
    print(f"- **Skill**: {spotlight['skill']}")
    print(f"- **Last modified**: {mod_time}")
    print(f"- **Signal**: {spotlight['signal']}")
    if spotlight['reasons']:
        print(f"- **Failure reasons**: {', '.join(spotlight['reasons'])}")
    print(f"- **Suggested action**: {spotlight['action']}")

if __name__ == "__main__":
    main()
