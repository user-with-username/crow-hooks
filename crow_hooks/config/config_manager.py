import os
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import toml


class ConfigurationManager:
    """Class for working with configuration files."""

    @staticmethod
    def load_toml(path: Path) -> Dict[str, Any]:
        """Loads TOML configuration."""
        if toml is None:
            return {}
        try:
            return toml.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return {}

    @staticmethod
    def find_executable(names: List[str]) -> Optional[str]:
        """Finds executable in system."""
        for name in names:
            path = shutil.which(name)
            if path:
                return path
        return None
