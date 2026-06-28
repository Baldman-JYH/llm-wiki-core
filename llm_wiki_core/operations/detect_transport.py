from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import os
import platform
from pathlib import Path
import shutil


SNAPSHOT_PATH = Path(".vault-meta") / "transport.json"
PROBE_PATH = Path(".vault-meta") / "obsidian-cli-probe.md"
PROBE_BASE = "llm-wiki-core obsidian probe\n"
PROBE_APPEND = "append-ok\n"
REQUIRED_OBSIDIAN_CAPABILITIES = ("read", "write", "append", "list", "search")


@dataclass(frozen=True)
class TransportAvailability:
    available: bool
    executable: str | None = None
    implemented: bool = False
    reason: str = ""
    capabilities: dict[str, bool] = field(default_factory=dict)
    vault_selector: str | None = None
    transport_kind: str = ""


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


def detect_transport(
    vault_root: str | Path,
    force: bool = False,
    runner: object | None = None,
    which: object | None = None,
) -> TransportDetectionResult:
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

    snapshot = _detect_snapshot(root, runner=runner, which=which)
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


def _detect_snapshot(root: Path, runner: object | None = None, which: object | None = None) -> TransportSnapshot:
    which_fn = which or shutil.which
    official_executable = which_fn("obsidian")
    legacy_executable = which_fn("obsidian-cli")

    official_availability = _detect_official_obsidian(root, official_executable, runner)
    legacy_availability = _detect_legacy_obsidian_cli(legacy_executable)

    preferred = "obsidian" if official_availability.implemented else "filesystem"
    fallback_chain = ["obsidian", "filesystem"] if official_availability.implemented else ["filesystem"]

    return TransportSnapshot(
        schema_version=1,
        detected_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        platform=platform.system() or "unknown",
        vault_root=str(root.resolve()).replace("\\", "/"),
        preferred=preferred,
        fallback_chain=fallback_chain,
        available={
            "obsidian": official_availability,
            "obsidian-cli": legacy_availability,
            "filesystem": TransportAvailability(
                available=True,
                executable=None,
                implemented=True,
                reason="filesystem transport is implemented and used as the MVP runtime transport.",
                transport_kind="filesystem",
            ),
        },
        manual_override=None,
    )


def _detect_official_obsidian(
    root: Path,
    executable: str | None,
    runner: object | None,
) -> TransportAvailability:
    capabilities = _empty_capabilities()
    if not executable:
        return TransportAvailability(
            available=False,
            executable=None,
            implemented=False,
            reason="official Obsidian CLI executable was not detected.",
            capabilities=capabilities,
            vault_selector=root.name,
            transport_kind="official",
        )

    implemented, probed_capabilities, vault_selector, reason = _probe_official_obsidian(root, executable, runner)
    return TransportAvailability(
        available=True,
        executable=_normalize_executable_path(executable),
        implemented=implemented,
        reason=reason,
        capabilities=probed_capabilities,
        vault_selector=vault_selector,
        transport_kind="official",
    )


def _detect_legacy_obsidian_cli(executable: str | None) -> TransportAvailability:
    return TransportAvailability(
        available=executable is not None,
        executable=_normalize_executable_path(executable) if executable else None,
        implemented=False,
        reason=(
            "legacy obsidian-cli detected but remains metadata-only and unimplemented in R2."
            if executable
            else "legacy obsidian-cli executable was not detected."
        ),
        capabilities={},
        vault_selector=None,
        transport_kind="legacy",
    )


def _empty_capabilities() -> dict[str, bool]:
    return {name: False for name in REQUIRED_OBSIDIAN_CAPABILITIES}


def _probe_official_obsidian(
    root: Path,
    executable: str,
    runner: object | None,
) -> tuple[bool, dict[str, bool], str, str]:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport, ObsidianCliTransportError
    from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliProfile

    vault_selector = root.name
    capabilities = _empty_capabilities()
    profile = ObsidianCliProfile(executable=executable, vault_selector=vault_selector)
    transport = ObsidianCliTransport(
        root,
        executable=executable,
        vault_selector=vault_selector,
        runner=runner,
    )

    try:
        binding_result = transport.runner.run(
            profile.vault_info_path_argv(),
            timeout_seconds=profile.timeout_seconds,
        )
        if binding_result.returncode != 0:
            message = binding_result.stderr.strip() or "vault binding probe failed"
            return False, capabilities, vault_selector, f"official Obsidian CLI probe failed: {message}"

        bound_path = binding_result.stdout.strip()
        expected_root = _normalize_path_for_compare(root)
        actual_root = _normalize_path_for_compare(bound_path)
        if not bound_path or actual_root != expected_root:
            return (
                False,
                capabilities,
                vault_selector,
                "official Obsidian CLI probe failed: selector is bound to a different vault path "
                f"(expected {expected_root}, got {actual_root or '<empty>'}).",
            )

        help_result = transport.runner.run(profile.help_argv(), timeout_seconds=profile.timeout_seconds)
        if help_result.returncode != 0:
            message = help_result.stderr.strip() or "help probe failed"
            return False, capabilities, vault_selector, f"official Obsidian CLI probe failed: {message}"

        index_text = transport.read_text("wiki/index.md")
        if "# Wiki Index" not in index_text:
            return (
                False,
                capabilities,
                vault_selector,
                "official Obsidian CLI probe failed: wiki/index.md did not match this vault.",
            )
        capabilities["read"] = True

        transport.write_text(PROBE_PATH, PROBE_BASE)
        capabilities["write"] = True
        transport.append_text(PROBE_PATH, PROBE_APPEND)
        capabilities["append"] = True

        probe_text = transport.read_text(PROBE_PATH)
        if PROBE_BASE not in probe_text or PROBE_APPEND.strip() not in probe_text:
            return (
                False,
                capabilities,
                vault_selector,
                "official Obsidian CLI probe failed: write/append round trip mismatch.",
            )

        markdown_files = transport.list_markdown("wiki")
        capabilities["list"] = "wiki/index.md" in markdown_files
        search_results = transport.search_text("Wiki", "wiki")
        capabilities["search"] = bool(search_results)
    except ObsidianCliTransportError as error:
        return False, capabilities, vault_selector, f"official Obsidian CLI probe failed: {error}"
    finally:
        probe_file = root / PROBE_PATH
        if probe_file.exists():
            probe_file.unlink()

    implemented = all(capabilities.values())
    reason = (
        "official Obsidian CLI verified for this vault."
        if implemented
        else "official Obsidian CLI probe failed: one or more capabilities were unavailable."
    )
    return implemented, capabilities, vault_selector, reason


def _normalize_executable_path(executable: str) -> str:
    if executable == Path(executable).name:
        return executable
    try:
        return str(Path(executable).resolve()).replace("\\", "/")
    except OSError:
        return executable.replace("\\", "/")


def _normalize_path_for_compare(path_value: str | Path) -> str:
    try:
        normalized = str(Path(path_value).resolve()).replace("\\", "/")
    except OSError:
        normalized = str(path_value).replace("\\", "/")
    return os.path.normcase(normalized)


def _load_snapshot(path: Path) -> TransportSnapshot:
    data = json.loads(path.read_text(encoding="utf-8"))
    available = {
        name: TransportAvailability(
            available=bool(value.get("available", False)),
            executable=value.get("executable"),
            implemented=bool(value.get("implemented", name == "filesystem")),
            reason=str(value.get("reason", "")),
            capabilities={
                str(capability_name): bool(enabled)
                for capability_name, enabled in value.get("capabilities", {}).items()
            },
            vault_selector=value.get("vault_selector"),
            transport_kind=str(
                value.get(
                    "transport_kind",
                    "filesystem" if name == "filesystem" else "",
                )
            ),
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
                "capabilities": availability.capabilities,
                "vault_selector": availability.vault_selector,
                "transport_kind": availability.transport_kind,
            }
            for name, availability in snapshot.available.items()
        },
        "manual_override": snapshot.manual_override,
    }
