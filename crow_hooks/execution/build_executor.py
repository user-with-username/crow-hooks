import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional


class BuildExecutor:
    """Class for executing build commands."""

    def __init__(
        self, project_root: Path, environment: Optional[Dict[str, str]] = None
    ):
        self.project_root = project_root
        self.environment = dict(environment or os.environ)
        self.crow_cli = shutil.which("crow")

    def execute_command(
        self,
        command: List[str],
        check_success: bool = True,
        capture_output: bool = False,
        custom_environment: Optional[Dict[str, str]] = None,
        working_directory: Optional[str] = None,
    ) -> subprocess.CompletedProcess:
        """Executes system command."""
        final_environment = dict(self.environment)
        if custom_environment:
            final_environment.update(custom_environment)

        print("[build] executing:", " ".join(command))

        return subprocess.run(
            command,
            check=check_success,
            capture_output=capture_output,
            env=final_environment,
            cwd=(working_directory or str(self.project_root)),
        )

    def execute_shell_command(
        self, command: str, **kwargs
    ) -> subprocess.CompletedProcess:
        """Executes shell command."""
        shell_path = shutil.which("sh") or "/bin/sh"
        return self.execute_command([shell_path, "-c", command], **kwargs)

    def execute_crow_command(
        self, arguments: List[str], **kwargs
    ) -> subprocess.CompletedProcess:
        """Executes crow CLI command."""
        if not self.crow_cli:
            raise RuntimeError("crow CLI not found in system")
        return self.execute_command([self.crow_cli] + arguments, **kwargs)
