import os
import platform
from typing import Dict, Any, List, Optional
from ..config import ConfigurationManager


class CompilerDetector:
    """Class for detecting and configuring compilers."""

    def __init__(self):
        self.config_manager = ConfigurationManager()

    def detect_compilers(self) -> Dict[str, str]:
        """Detects available compilers."""
        if platform.system().lower() == "windows":
            msvc_compiler = self.config_manager.find_executable(["cl"])
            if msvc_compiler:
                return {"c_compiler": msvc_compiler, "cpp_compiler": msvc_compiler}

        c_compiler = (
            os.environ.get("CC")
            or self.config_manager.find_executable(["cc", "gcc", "clang"])
            or "cc"
        )

        cpp_compiler = (
            os.environ.get("CXX")
            or self.config_manager.find_executable(["c++", "g++", "clang++"])
            or "c++"
        )

        return {"c_compiler": c_compiler, "cpp_compiler": cpp_compiler}

    def collect_compiler_flags(self, config: Dict[str, Any]) -> Dict[str, List[str]]:
        """Collects compiler flags from configuration and environment variables."""
        build_config = config.get("build", {}) if isinstance(config, dict) else {}

        c_flags = build_config.get("cflags", []) or os.environ.get("CFLAGS", "").split()

        cpp_flags = (
            build_config.get("cxxflags", []) or os.environ.get("CXXFLAGS", "").split()
        )

        linker_flags = (
            build_config.get("ldflags", []) or os.environ.get("LDFLAGS", "").split()
        )

        return {
            "c_flags": [flag for flag in c_flags if flag],
            "cpp_flags": [flag for flag in cpp_flags if flag],
            "linker_flags": [flag for flag in linker_flags if flag],
        }
