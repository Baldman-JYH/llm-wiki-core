from __future__ import annotations

import pytest


class FakeRunner:
    def __init__(self, responses: dict[tuple[str, ...], tuple[int, str, str]]) -> None:
        self.responses = responses
        self.calls: list[list[str]] = []

    def run(self, argv: list[str], timeout_seconds: int):
        from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliRunResult

        self.calls.append(list(argv))
        returncode, stdout, stderr = self.responses.get(tuple(argv), (1, "", "unexpected command"))
        return ObsidianCliRunResult(argv=list(argv), returncode=returncode, stdout=stdout, stderr=stderr)


def test_obsidian_cli_transport_reads_writes_and_appends_text(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "vault=Vault", "read", "path=wiki/index.md"): (0, "# Wiki Index\n", ""),
            (
                "obsidian",
                "vault=Vault",
                "create",
                "path=wiki/concepts/hot-cache.md",
                "content=# Hot Cache\n",
                "overwrite",
            ): (0, "", ""),
            (
                "obsidian",
                "vault=Vault",
                "append",
                "path=wiki/concepts/hot-cache.md",
                "content=\ncontext\n",
            ): (0, "", ""),
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    assert transport.read_text("wiki/index.md") == "# Wiki Index\n"
    assert transport.write_text("wiki/concepts/hot-cache.md", "# Hot Cache\n") == "wiki/concepts/hot-cache.md"
    assert transport.append_text("wiki/concepts/hot-cache.md", "\ncontext\n") == "wiki/concepts/hot-cache.md"


def test_obsidian_cli_transport_lists_markdown_files(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "vault=Vault", "files", "folder=wiki"): (
                0,
                "wiki/index.md\nwiki/readme.txt\nwiki/concepts/Hot Cache.md\n",
                "",
            )
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    assert transport.list_markdown("wiki") == ["wiki/concepts/Hot Cache.md", "wiki/index.md"]


def test_obsidian_cli_transport_searches_context_output(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "vault=Vault", "search:context", "query=hot cache", "path=wiki"): (
                0,
                "wiki/concepts/Hot Cache.md:2:Recent context for the agent.\nwiki/index.md:3:- [[Hot Cache]]\n",
                "",
            )
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    results = transport.search_text("hot cache", root="wiki")

    assert [(result.path, result.line_number, result.line) for result in results] == [
        ("wiki/concepts/Hot Cache.md", 2, "Recent context for the agent."),
        ("wiki/index.md", 3, "- [[Hot Cache]]"),
    ]


def test_obsidian_cli_transport_exists_uses_read_result(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "vault=Vault", "read", "path=wiki/index.md"): (0, "# Wiki Index\n", ""),
            ("obsidian", "vault=Vault", "read", "path=wiki/missing.md"): (1, "", "not found"),
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    assert transport.exists("wiki/index.md") is True
    assert transport.exists("wiki/missing.md") is False


def test_obsidian_cli_transport_rejects_unsafe_paths(tmp_path) -> None:
    from llm_wiki_core.transport import PathOutsideVaultError
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliTransport

    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=FakeRunner({}))

    with pytest.raises(PathOutsideVaultError):
        transport.read_text("../outside.md")

    with pytest.raises(PathOutsideVaultError):
        transport.write_text(tmp_path / "absolute.md", "content")


def test_obsidian_cli_transport_nonzero_exit_raises_command_error(tmp_path) -> None:
    from llm_wiki_core.transport.obsidian_cli import ObsidianCliCommandError, ObsidianCliTransport

    runner = FakeRunner(
        {
            ("obsidian", "vault=Vault", "read", "path=wiki/index.md"): (2, "", "Obsidian app is not running"),
        }
    )
    transport = ObsidianCliTransport(tmp_path, executable="obsidian", vault_selector="Vault", runner=runner)

    with pytest.raises(ObsidianCliCommandError, match="read failed"):
        transport.read_text("wiki/index.md")
