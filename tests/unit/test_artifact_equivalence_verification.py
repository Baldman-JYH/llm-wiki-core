from __future__ import annotations

import json


def test_mvp_artifact_level_equivalence_verification(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations.continue_ import continue_wiki
    from llm_wiki_core.operations.detect_transport import detect_transport
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.lint import lint_wiki
    from llm_wiki_core.operations.query import query_wiki
    from llm_wiki_core.operations.save import save_insight
    from llm_wiki_core.operations.status import status_wiki

    monkeypatch.setenv("PATH", "")
    vault = tmp_path / "vault"
    raw_text = (
        "# Karpathy LLM Wiki\n\n"
        "The LLM Wiki pattern keeps raw sources immutable while the agent maintains durable Markdown pages, "
        "indexes, logs, and recent context."
    )

    init_result = init_vault(vault, purpose="Verify artifact-level equivalence")
    assert init_result.status == "success"

    required_paths = [
        ".raw/.manifest.json",
        "wiki/index.md",
        "wiki/log.md",
        "wiki/hot.md",
        "wiki/overview.md",
        "wiki/sources",
        "wiki/entities",
        "wiki/concepts",
        "wiki/questions",
        "wiki/comparisons",
        "wiki/meta",
        "AGENTS.md",
    ]
    for relative in required_paths:
        assert (vault / relative).exists(), relative

    agents = (vault / "AGENTS.md").read_text(encoding="utf-8")
    assert "artifact-level equivalence" in agents
    assert "llm-wiki ingest" in agents
    assert "resume wiki context" in agents

    transport_result = detect_transport(vault, force=True)
    snapshot = json.loads((vault / ".vault-meta" / "transport.json").read_text(encoding="utf-8"))
    assert transport_result.snapshot.preferred == "filesystem"
    assert snapshot["preferred"] == "filesystem"
    assert snapshot["available"]["filesystem"]["available"] is True
    assert snapshot["available"]["filesystem"]["implemented"] is True
    assert snapshot["available"]["obsidian-cli"]["implemented"] is False

    source = vault / ".raw" / "articles" / "karpathy-llm-wiki.md"
    source.parent.mkdir(parents=True)
    source.write_text(raw_text, encoding="utf-8")

    ingest_result = ingest_source(vault, ".raw/articles/karpathy-llm-wiki.md")
    assert ingest_result.status == "success"
    assert source.read_text(encoding="utf-8") == raw_text
    assert ingest_result.files_created == ["wiki/sources/Karpathy Llm Wiki.md"]
    assert "wiki/index.md" in ingest_result.files_updated
    assert "wiki/log.md" in ingest_result.files_updated
    assert "wiki/hot.md" in ingest_result.files_updated
    assert ".raw/.manifest.json" in ingest_result.files_updated

    manifest = json.loads((vault / ".raw" / ".manifest.json").read_text(encoding="utf-8"))
    record = manifest["sources"]["articles/karpathy-llm-wiki.md"]
    assert record["source_path"] == ".raw/articles/karpathy-llm-wiki.md"
    assert record["status"] == "ingested"
    assert record["content_fingerprint"].startswith("sha256:")
    assert record["generated_pages"] == ["wiki/sources/Karpathy Llm Wiki.md"]

    source_page = (vault / "wiki" / "sources" / "Karpathy Llm Wiki.md").read_text(encoding="utf-8")
    assert "type: source" in source_page
    assert 'source_path: ".raw/articles/karpathy-llm-wiki.md"' in source_page
    assert "content_fingerprint:" in source_page
    assert "Raw source: `.raw/articles/karpathy-llm-wiki.md`" in source_page

    index_after_ingest = (vault / "wiki" / "index.md").read_text(encoding="utf-8")
    log_after_ingest = (vault / "wiki" / "log.md").read_text(encoding="utf-8")
    hot_after_ingest = (vault / "wiki" / "hot.md").read_text(encoding="utf-8")
    assert "[[Karpathy Llm Wiki]]" in index_after_ingest
    assert "ingest | Karpathy Llm Wiki" in log_after_ingest
    assert "Ingested [[Karpathy Llm Wiki]]" in hot_after_ingest

    before_query_files = sorted(path.relative_to(vault).as_posix() for path in (vault / "wiki").rglob("*.md"))
    query_result = query_wiki(vault, "What is the Karpathy LLM Wiki pattern?")
    after_query_files = sorted(path.relative_to(vault).as_posix() for path in (vault / "wiki").rglob("*.md"))
    assert query_result.status == "success"
    assert query_result.cited_pages == ["wiki/sources/Karpathy Llm Wiki.md"]
    assert "[[Karpathy Llm Wiki]]" in query_result.answer
    assert before_query_files == after_query_files

    save_result = save_insight(
        vault,
        title="Artifact Equivalence",
        content="Artifact-level equivalence verifies structure, metadata, links, logs, and lint results.",
    )
    assert save_result.status == "success"
    assert save_result.page_path == "wiki/questions/Artifact Equivalence.md"
    assert "wiki/questions/Artifact Equivalence.md" in save_result.files_created

    saved_page = (vault / "wiki" / "questions" / "Artifact Equivalence.md").read_text(encoding="utf-8")
    assert "type: question" in saved_page
    assert 'title: "Artifact Equivalence"' in saved_page
    assert "Artifact-level equivalence verifies" in saved_page

    index_after_save = (vault / "wiki" / "index.md").read_text(encoding="utf-8")
    log_after_save = (vault / "wiki" / "log.md").read_text(encoding="utf-8")
    hot_after_save = (vault / "wiki" / "hot.md").read_text(encoding="utf-8")
    assert "[[Artifact Equivalence]]" in index_after_save
    assert "save | Artifact Equivalence" in log_after_save
    assert "Saved [[Artifact Equivalence]]" in hot_after_save

    status_result = status_wiki(vault)
    assert status_result.status == "success"
    assert status_result.initialized is True
    assert status_result.source_count == 1
    assert status_result.preferred_transport == "filesystem"
    assert status_result.missing_required_paths == []

    continue_result = continue_wiki(vault)
    assert continue_result.status == "success"
    assert continue_result.files_read == ["wiki/hot.md", "wiki/index.md", "wiki/log.md"]
    assert "Recent Context" in continue_result.hot_context
    assert "Wiki Index" in continue_result.index_context
    assert any("save | Artifact Equivalence" in entry for entry in continue_result.recent_log_entries)

    lint_result = lint_wiki(vault)
    assert lint_result.status == "success"
    assert lint_result.counts == {"blocker": 0, "high": 0, "medium": 0, "low": 0}
    assert lint_result.report_path is not None
    assert (vault / lint_result.report_path).is_file()

