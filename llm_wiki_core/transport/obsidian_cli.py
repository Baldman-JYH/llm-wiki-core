from __future__ import annotations

from pathlib import Path
import subprocess

from llm_wiki_core.transport.filesystem import PathOutsideVaultError, SearchResult, _is_relative_to
from llm_wiki_core.transport.obsidian_cli_runner import (
    ObsidianCliProfile,
    ObsidianCliRunResult,
    ObsidianCliRunner,
    SubprocessObsidianCliRunner,
)


class ObsidianCliTransportError(Exception):
    """Base error for official Obsidian CLI transport operations."""


class ObsidianCliCommandError(ObsidianCliTransportError):
    """Raised when an Obsidian CLI command exits non-zero."""


class ObsidianCliTimeoutError(ObsidianCliTransportError):
    """Raised when an Obsidian CLI command times out."""


class ObsidianCliParseError(ObsidianCliTransportError):
    """Raised when Obsidian CLI output cannot be parsed."""


class ObsidianCliTransport:
    def __init__(
        self,
        vault_root: str | Path,
        executable: str = "obsidian",
        vault_selector: str | None = None,
        runner: ObsidianCliRunner | None = None,
        timeout_seconds: int = 10,
    ) -> None:
        self.vault_root = Path(vault_root).resolve()
        self.vault_selector = vault_selector or self.vault_root.name
        self.profile = ObsidianCliProfile(
            executable=executable,
            vault_selector=self.vault_selector,
            timeout_seconds=timeout_seconds,
        )
        self.runner = runner or SubprocessObsidianCliRunner()

    def read_text(self, relative_path: str | Path) -> str:
        path = self._normalize_vault_relative_path(relative_path)
        result = self._run("read", self.profile.read_argv(path))
        return result.stdout

    def write_text(self, relative_path: str | Path, content: str) -> str:
        path = self._normalize_vault_relative_path(relative_path)
        self._run("write", self.profile.write_argv(path, content))
        return path

    def append_text(self, relative_path: str | Path, content: str) -> str:
        path = self._normalize_vault_relative_path(relative_path)
        self._run("append", self.profile.append_argv(path, content))
        return path

    def exists(self, relative_path: str | Path) -> bool:
        path = self._normalize_vault_relative_path(relative_path)
        try:
            self._run("read", self.profile.read_argv(path))
        except ObsidianCliCommandError as error:
            message = str(error).casefold()
            if "not found" in message or "no such" in message or "missing" in message:
                return False
            raise
        return True

    def list_markdown(self, root: str | Path = "wiki") -> list[str]:
        root_path = self._normalize_vault_relative_path(root)
        result = self._run("files", self.profile.files_argv(root_path))
        paths = [line.strip() for line in result.stdout.splitlines() if line.strip()]
        return sorted(path for path in paths if path.lower().endswith(".md"))

    def search_text(self, query: str, root: str | Path = "wiki") -> list[SearchResult]:
        if not query:
            return []

        root_path = self._normalize_vault_relative_path(root)
        result = self._run("search", self.profile.search_argv(query, root_path))
        return _parse_search_results(result.stdout)

    def _run(self, operation: str, argv: list[str]) -> ObsidianCliRunResult:
        try:
            result = self.runner.run(argv, timeout_seconds=self.profile.timeout_seconds)
        except subprocess.TimeoutExpired as error:
            raise ObsidianCliTimeoutError(
                f"obsidian {operation} timed out after {self.profile.timeout_seconds}s"
            ) from error

        if result.returncode != 0:
            stderr = result.stderr.strip() or "no stderr"
            raise ObsidianCliCommandError(
                f"obsidian {operation} failed with exit {result.returncode}: {stderr}"
            )
        return result

    def _normalize_vault_relative_path(self, relative_path: str | Path) -> str:
        raw_path = Path(relative_path)
        if raw_path.is_absolute():
            raise PathOutsideVaultError(f"Path must be vault-relative: {raw_path}")

        resolved = (self.vault_root / raw_path).resolve()
        if not _is_relative_to(resolved, self.vault_root):
            raise PathOutsideVaultError(f"Path resolves outside vault: {relative_path}")
        return raw_path.as_posix()


def _parse_search_results(output: str) -> list[SearchResult]:
    results: list[SearchResult] = []
    for line in output.splitlines():
        if not line.strip():
            continue

        parts = line.split(":", 2)
        if len(parts) != 3:
            raise ObsidianCliParseError(f"Cannot parse search result line: {line}")

        path, line_number, text = parts
        try:
            parsed_line_number = int(line_number)
        except ValueError as error:
            raise ObsidianCliParseError(f"Cannot parse search result line number: {line}") from error

        results.append(SearchResult(path=path, line_number=parsed_line_number, line=text))
    return results
