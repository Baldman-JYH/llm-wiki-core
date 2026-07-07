from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_wiki_core.operations.ingest import (
    IngestResult,
    _load_manifest,
    _normalize_source_path,
    _title_from_source_path,
    ingest_source,
)
from llm_wiki_core.vault.routes import page_path_for_title
from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class BatchIngestItem:
    source_path: str
    status: str
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    error_type: str | None = None
    error_message: str | None = None


@dataclass(frozen=True)
class BatchIngestResult:
    operation: str
    status: str
    root_path: str
    total: int
    succeeded: int
    skipped: int
    failed: int
    items: list[BatchIngestItem] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def ingest_batch(
    vault_root: str | Path,
    source_root: str | Path,
    force: bool = False,
    transport: object | None = None,
) -> BatchIngestResult:
    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    raw_root = _validate_raw_source_root(_normalize_source_path(source_root))

    source_paths = _discover_markdown(active_transport, raw_root)
    if not source_paths:
        if _root_is_missing(active_transport, raw_root):
            raise FileNotFoundError(f"Raw source root not found under .raw/: {raw_root}")
        return BatchIngestResult(
            operation="ingest-batch",
            status="empty",
            root_path=raw_root,
            total=0,
            succeeded=0,
            skipped=0,
            failed=0,
            next_suggested_action="Add Markdown files under .raw/ and run ingest-batch again.",
        )

    items: list[BatchIngestItem] = []
    claimed_targets: dict[str, str] = {}
    for source_path in source_paths:
        target_page = _target_source_page(source_path)
        conflicting_source = claimed_targets.get(target_page)
        if conflicting_source is not None:
            items.append(
                BatchIngestItem(
                    source_path=source_path,
                    status="failed",
                    error_type="ValueError",
                    error_message=(
                        f"Source page conflict: {source_path} and {conflicting_source} both map to {target_page}"
                    ),
                )
            )
            continue

        claimed_targets[target_page] = source_path
        try:
            manifest_conflict = _find_manifest_conflicting_source(active_transport, source_path, target_page)
            if manifest_conflict is not None:
                raise ValueError(
                    f"Source page conflict: {target_page} is already owned by {manifest_conflict}; "
                    f"refusing to ingest {source_path}"
                )
            result = ingest_source(root, source_path, force=force, transport=active_transport)
        except Exception as error:  # noqa: BLE001 - batch mode must record per-source failures.
            items.append(
                BatchIngestItem(
                    source_path=source_path,
                    status="failed",
                    error_type=type(error).__name__,
                    error_message=str(error),
                )
            )
            continue

        items.append(_item_from_ingest_result(result))

    succeeded = sum(1 for item in items if item.status == "success")
    skipped = sum(1 for item in items if item.status == "skipped")
    failed = sum(1 for item in items if item.status == "failed")

    return BatchIngestResult(
        operation="ingest-batch",
        status=_batch_status(succeeded=succeeded, skipped=skipped, failed=failed),
        root_path=raw_root,
        total=len(items),
        succeeded=succeeded,
        skipped=skipped,
        failed=failed,
        items=items,
        next_suggested_action="Query the wiki, lint the vault, or ingest another batch.",
    )


def _validate_raw_source_root(raw_relative: Path) -> str:
    raw_path = raw_relative.as_posix()
    parts = raw_relative.parts
    if not parts or parts[0] != ".raw":
        raise ValueError(f"source_root must be .raw/ or under .raw/: {raw_path}")
    if ".." in parts:
        raise ValueError(f"source_root under .raw/ must not contain '..': {raw_path}")
    return ".raw" if len(parts) == 1 else raw_path


def _discover_markdown(transport: object, raw_root: str) -> list[str]:
    if raw_root.lower().endswith(".md"):
        if not transport.exists(raw_root):  # type: ignore[attr-defined]
            raise FileNotFoundError(f"Raw source root not found under .raw/: {raw_root}")
        return [raw_root]
    return sorted(transport.list_markdown(raw_root))  # type: ignore[attr-defined]


def _root_is_missing(transport: object, raw_root: str) -> bool:
    try:
        return not transport.exists(raw_root)  # type: ignore[attr-defined]
    except Exception as error:  # noqa: BLE001 - transport-specific directory probes may not be supported.
        return _is_missing_error(error)


def _is_missing_error(error: Exception) -> bool:
    message = str(error).casefold()
    return "not found" in message or "no such" in message or "missing" in message


def _target_source_page(source_path: str) -> str:
    title = _title_from_source_path(_normalize_source_path(source_path))
    return page_path_for_title("source", title)


def _find_manifest_conflicting_source(transport: object, source_path: str, target_page: str) -> str | None:
    manifest = _load_manifest(transport)
    current_source = _validate_raw_source_root(_normalize_source_path(source_path))
    sources = manifest["sources"]

    for manifest_key, record in sources.items():
        generated_pages = record.get("generated_pages", [])
        if target_page not in generated_pages:
            continue

        recorded_source = record.get("source_path") or f".raw/{manifest_key}"
        if recorded_source != current_source:
            return str(recorded_source)

    return None


def _item_from_ingest_result(result: IngestResult) -> BatchIngestItem:
    return BatchIngestItem(
        source_path=result.source_path,
        status=result.status,
        files_created=list(result.files_created),
        files_updated=list(result.files_updated),
        files_skipped=list(result.files_skipped),
    )


def _batch_status(succeeded: int, skipped: int, failed: int) -> str:
    if failed == 0:
        return "success"
    if succeeded or skipped:
        return "partial"
    return "failed"
