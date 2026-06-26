from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import platform
from pathlib import Path
import shutil


SNAPSHOT_PATH = Path(".vault-meta") / "transport.json"


@dataclass(frozen=True)
class TransportAvailability:
    available: bool
    executable: str | None = None
    implemented: bool = False
    reason: str = ""


@dataclass(frozen=True)
class TransportSnapshot:
    schema_version: int
    detected_at: str | None = None
    platform: str | None = None
    vault_root: str | None = None
    preferred: str = "filesystem"
    fallback_chain: list[str] = field(default_factory=lambda: ["filesystem"])
    available: dict[str, TransportAvailability] = field(default_factory=dict)
    manual_override: str | None = None


@dataclass(frozen=True)
class TransportDetectionResult:
    operation: str
    status: str
    snapshot: TransportSnapshot
    snapshot_path: str
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def detect_transport(vault_root: str | Path, force: bool = False) -> TransportDetectionResult:
    root = Path(vault_root)
    root.mkdir(parents=True, exist_ok=True)
    snapshot_path = root / SNAPSHOT_PATH

    if snapshot_path.exists() and not force:
        snapshot = _load_snapshot(snapshot_path)
        return TransportDetectionResult(
            operation="detect-transport",
            status="success",
            snapshot=snapshot,
            snapshot_path=SNAPSHOT_PATH.as_posix(),
            next_suggested_action="Use the preferred transport for future operations.",
        )

    snapshot = _detect_snapshot(root)
    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    existed = snapshot_path.exists()
    snapshot_path.write_text(json.dumps(_snapshot_to_json(snapshot), indent=2) + "\n", encoding="utf-8")

    return TransportDetectionResult(
        operation="detect-transport",
        status="success",
        snapshot=snapshot,
        snapshot_path=SNAPSHOT_PATH.as_posix(),
        files_created=[] if existed else [SNAPSHOT_PATH.as_posix()],
        files_updated=[SNAPSHOT_PATH.as_posix()] if existed else [],
        next_suggested_action="Use the preferred transport for future operations.",
    )


def _detect_snapshot(root: Path) -> TransportSnapshot:
    executable = shutil.which("obsidian-cli") or shutil.which("obsidian")
    obsidian_available = executable is not None

    return TransportSnapshot(
        schema_version=1,
        detected_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        platform=platform.system() or "unknown",
        vault_root=str(root.resolve()).replace("\\", "/"),
        preferred="filesystem",
        fallback_chain=["filesystem"],
        available={
            "obsidian-cli": TransportAvailability(
                available=obsidian_available,
                executable=str(Path(executable).resolve()).replace("\\", "/") if executable else None,
                implemented=False,
                reason=(
                    "obsidian-cli detected but actual read/write/search transport is not implemented in this MVP."
                    if obsidian_available
                    else "obsidian-cli executable was not detected."
                ),
            ),
            "filesystem": TransportAvailability(
                available=True,
                executable=None,
                implemented=True,
                reason="filesystem transport is implemented and used as the MVP runtime transport.",
            ),
        },
        manual_override=None,
    )


def _load_snapshot(path: Path) -> TransportSnapshot:
    data = json.loads(path.read_text(encoding="utf-8"))
    available = {
        name: TransportAvailability(
            available=bool(value.get("available", False)),
            executable=value.get("executable"),
            implemented=bool(value.get("implemented", name == "filesystem")),
            reason=str(value.get("reason", "")),
        )
        for name, value in data.get("available", {}).items()
    }
    return TransportSnapshot(
        schema_version=int(data.get("schema_version", 1)),
        detected_at=data.get("detected_at"),
        platform=data.get("platform"),
        vault_root=data.get("vault_root"),
        preferred=data.get("preferred", "filesystem"),
        fallback_chain=list(data.get("fallback_chain", ["filesystem"])),
        available=available,
        manual_override=data.get("manual_override"),
    )


def _snapshot_to_json(snapshot: TransportSnapshot) -> dict[str, object]:
    return {
        "schema_version": snapshot.schema_version,
        "detected_at": snapshot.detected_at,
        "platform": snapshot.platform,
        "vault_root": snapshot.vault_root,
        "preferred": snapshot.preferred,
        "fallback_chain": snapshot.fallback_chain,
        "available": {
            name: {
                "available": availability.available,
                "executable": availability.executable,
                "implemented": availability.implemented,
                "reason": availability.reason,
            }
            for name, availability in snapshot.available.items()
        },
        "manual_override": snapshot.manual_override,
    }
