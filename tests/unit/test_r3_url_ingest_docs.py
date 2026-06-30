from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_documents_url_ingest_and_boundaries() -> None:
    readme = _read("README.md")

    assert "ingest-url" in readme
    assert "llm-wiki ingest-url <vault> https://example.com/article" in readme
    assert "immutable" in readme
    assert "text-only" in readme
    assert "Karpathy" in readme
    assert "AgriciDaniel/claude-obsidian" in readme


def test_user_guide_documents_url_ingest_usage() -> None:
    guide = _read("docs/user-guide.md")

    assert "llm-wiki ingest-url <vault> https://example.com/article" in guide
    assert ".raw/url/" in guide
    assert "text-only" in guide
    assert "JavaScript rendering" in guide
    assert "defuddle" in guide


def test_operation_and_manifest_contracts_document_url_sources() -> None:
    operation_contract = _read("docs/operation-contract.md")
    manifest_schema = _read("docs/manifest-schema.md")

    assert "`ingest-url`" in operation_contract
    assert "source_type" in manifest_schema
    assert "`url`" in manifest_schema
    assert "source_url" in manifest_schema
    assert "raw_snapshot_path" in manifest_schema


def test_roadmap_records_r3_2_url_ingest_status() -> None:
    schedule = _read("docs/roadmap-schedule.md")

    assert "R3.2: URL Ingest" in schedule
    assert "immutable" in schedule
    assert "text-only" in schedule
    assert "Full readability" in schedule
