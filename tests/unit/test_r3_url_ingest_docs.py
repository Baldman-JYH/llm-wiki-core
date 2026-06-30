from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_documents_url_ingest_and_boundaries() -> None:
    readme = _read("README.md")

    assert "ingest-url" in readme
    assert "llm-wiki ingest-url <vault> https://example.com/article" in readme
    assert "immutable `.raw/url/` snapshots" in readme
    assert "R3.2 is text-only." in readme
    assert "does not include full readability, defuddle, JavaScript rendering, authenticated pages, or crawling." in readme
    assert "Karpathy" in readme
    assert "AgriciDaniel/claude-obsidian" in readme


def test_user_guide_documents_url_ingest_usage() -> None:
    guide = _read("docs/user-guide.md")

    assert "llm-wiki ingest-url <vault> https://example.com/article" in guide
    assert ".raw/url/" in guide
    assert "R3.2 remains text-only." in guide
    assert "It does not include full readability, defuddle, JavaScript rendering, authenticated pages, or crawling." in guide
    assert "remain outside R3.2" in guide


def test_operation_and_manifest_contracts_document_url_sources() -> None:
    operation_contract = _read("docs/operation-contract.md")
    manifest_schema = _read("docs/manifest-schema.md")

    assert "`ingest-url`" in operation_contract
    assert "`ingest-batch`" in operation_contract
    assert "per-source success, skipped, and failed items" in operation_contract
    assert "only local Markdown roots under `.raw/`" in operation_contract
    assert "source_type" in manifest_schema
    assert "`url`" in manifest_schema
    assert "source_url" in manifest_schema
    assert "requested_url" in manifest_schema
    assert "raw_snapshot_path" in manifest_schema


def test_roadmap_records_r3_2_url_ingest_status() -> None:
    schedule = _read("docs/roadmap-schedule.md")

    assert "R3.2: URL Ingest" in schedule
    assert "immutable `.raw/url/` snapshots" in schedule
    assert "text-only decoded raw payload preservation" in schedule
    assert "Non-scope:" in schedule
    assert "- Full readability" in schedule
    assert "- defuddle" in schedule
    assert "- JavaScript rendering" in schedule
    assert "Follow-up:" in schedule
    assert "remains deferred" in schedule


def test_r3_2_docs_do_not_include_local_absolute_paths() -> None:
    checked_files = [
        "docs/superpowers/plans/2026-06-30-r3-2-url-ingest.md",
        "docs/superpowers/specs/2026-06-30-r3-2-url-ingest-design.md",
        "README.md",
        "docs/user-guide.md",
        "docs/manifest-schema.md",
    ]

    for relative in checked_files:
        text = _read(relative)
        assert "D:\\ai" not in text
        assert "D:/ai" not in text
