from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class ContinueResult:
    operation: str
    status: str
    hot_context: str = ""
    index_context: str = ""
    recent_log_entries: list[str] = field(default_factory=list)
    files_read: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def continue_wiki(vault_root: str | Path, transport: object | None = None) -> ContinueResult:
    selection = None if transport is not None else select_runtime_transport(vault_root)
    active_transport = transport or selection.transport
    files_read: list[str] = []

    hot_context = _read_if_exists(active_transport, "wiki/hot.md", files_read)
    index_context = _read_if_exists(active_transport, "wiki/index.md", files_read)
    log_context = _read_if_exists(active_transport, "wiki/log.md", files_read)
    recent_log_entries = _recent_log_entries(log_context)
    has_context = bool(hot_context or index_context or log_context)

    return ContinueResult(
        operation="continue",
        status="success" if has_context else "needs_init",
        hot_context=hot_context,
        index_context=index_context,
        recent_log_entries=recent_log_entries,
        files_read=files_read,
        warnings=list(selection.warnings) if selection else [],
        next_suggested_action=(
            "Use hot and index context before query, ingest, save, or lint."
            if has_context
            else "Run init to create the LLM Wiki scaffold."
        ),
    )


def _read_if_exists(transport: object, relative_path: str, files_read: list[str]) -> str:
    if not transport.exists(relative_path):  # type: ignore[attr-defined]
        return ""
    files_read.append(relative_path)
    return transport.read_text(relative_path)  # type: ignore[attr-defined]


def _recent_log_entries(log_context: str, limit: int = 5) -> list[str]:
    entries = [line for line in log_context.splitlines() if line.startswith("## ")]
    return entries[:limit]
