from __future__ import annotations

import json


def test_mvp_cli_flow_produces_artifact_level_equivalent_wiki(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    vault = tmp_path / "vault"

    assert main(["init", str(vault), "--purpose", "Validate the local LLM Wiki MVP."]) == 0
    assert (vault / ".raw" / ".manifest.json").is_file()
    assert (vault / "wiki" / "index.md").is_file()
    assert (vault / "wiki" / "log.md").is_file()
    assert (vault / "wiki" / "hot.md").is_file()
    assert (vault / "AGENTS.md").is_file()

    assert main(["detect-transport", str(vault), "--force"]) == 0
    transport = json.loads((vault / ".vault-meta" / "transport.json").read_text(encoding="utf-8"))
    assert transport["available"]["filesystem"]["available"] is True
    assert "filesystem" in transport["fallback_chain"]

    source = vault / ".raw" / "articles" / "karpathy-llm-wiki.md"
    source.parent.mkdir(parents=True)
    source.write_text(
        "# Karpathy LLM Wiki\n\n"
        "A human-curated source becomes durable Markdown wiki knowledge with links and logs.",
        encoding="utf-8",
    )

    assert main(["ingest", str(vault), ".raw/articles/karpathy-llm-wiki.md"]) == 0
    assert (vault / "wiki" / "sources" / "Karpathy Llm Wiki.md").is_file()

    assert main(["query", str(vault), "Karpathy LLM Wiki"]) == 0
    query_output = capsys.readouterr().out
    assert "query success" in query_output
    assert "[[Karpathy Llm Wiki]]" in query_output

    assert (
        main(
            [
                "save",
                str(vault),
                "--title",
                "Artifact Equivalence",
                "--content",
                "Artifact-level equivalence checks structure, links, metadata, and reports.",
            ]
        )
        == 0
    )
    assert (vault / "wiki" / "questions" / "Artifact Equivalence.md").is_file()

    assert main(["lint", str(vault)]) == 0
    lint_output = capsys.readouterr().out
    assert "lint success" in lint_output
    assert "blocker: 0" in lint_output
    assert list((vault / "wiki" / "meta").glob("lint-report-*.md"))

