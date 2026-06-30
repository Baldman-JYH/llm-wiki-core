from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path

import pytest


def test_url_fetch_defaults_match_brief_plan_values() -> None:
    from llm_wiki_core.operations.ingest_url import DEFAULT_TIMEOUT_SECONDS, MAX_RESPONSE_BYTES

    assert DEFAULT_TIMEOUT_SECONDS == 10
    assert MAX_RESPONSE_BYTES == 2_000_000


def test_validate_http_url_accepts_http_and_https() -> None:
    from llm_wiki_core.operations.ingest_url import _validate_http_url

    assert _validate_http_url("https://example.com/article") == "https://example.com/article"
    assert _validate_http_url("http://127.0.0.1:8000/page") == "http://127.0.0.1:8000/page"


@pytest.mark.parametrize(
    "url",
    [
        "",
        "example.com/article",
        "file:///tmp/source.md",
        "ftp://example.com/file.txt",
        "data:text/plain,hello",
        "javascript:alert(1)",
    ],
)
def test_validate_http_url_rejects_unsupported_urls(url: str) -> None:
    from llm_wiki_core.operations.ingest_url import _validate_http_url

    with pytest.raises(ValueError, match="Only explicit http and https URLs are supported"):
        _validate_http_url(url)


def test_decode_text_body_uses_declared_charset_and_rejects_binary() -> None:
    from llm_wiki_core.operations.ingest_url import _decode_text_body

    assert _decode_text_body("café".encode("utf-8"), "text/plain; charset=utf-8") == "café"

    with pytest.raises(ValueError, match="URL response is not supported text content"):
        _decode_text_body(b"\xff\xfe\x00\x00", "application/octet-stream")


def test_extract_readable_text_removes_scripts_styles_and_decodes_entities() -> None:
    from llm_wiki_core.operations.ingest_url import _extract_readable_text

    html = (
        "<html><head><title>Example &amp; Test</title><style>.x{}</style></head>"
        "<body><h1>Hello &amp; Wiki</h1><script>alert(1)</script><p>Useful text.</p></body></html>"
    )

    text = _extract_readable_text(html, "text/html; charset=utf-8")

    assert "Hello & Wiki" in text
    assert "Useful text." in text
    assert "alert(1)" not in text
    assert ".x{}" not in text


def test_build_snapshot_paths_are_vault_relative_unique_and_textual() -> None:
    from llm_wiki_core.operations.ingest_url import _build_snapshot_paths

    fetched_at = datetime(2026, 6, 30, 1, 2, 3, tzinfo=timezone.utc)
    paths = _build_snapshot_paths(
        "https://Example.com/articles/Hello%20World?x=1",
        fetched_at,
        "text/html; charset=utf-8",
    )

    assert paths.snapshot_dir.startswith(".raw/url/2026-06-30/example-com/20260630T010203")
    assert paths.source_path.endswith("/source.md")
    assert paths.raw_snapshot_path.endswith("/response.html")
    assert paths.metadata_path.endswith("/metadata.json")
    assert ".." not in paths.snapshot_dir
    assert "\\" not in paths.snapshot_dir


def test_build_snapshot_paths_differ_for_same_url_within_same_second() -> None:
    from llm_wiki_core.operations.ingest_url import _build_snapshot_paths

    first = _build_snapshot_paths(
        "https://example.com/article",
        datetime(2026, 6, 30, 1, 2, 3, 123456, tzinfo=timezone.utc),
        "text/html; charset=utf-8",
    )
    second = _build_snapshot_paths(
        "https://example.com/article",
        datetime(2026, 6, 30, 1, 2, 3, 654321, tzinfo=timezone.utc),
        "text/html; charset=utf-8",
    )

    assert first.snapshot_dir != second.snapshot_dir
    assert first.snapshot_dir.startswith(".raw/url/2026-06-30/example-com/20260630T010203")
    assert second.snapshot_dir.startswith(".raw/url/2026-06-30/example-com/20260630T010203")


def test_source_markdown_contains_url_provenance_and_extracted_text() -> None:
    from llm_wiki_core.operations.ingest_url import UrlFetchResponse, _source_markdown

    fetched_at = datetime(2026, 6, 30, 1, 2, 3, tzinfo=timezone.utc)
    response = UrlFetchResponse(
        requested_url="https://example.com/article",
        final_url="https://example.com/article",
        status_code=200,
        content_type="text/html; charset=utf-8",
        body=b"<h1>Hello</h1>",
    )

    markdown = _source_markdown(
        response,
        fetched_at,
        ".raw/url/2026-06-30/example-com/snapshot/response.html",
        "Hello\nUseful body.",
    )

    assert "source_type: url" in markdown
    assert 'source_url: "https://example.com/article"' in markdown
    assert "fetched_at: 2026-06-30T01:02:03+00:00" in markdown
    assert "http_status: 200" in markdown
    assert 'raw_snapshot_path: ".raw/url/2026-06-30/example-com/snapshot/response.html"' in markdown
    assert "## Extracted Text" in markdown
    assert "Useful body." in markdown


def _fixed_now() -> datetime:
    return datetime(2026, 6, 30, 1, 2, 3, tzinfo=timezone.utc)


def test_ingest_url_creates_immutable_snapshot_and_manifest_record(tmp_path: Path) -> None:
    from llm_wiki_core.operations.ingest_url import UrlFetchResponse, ingest_url
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="URL ingest")

    def fetcher(url: str) -> UrlFetchResponse:
        return UrlFetchResponse(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/html; charset=utf-8",
            body=b"<html><head><title>Ignored</title></head><body><h1>Hello Wiki</h1><p>Useful body.</p></body></html>",
        )

    result = ingest_url(
        tmp_path,
        "https://example.com/articles/hello",
        fetcher=fetcher,
        now=_fixed_now,
    )

    assert result.operation == "ingest-url"
    assert result.status == "success"
    assert result.url == "https://example.com/articles/hello"
    assert result.snapshot_path.startswith(".raw/url/2026-06-30/example-com/20260630T010203")
    assert result.source_path.endswith("/source.md")
    assert result.raw_snapshot_path.endswith("/response.html")
    assert (tmp_path / result.source_path).is_file()
    assert (tmp_path / result.raw_snapshot_path).read_text(encoding="utf-8").startswith("<html>")

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    source_key = result.source_path.removeprefix(".raw/")
    record = manifest["sources"][source_key]
    assert record["source_type"] == "url"
    assert record["source_url"] == "https://example.com/articles/hello"
    assert record["http_status"] == 200
    assert record["content_type"] == "text/html; charset=utf-8"
    assert record["raw_snapshot_path"] == result.raw_snapshot_path
    assert record["generated_pages"][0].startswith("wiki/sources/Example Com Hello 20260630T010203")

    source_page_path = tmp_path / record["generated_pages"][0]
    source_page = source_page_path.read_text(encoding="utf-8")
    summary_section = source_page.split("## Summary\n", 1)[1].split("\n## Source Notes", 1)[0].strip()
    assert "Hello Wiki" in summary_section or "Useful body." in summary_section
    assert "---" not in summary_section


def test_ingest_url_repeated_fetch_creates_new_snapshot(tmp_path: Path) -> None:
    from llm_wiki_core.operations.ingest_url import UrlFetchResponse, ingest_url
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="URL immutable snapshots")

    def fetcher(url: str) -> UrlFetchResponse:
        return UrlFetchResponse(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/plain; charset=utf-8",
            body=b"same body",
        )

    first_time = datetime(2026, 6, 30, 1, 2, 3, tzinfo=timezone.utc)
    second_time = datetime(2026, 6, 30, 1, 2, 4, tzinfo=timezone.utc)

    first = ingest_url(tmp_path, "https://example.com/a", fetcher=fetcher, now=lambda: first_time)
    second = ingest_url(tmp_path, "https://example.com/a", fetcher=fetcher, now=lambda: second_time)

    assert first.snapshot_path != second.snapshot_path
    assert (tmp_path / first.source_path).is_file()
    assert (tmp_path / second.source_path).is_file()

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    assert first.source_path.removeprefix(".raw/") in manifest["sources"]
    assert second.source_path.removeprefix(".raw/") in manifest["sources"]


def test_ingest_url_rejects_empty_extracted_text_without_wiki_update(tmp_path: Path) -> None:
    from llm_wiki_core.operations.ingest_url import UrlFetchResponse, ingest_url
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="URL empty text")

    def fetcher(url: str) -> UrlFetchResponse:
        return UrlFetchResponse(
            requested_url=url,
            final_url=url,
            status_code=200,
            content_type="text/html; charset=utf-8",
            body=b"<html><script>alert(1)</script><style>.x{}</style></html>",
        )

    with pytest.raises(ValueError, match="URL response did not contain readable text"):
        ingest_url(tmp_path, "https://example.com/empty", fetcher=fetcher, now=_fixed_now)

    assert not list((tmp_path / "wiki" / "sources").glob("*.md"))
    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    assert manifest["sources"] == {}


def test_ingest_url_can_fetch_from_local_http_server(tmp_path: Path) -> None:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
    from threading import Thread

    from llm_wiki_core.operations.ingest_url import ingest_url
    from llm_wiki_core.operations.init import init_vault

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            body = b"<html><body><h1>Local Source</h1><p>Served locally.</p></body></html>"
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args: object) -> None:
            return

    init_vault(tmp_path, purpose="Local URL server")
    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{server.server_port}/source"
        result = ingest_url(tmp_path, url, now=_fixed_now)
    finally:
        server.shutdown()
        thread.join(timeout=5)

    assert result.status == "success"
    assert (tmp_path / result.source_path).read_text(encoding="utf-8").count("Served locally.") == 1
