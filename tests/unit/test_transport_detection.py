from __future__ import annotations

import json


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

    monkeypatch.setenv("PATH", "")

    result = detect_transport(
        tmp_path,
        force=True,
        which=lambda name: "legacy-obsidian-cli" if name == "obsidian-cli" else None,
    )

    assert result.snapshot.preferred == "filesystem"
    assert result.snapshot.available["obsidian-cli"].available is True
    assert result.snapshot.available["obsidian-cli"].implemented is False
    assert result.snapshot.available["obsidian-cli"].transport_kind == "legacy"
    assert result.snapshot.available["obsidian-cli"].executable is not None
    assert result.snapshot.available["filesystem"].available is True
    assert result.snapshot.available["filesystem"].implemented is True


def test_detect_transport_records_official_obsidian_probe_failure_as_filesystem(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    class ProbeFailRunner:
        def run(self, argv: list[str], timeout_seconds: int):
            from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliRunResult

            if argv[:2] == ["obsidian", "--help"]:
                return ObsidianCliRunResult(argv, 0, "read\ncreate\nappend\nfiles\nsearch:context\n", "")
            return ObsidianCliRunResult(argv, 1, "", "Obsidian app is not running")

    monkeypatch.setenv("PATH", "")

    result = detect_transport(
        tmp_path,
        force=True,
        runner=ProbeFailRunner(),
        which=lambda name: "obsidian" if name == "obsidian" else None,
    )

    assert result.snapshot.preferred == "filesystem"
    assert result.snapshot.available["obsidian"].available is True
    assert result.snapshot.available["obsidian"].implemented is False
    assert result.snapshot.available["obsidian"].capabilities["read"] is False
    assert "probe failed" in result.snapshot.available["obsidian"].reason


def test_detect_transport_can_prefer_official_obsidian_after_all_probes_pass(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    class ProbePassRunner:
        def run(self, argv: list[str], timeout_seconds: int):
            from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliRunResult

            command = argv[1]
            if command == "--help":
                return ObsidianCliRunResult(argv, 0, "read\ncreate\nappend\nfiles\nsearch:context\n", "")
            if command == "read" and "path=wiki/index.md" in argv:
                return ObsidianCliRunResult(argv, 0, "# Wiki Index\n", "")
            if command == "create":
                return ObsidianCliRunResult(argv, 0, "", "")
            if command == "append":
                return ObsidianCliRunResult(argv, 0, "", "")
            if command == "read" and "path=.vault-meta/obsidian-cli-probe.md" in argv:
                return ObsidianCliRunResult(argv, 0, "llm-wiki-core obsidian probe\nappend-ok\n", "")
            if command == "files":
                return ObsidianCliRunResult(argv, 0, "wiki/index.md\n", "")
            if command == "search:context":
                return ObsidianCliRunResult(argv, 0, "wiki/index.md:1:# Wiki Index\n", "")
            return ObsidianCliRunResult(argv, 1, "", "unexpected")

    monkeypatch.setenv("PATH", "")

    result = detect_transport(
        tmp_path,
        force=True,
        runner=ProbePassRunner(),
        which=lambda name: "obsidian" if name == "obsidian" else None,
    )

    official = result.snapshot.available["obsidian"]
    assert result.snapshot.preferred == "obsidian"
    assert result.snapshot.fallback_chain == ["obsidian", "filesystem"]
    assert official.available is True
    assert official.implemented is True
    assert official.vault_selector == tmp_path.name
    assert official.capabilities == {
        "read": True,
        "write": True,
        "append": True,
        "list": True,
        "search": True,
    }
    assert not (tmp_path / ".vault-meta" / "obsidian-cli-probe.md").exists()


def test_detect_transport_records_legacy_obsidian_cli_as_unimplemented(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.detect_transport import detect_transport

    monkeypatch.setenv("PATH", "")

    result = detect_transport(
        tmp_path,
        force=True,
        which=lambda name: "legacy-obsidian-cli" if name == "obsidian-cli" else None,
    )

    legacy = result.snapshot.available["obsidian-cli"]
    assert result.snapshot.preferred == "filesystem"
    assert legacy.available is True
    assert legacy.implemented is False
    assert legacy.transport_kind == "legacy"


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
    assert snapshot["available"]["obsidian-cli"]["transport_kind"] == "legacy"
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
