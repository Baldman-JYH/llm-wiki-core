from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
import subprocess


@dataclass(frozen=True)
class ObsidianCliRunResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str


class ObsidianCliRunner(Protocol):
    def run(self, argv: list[str], timeout_seconds: int) -> ObsidianCliRunResult:
        ...


class SubprocessObsidianCliRunner:
    def run(self, argv: list[str], timeout_seconds: int) -> ObsidianCliRunResult:
        completed = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=False,
            timeout=timeout_seconds,
            check=False,
        )
        return ObsidianCliRunResult(
            argv=list(argv),
            returncode=completed.returncode,
            stdout=completed.stdout,
            stderr=completed.stderr,
        )


@dataclass(frozen=True)
class ObsidianCliProfile:
    executable: str
    vault_selector: str
    timeout_seconds: int = 10

    def help_argv(self) -> list[str]:
        return [self.executable, "--help"]

    def vault_info_path_argv(self) -> list[str]:
        return [self.executable, self._vault_arg(), "vault", "info=path"]

    def read_argv(self, relative_path: str) -> list[str]:
        return [self.executable, self._vault_arg(), "read", f"path={relative_path}"]

    def write_argv(self, relative_path: str, content: str) -> list[str]:
        return [
            self.executable,
            self._vault_arg(),
            "create",
            f"path={relative_path}",
            f"content={content}",
            "overwrite",
        ]

    def append_argv(self, relative_path: str, content: str) -> list[str]:
        return [
            self.executable,
            self._vault_arg(),
            "append",
            f"path={relative_path}",
            f"content={content}",
        ]

    def files_argv(self, root: str = "wiki") -> list[str]:
        return [self.executable, self._vault_arg(), "files", f"folder={root}"]

    def search_argv(self, query: str, root: str = "wiki") -> list[str]:
        return [
            self.executable,
            self._vault_arg(),
            "search:context",
            f"query={query}",
            f"path={root}",
        ]

    def _vault_arg(self) -> str:
        return f"vault={self.vault_selector}"
