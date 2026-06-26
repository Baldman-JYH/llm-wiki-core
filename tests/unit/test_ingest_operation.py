from __future__ import annotations

import json


def test_ingest_source_creates_source_page_and_updates_indexes(tmp_path) -> None:
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Test ingest")
    source = tmp_path / ".raw" / "articles" / "karpathy-llm-wiki.md"
    source.parent.mkdir(parents=True)
    original = "# Karpathy LLM Wiki\n\nA pattern for compounding Markdown knowledge."
    source.write_text(original, encoding="utf-8")

    result = ingest_source(tmp_path, ".raw/articles/karpathy-llm-wiki.md")

    assert result.operation == "ingest"
    assert result.status == "success"
    assert source.read_text(encoding="utf-8") == original
    assert (tmp_path / "wiki" / "sources" / "Karpathy Llm Wiki.md").is_file()
    assert "wiki/sources/Karpathy Llm Wiki.md" in result.files_created
    assert "wiki/index.md" in result.files_updated
    assert "wiki/log.md" in result.files_updated
    assert "wiki/hot.md" in result.files_updated


def test_ingest_source_writes_manifest_record(tmp_path) -> None:
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Test manifest")
    source = tmp_path / ".raw" / "articles" / "example.md"
    source.parent.mkdir(parents=True)
    source.write_text("Example source body.", encoding="utf-8")

    ingest_source(tmp_path, ".raw/articles/example.md")

    manifest = json.loads((tmp_path / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    record = manifest["sources"]["articles/example.md"]
    assert record["source_path"] == ".raw/articles/example.md"
    assert record["source_type"] == "file"
    assert record["status"] == "ingested"
    assert record["content_fingerprint"].startswith("sha256:")
    assert record["generated_pages"] == ["wiki/sources/Example.md"]
    assert "wiki/index.md" in record["updated_pages"]


def test_ingest_source_skips_unchanged_source_without_force(tmp_path) -> None:
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Test skip")
    source = tmp_path / ".raw" / "articles" / "example.md"
    source.parent.mkdir(parents=True)
    source.write_text("Example source body.", encoding="utf-8")

    ingest_source(tmp_path, ".raw/articles/example.md")
    source_page = tmp_path / "wiki" / "sources" / "Example.md"
    source_page.write_text("custom source page", encoding="utf-8")

    result = ingest_source(tmp_path, ".raw/articles/example.md")

    assert result.status == "skipped"
    assert "wiki/sources/Example.md" in result.files_skipped
    assert source_page.read_text(encoding="utf-8") == "custom source page"


def test_ingest_source_force_reingests_unchanged_source(tmp_path) -> None:
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Test force")
    source = tmp_path / ".raw" / "articles" / "example.md"
    source.parent.mkdir(parents=True)
    source.write_text("Example source body.", encoding="utf-8")

    ingest_source(tmp_path, ".raw/articles/example.md")
    source_page = tmp_path / "wiki" / "sources" / "Example.md"
    source_page.write_text("custom source page", encoding="utf-8")

    result = ingest_source(tmp_path, ".raw/articles/example.md", force=True)

    assert result.status == "success"
    assert "wiki/sources/Example.md" in result.files_updated
    assert "custom source page" not in source_page.read_text(encoding="utf-8")


def test_ingest_source_rejects_paths_outside_raw(tmp_path) -> None:
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Test reject")
    outside = tmp_path / "notes.md"
    outside.write_text("Do not ingest this.", encoding="utf-8")

    try:
        ingest_source(tmp_path, "notes.md")
    except ValueError as error:
        assert "must be under .raw/" in str(error)
    else:
        raise AssertionError("Expected ValueError")


def test_ingest_source_uses_transport_for_read_and_write_paths(tmp_path) -> None:
    from llm_wiki_core.operations.ingest import ingest_source

    class SpyTransport:
        def __init__(self) -> None:
            self.exists_paths: list[str] = []
            self.read_paths: list[str] = []
            self.write_calls: list[tuple[str, str]] = []
            self.files = {
                ".raw/articles/example.md": "Example source body.",
                ".raw/.manifest.json": '{"schema_version": 1, "updated": "", "sources": {}}\n',
                "wiki/index.md": "# Wiki Index\n\n## Sources\n",
                "wiki/log.md": "# Operation Log\n\n",
                "wiki/hot.md": "# Recent Context\n",
            }

        def exists(self, relative_path: str) -> bool:
            self.exists_paths.append(relative_path)
            return relative_path in self.files

        def read_text(self, relative_path: str) -> str:
            self.read_paths.append(relative_path)
            return self.files[relative_path]

        def write_text(self, relative_path: str, content: str) -> str:
            self.write_calls.append((relative_path, content))
            self.files[relative_path] = content
            return relative_path

    transport = SpyTransport()

    result = ingest_source(tmp_path, ".raw/articles/example.md", transport=transport)

    written_paths = [path for path, _ in transport.write_calls]
    assert result.status == "success"
    assert ".raw/articles/example.md" in transport.exists_paths
    assert ".raw/articles/example.md" in transport.read_paths
    assert ".raw/.manifest.json" in transport.read_paths
    assert "wiki/sources/Example.md" in written_paths
    assert "wiki/index.md" in written_paths
    assert "wiki/log.md" in written_paths
    assert "wiki/hot.md" in written_paths
    assert ".raw/.manifest.json" in written_paths


def test_cli_ingest_prints_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI ingest")
    source = tmp_path / ".raw" / "articles" / "example.md"
    source.parent.mkdir(parents=True)
    source.write_text("Example source body.", encoding="utf-8")

    exit_code = main(["ingest", str(tmp_path), ".raw/articles/example.md"])

    assert exit_code == 0
    assert (tmp_path / "wiki" / "sources" / "Example.md").is_file()
    output = capsys.readouterr().out
    assert "ingest success" in output
    assert "source: .raw/articles/example.md" in output
