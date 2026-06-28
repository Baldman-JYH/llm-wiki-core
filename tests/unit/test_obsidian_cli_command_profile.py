from __future__ import annotations


def test_official_obsidian_profile_builds_name_value_commands() -> None:
    from llm_wiki_core.transport.obsidian_cli_runner import ObsidianCliProfile

    profile = ObsidianCliProfile(executable="obsidian", vault_selector="Research Vault")

    assert profile.help_argv() == ["obsidian", "--help"]
    assert profile.read_argv("wiki/index.md") == [
        "obsidian",
        "read",
        "vault=Research Vault",
        "path=wiki/index.md",
    ]
    write_argv = profile.write_argv("wiki/notes/热缓存.md", "line 1\nline 2\n")
    assert write_argv == [
        "obsidian",
        "create",
        "vault=Research Vault",
        "path=wiki/notes/热缓存.md",
        "content=line 1\nline 2\n",
        "overwrite=true",
    ]
    assert write_argv[3] == "path=wiki/notes/热缓存.md"
    assert profile.append_argv("wiki/log.md", "append\n") == [
        "obsidian",
        "append",
        "vault=Research Vault",
        "path=wiki/log.md",
        "content=append\n",
    ]
    assert profile.files_argv("wiki") == [
        "obsidian",
        "files",
        "vault=Research Vault",
        "path=wiki",
    ]
    assert profile.search_argv("hot cache", "wiki") == [
        "obsidian",
        "search:context",
        "vault=Research Vault",
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
