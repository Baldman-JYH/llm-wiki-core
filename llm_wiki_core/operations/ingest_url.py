from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from llm_wiki_core.operations.ingest import ingest_source
from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class UrlFetchResponse:
    requested_url: str
    final_url: str
    status_code: int
    content_type: str
    body: bytes


@dataclass(frozen=True)
class SnapshotPaths:
    snapshot_dir: str
    source_path: str
    raw_snapshot_path: str
    metadata_path: str


@dataclass(frozen=True)
class UrlIngestResult:
    operation: str
    status: str
    url: str
    source_path: str
    snapshot_path: str
    raw_snapshot_path: str
    files_created: list[str] = field(default_factory=list)
    files_updated: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    next_suggested_action: str = ""


TEXTUAL_CONTENT_TYPES = (
    "text/html",
    "text/plain",
    "text/markdown",
    "application/xhtml+xml",
    "application/xml",
    "application/json",
)

DEFAULT_TIMEOUT_SECONDS = 10
MAX_RESPONSE_BYTES = 2_000_000


def _validate_http_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("Only explicit http and https URLs are supported.")
    return url


def _decode_text_body(body: bytes, content_type: str) -> str:
    lowered = content_type.lower()
    if not any(lowered.startswith(allowed) for allowed in TEXTUAL_CONTENT_TYPES):
        raise ValueError("URL response is not supported text content.")

    charset = "utf-8"
    match = re.search(r"charset=([^;\s]+)", content_type, flags=re.IGNORECASE)
    if match:
        charset = match.group(1).strip('"')

    try:
        return body.decode(charset)
    except UnicodeDecodeError as error:
        raise ValueError("URL response could not be decoded as text.") from error


class _ReadableHtmlParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self._skip_depth = 0
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower = tag.lower()
        if lower in {"script", "style"}:
            self._skip_depth += 1
            return
        if lower in {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        lower = tag.lower()
        if lower in {"script", "style"} and self._skip_depth:
            self._skip_depth -= 1
            return
        if lower in {"p", "div", "li", "h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            self.parts.append(data)


def _extract_readable_text(text: str, content_type: str) -> str:
    if content_type.lower().startswith(("text/html", "application/xhtml+xml")):
        parser = _ReadableHtmlParser()
        parser.feed(text)
        parser.close()
        text = "".join(parser.parts)

    text = unescape(text)
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return "\n".join(line for line in lines if line)


def _build_snapshot_paths(url: str, fetched_at: datetime, content_type: str) -> SnapshotPaths:
    parsed = urlparse(url)
    host_slug = _slug(parsed.hostname or "unknown-host")
    timestamp = fetched_at.strftime("%Y%m%dT%H%M%S%f")
    date = fetched_at.date().isoformat()
    url_hash = hashlib.sha256(url.encode("utf-8")).hexdigest()[:12]
    snapshot_dir = f".raw/url/{date}/{host_slug}/{timestamp}-{url_hash}"
    raw_name = "response.html" if content_type.lower().startswith(("text/html", "application/xhtml+xml")) else "response.txt"
    return SnapshotPaths(
        snapshot_dir=snapshot_dir,
        source_path=f"{snapshot_dir}/source.md",
        raw_snapshot_path=f"{snapshot_dir}/{raw_name}",
        metadata_path=f"{snapshot_dir}/metadata.json",
    )


def _slug(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return slug or "untitled"


def _source_markdown(
    response: UrlFetchResponse,
    fetched_at: datetime,
    raw_snapshot_path: str,
    readable_text: str,
) -> str:
    fetched = fetched_at.isoformat(timespec="seconds")
    return (
        "---\n"
        "source_type: url\n"
        f'source_url: "{response.final_url}"\n'
        f"fetched_at: {fetched}\n"
        f"http_status: {response.status_code}\n"
        f'content_type: "{response.content_type}"\n'
        f'raw_snapshot_path: "{raw_snapshot_path}"\n'
        "---\n\n"
        f"# URL Source: {response.final_url}\n\n"
        f"Original URL: {response.requested_url}\n\n"
        f"Final URL: {response.final_url}\n\n"
        "## Extracted Text\n\n"
        f"{readable_text}\n"
    )


def _source_page_title(response: UrlFetchResponse, fetched_at: datetime) -> str:
    parsed = urlparse(response.final_url)
    host = parsed.hostname or "url-source"
    path_part = parsed.path.strip("/").split("/")[-1] or "source"
    base = _slug(f"{host}-{path_part}").replace("-", " ").title()
    timestamp = fetched_at.strftime("%Y%m%dT%H%M%S")
    url_hash = hashlib.sha256(response.final_url.encode("utf-8")).hexdigest()[:8]
    return f"{base} {timestamp} {url_hash}"


def _fetch_url(url: str, timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS) -> UrlFetchResponse:
    request = Request(url, headers={"User-Agent": "llm-wiki-core/0.1 URL ingest"})
    with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310 - explicit user-supplied URL ingest.
        final_url = response.geturl()
        _validate_http_url(final_url)
        body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("URL response exceeds the maximum supported size.")
        status_code = response.getcode()
        return UrlFetchResponse(
            requested_url=url,
            final_url=final_url,
            status_code=int(200 if status_code is None else status_code),
            content_type=response.headers.get("Content-Type", "text/plain; charset=utf-8"),
            body=body,
        )


def _metadata_json(response: UrlFetchResponse, fetched_at: datetime, paths: SnapshotPaths) -> str:
    return (
        json.dumps(
            {
                "source_type": "url",
                "source_url": response.final_url,
                "requested_url": response.requested_url,
                "fetched_at": fetched_at.astimezone().isoformat(timespec="seconds"),
                "http_status": response.status_code,
                "content_type": response.content_type,
                "source_path": paths.source_path,
                "raw_snapshot_path": paths.raw_snapshot_path,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def ingest_url(
    vault_root: str | Path,
    url: str,
    fetcher: Callable[[str], UrlFetchResponse] | None = None,
    now: Callable[[], datetime] | None = None,
    transport: object | None = None,
) -> UrlIngestResult:
    validated_url = _validate_http_url(url)
    fetched_at = now() if now is not None else datetime.now().astimezone()
    response = (fetcher or _fetch_url)(validated_url)
    _validate_http_url(response.final_url)
    raw_text = _decode_text_body(response.body, response.content_type)
    readable_text = _extract_readable_text(raw_text, response.content_type)
    if not readable_text.strip():
        raise ValueError("URL response did not contain readable text.")

    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    paths = _build_snapshot_paths(response.final_url, fetched_at, response.content_type)
    source_text = _source_markdown(response, fetched_at, paths.raw_snapshot_path, readable_text)
    metadata_text = _metadata_json(response, fetched_at, paths)

    files_created: list[str] = []
    for relative, content in (
        (paths.raw_snapshot_path, raw_text),
        (paths.metadata_path, metadata_text),
        (paths.source_path, source_text),
    ):
        if active_transport.exists(relative):  # type: ignore[attr-defined]
            raise FileExistsError(f"URL snapshot path already exists: {relative}")
        active_transport.write_text(relative, content)  # type: ignore[attr-defined]
        files_created.append(relative)

    fetched = fetched_at.astimezone().isoformat(timespec="seconds")
    ingest_result = ingest_source(
        root,
        paths.source_path,
        transport=active_transport,
        source_type="url",
        source_title=_source_page_title(response, fetched_at),
        manifest_metadata={
            "source_url": response.final_url,
            "requested_url": response.requested_url,
            "fetched_at": fetched,
            "http_status": response.status_code,
            "content_type": response.content_type,
            "raw_snapshot_path": paths.raw_snapshot_path,
        },
    )

    return UrlIngestResult(
        operation="ingest-url",
        status=ingest_result.status,
        url=response.final_url,
        source_path=paths.source_path,
        snapshot_path=paths.snapshot_dir,
        raw_snapshot_path=paths.raw_snapshot_path,
        files_created=files_created + list(ingest_result.files_created),
        files_updated=list(ingest_result.files_updated),
        warnings=list(ingest_result.warnings),
        next_suggested_action="Query the wiki, lint the vault, or ingest another URL.",
    )
