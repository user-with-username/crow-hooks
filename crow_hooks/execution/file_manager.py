from pathlib import Path
from typing import List


class FileManager:
    """Class for managing project files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root

    def find_files_by_patterns(self, patterns: List[str]) -> List[str]:
        """Finds files by patterns."""
        found_files = []
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if file_path.is_file():
                    found_files.append(str(file_path.relative_to(self.project_root)))
        return found_files
