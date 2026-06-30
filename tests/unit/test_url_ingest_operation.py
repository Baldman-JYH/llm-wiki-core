from __future__ import annotations

from datetime import datetime, timezone

import pytest


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
