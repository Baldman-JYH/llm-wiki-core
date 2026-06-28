from __future__ import annotations


def test_official_obsidian_profile_builds_name_value_commands() -> None:
    from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliProfile

    profile = ObsidianCliProfile(executable="obsidian", vault_selector="Research Vault")

    assert profile.help_argv() == ["obsidian", "--help"]
    assert profile.vault_info_path_argv() == [
        "obsidian",
        "vault=Research Vault",
        "vault",
        "info=path",
    ]
    assert profile.read_argv("wiki/index.md") == [
        "obsidian",
        "vault=Research Vault",
        "read",
        "path=wiki/index.md",
    ]
    write_argv = profile.write_argv("wiki/notes/hot-cache.md", "line 1\nline 2\n")
    assert write_argv == [
        "obsidian",
        "vault=Research Vault",
        "create",
        "path=wiki/notes/hot-cache.md",
        "content=line 1\nline 2\n",
        "overwrite",
    ]
    assert write_argv[3] == "path=wiki/notes/hot-cache.md"
    assert profile.append_argv("wiki/log.md", "append\n") == [
        "obsidian",
        "vault=Research Vault",
        "append",
        "path=wiki/log.md",
        "content=append\n",
    ]
    assert profile.files_argv("wiki") == [
        "obsidian",
        "vault=Research Vault",
        "files",
        "folder=wiki",
    ]
    assert profile.search_argv("hot cache", "wiki") == [
        "obsidian",
        "vault=Research Vault",
        "search:context",
        "query=hot cache",
        "path=wiki",
    ]


def test_transport_package_exports_obsidian_cli_symbols() -> None:
    from llm_wiki_core.transport import (
        ObsidianCliProfile,
        ObsidianCliRunner,
        ObsidianCliRunResult,
        SubprocessObsidianCliRunner,
    )

    assert ObsidianCliProfile.__name__ == "ObsidianCliProfile"
    assert ObsidianCliRunner.__name__ == "ObsidianCliRunner"
    assert SubprocessObsidianCliRunner.__name__ == "SubprocessObsidianCliRunner"
    assert ObsidianCliRunResult.__name__ == "ObsidianCliRunResult"


def test_subprocess_runner_captures_stdout_stderr_and_return_code() -> None:
    from llm_wiki_core.transport.obsidian_cli_runner import SubprocessObsidianCliRunner

    runner = SubprocessObsidianCliRunner()
    result = runner.run(
        [
            "python",
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr); sys.exit(3)",
        ],
        timeout_seconds=5,
    )

    assert result.returncode == 3
    assert result.stdout.strip() == "out"
    assert result.stderr.strip() == "err"
    assert result.argv[0] == "python"
