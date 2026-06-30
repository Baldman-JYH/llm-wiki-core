from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import hashlib
from html import unescape
from html.parser import HTMLParser
import re
from urllib.parse import urlparse


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


TEXTUAL_CONTENT_TYPES = (
    "text/html",
    "text/plain",
    "text/markdown",
    "application/xhtml+xml",
    "application/xml",
    "application/json",
)


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
    timestamp = fetched_at.strftime("%Y%m%dT%H%M%S")
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
