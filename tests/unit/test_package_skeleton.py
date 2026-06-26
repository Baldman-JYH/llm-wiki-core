from __future__ import annotations

import pytest


def test_package_exposes_version() -> None:
    import llm_wiki_core

    assert llm_wiki_core.__version__ == "0.1.0"


def test_cli_help_exits_successfully(capsys: pytest.CaptureFixture[str]) -> None:
    from llm_wiki_core.cli import main

    with pytest.raises(SystemExit) as exc_info:
        main(["--help"])

    assert exc_info.value.code == 0
    assert "Neutral LLM Wiki core" in capsys.readouterr().out


def test_cli_without_arguments_exits_successfully() -> None:
    from llm_wiki_core.cli import main

    assert main([]) == 0


def test_core_skeleton_modules_import() -> None:
    import llm_wiki_core.operations.continue_
    import llm_wiki_core.operations.detect_transport
    import llm_wiki_core.operations.ingest
    import llm_wiki_core.operations.init
    import llm_wiki_core.operations.lint
    import llm_wiki_core.operations.query
    import llm_wiki_core.operations.save
    import llm_wiki_core.operations.status
    import llm_wiki_core.schema.frontmatter
    import llm_wiki_core.schema.manifest
    import llm_wiki_core.schema.wikilinks
    import llm_wiki_core.transport.filesystem
    import llm_wiki_core.transport.obsidian_cli
    import llm_wiki_core.transport.snapshot
    import llm_wiki_core.validation.lint_report
    import llm_wiki_core.validation.parity
    import llm_wiki_core.vault.hot
    import llm_wiki_core.vault.index
    import llm_wiki_core.vault.log
    import llm_wiki_core.vault.paths
    import llm_wiki_core.vault.scaffold
