from __future__ import annotations

from pathlib import Path


class ObsidianCliTransportNotImplementedError(NotImplementedError):
    """Raised when the contract-only Obsidian CLI transport is used."""


class ObsidianCliTransport:
    def __init__(self, vault_root: str | Path) -> None:
        self.vault_root = Path(vault_root)

    def read_text(self, relative_path: str | Path) -> str:
        raise _not_implemented_error()

    def write_text(self, relative_path: str | Path, content: str) -> str:
        raise _not_implemented_error()

    def append_text(self, relative_path: str | Path, content: str) -> str:
        raise _not_implemented_error()

    def exists(self, relative_path: str | Path) -> bool:
        raise _not_implemented_error()

    def list_markdown(self, root: str | Path = "wiki") -> list[str]:
        raise _not_implemented_error()

    def search_text(self, query: str, root: str | Path = "wiki") -> list[object]:
        raise _not_implemented_error()


def _not_implemented_error() -> ObsidianCliTransportNotImplementedError:
    return ObsidianCliTransportNotImplementedError(
        "Obsidian CLI transport is a contract boundary only; actual read/write/search is not implemented in this MVP."
    )

