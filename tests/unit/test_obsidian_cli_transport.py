from __future__ import annotations

import pytest


def test_obsidian_cli_transport_methods_raise_boundary_error(tmp_path) -> None:
    from llm_wiki_core.transport import ObsidianCliTransport, ObsidianCliTransportNotImplementedError

    transport = ObsidianCliTransport(tmp_path)

    calls = [
        lambda: transport.read_text("wiki/index.md"),
        lambda: transport.write_text("wiki/index.md", "content"),
        lambda: transport.append_text("wiki/index.md", "content"),
        lambda: transport.exists("wiki/index.md"),
        lambda: transport.list_markdown("wiki"),
        lambda: transport.search_text("query", "wiki"),
    ]

    for call in calls:
        with pytest.raises(ObsidianCliTransportNotImplementedError, match="not implemented"):
            call()

