from __future__ import annotations

import json


def _seed_search_vault(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight

    init_vault(tmp_path, purpose="Search CLI test")
    save_insight(
        tmp_path,
        content="Durable Markdown knowledge belongs in the wiki.",
        title="Durable Wiki",
        target_type="concept",
    )


def test_cli_search_prints_ranked_results(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    _seed_search_vault(tmp_path)

    exit_code = main(["search", str(tmp_path), "durable wiki knowledge", "--limit", "1"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "search success" in output
    assert "query: durable wiki knowledge" in output
    assert "searched pages:" in output
    assert "wiki/concepts/Durable Wiki.md" in output
    assert "[[Durable Wiki]]" in output


def test_cli_search_json_output_is_machine_readable(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    _seed_search_vault(tmp_path)

    exit_code = main(["search", str(tmp_path), "durable wiki knowledge", "--limit", "1", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["operation"] == "search"
    assert payload["status"] == "success"
    assert payload["query"] == "durable wiki knowledge"
    assert payload["limit"] == 1
    assert payload["results"][0]["path"] == "wiki/concepts/Durable Wiki.md"
    assert payload["results"][0]["title"] == "Durable Wiki"
    assert "score" in payload["results"][0]


def test_cli_search_reports_invalid_limit(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    _seed_search_vault(tmp_path)

    exit_code = main(["search", str(tmp_path), "durable wiki", "--limit", "0"])

    assert exit_code == 1
    error = capsys.readouterr().err
    assert "search error" in error
    assert "limit must be a positive integer" in error
