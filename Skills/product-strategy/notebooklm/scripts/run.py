#!/usr/bin/env python3
"""
Universal runner for NotebookLM skill scripts
Ensures all scripts run with the correct virtual environment
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

AVAILABLE_SCRIPT_DESCRIPTIONS = {
    "ask_question.py": "Query NotebookLM",
    "notebook_manager.py": "Manage notebook library",
    "auto_sync.py": "Incremental local-folder sync into notebook sources",
    "audio_generator.py": "Generate Audio Overview with custom prompts",
    "video_generator.py": "Generate Video Overview with custom prompts",
    "add_source.py": "Add sources to notebooks",
    "list_sources.py": "List sources by reading UI (reliable)",
    "remove_source.py": "Remove source from notebook (PERMANENT)",
    "auth_manager.py": "Handle authentication",
    "cleanup_manager.py": "Clean up skill data",
}


def print_available_scripts():
    """Print available scripts in the scripts folder."""
    script_names = sorted(AVAILABLE_SCRIPT_DESCRIPTIONS)
    if not script_names:
        print("  [none]")
        return

    for script_name in script_names:
        description = AVAILABLE_SCRIPT_DESCRIPTIONS.get(script_name, "Run this script")
        print(f"  {script_name:<20} - {description}")

def get_system_python_command():
    """Get the system Python command (python3 or python)"""
    # Check python3 first (preferred)
    if shutil.which('python3'):
        return 'python3'
    # Fall back to python
    if shutil.which('python'):
        return 'python'
    # Last resort - use whatever ran this script
    return sys.executable


def get_venv_python():
    """Get the virtual environment Python executable"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"

    if os.name == 'nt':  # Windows
        venv_python = venv_dir / "Scripts" / "python.exe"
    else:  # Unix/Linux/Mac
        venv_python = venv_dir / "bin" / "python"

    return venv_python


def ensure_venv():
    """Ensure virtual environment exists"""
    skill_dir = Path(__file__).parent.parent
    venv_dir = skill_dir / ".venv"
    setup_script = skill_dir / "scripts" / "setup_environment.py"

    # Check if venv exists
    if not venv_dir.exists():
        print("🔧 First-time setup: Creating virtual environment...")
        print("   This may take a minute...")

        # Run setup with system Python
        result = subprocess.run([sys.executable, str(setup_script)])
        if result.returncode != 0:
            print("❌ Failed to set up environment")
            sys.exit(1)

        print("✅ Environment ready!")

    return get_venv_python()


def main():
    """Main runner"""
    if len(sys.argv) < 2:
        python_cmd = get_system_python_command()
        print(f"Usage: {python_cmd} run.py <script_name> [args...]")
        print("\nAvailable scripts:")
        print_available_scripts()
        sys.exit(1)

    script_name = sys.argv[1]
    script_args = sys.argv[2:]

    # Handle both "Infrastructure/scripts/script.py" and "script.py" formats
    if script_name.startswith('Infrastructure/scripts/'):
        # Remove the Infrastructure/scripts/ prefix if provided
        script_name = script_name[8:]  # len('Infrastructure/scripts/') = 8

    # Ensure .py extension
    if not script_name.endswith('.py'):
        script_name += '.py'

    # Get script path
    skill_dir = Path(__file__).parent.parent
    script_path = skill_dir / "scripts" / script_name

    if not script_path.exists():
        print(f"❌ Script not found: {script_name}")
        print(f"   Working directory: {Path.cwd()}")
        print(f"   Skill directory: {skill_dir}")
        print(f"   Looked for: {script_path}")
        sys.exit(1)

    # Ensure venv exists and get Python executable
    venv_python = ensure_venv()

    # Build command
    cmd = [str(venv_python), str(script_path)] + script_args

    # Run the script
    try:
        result = subprocess.run(cmd)
        sys.exit(result.returncode)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
