import os
from pathlib import Path
from typing import List


class SourceDiscoverer:
    """Class for discovering project source files."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.build_dir = Path(
            os.environ.get("CROW_BUILD_DIR", str(project_root / "build"))
        )

    def discover_source_files(self, patterns: List[str] = None) -> List[str]:
        """Discovers source files by patterns."""
        if patterns is None:
            patterns = ["**/*.c", "**/*.cc", "**/*.cpp", "**/*.cxx", "**/*.c++"]

        sources = []
        for pattern in patterns:
            for file_path in self.project_root.glob(pattern):
                if self.build_dir in file_path.parents:
                    continue
                if file_path.is_file():
                    sources.append(str(file_path.relative_to(self.project_root)))

        sources.sort()
        return sources

    def discover_include_directories(self) -> List[str]:
        """Discovers header file directories."""
        common_dirs = ["include", "inc", "src", "headers"]
        found_dirs = []

        for dir_name in common_dirs:
            dir_path = self.project_root / dir_name
            if dir_path.exists() and dir_path.is_dir():
                found_dirs.append(str(dir_path.relative_to(self.project_root)))

        for header_file in self.project_root.rglob("*.h"):
            dir_path = str(header_file.parent.relative_to(self.project_root))
            if dir_path not in found_dirs:
                found_dirs.append(dir_path)

        return found_dirs
