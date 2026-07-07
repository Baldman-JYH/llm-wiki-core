from __future__ import annotations

import pytest


class SpyTransport:
    def __init__(self) -> None:
        self.list_roots: list[str] = []
        self.read_paths: list[str] = []
        self.write_attempted = False
        self.files = {
            "wiki/index.md": "# Wiki Index\n\n- [[Durable Wiki]]\n",
            "wiki/hot.md": "# Hot\n\nRecent context mentions durable wiki.",
            "wiki/sources/Karpathy LLM Wiki.md": "# Karpathy LLM Wiki\n\nThe LLM Wiki pattern compiles knowledge into Markdown pages.",
            "wiki/concepts/Durable Wiki.md": "# Durable Wiki\n\nA durable wiki keeps durable Markdown knowledge.",
            "wiki/meta/Lint Report.md": "# Lint Report\n\nDurable operational note.",
            ".raw/articles/source.md": "# Raw\n\nDurable raw source.",
        }

    def list_markdown(self, root: str = "wiki") -> list[str]:
        self.list_roots.append(root)
        return sorted(path for path in self.files if path.startswith(root + "/") and path.endswith(".md"))

    def read_text(self, relative_path: str) -> str:
        self.read_paths.append(relative_path)
        return self.files[relative_path]

    def write_text(self, relative_path: str, content: str) -> str:
        self.write_attempted = True
        raise AssertionError(f"search must not write {relative_path}: {content}")


def test_search_wiki_returns_ranked_wiki_pages_without_mutation(tmp_path) -> None:
    from llm_wiki_core.operations.search import search_wiki

    transport = SpyTransport()

    result = search_wiki(tmp_path, "durable wiki knowledge", limit=2, transport=transport)

    assert result.operation == "search"
    assert result.status == "success"
    assert result.query == "durable wiki knowledge"
    assert result.limit == 2
    assert result.searched_roots == [
        "wiki/sources",
        "wiki/concepts",
        "wiki/entities",
        "wiki/questions",
        "wiki/comparisons",
    ]
    assert result.searched_pages == 2
    assert [page.path for page in result.results] == [
        "wiki/concepts/Durable Wiki.md",
        "wiki/sources/Karpathy LLM Wiki.md",
    ]
    assert result.results[0].title == "Durable Wiki"
    assert result.results[0].matched_terms == ["durable", "wiki", "knowledge"]
    assert result.results[0].snippet == "# Durable Wiki"
    assert transport.list_roots == [
        "wiki/sources",
        "wiki/concepts",
        "wiki/entities",
        "wiki/questions",
        "wiki/comparisons",
    ]
    assert ".raw/articles/source.md" not in transport.read_paths
    assert "wiki/index.md" not in transport.read_paths
    assert "wiki/hot.md" not in transport.read_paths
    assert "wiki/meta/Lint Report.md" not in transport.read_paths
    assert transport.read_paths.count("wiki/sources/Karpathy LLM Wiki.md") == 1
    assert transport.read_paths.count("wiki/concepts/Durable Wiki.md") == 1
    assert transport.write_attempted is False


def test_search_wiki_reports_no_results_for_uncovered_topic(tmp_path) -> None:
    from llm_wiki_core.operations.search import search_wiki

    result = search_wiki(tmp_path, "unrepresented topic", transport=SpyTransport())

    assert result.status == "no_results"
    assert result.results == []
    assert result.searched_pages == 2


def test_search_wiki_rejects_invalid_limit(tmp_path) -> None:
    from llm_wiki_core.operations.search import search_wiki

    with pytest.raises(ValueError, match="limit must be a positive integer"):
        search_wiki(tmp_path, "durable wiki", limit=0, transport=SpyTransport())


def test_search_wiki_rejects_stopword_only_query(tmp_path) -> None:
    from llm_wiki_core.operations.search import search_wiki

    with pytest.raises(ValueError, match="search query has no searchable terms"):
        search_wiki(tmp_path, "what is the and", transport=SpyTransport())


def test_search_wiki_roots_come_from_organization_routes(tmp_path, monkeypatch) -> None:
    import llm_wiki_core.operations.search as search_module
    from llm_wiki_core.operations.search import search_wiki

    monkeypatch.setattr(
        search_module,
        "search_roots_for_organization",
        lambda _organization="generic": ("wiki/routed-search",),
    )

    class RoutedSearchTransport:
        def __init__(self) -> None:
            self.list_roots: list[str] = []
            self.files = {
                "wiki/routed-search/Route Result.md": "# Route Result\n\nDurable routed search content.",
                "wiki/sources/Ignored.md": "# Ignored\n\nDurable content outside routed roots.",
            }

        def list_markdown(self, root: str = "wiki") -> list[str]:
            self.list_roots.append(root)
            return sorted(path for path in self.files if path.startswith(root + "/") and path.endswith(".md"))

        def read_text(self, relative_path: str) -> str:
            return self.files[relative_path]

    transport = RoutedSearchTransport()

    result = search_wiki(tmp_path, "durable routed", transport=transport)

    assert result.searched_roots == ["wiki/routed-search"]
    assert transport.list_roots == ["wiki/routed-search"]
    assert [page.path for page in result.results] == ["wiki/routed-search/Route Result.md"]


def test_search_wiki_default_transport_propagates_selection_warnings(tmp_path, monkeypatch) -> None:
    from llm_wiki_core.operations import search as search_module
    from llm_wiki_core.operations.search import search_wiki

    selected_transport = SpyTransport()

    class Selection:
        def __init__(self) -> None:
            self.transport = selected_transport
            self.warnings = ["fallback warning"]

    monkeypatch.setattr(search_module, "select_runtime_transport", lambda _root: Selection())

    result = search_wiki(tmp_path, "durable wiki")

    assert result.warnings == ["fallback warning"]
