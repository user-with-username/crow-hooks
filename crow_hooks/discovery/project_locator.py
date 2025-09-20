import os
from pathlib import Path
from typing import Optional


class ProjectLocator:
    """Class for locating project and its root directory."""

    def __init__(self, start_dir: Optional[str] = None):
        self.start_path = Path(start_dir or os.getcwd()).resolve()

    def find_project_root(self, marker_names=("crow.toml", ".git")) -> Optional[Path]:
        """Finds project root directory by markers."""
        current = self.start_path
        for _ in range(0, 64):
            for name in marker_names:
                candidate = current / name
                if candidate.exists():
                    return current
            if current.parent == current:
                break
            current = current.parent
        return None
