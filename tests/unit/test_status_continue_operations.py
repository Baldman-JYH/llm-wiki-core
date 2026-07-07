from __future__ import annotations


def test_status_wiki_reports_initialized_vault_metadata(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.status import status_wiki

    monkeypatch.setenv("PATH", "")
    init_vault(tmp_path, purpose="Status test")
    source = tmp_path / ".raw" / "articles" / "example.md"
    source.parent.mkdir(parents=True)
    source.write_text("Example source body.", encoding="utf-8")
    ingest_source(tmp_path, ".raw/articles/example.md")
    detect_transport(tmp_path, force=True)

    result = status_wiki(tmp_path)

    assert result.operation == "status"
    assert result.status == "success"
    assert result.initialized is True
    assert result.missing_required_paths == []
    assert result.source_count == 1
    assert result.preferred_transport == "filesystem"
    assert result.recent_log_entry.startswith("## [")
    assert result.next_suggested_action == "Continue with query, ingest, save, or lint."


def test_status_wiki_falls_back_from_legacy_unimplemented_transport_snapshot(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.status import status_wiki

    init_vault(tmp_path, purpose="Legacy snapshot")
    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        '{"preferred": "obsidian-cli", "available": {"obsidian-cli": {"available": true}, "filesystem": {"available": true}}}\n',
        encoding="utf-8",
    )

    result = status_wiki(tmp_path)

    assert result.status == "success"
    assert result.preferred_transport == "filesystem"
    assert any("not implemented" in warning for warning in result.warnings)


def test_status_required_paths_come_from_organization_contract(tmp_path, monkeypatch) -> None:
    import llm_wiki_core.operations.status as status_module
    from llm_wiki_core.operations.status import status_wiki

    monkeypatch.setattr(
        status_module,
        "required_paths_for_organization",
        lambda _organization="generic": ("wiki/routed-required.md",),
    )

    class SpyTransport:
        def __init__(self) -> None:
            self.exists_paths: list[str] = []

        def exists(self, relative_path: str) -> bool:
            self.exists_paths.append(relative_path)
            return False

    transport = SpyTransport()

    result = status_wiki(tmp_path, transport=transport)

    assert result.status == "incomplete"
    assert result.missing_required_paths == ["wiki/routed-required.md"]
    assert "wiki/routed-required.md" in transport.exists_paths


def test_status_wiki_reports_incomplete_vault_without_writing(tmp_path) -> None:
    from llm_wiki_core.operations.status import status_wiki

    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = status_wiki(tmp_path)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert result.status == "incomplete"
    assert result.initialized is False
    assert ".raw/.manifest.json" in result.missing_required_paths
    assert "wiki/index.md" in result.missing_required_paths
    assert result.source_count == 0
    assert result.preferred_transport == "filesystem"
    assert result.next_suggested_action == "Run init to create the LLM Wiki scaffold."
    assert before == after


def test_cli_status_prints_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI status")

    exit_code = main(["status", str(tmp_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "status success" in output
    assert "initialized: true" in output
    assert "sources: 0" in output


def test_cli_status_prints_transport_warnings(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI status warnings")
    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        '{"preferred": "obsidian-cli", "available": {"obsidian-cli": {"available": true, "implemented": false}, "filesystem": {"available": true, "implemented": true}}}\n',
        encoding="utf-8",
    )

    exit_code = main(["status", str(tmp_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "warnings:" in output
    assert "obsidian-cli" in output


def test_continue_wiki_reads_hot_index_and_recent_log_without_writing(tmp_path) -> None:
    from llm_wiki_core.operations.continue_ import continue_wiki
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Continue test")
    source = tmp_path / ".raw" / "articles" / "example.md"
    source.parent.mkdir(parents=True)
    source.write_text("Example source body.", encoding="utf-8")
    ingest_source(tmp_path, ".raw/articles/example.md")
    before = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))

    result = continue_wiki(tmp_path)

    after = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*"))
    assert result.operation == "continue"
    assert result.status == "success"
    assert "Recent Context" in result.hot_context
    assert "Wiki Index" in result.index_context
    assert any("ingest" in entry for entry in result.recent_log_entries)
    assert result.files_read == ["wiki/hot.md", "wiki/index.md", "wiki/log.md"]
    assert result.next_suggested_action == "Use hot and index context before query, ingest, save, or lint."
    assert before == after


def test_continue_wiki_reports_needs_init_for_empty_vault(tmp_path) -> None:
    from llm_wiki_core.operations.continue_ import continue_wiki

    result = continue_wiki(tmp_path)

    assert result.status == "needs_init"
    assert result.hot_context == ""
    assert result.index_context == ""
    assert result.recent_log_entries == []
    assert result.files_read == []
    assert result.next_suggested_action == "Run init to create the LLM Wiki scaffold."


def test_cli_continue_prints_context_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI continue")

    exit_code = main(["continue", str(tmp_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "continue success" in output
    assert "files read: 3" in output
    assert "recent log:" in output


def test_cli_continue_prints_transport_warnings(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI continue warnings")
    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        '{"preferred": "obsidian-cli", "available": {"obsidian-cli": {"available": true, "implemented": false}, "filesystem": {"available": true, "implemented": true}}}\n',
        encoding="utf-8",
    )

    exit_code = main(["continue", str(tmp_path)])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "warnings:" in output
    assert "obsidian-cli" in output
