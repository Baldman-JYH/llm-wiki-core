from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
from llm_wiki_core.vault.routes import page_path_for_title

from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class SaveResult:
    operation: str
    status: str
    page_path: str
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


def save_insight(
    vault_root: str | Path,
    content: str,
    title: str | None = None,
    target_type: str = "question",
    transport: object | None = None,
) -> SaveResult:
    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    page_title = _title(title or content)
    page_path = _page_path_for_type(target_type, page_title)
    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    date = timestamp[:10]
    files_created: list[str] = []
    files_updated: list[str] = []

    existed = active_transport.exists(page_path)  # type: ignore[attr-defined]
    active_transport.write_text(page_path, _saved_page(target_type, page_title, content, date, timestamp))  # type: ignore[attr-defined]
    if existed:
        files_updated.append(page_path)
    else:
        files_created.append(page_path)

    _update_index(active_transport, page_title, target_type, files_updated)
    _prepend_log(active_transport, page_title, page_path, date, files_updated)
    _write_hot(active_transport, page_title, page_path, date, timestamp, files_updated)

    return SaveResult(
        operation="save",
        status="success",
        page_path=page_path,
        files_created=files_created,
        files_updated=files_updated,
        next_suggested_action="Query the wiki or continue saving durable insights.",
    )


def _page_path_for_type(target_type: str, page_title: str) -> str:
    if target_type == "question":
        return page_path_for_title("question", page_title)
    if target_type == "concept":
        return page_path_for_title("concept", page_title)
    raise ValueError("target_type must be question or concept")


def _title(value: str) -> str:
    first_line = value.strip().splitlines()[0] if value.strip() else "Saved Insight"
    words = re.findall(r"[A-Za-z0-9]+", first_line)
    return " ".join(words[:8]).title() or "Saved Insight"


def _saved_page(page_type: str, title: str, content: str, date: str, timestamp: str) -> str:
    return (
        "---\n"
        f"type: {page_type}\n"
        f'title: "{title}"\n'
        f"created: {date}\n"
        f"updated: {timestamp}\n"
        "status: seed\n"
        "---\n\n"
        f"# {title}\n\n"
        f"{content.strip()}\n"
    )


def _update_index(transport: object, title: str, target_type: str, files_updated: list[str]) -> None:
    relative = "wiki/index.md"
    section = "## Questions" if target_type == "question" else "## Concepts"
    entry = f"- [[{title}]] — saved {target_type}"
    content = transport.read_text(relative) if transport.exists(relative) else "# Wiki Index\n"  # type: ignore[attr-defined]
    if entry not in content:
        if section in content:
            content = content.replace(section, f"{section}\n{entry}", 1)
        else:
            content = content.rstrip() + f"\n\n{section}\n{entry}\n"
    transport.write_text(relative, content)  # type: ignore[attr-defined]
    _append_once(files_updated, relative)


def _prepend_log(transport: object, title: str, page_path: str, date: str, files_updated: list[str]) -> None:
    relative = "wiki/log.md"
    existing = transport.read_text(relative) if transport.exists(relative) else "# Operation Log\n"  # type: ignore[attr-defined]
    entry = (
        f"## [{date}] save | {title}\n"
        f"- Page: `{page_path}`\n"
        f"- Summary: [[{title}]]\n"
    )
    if "# Operation Log\n\n" in existing:
        content = existing.replace("# Operation Log\n\n", f"# Operation Log\n\n{entry}\n", 1)
    else:
        content = entry + "\n" + existing
    transport.write_text(relative, content)  # type: ignore[attr-defined]
    _append_once(files_updated, relative)


def _write_hot(transport: object, title: str, page_path: str, date: str, timestamp: str, files_updated: list[str]) -> None:
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
        f"{date} - Saved [[{title}]].\n\n"
        "## Key Recent Facts\n"
        f"- Latest saved wiki page: [[{title}]].\n\n"
        "## Recent Changes\n"
        f"- Created or updated: `{page_path}`\n\n"
        "## Active Threads\n"
        "- Continue query/save workflows or ingest more sources.\n"
    )
    transport.write_text(relative, content)  # type: ignore[attr-defined]
    _append_once(files_updated, relative)


def _append_once(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)
