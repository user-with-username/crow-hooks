import os
import platform
from pathlib import Path
from typing import List, Optional, Dict, Any

from ..discovery import ProjectLocator, SourceDiscoverer, CompilerDetector
from ..config import ConfigurationManager
from ..execution import BuildExecutor, FileManager
from ..compilation import BuildArtifactManager, CompilationManager


class HookContext:
    """Context available inside hook scripts - Public User API."""

    def __init__(self, start_dir: Optional[str] = None):
        self._locator = ProjectLocator(start_dir)
        self._config_manager = ConfigurationManager()

        self.start_dir = Path(start_dir or os.getcwd())
        self.project_root = self._locator.find_project_root() or self.start_dir

        self.crow_toml_path = self.project_root / "crow.toml"
        self.config = (
            self._config_manager.load_toml(self.crow_toml_path)
            if self.crow_toml_path.exists()
            else {}
        )

        self.env = dict(os.environ)

        self.build_dir = Path(
            os.environ.get("CROW_BUILD_DIR", str(self.project_root / "build"))
        )
        self.os = platform.system().lower()

        self._source_discoverer = SourceDiscoverer(self.project_root)
        self._compiler_detector = CompilerDetector()
        self._file_manager = FileManager(self.project_root)
        self._artifact_manager = BuildArtifactManager(self.project_root)
        self._build_executor = BuildExecutor(self.project_root, self.env)
        self._artifact_manager.prepare_build_directory()

        self.sources = self._source_discoverer.discover_source_files()
        self.include_dirs = self._source_discoverer.discover_include_directories()
        self.compiler = self._compiler_detector.detect_compilers()
        self.cflags = self._compiler_detector.collect_compiler_flags(self.config)

        self._compilation_manager = CompilationManager(
            self._build_executor,
            self._file_manager,
            self._artifact_manager,
            self.compiler,
            self.cflags,
            self.include_dirs,
        )

        self.targets = self._artifact_manager.artifacts

    def run(self, cmd: List[str], check=True, capture_output=False, env=None, cwd=None):
        """Execute a system command."""
        return self._build_executor.execute_command(
            cmd, check, capture_output, env, cwd
        )

    def sh(self, cmd: str, **kwargs):
        """Execute a shell command."""
        return self._build_executor.execute_shell_command(cmd, **kwargs)

    def crow(self, args: List[str], **kwargs):
        """Execute crow CLI command directly."""
        return self._build_executor.execute_crow_command(args, **kwargs)

    def find_sources(self, patterns: List[str]) -> List[str]:
        """Find source files by patterns."""
        return self._file_manager.find_files_by_patterns(patterns)

    def compile_target(
        self,
        name: str,
        sources: Optional[List[str]] = None,
        extra_cflags: Optional[List[str]] = None,
        extra_ldflags: Optional[List[str]] = None,
        cxx: bool = True,
    ) -> Path:
        """Compile an executable target."""
        return self._compilation_manager.compile_executable(
            name, sources, extra_cflags, extra_ldflags, cxx
        )

    def compile_library(
        self,
        name: str,
        sources: Optional[List[str]] = None,
        static: bool = True,
        extra_flags: Optional[List[str]] = None,
    ) -> Path:
        """Compile a library."""
        return self._compilation_manager.compile_library(
            name, sources, static, extra_flags
        )
