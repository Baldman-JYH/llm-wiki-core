from __future__ import annotations


def _seed_wiki(tmp_path) -> None:
    from llm_wiki_core.operations.ingest import ingest_source
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="Query and save test")
    source = tmp_path / ".raw" / "articles" / "karpathy-llm-wiki.md"
    source.parent.mkdir(parents=True)
    source.write_text("# Karpathy LLM Wiki\n\nA pattern for compounding Markdown knowledge.", encoding="utf-8")
    ingest_source(tmp_path, ".raw/articles/karpathy-llm-wiki.md")


def test_query_wiki_returns_cited_pages_without_modifying_wiki(tmp_path) -> None:
    from llm_wiki_core.operations.query import query_wiki

    _seed_wiki(tmp_path)
    before = sorted(path.relative_to(tmp_path).as_posix() for path in (tmp_path / "wiki").rglob("*.md"))

    result = query_wiki(tmp_path, "What is Karpathy LLM Wiki?")

    after = sorted(path.relative_to(tmp_path).as_posix() for path in (tmp_path / "wiki").rglob("*.md"))
    assert result.operation == "query"
    assert result.status == "success"
    assert "[[Karpathy Llm Wiki]]" in result.answer
    assert result.cited_pages == ["wiki/sources/Karpathy Llm Wiki.md"]
    assert result.gaps == []
    assert before == after


def test_query_wiki_reports_gap_when_no_relevant_page_exists(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.query import query_wiki

    init_vault(tmp_path, purpose="Empty query test")

    result = query_wiki(tmp_path, "unrepresented topic")

    assert result.status == "needs_sources"
    assert result.cited_pages == []
    assert result.gaps == ["No relevant wiki page found for: unrepresented topic"]


def test_query_wiki_reports_gap_for_stopword_only_question(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.query import query_wiki

    init_vault(tmp_path, purpose="Stopword query test")

    result = query_wiki(tmp_path, "what is the and")

    assert result.operation == "query"
    assert result.status == "needs_sources"
    assert result.cited_pages == []
    assert result.gaps == ["No relevant wiki page found for: what is the and"]


def test_query_wiki_reads_pages_through_transport(tmp_path) -> None:
    from llm_wiki_core.operations.query import query_wiki

    class SpyTransport:
        def __init__(self) -> None:
            self.read_paths: list[str] = []
            self.list_roots: list[str] = []
            self.files = {
                "wiki/hot.md": "# Hot\n",
                "wiki/index.md": "# Index\n",
                "wiki/sources/Transport Page.md": "# Transport Page\n\nTransport makes Wiki reads portable.",
                "wiki/concepts/Other.md": "# Other\n\nNo useful match.",
            }

        def read_text(self, relative_path: str) -> str:
            self.read_paths.append(relative_path)
            return self.files[relative_path]

        def list_markdown(self, root: str = "wiki") -> list[str]:
            self.list_roots.append(root)
            return sorted(path for path in self.files if path.startswith(root + "/") and path.endswith(".md"))

    transport = SpyTransport()

    result = query_wiki(tmp_path, "transport wiki", transport=transport)

    assert result.status == "success"
    assert result.cited_pages == ["wiki/sources/Transport Page.md"]
    assert "[[Transport Page]]" in result.answer
    assert "wiki/hot.md" in transport.read_paths
    assert "wiki/index.md" in transport.read_paths
    assert "wiki/sources/Transport Page.md" in transport.read_paths
    assert "wiki/sources" in transport.list_roots
    assert "wiki/concepts" in transport.list_roots


def test_query_delegates_candidate_selection_to_search_wiki(tmp_path, monkeypatch) -> None:
    from types import SimpleNamespace

    import llm_wiki_core.operations.query as query_module

    class SpyTransport:
        def __init__(self) -> None:
            self.read_paths: list[str] = []
            self.files = {
                "wiki/hot.md": "# Hot\n",
                "wiki/index.md": "# Index\n",
            }

        def read_text(self, relative_path: str) -> str:
            self.read_paths.append(relative_path)
            return self.files[relative_path]

    calls: list[tuple[object, str, int, object]] = []

    def fake_search_wiki(vault_root, question: str, *, limit: int, transport: object):
        calls.append((vault_root, question, limit, transport))
        return SimpleNamespace(
            results=[
                SimpleNamespace(
                    path="wiki/concepts/Search Delegation.md",
                    title="Search Delegation",
                    snippet="Delegated search result.",
                )
            ]
        )

    monkeypatch.setattr(query_module, "search_wiki", fake_search_wiki)
    transport = SpyTransport()

    result = query_module.query_wiki(tmp_path, "delegated search", transport=transport)

    assert result.status == "success"
    assert result.cited_pages == ["wiki/concepts/Search Delegation.md"]
    assert calls == [(tmp_path, "delegated search", 3, transport)]
    assert transport.read_paths == ["wiki/hot.md", "wiki/index.md"]


def test_query_ignores_index_only_matches_when_selecting_cited_pages(tmp_path) -> None:
    from llm_wiki_core.operations.query import query_wiki

    class SpyTransport:
        def __init__(self) -> None:
            self.read_paths: list[str] = []
            self.files = {
                "wiki/hot.md": "# Hot\n",
                "wiki/index.md": "# Index\n\nThis index mentions index-only-topic.",
                "wiki/sources/Source Page.md": "# Source Page\n\nNo relevant source evidence.",
            }

        def read_text(self, relative_path: str) -> str:
            self.read_paths.append(relative_path)
            return self.files[relative_path]

        def list_markdown(self, root: str = "wiki") -> list[str]:
            return sorted(path for path in self.files if path.startswith(root + "/") and path.endswith(".md"))

    transport = SpyTransport()

    result = query_wiki(tmp_path, "index-only-topic", transport=transport)

    assert result.status == "needs_sources"
    assert result.cited_pages == []
    assert "wiki/index.md" in transport.read_paths
    assert "wiki/hot.md" in transport.read_paths


def test_query_uses_retrieval_foundation_for_ranked_pages(tmp_path) -> None:
    from llm_wiki_core.operations.query import query_wiki

    class SpyTransport:
        def __init__(self) -> None:
            self.files = {
                "wiki/hot.md": "# Hot\n",
                "wiki/index.md": "# Index\n",
                "wiki/concepts/Durable Wiki.md": "# Durable Wiki\n\nDurable wiki knowledge appears several times. Durable wiki.",
                "wiki/sources/Karpathy LLM Wiki.md": "# Karpathy LLM Wiki\n\nThe LLM Wiki pattern compiles knowledge.",
            }

        def read_text(self, relative_path: str) -> str:
            return self.files[relative_path]

        def list_markdown(self, root: str = "wiki") -> list[str]:
            return sorted(path for path in self.files if path.startswith(root + "/") and path.endswith(".md"))

    result = query_wiki(tmp_path, "durable wiki knowledge", transport=SpyTransport())

    assert result.status == "success"
    assert result.cited_pages[0] == "wiki/concepts/Durable Wiki.md"
    assert "[[Durable Wiki]]" in result.answer


def test_save_insight_creates_question_page_and_updates_wiki(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight

    init_vault(tmp_path, purpose="Save test")

    result = save_insight(
        tmp_path,
        content="Artifact-level equivalence means structure and metadata match.",
        title="Artifact Equivalence",
    )

    page = tmp_path / "wiki" / "questions" / "Artifact Equivalence.md"
    assert result.operation == "save"
    assert result.status == "success"
    assert page.is_file()
    assert "Artifact-level equivalence" in page.read_text(encoding="utf-8")
    assert "wiki/questions/Artifact Equivalence.md" in result.files_created
    assert "wiki/index.md" in result.files_updated
    assert "wiki/log.md" in result.files_updated
    assert "wiki/hot.md" in result.files_updated
    hot = (tmp_path / "wiki" / "hot.md").read_text(encoding="utf-8")
    assert "created: " in hot
    assert "status: active" in hot


def test_save_insight_can_create_concept_page(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight

    init_vault(tmp_path, purpose="Concept save test")

    result = save_insight(
        tmp_path,
        content="Hot cache is recent context, not a journal.",
        title="Hot Cache",
        target_type="concept",
    )

    assert result.status == "success"
    assert (tmp_path / "wiki" / "concepts" / "Hot Cache.md").is_file()


def test_save_question_page_path_comes_from_organization_route(tmp_path, monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    routed = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "question": "wiki/routed-questions"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": routed)

    init_vault(tmp_path, purpose="Route save question")

    result = save_insight(
        tmp_path,
        content="Route-backed question save.",
        title="Route Question",
    )

    assert result.page_path == "wiki/routed-questions/Route Question.md"
    assert (tmp_path / "wiki" / "routed-questions" / "Route Question.md").is_file()
    assert not (tmp_path / "wiki" / "questions" / "Route Question.md").exists()


def test_save_concept_page_path_comes_from_organization_route(tmp_path, monkeypatch) -> None:
    from dataclasses import replace
    from types import MappingProxyType

    import llm_wiki_core.vault.routes as routes_module
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight
    from llm_wiki_core.vault.scaffold import get_organization_definition

    base = get_organization_definition("generic")
    routed = replace(
        base,
        page_type_routes=MappingProxyType({**base.page_type_routes, "concept": "wiki/routed-concepts"}),
    )
    monkeypatch.setattr(routes_module, "get_organization_definition", lambda _name="generic": routed)

    init_vault(tmp_path, purpose="Route save concept")

    result = save_insight(
        tmp_path,
        content="Route-backed concept save.",
        title="Route Concept",
        target_type="concept",
    )

    assert result.page_path == "wiki/routed-concepts/Route Concept.md"
    assert (tmp_path / "wiki" / "routed-concepts" / "Route Concept.md").is_file()
    assert not (tmp_path / "wiki" / "concepts" / "Route Concept.md").exists()


def test_save_target_type_allowlist_is_preserved(tmp_path) -> None:
    import pytest

    from llm_wiki_core.operations.save import save_insight

    with pytest.raises(ValueError, match="target_type must be question or concept"):
        save_insight(tmp_path, content="Entity saves are not part of R5.1.", target_type="entity")


def test_save_insight_uses_transport_for_write_paths(tmp_path) -> None:
    from llm_wiki_core.operations.save import save_insight

    class SpyTransport:
        def __init__(self) -> None:
            self.exists_paths: list[str] = []
            self.read_paths: list[str] = []
            self.write_calls: list[tuple[str, str]] = []
            self.files = {
                "wiki/index.md": "# Wiki Index\n\n## Questions\n",
                "wiki/log.md": "# Operation Log\n\n",
                "wiki/hot.md": "# Recent Context\n",
            }

        def exists(self, relative_path: str) -> bool:
            self.exists_paths.append(relative_path)
            return relative_path in self.files

        def read_text(self, relative_path: str) -> str:
            self.read_paths.append(relative_path)
            return self.files[relative_path]

        def write_text(self, relative_path: str, content: str) -> str:
            self.write_calls.append((relative_path, content))
            self.files[relative_path] = content
            return relative_path

    transport = SpyTransport()

    result = save_insight(
        tmp_path,
        content="Transport-backed save belongs in the wiki.",
        title="Transport Save",
        transport=transport,
    )

    written_paths = [path for path, _ in transport.write_calls]
    assert result.status == "success"
    assert result.page_path == "wiki/questions/Transport Save.md"
    assert "wiki/questions/Transport Save.md" in written_paths
    assert "wiki/index.md" in transport.read_paths
    assert "wiki/index.md" in written_paths
    assert "wiki/log.md" in transport.read_paths
    assert "wiki/log.md" in written_paths
    assert "wiki/hot.md" in written_paths


def test_cli_query_prints_answer(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    _seed_wiki(tmp_path)

    exit_code = main(["query", str(tmp_path), "Karpathy LLM Wiki"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "query success" in output
    assert "[[Karpathy Llm Wiki]]" in output


def test_cli_save_prints_summary(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main
    from llm_wiki_core.operations.init import init_vault

    init_vault(tmp_path, purpose="CLI save")

    exit_code = main(
        [
            "save",
            str(tmp_path),
            "--title",
            "Saved Insight",
            "--content",
            "Saved content belongs in the wiki.",
        ]
    )

    assert exit_code == 0
    assert (tmp_path / "wiki" / "questions" / "Saved Insight.md").is_file()
    output = capsys.readouterr().out
    assert "save success" in output
    assert "page: wiki/questions/Saved Insight.md" in output
