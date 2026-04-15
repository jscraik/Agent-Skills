import os
from pathlib import Path
from typing import Optional

def find_repo_root(start_path: Optional[Path] = None) -> Path:
    """Search upwards for the nearest .git directory."""
    current = Path(start_path or os.getcwd()).resolve()
    
    for parent in [current, *current.parents]:
        if (parent / ".git").exists():
            return parent
            
    # Fallback to current directory if no .git found
    return current
