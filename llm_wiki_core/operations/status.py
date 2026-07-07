from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from llm_wiki_core.vault.scaffold import required_paths_for_organization
from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class StatusResult:
    operation: str
    status: str
    initialized: bool
    missing_required_paths: list[str] = field(default_factory=list)
    source_count: int = 0
    preferred_transport: str | None = None
    recent_log_entry: str = ""
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def status_wiki(vault_root: str | Path, transport: object | None = None) -> StatusResult:
    selection = None if transport is not None else select_runtime_transport(vault_root)
    active_transport = transport or selection.transport
    warnings: list[str] = list(selection.warnings) if selection else []
    required_paths = required_paths_for_organization("generic")
    missing = [path for path in required_paths if not active_transport.exists(path)]  # type: ignore[attr-defined]
    initialized = not missing

    source_count = _source_count(active_transport, warnings)
    preferred_transport = selection.name if selection else _preferred_transport(active_transport, warnings)
    recent_log_entry = _recent_log_entry(active_transport)

    return StatusResult(
        operation="status",
        status="success" if initialized else "incomplete",
        initialized=initialized,
        missing_required_paths=missing,
        source_count=source_count,
        preferred_transport=preferred_transport,
        recent_log_entry=recent_log_entry,
        warnings=warnings,
        next_suggested_action=(
            "Continue with query, ingest, save, or lint."
            if initialized
            else "Run init to create the LLM Wiki scaffold."
        ),
    )


def _source_count(transport: object, warnings: list[str]) -> int:
    if not transport.exists(".raw/.manifest.json"):  # type: ignore[attr-defined]
        return 0
    try:
        manifest = json.loads(transport.read_text(".raw/.manifest.json"))  # type: ignore[attr-defined]
    except json.JSONDecodeError as error:
        warnings.append(f"Manifest is not valid JSON: {error.msg}.")
        return 0
    sources = manifest.get("sources", {})
    return len(sources) if isinstance(sources, dict) else 0


def _preferred_transport(transport: object, warnings: list[str]) -> str | None:
    path = ".vault-meta/transport.json"
    if not transport.exists(path):  # type: ignore[attr-defined]
        return None
    try:
        snapshot = json.loads(transport.read_text(path))  # type: ignore[attr-defined]
    except json.JSONDecodeError as error:
        warnings.append(f"Transport snapshot is not valid JSON: {error.msg}.")
        return None
    preferred = snapshot.get("preferred")
    return preferred if isinstance(preferred, str) else None


def _recent_log_entry(transport: object) -> str:
    if not transport.exists("wiki/log.md"):  # type: ignore[attr-defined]
        return ""
    for line in transport.read_text("wiki/log.md").splitlines():  # type: ignore[attr-defined]
        if line.startswith("## "):
            return line
    return ""
