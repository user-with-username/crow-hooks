import platform
from pathlib import Path
from typing import List, Dict, Optional, Any
from ..execution import BuildExecutor, FileManager


class CompilationManager:
    """Class for managing compilation process."""

    def __init__(
        self,
        build_executor: BuildExecutor,
        file_manager: FileManager,
        artifact_manager: "BuildArtifactManager",
        compiler_info: Dict[str, str],
        flags: Dict[str, List[str]],
        include_dirs: List[str],
    ):
        self.executor = build_executor
        self.files = file_manager
        self.artifacts = artifact_manager
        self.compilers = compiler_info
        self.flags = flags
        self.include_directories = include_dirs
        self.operating_system = platform.system().lower()

    def compile_executable(
        self,
        name: str,
        sources: Optional[List[str]] = None,
        extra_cflags: Optional[List[str]] = None,
        extra_ldflags: Optional[List[str]] = None,
        use_cpp: bool = True,
    ) -> Path:
        """Compiles executable file."""
        if self.executor.crow_cli:
            self.executor.execute_crow_command(["build", "--target", name])
            return self.artifacts.build_directory / name

        self.artifacts.prepare_build_directory()
        source_files = sources or []

        if not source_files:
            raise RuntimeError("No source files found for compilation")

        compiler = (
            self.compilers["cpp_compiler"] if use_cpp else self.compilers["c_compiler"]
        )
        output_path = self.artifacts.build_directory / name

        command = [compiler]
        command += self.flags["cpp_flags"] if use_cpp else self.flags["c_flags"]

        if extra_cflags:
            command += extra_cflags

        for include_dir in self.include_directories:
            command += ["-I", str(self.files.project_root / include_dir)]

        absolute_sources = [
            str(self.files.project_root / source) for source in source_files
        ]
        command += absolute_sources
        command += ["-o", str(output_path)]

        if extra_ldflags:
            command += extra_ldflags

        command += self.flags["linker_flags"]

        self.executor.execute_command(command)

        artifact_info = {
            "path": str(output_path),
            "sources": source_files,
            "type": "executable",
        }
        self.artifacts.register_artifact(name, artifact_info)

        return output_path

    def compile_library(
        self,
        name: str,
        sources: Optional[List[str]] = None,
        static: bool = True,
        extra_flags: Optional[List[str]] = None,
    ) -> Path:
        """Compiles library."""
        if self.executor.crow_cli:
            self.executor.execute_crow_command(["build", "--lib", name])
            return (
                self.artifacts.build_directory / f"lib{name}.{'a' if static else 'so'}"
            )

        self.artifacts.prepare_build_directory()
        source_files = sources or []

        if self.operating_system == "windows":
            return self._compile_windows_library(
                name, source_files, static, extra_flags
            )
        else:
            return self._compile_unix_library(name, source_files, static, extra_flags)

    def _compile_windows_library(
        self,
        name: str,
        sources: List[str],
        static: bool,
        extra_flags: Optional[List[str]] = None,
    ) -> Path:
        """Compiles library on Windows."""

        from ..discovery import ConfigurationManager

        output_file = self.artifacts.build_directory / (
            f"{name}.lib" if static else f"{name}.dll"
        )
        compiler = self.compilers["cpp_compiler"]
        object_files = []

        for source in sources:
            obj_file = self.artifacts.build_directory / (
                Path(source).with_suffix(".obj").name
            )
            command = [
                compiler,
                "/c",
                str(self.files.project_root / source),
                "/Fo" + str(obj_file),
            ]

            for include_dir in self.include_directories:
                command += ["/I", str(self.files.project_root / include_dir)]

            if extra_flags:
                command += extra_flags

            self.executor.execute_command(command)
            object_files.append(str(obj_file))

        if static:
            lib_tool = ConfigurationManager.find_executable(["lib"])
            if not lib_tool:
                raise RuntimeError("MSVC lib tool not found")
            self.executor.execute_command(
                [lib_tool, "/OUT:" + str(output_file)] + object_files
            )
        else:
            linker = ConfigurationManager.find_executable(["link"])
            if not linker:
                raise RuntimeError("MSVC link tool not found")
            self.executor.execute_command(
                [linker, "/DLL", "/OUT:" + str(output_file)] + object_files
            )

        return output_file

    def _compile_unix_library(
        self,
        name: str,
        sources: List[str],
        static: bool,
        extra_flags: Optional[List[str]] = None,
    ) -> Path:
        """Compiles library on Unix-like systems."""
        if static:
            return self._compile_static_library(name, sources, extra_flags)
        else:
            return self._compile_shared_library(name, sources, extra_flags)

    def _compile_static_library(
        self, name: str, sources: List[str], extra_flags: Optional[List[str]] = None
    ) -> Path:
        """Compiles static library."""

        from ..discovery import ConfigurationManager

        obj_dir = self.artifacts.build_directory / (name + "_objects")
        obj_dir.mkdir(parents=True, exist_ok=True)
        object_files = []

        for source in sources:
            source_abs = self.files.project_root / source
            obj_file = obj_dir / (Path(source).with_suffix(".o").name)

            command = [
                self.compilers["cpp_compiler"],
                "-c",
                str(source_abs),
                "-o",
                str(obj_file),
            ]
            command += self.flags["cpp_flags"]

            if extra_flags:
                command += extra_flags

            for include_dir in self.include_directories:
                command += ["-I", str(self.files.project_root / include_dir)]

            self.executor.execute_command(command)
            object_files.append(str(obj_file))

        archive_file = self.artifacts.build_directory / f"lib{name}.a"
        archiver = ConfigurationManager.find_executable(["ar", "emar"]) or "ar"
        self.executor.execute_command(
            [archiver, "rcs", str(archive_file)] + object_files
        )

        artifact_info = {
            "path": str(archive_file),
            "type": "static",
            "objects": object_files,
        }
        self.artifacts.register_artifact(name, artifact_info)

        return archive_file

    def _compile_shared_library(
        self, name: str, sources: List[str], extra_flags: Optional[List[str]] = None
    ) -> Path:
        """Compiles shared library."""
        output_file = self.artifacts.build_directory / f"lib{name}.so"
        command = [self.compilers["cpp_compiler"], "-shared"]
        command += self.flags["cpp_flags"]

        if extra_flags:
            command += extra_flags

        for source in sources:
            command.append(str(self.files.project_root / source))

        command += ["-o", str(output_file)]
        self.executor.execute_command(command)

        artifact_info = {"path": str(output_file), "type": "shared"}
        self.artifacts.register_artifact(name, artifact_info)

        return output_file
