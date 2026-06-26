from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class TransportError(Exception):
    """Base error for transport operations."""


class PathOutsideVaultError(TransportError):
    """Raised when a vault-relative path resolves outside the vault root."""


@dataclass(frozen=True)
class SearchResult:
    path: str
    line_number: int
    line: str


class FilesystemTransport:
    def __init__(self, vault_root: str | Path) -> None:
        self.vault_root = Path(vault_root).resolve()
        self.vault_root.mkdir(parents=True, exist_ok=True)

    def read_text(self, relative_path: str | Path) -> str:
        path = self._resolve_vault_path(relative_path)
        return path.read_text(encoding="utf-8")

    def write_text(self, relative_path: str | Path, content: str) -> str:
        path = self._resolve_vault_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return self._relative(path)

    def append_text(self, relative_path: str | Path, content: str) -> str:
        path = self._resolve_vault_path(relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as handle:
            handle.write(content)
        return self._relative(path)

    def exists(self, relative_path: str | Path) -> bool:
        path = self._resolve_vault_path(relative_path)
        return path.exists()

    def list_markdown(self, root: str | Path = "wiki") -> list[str]:
        directory = self._resolve_vault_path(root)
        if not directory.exists():
            return []
        if directory.is_file():
            return [self._relative(directory)] if directory.suffix.lower() == ".md" else []
        return sorted(self._relative(path) for path in directory.rglob("*.md") if path.is_file())

    def search_text(self, query: str, root: str | Path = "wiki") -> list[SearchResult]:
        needle = query.casefold()
        if not needle:
            return []

        results: list[SearchResult] = []
        for relative in self.list_markdown(root):
            path = self._resolve_vault_path(relative)
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                if needle in line.casefold():
                    results.append(SearchResult(path=relative, line_number=line_number, line=line))
        return results

    def _resolve_vault_path(self, relative_path: str | Path) -> Path:
        raw_path = Path(relative_path)
        if raw_path.is_absolute():
            raise PathOutsideVaultError(f"Path must be vault-relative: {raw_path}")

        resolved = (self.vault_root / raw_path).resolve()
        if not _is_relative_to(resolved, self.vault_root):
            raise PathOutsideVaultError(f"Path resolves outside vault: {relative_path}")
        return resolved

    def _relative(self, path: Path) -> str:
        return path.relative_to(self.vault_root).as_posix()


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
