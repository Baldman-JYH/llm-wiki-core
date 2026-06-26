from __future__ import annotations

import json


def _last_json(stdout: str) -> dict[str, object]:
    lines = [line for line in stdout.splitlines() if line.strip()]
    assert lines
    return json.loads(lines[-1])


def test_cli_init_supports_json_output(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    result = main(["init", str(tmp_path), "--purpose", "JSON CLI", "--json"])

    assert result == 0
    payload = _last_json(capsys.readouterr().out)
    assert payload["operation"] == "init"
    assert payload["status"] == "success"
    assert payload["next_suggested_action"]
    assert "files_created" in payload


def test_cli_status_supports_json_output(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    assert main(["init", str(tmp_path), "--purpose", "JSON status"]) == 0
    capsys.readouterr()

    result = main(["status", str(tmp_path), "--json"])

    assert result == 0
    payload = _last_json(capsys.readouterr().out)
    assert payload["operation"] == "status"
    assert payload["status"] == "success"
    assert payload["initialized"] is True
    assert payload["preferred_transport"] == "filesystem"


def test_cli_json_errors_are_machine_readable(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="JSON error")

    result = main(["ingest", str(tmp_path), "notes/source.md", "--json"])

    assert result == 1
    payload = _last_json(capsys.readouterr().out)
    assert payload["operation"] == "ingest"
    assert payload["status"] == "error"
    error = payload["error"]
    assert isinstance(error, dict)
    assert error["type"] == "ValueError"
    assert ".raw/" in str(error["message"])
