from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from pathlib import Path

from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class IngestResult:
    operation: str
    status: str
    source_path: str
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    files_skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def ingest_source(
    vault_root: str | Path,
    source_path: str | Path,
    force: bool = False,
    transport: object | None = None,
) -> IngestResult:
    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    raw_relative = _normalize_source_path(source_path)
    raw_path = _validate_raw_source_path(raw_relative)
    if not active_transport.exists(raw_path):  # type: ignore[attr-defined]
        raise FileNotFoundError(f"Raw source not found under .raw/: {raw_path}")

    source_text = active_transport.read_text(raw_path)  # type: ignore[attr-defined]
    fingerprint = _fingerprint(source_text)
    manifest = _load_manifest(active_transport)
    source_key = raw_path[len(".raw/") :]
    title = _title_from_source_path(raw_relative)
    source_page_relative = Path("wiki") / "sources" / f"{title}.md"
    source_page_path = source_page_relative.as_posix()

    existing_record = manifest["sources"].get(source_key)
    if existing_record and existing_record.get("content_fingerprint") == fingerprint and not force:
        return IngestResult(
            operation="ingest",
            status="skipped",
            source_path=raw_path,
            files_skipped=[source_page_path],
            next_suggested_action="Use force=True to re-ingest unchanged source.",
        )

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    date = timestamp[:10]
    files_created: list[str] = []
    files_updated: list[str] = []

    source_page_content = _source_page(title, raw_path, fingerprint, source_text, date, timestamp)
    _write_text(active_transport, source_page_path, source_page_content, files_created, files_updated)

    _update_index(active_transport, title, raw_path, files_updated)
    _prepend_log(active_transport, title, raw_path, source_page_path, date, files_updated)
    _write_hot(active_transport, title, source_page_path, date, timestamp, files_updated)

    manifest["schema_version"] = 1
    manifest["updated"] = timestamp
    manifest.setdefault("sources", {})
    manifest["sources"][source_key] = {
        "source_path": raw_path,
        "source_type": "file",
        "status": "ingested",
        "first_ingested": existing_record.get("first_ingested") if existing_record else timestamp,
        "last_ingested": timestamp,
        "content_fingerprint": fingerprint,
        "generated_pages": [source_page_path],
        "updated_pages": ["wiki/index.md", "wiki/log.md", "wiki/hot.md"],
        "notes": "",
    }
    active_transport.write_text(".raw/.manifest.json", json.dumps(manifest, indent=2) + "\n")  # type: ignore[attr-defined]
    files_updated.append(".raw/.manifest.json")

    return IngestResult(
        operation="ingest",
        status="success",
        source_path=raw_path,
        files_created=files_created,
        files_updated=files_updated,
        next_suggested_action="Query the wiki or ingest another raw source.",
    )


def _normalize_source_path(source_path: str | Path) -> Path:
    raw = Path(source_path)
    if raw.is_absolute():
        parts = raw.parts
        if ".raw" in parts:
            raw_index = parts.index(".raw")
            return Path(*parts[raw_index:])
        return raw
    return raw


def _validate_raw_source_path(raw_relative: Path) -> str:
    raw_path = raw_relative.as_posix()
    parts = raw_relative.parts
    if not parts or parts[0] != ".raw" or len(parts) == 1:
        raise ValueError(f"source_path must be under .raw/: {raw_path}")
    if ".." in parts:
        raise ValueError(f"source_path under .raw/ must not contain '..': {raw_path}")
    return raw_path


def _load_manifest(transport: object) -> dict[str, object]:
    if transport.exists(".raw/.manifest.json"):  # type: ignore[attr-defined]
        return json.loads(transport.read_text(".raw/.manifest.json"))  # type: ignore[attr-defined]
    return {"schema_version": 1, "updated": "", "sources": {}}


def _fingerprint(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _title_from_source_path(source_path: Path) -> str:
    return source_path.stem.replace("-", " ").replace("_", " ").title()


def _first_non_empty_line(text: str) -> str:
    for line in text.splitlines():
        stripped = line.strip().lstrip("#").strip()
        if stripped:
            return stripped
    return "No non-empty content found."


def _source_page(title: str, source_path: str, fingerprint: str, source_text: str, date: str, timestamp: str) -> str:
    summary = _first_non_empty_line(source_text)
    return (
        "---\n"
        "type: source\n"
        f'title: "{title}"\n'
        f"created: {date}\n"
        f"updated: {timestamp}\n"
        "status: ingested\n"
        f'source_path: "{source_path}"\n'
        f'content_fingerprint: "{fingerprint}"\n'
        "---\n\n"
        f"# {title}\n\n"
        f"Raw source: `{source_path}`\n\n"
        "## Summary\n"
        f"{summary}\n\n"
        "## Source Notes\n"
        "This deterministic MVP summary captures the first non-empty source line. "
        "Richer LLM synthesis belongs in a later milestone.\n"
    )


def _write_text(transport: object, relative: str, content: str, files_created: list[str], files_updated: list[str]) -> None:
    existed = transport.exists(relative)  # type: ignore[attr-defined]
    transport.write_text(relative, content)  # type: ignore[attr-defined]
    if existed:
        files_updated.append(relative)
    else:
        files_created.append(relative)


def _update_index(transport: object, title: str, source_path: str, files_updated: list[str]) -> None:
    relative = "wiki/index.md"
    content = transport.read_text(relative) if transport.exists(relative) else "# Wiki Index\n\n## Sources\n"  # type: ignore[attr-defined]
    entry = f"- [[{title}]] — file source `{source_path}`"
    if entry not in content:
        if "## Sources" in content:
            content = content.replace("## Sources", f"## Sources\n{entry}", 1)
        else:
            content = content.rstrip() + f"\n\n## Sources\n{entry}\n"
    transport.write_text(relative, content)  # type: ignore[attr-defined]
    _append_once(files_updated, relative)


def _prepend_log(transport: object, title: str, source_path: str, source_page: str, date: str, files_updated: list[str]) -> None:
    relative = "wiki/log.md"
    existing = transport.read_text(relative) if transport.exists(relative) else "# Operation Log\n"  # type: ignore[attr-defined]
    entry = (
        f"## [{date}] ingest | {title}\n"
        f"- Source: `{source_path}`\n"
        f"- Summary: [[{title}]]\n"
        f"- Pages created: [[{title}]]\n"
        "- Pages updated: [[Wiki Index]], [[Hot Cache]]\n"
    )
    if "---\n\n# Operation Log" in existing:
        content = existing.replace("# Operation Log\n\n", f"# Operation Log\n\n{entry}\n", 1)
    else:
        content = entry + "\n" + existing
    transport.write_text(relative, content)  # type: ignore[attr-defined]
    _append_once(files_updated, relative)


def _write_hot(transport: object, title: str, source_page: str, date: str, timestamp: str, files_updated: list[str]) -> None:
    relative = "wiki/hot.md"
    content = (
        "---\n"
        "type: meta\n"
        'title: "Hot Cache"\n'
        f"created: {date}\n"
        f"updated: {timestamp}\n"
        "status: active\n"
        "---\n\n"
        "# Recent Context\n\n"
        "## Last Updated\n"
        f"{date} - Ingested [[{title}]].\n\n"
        "## Key Recent Facts\n"
        f"- Latest ingested source summary: [[{title}]].\n\n"
        "## Recent Changes\n"
        f"- Created or updated: `{source_page}`\n\n"
        "## Active Threads\n"
        "- Continue ingesting raw sources or query the wiki.\n"
    )
    transport.write_text(relative, content)  # type: ignore[attr-defined]
    _append_once(files_updated, relative)


def _append_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)
