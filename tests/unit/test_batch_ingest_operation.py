from __future__ import annotations

import json
from pathlib import Path

import pytest


def _init_batch_vault(tmp_path: Path) -> None:
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Batch ingest test")


def _write_raw(vault: Path, relative: str, content: str) -> Path:
    source = vault / ".raw" / relative
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text(content, encoding="utf-8")
    return source


def test_ingest_batch_ingests_multiple_markdown_sources_and_manifest_records(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    first = _write_raw(tmp_path, "articles/beta.md", "# Beta\n\nSecond source.")
    second = _write_raw(tmp_path, "articles/alpha.md", "# Alpha\n\nFirst source.")

    result = ingest_batch(tmp_path, ".raw/articles")

    assert result.operation == "ingest-batch"
    assert result.status == "success"
    assert result.root_path == ".raw/articles"
    assert result.total == 2
    assert result.succeeded == 2
    assert result.skipped == 0
    assert result.failed == 0
    assert [item.source_path for item in result.items] == [
        ".raw/articles/alpha.md",
        ".raw/articles/beta.md",
    ]
    assert first.read_text(encoding="utf-8") == "# Beta\n\nSecond source."
    assert second.read_text(encoding="utf-8") == "# Alpha\n\nFirst source."
    assert (tmp_path / "wiki" / "sources" / "Alpha.md").is_file()
    assert (tmp_path / "wiki" / "sources" / "Beta.md").is_file()

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    assert sorted(manifest["sources"]) == ["articles/alpha.md", "articles/beta.md"]


def test_ingest_batch_counts_unchanged_sources_as_skipped_and_force_reingests(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    _write_raw(tmp_path, "articles/example.md", "# Example\n\nOriginal.")

    first = ingest_batch(tmp_path, ".raw/articles")
    assert first.status == "success"
    assert first.succeeded == 1

    source_page = tmp_path / "wiki" / "sources" / "Example.md"
    source_page.write_text("custom source page", encoding="utf-8")

    second = ingest_batch(tmp_path, ".raw/articles")
    assert second.status == "success"
    assert second.succeeded == 0
    assert second.skipped == 1
    assert second.items[0].status == "skipped"
    assert source_page.read_text(encoding="utf-8") == "custom source page"

    forced = ingest_batch(tmp_path, ".raw/articles", force=True)
    assert forced.status == "success"
    assert forced.succeeded == 1
    assert forced.skipped == 0
    assert "custom source page" not in source_page.read_text(encoding="utf-8")


def test_ingest_batch_rejects_missing_source_root(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)

    with pytest.raises(FileNotFoundError, match=r"Raw source root not found under \.raw/: \.raw/articles"):
        ingest_batch(tmp_path, ".raw/articles")


def test_ingest_batch_rejects_source_root_outside_raw(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)

    with pytest.raises(ValueError, match=r"source_root must be \.raw/ or under \.raw/:"):
        ingest_batch(tmp_path, "notes")


def test_ingest_batch_rejects_raw_path_traversal(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)

    with pytest.raises(ValueError, match=r"source_root under \.raw/ must not contain '\.\.'"):
        ingest_batch(tmp_path, ".raw/../articles")


def test_ingest_batch_returns_empty_for_existing_root_without_markdown(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    notes = tmp_path / ".raw" / "notes"
    notes.mkdir(parents=True)
    (notes / "not-markdown.txt").write_text("plain text", encoding="utf-8")

    result = ingest_batch(tmp_path, ".raw/notes")

    assert result.status == "empty"
    assert result.total == 0
    assert result.succeeded == 0
    assert result.skipped == 0
    assert result.failed == 0
    assert result.items == []
    assert "Add Markdown files under .raw/" in result.next_suggested_action


def test_ingest_batch_accepts_single_markdown_file_root(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    _write_raw(tmp_path, "articles/single.md", "# Single\n\nOnly one.")

    result = ingest_batch(tmp_path, ".raw/articles/single.md")

    assert result.status == "success"
    assert result.total == 1
    assert result.items[0].source_path == ".raw/articles/single.md"
    assert (tmp_path / "wiki" / "sources" / "Single.md").is_file()


def test_ingest_batch_duplicate_basename_does_not_silently_overwrite(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    _write_raw(tmp_path, "a/report.md", "# First Report\n\nAlpha source.")
    _write_raw(tmp_path, "b/report.md", "# Second Report\n\nBeta source.")

    result = ingest_batch(tmp_path, ".raw")

    assert result.status == "partial"
    assert result.total == 2
    assert result.succeeded == 1
    assert result.failed == 1
    assert [item.source_path for item in result.items] == [
        ".raw/a/report.md",
        ".raw/b/report.md",
    ]
    assert [item.status for item in result.items] == ["success", "failed"]
    assert result.items[1].error_type == "ValueError"
    assert "wiki/sources/Report.md" in (result.items[1].error_message or "")

    source_page = tmp_path / "wiki" / "sources" / "Report.md"
    source_page_text = source_page.read_text(encoding="utf-8")
    assert 'source_path: ".raw/a/report.md"' in source_page_text
    assert ".raw/b/report.md" not in source_page_text

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    assert sorted(manifest["sources"]) == ["a/report.md"]
    assert manifest["sources"]["a/report.md"]["generated_pages"] == ["wiki/sources/Report.md"]


def test_ingest_batch_rejects_cross_batch_duplicate_basename_without_overwriting_existing_source_page(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    _init_batch_vault(tmp_path)
    _write_raw(tmp_path, "a/report.md", "# First Report\n\nAlpha source.")

    first = ingest_batch(tmp_path, ".raw/a")
    assert first.status == "success"
    assert first.succeeded == 1

    source_page = tmp_path / "wiki" / "sources" / "Report.md"
    first_source_page = source_page.read_text(encoding="utf-8")
    first_manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))

    _write_raw(tmp_path, "b/report.md", "# Second Report\n\nBeta source.")

    second = ingest_batch(tmp_path, ".raw/b")

    assert second.status == "failed"
    assert second.total == 1
    assert second.succeeded == 0
    assert second.failed == 1
    assert [item.status for item in second.items] == ["failed"]
    failed_item = second.items[0]
    assert failed_item.source_path == ".raw/b/report.md"
    assert failed_item.error_type == "ValueError"
    assert "wiki/sources/Report.md" in (failed_item.error_message or "")
    assert ".raw/a/report.md" in (failed_item.error_message or "")

    assert source_page.read_text(encoding="utf-8") == first_source_page
    assert 'source_path: ".raw/a/report.md"' in first_source_page
    assert ".raw/b/report.md" not in source_page.read_text(encoding="utf-8")

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    assert manifest["sources"] == first_manifest["sources"]
    assert sorted(manifest["sources"]) == ["a/report.md"]
    assert "b/report.md" not in manifest["sources"]


def test_ingest_batch_directory_root_discovers_before_exists_probe(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    class DirectoryDiscoveryTransport:
        def __init__(self) -> None:
            self.calls: list[tuple[str, str]] = []

        def exists(self, relative_path: str) -> bool:
            self.calls.append(("exists", relative_path))
            if relative_path == ".raw/articles":
                raise RuntimeError("directory exists probe unsupported")
            return False

        def list_markdown(self, root: str) -> list[str]:
            self.calls.append(("list_markdown", root))
            assert self.calls == [("list_markdown", ".raw/articles")]
            return []

    result = ingest_batch(tmp_path, ".raw/articles", transport=DirectoryDiscoveryTransport())

    assert result.status == "empty"
    assert result.root_path == ".raw/articles"


def test_ingest_batch_captures_per_file_failure_and_continues(tmp_path) -> None:
    from llm_wiki_core.operations.ingest_batch import ingest_batch

    class PartialFailureTransport:
        def __init__(self) -> None:
            self.list_calls: list[str] = []
            self.files = {
                ".raw/.manifest.json": '{"schema_version": 1, "updated": "", "sources": {}}\n',
                ".raw/articles/ok.md": "# Ok\n\nReadable.",
                "wiki/index.md": "# Wiki Index\n\n## Sources\n",
                "wiki/log.md": "# Operation Log\n\n",
                "wiki/hot.md": "# Recent Context\n",
            }

        def exists(self, relative_path: str) -> bool:
            return relative_path in {".raw/articles", ".raw/articles/broken.md"} or relative_path in self.files

        def list_markdown(self, root: str) -> list[str]:
            self.list_calls.append(root)
            return [".raw/articles/broken.md", ".raw/articles/ok.md"]

        def read_text(self, relative_path: str) -> str:
            if relative_path == ".raw/articles/broken.md":
                raise ValueError("cannot read source")
            return self.files[relative_path]

        def write_text(self, relative_path: str, content: str) -> str:
            self.files[relative_path] = content
            return relative_path

    transport = PartialFailureTransport()

    result = ingest_batch(tmp_path, ".raw/articles", transport=transport)

    assert transport.list_calls == [".raw/articles"]
    assert result.status == "partial"
    assert result.total == 2
    assert result.succeeded == 1
    assert result.failed == 1
    assert [item.status for item in result.items] == ["failed", "success"]
    failed = result.items[0]
    assert failed.source_path == ".raw/articles/broken.md"
    assert failed.error_type == "ValueError"
    assert failed.error_message == "cannot read source"
    assert "wiki/sources/Ok.md" in transport.files
