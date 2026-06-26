from __future__ import annotations

import json


def test_runtime_transport_defaults_to_filesystem_without_snapshot(tmp_path) -> None:
    from llm_wiki_core.transport import FilesystemTransport, select_runtime_transport

    selection = select_runtime_transport(tmp_path)

    assert selection.name == "filesystem"
    assert isinstance(selection.transport, FilesystemTransport)
    assert selection.snapshot_preferred is None
    assert selection.warnings == []


def test_runtime_transport_falls_back_from_legacy_obsidian_preference(tmp_path) -> None:
    from llm_wiki_core.transport import select_runtime_transport

    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "preferred": "obsidian-cli",
                "fallback_chain": ["obsidian-cli", "filesystem"],
                "available": {
                    "obsidian-cli": {"available": True, "executable": "obsidian-cli"},
                    "filesystem": {"available": True, "executable": None},
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    selection = select_runtime_transport(tmp_path)

    assert selection.name == "filesystem"
    assert selection.snapshot_preferred == "obsidian-cli"
    assert any("not implemented" in warning for warning in selection.warnings)


def test_runtime_transport_falls_back_from_current_unimplemented_obsidian_snapshot(tmp_path) -> None:
    from llm_wiki_core.transport import select_runtime_transport

    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "preferred": "obsidian-cli",
                "fallback_chain": ["filesystem"],
                "available": {
                    "obsidian-cli": {
                        "available": True,
                        "implemented": False,
                        "reason": "contract boundary only",
                    },
                    "filesystem": {
                        "available": True,
                        "implemented": True,
                    },
                },
            }
        )
        + "\n",
        encoding="utf-8",
    )

    selection = select_runtime_transport(tmp_path)

    assert selection.name == "filesystem"
    assert selection.snapshot_preferred == "obsidian-cli"
    assert any("not implemented" in warning for warning in selection.warnings)


def test_runtime_transport_warns_and_uses_filesystem_for_invalid_snapshot(tmp_path) -> None:
    from llm_wiki_core.transport import select_runtime_transport

    snapshot = tmp_path / ".vault-meta" / "transport.json"
    snapshot.parent.mkdir(parents=True)
    snapshot.write_text("{not json", encoding="utf-8")

    selection = select_runtime_transport(tmp_path)

    assert selection.name == "filesystem"
    assert selection.snapshot_preferred is None
    assert any("not valid JSON" in warning for warning in selection.warnings)

