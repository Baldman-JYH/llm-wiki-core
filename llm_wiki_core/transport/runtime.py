from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from llm_wiki_core.transport.filesystem import FilesystemTransport
from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport


TRANSPORT_SNAPSHOT_PATH = Path(".vault-meta") / "transport.json"
REQUIRED_OBSIDIAN_CAPABILITIES = ("read", "write", "append", "list", "search")


@dataclass(frozen=True)
class RuntimeTransportSelection:
    name: str
    transport: object
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

    if preferred_name == "obsidian":
        obsidian_result = _obsidian_transport_from_snapshot(root, snapshot)
        if isinstance(obsidian_result, RuntimeTransportSelection):
            return obsidian_result
        warnings = obsidian_result
    else:
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

    if preferred_name == "obsidian-cli":
        return ["Preferred transport 'obsidian-cli' is a legacy CLI and is not implemented by R2; using filesystem."]

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


def _obsidian_transport_from_snapshot(
    root: Path, snapshot: dict[str, object]
) -> RuntimeTransportSelection | list[str]:
    available = snapshot.get("available", {})
    if not isinstance(available, dict):
        return ["Preferred transport 'obsidian' has no availability metadata; using filesystem."]

    metadata = available.get("obsidian", {})
    if not isinstance(metadata, dict):
        return ["Preferred transport 'obsidian' has invalid metadata; using filesystem."]

    if not bool(metadata.get("available", False)):
        return ["Preferred transport 'obsidian' is not available; using filesystem."]
    if not bool(metadata.get("implemented", False)):
        return ["Preferred transport 'obsidian' is not implemented; using filesystem."]

    capabilities = metadata.get("capabilities", {})
    if not isinstance(capabilities, dict) or not all(
        bool(capabilities.get(name)) for name in REQUIRED_OBSIDIAN_CAPABILITIES
    ):
        return ["Preferred transport 'obsidian' is missing required capabilities; using filesystem."]

    executable = metadata.get("executable")
    if not isinstance(executable, str) or not executable:
        return ["Preferred transport 'obsidian' has no executable metadata; using filesystem."]

    vault_selector = metadata.get("vault_selector")
    if not isinstance(vault_selector, str) or not vault_selector:
        return ["Preferred transport 'obsidian' has no vault selector metadata; using filesystem."]

    return RuntimeTransportSelection(
        name="obsidian",
        transport=ObsidianCliTransport(root, executable=executable, vault_selector=vault_selector),
        snapshot_preferred="obsidian",
    )
