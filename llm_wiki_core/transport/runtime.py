from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from llm_wiki_core.transport.filesystem import FilesystemTransport


TRANSPORT_SNAPSHOT_PATH = Path(".vault-meta") / "transport.json"


@dataclass(frozen=True)
class RuntimeTransportSelection:
    name: str
    transport: FilesystemTransport
    warnings: list[str] = field(default_factory=list)
    snapshot_preferred: str | None = None


def select_runtime_transport(vault_root: str | Path) -> RuntimeTransportSelection:
    root = Path(vault_root)
    filesystem = FilesystemTransport(root)
    snapshot_path = root / TRANSPORT_SNAPSHOT_PATH

    if not snapshot_path.exists():
        return RuntimeTransportSelection(name="filesystem", transport=filesystem)

    try:
        snapshot = json.loads(snapshot_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        return RuntimeTransportSelection(
            name="filesystem",
            transport=filesystem,
            warnings=[f"Transport snapshot is not valid JSON: {error.msg}; using filesystem."],
        )

    preferred = snapshot.get("preferred")
    preferred_name = preferred if isinstance(preferred, str) else None
    warnings = _warnings_for_snapshot(snapshot, preferred_name)

    return RuntimeTransportSelection(
        name="filesystem",
        transport=filesystem,
        warnings=warnings,
        snapshot_preferred=preferred_name,
    )


def _warnings_for_snapshot(snapshot: dict[str, object], preferred_name: str | None) -> list[str]:
    if preferred_name in (None, "filesystem"):
        return []

    available = snapshot.get("available", {})
    if not isinstance(available, dict):
        return [f"Preferred transport '{preferred_name}' has no availability metadata; using filesystem."]

    preferred_metadata = available.get(preferred_name, {})
    if not isinstance(preferred_metadata, dict):
        return [f"Preferred transport '{preferred_name}' has invalid metadata; using filesystem."]

    is_available = bool(preferred_metadata.get("available", False))
    is_implemented = bool(preferred_metadata.get("implemented", False))

    if not is_available:
        return [f"Preferred transport '{preferred_name}' is not available; using filesystem."]
    if not is_implemented:
        return [f"Preferred transport '{preferred_name}' is not implemented; using filesystem."]
    return [f"Preferred transport '{preferred_name}' is not supported by the MVP runtime selector; using filesystem."]

