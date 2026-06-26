from __future__ import annotations

import json
import os


def test_detect_transport_prefers_filesystem_when_obsidian_cli_missing(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    monkeypatch.setenv("PATH", "")

    result = detect_transport(tmp_path)

    assert result.operation == "detect-transport"
    assert result.status == "success"
    assert result.snapshot.preferred == "filesystem"
    assert result.snapshot.available["filesystem"].available is True
    assert result.snapshot.available["obsidian-cli"].available is False
    assert (tmp_path / ".vault-meta" / "transport.json").is_file()


def test_detect_transport_records_obsidian_cli_as_available_but_unimplemented(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    executable = bin_dir / ("obsidian-cli.bat" if os.name == "nt" else "obsidian-cli")
    executable.write_text("@echo off\n" if os.name == "nt" else "#!/bin/sh\n", encoding="utf-8")
    if os.name != "nt":
        executable.chmod(0o755)
    monkeypatch.setenv("PATH", str(bin_dir))

    result = detect_transport(tmp_path, force=True)

    assert result.snapshot.preferred == "filesystem"
    assert result.snapshot.available["obsidian-cli"].available is True
    assert result.snapshot.available["obsidian-cli"].implemented is False
    assert "not implemented" in result.snapshot.available["obsidian-cli"].reason
    assert result.snapshot.available["obsidian-cli"].executable is not None
    assert result.snapshot.available["filesystem"].available is True
    assert result.snapshot.available["filesystem"].implemented is True


def test_transport_snapshot_json_shape(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    monkeypatch.setenv("PATH", "")
    detect_transport(tmp_path)

    snapshot = json.loads((tmp_path / ".vault-meta" / "transport.json").read_text(encoding="utf-8"))

    assert snapshot["schema_version"] == 1
    assert snapshot["preferred"] == "filesystem"
    assert snapshot["fallback_chain"] == ["filesystem"]
    assert snapshot["available"]["filesystem"]["available"] is True
    assert snapshot["available"]["filesystem"]["implemented"] is True
    assert snapshot["available"]["obsidian-cli"]["implemented"] is False
    assert snapshot["manual_override"] is None


def test_detect_transport_reuses_snapshot_unless_forced(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    monkeypatch.setenv("PATH", "")
    first = detect_transport(tmp_path)
    snapshot_path = tmp_path / ".vault-meta" / "transport.json"
    snapshot_path.write_text('{"preferred": "manual"}\n', encoding="utf-8")

    reused = detect_transport(tmp_path)
    refreshed = detect_transport(tmp_path, force=True)

    assert reused.snapshot.preferred == "manual"
    assert first.snapshot.preferred == "filesystem"
    assert refreshed.snapshot.preferred == "filesystem"


def test_cli_detect_transport_writes_snapshot_and_prints_summary(tmp_path, monkeypatch, capsys) -> None:
    from llm_wiki_core.cli import main

    monkeypatch.setenv("PATH", "")

    exit_code = main(["detect-transport", str(tmp_path)])

    assert exit_code == 0
    assert (tmp_path / ".vault-meta" / "transport.json").is_file()
    output = capsys.readouterr().out
    assert "detect-transport success" in output
    assert "preferred: filesystem" in output
