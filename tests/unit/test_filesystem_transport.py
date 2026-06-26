from __future__ import annotations

import pytest


def test_filesystem_transport_reads_writes_and_appends_utf8_text(tmp_path) -> None:
    from llm_wiki_core.transport.filesystem import FilesystemTransport

    transport = FilesystemTransport(tmp_path)

    written = transport.write_text("wiki/concepts/热缓存.md", "# 热缓存\n")
    appended = transport.append_text("wiki/concepts/热缓存.md", "\nLLM Wiki context cache.\n")

    assert written == "wiki/concepts/热缓存.md"
    assert appended == "wiki/concepts/热缓存.md"
    assert transport.read_text("wiki/concepts/热缓存.md") == "# 热缓存\n\nLLM Wiki context cache.\n"


def test_filesystem_transport_lists_markdown_files_under_root(tmp_path) -> None:
    from llm_wiki_core.transport.filesystem import FilesystemTransport

    transport = FilesystemTransport(tmp_path)
    transport.write_text("wiki/index.md", "# Index\n")
    transport.write_text("wiki/sources/Source A.md", "# Source A\n")
    transport.write_text("wiki/assets/readme.txt", "not markdown")

    assert transport.list_markdown() == ["wiki/index.md", "wiki/sources/Source A.md"]
    assert transport.list_markdown("wiki/sources") == ["wiki/sources/Source A.md"]


def test_filesystem_transport_searches_markdown_case_insensitively(tmp_path) -> None:
    from llm_wiki_core.transport.filesystem import FilesystemTransport

    transport = FilesystemTransport(tmp_path)
    transport.write_text("wiki/index.md", "# Index\n- [[Hot Cache]]\n")
    transport.write_text("wiki/concepts/Hot Cache.md", "# Hot Cache\nRecent context for the agent.\n")
    transport.write_text("wiki/sources/Other.md", "# Other\nNo match.\n")

    results = transport.search_text("hot cache")

    assert [(result.path, result.line_number, result.line.strip()) for result in results] == [
        ("wiki/concepts/Hot Cache.md", 1, "# Hot Cache"),
        ("wiki/index.md", 2, "- [[Hot Cache]]"),
    ]


def test_filesystem_transport_rejects_paths_outside_vault(tmp_path) -> None:
    from llm_wiki_core.transport.filesystem import FilesystemTransport, PathOutsideVaultError

    transport = FilesystemTransport(tmp_path)

    with pytest.raises(PathOutsideVaultError):
        transport.read_text("../outside.md")

    with pytest.raises(PathOutsideVaultError):
        transport.write_text(tmp_path.parent / "outside.md", "outside")

    with pytest.raises(PathOutsideVaultError):
        transport.list_markdown("../outside")

    with pytest.raises(PathOutsideVaultError):
        transport.search_text("anything", root="../outside")

