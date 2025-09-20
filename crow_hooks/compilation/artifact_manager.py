import os
from pathlib import Path
from typing import Dict, Any


class BuildArtifactManager:
    """Class for managing build artifacts."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.build_directory = Path(
            os.environ.get("CROW_BUILD_DIR", str(project_root / "build"))
        )
        self.artifacts: Dict[str, Dict[str, Any]] = {}

    def prepare_build_directory(self):
        """Prepares build directory."""
        self.build_directory.mkdir(parents=True, exist_ok=True)

    def register_artifact(self, name: str, artifact_info: Dict[str, Any]):
        """Registers created artifact."""
        self.artifacts[name] = artifact_info
