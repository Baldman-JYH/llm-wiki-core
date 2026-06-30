from __future__ import annotations

import pytest


def test_tokenize_filters_common_stopwords_and_keeps_domain_terms() -> None:
    from llm_wiki_core.retrieval.lexical import tokenize

    assert tokenize("What is the durable LLM Wiki pattern?") == ["durable", "llm", "wiki", "pattern"]


def test_search_documents_ranks_more_relevant_page_first() -> None:
    from llm_wiki_core.retrieval.lexical import SearchDocument, search_documents

    documents = [
        SearchDocument(
            path="wiki/concepts/Other.md",
            title="Other",
            text="# Other\n\nA short note about unrelated tooling.",
        ),
        SearchDocument(
            path="wiki/concepts/Durable Wiki.md",
            title="Durable Wiki",
            text="# Durable Wiki\n\nA durable wiki keeps durable Markdown knowledge in the wiki.",
        ),
        SearchDocument(
            path="wiki/sources/Karpathy LLM Wiki.md",
            title="Karpathy LLM Wiki",
            text="# Karpathy LLM Wiki\n\nThe LLM Wiki pattern compiles knowledge into Markdown pages.",
        ),
    ]

    results = search_documents("durable wiki knowledge", documents, limit=2)

    assert [result.path for result in results] == [
        "wiki/concepts/Durable Wiki.md",
        "wiki/sources/Karpathy LLM Wiki.md",
    ]
    assert results[0].matched_terms == ["durable", "wiki", "knowledge"]
    assert results[0].score > results[1].score


def test_search_documents_matched_terms_uses_document_level_tokens() -> None:
    from llm_wiki_core.retrieval.lexical import SearchDocument, search_documents

    document = SearchDocument(
        path="wiki/concepts/Durable Wiki.md",
        title="Durable Wiki",
        text="# Durable Wiki\n\nA durable wiki keeps durable Markdown knowledge in the wiki.",
    )

    results = search_documents("durable wiki knowledge", [document], limit=1)

    assert results[0].matched_terms == ["durable", "wiki", "knowledge"]
    assert results[0].snippet == "# Durable Wiki"


def test_search_documents_tie_breaks_by_path() -> None:
    from llm_wiki_core.retrieval.lexical import SearchDocument, search_documents

    documents = [
        SearchDocument(path="wiki/sources/B.md", title="B", text="# B\n\nTransport search."),
        SearchDocument(path="wiki/concepts/A.md", title="A", text="# A\n\nTransport search."),
    ]

    results = search_documents("transport", documents, limit=5)

    assert [result.path for result in results] == ["wiki/concepts/A.md", "wiki/sources/B.md"]


@pytest.mark.parametrize(
    "text",
    [
        "---\ntype: concept\n---\n\n# Hot Cache\n\nRecent    context for the agent.",
        "---\r\ntype: concept\r\n---\r\n\r\n# Hot Cache\r\n\r\nRecent    context for the agent.",
    ],
)
def test_search_documents_snippet_strips_frontmatter_and_collapses_whitespace(text: str) -> None:
    from llm_wiki_core.retrieval.lexical import SearchDocument, search_documents

    document = SearchDocument(
        path="wiki/concepts/Hot Cache.md",
        title="Hot Cache",
        text=text,
    )

    results = search_documents("type concept hot", [document], limit=1)

    assert results[0].snippet == "# Hot Cache"
    assert "type: concept" not in results[0].snippet


def test_search_documents_does_not_match_frontmatter_only_terms() -> None:
    from llm_wiki_core.retrieval.lexical import SearchDocument, search_documents

    document = SearchDocument(
        path="wiki/concepts/Status Only.md",
        title="Status Only",
        text="---\nstatus: active\ntype: concept\n---\n\n# Status Only\n\nBody discusses durable wiki notes.",
    )

    results = search_documents("active concept", [document], limit=5)

    assert results == []


def test_search_documents_rejects_empty_or_stopword_only_query() -> None:
    from llm_wiki_core.retrieval.lexical import InvalidSearchQueryError, SearchDocument, search_documents

    documents = [SearchDocument(path="wiki/sources/A.md", title="A", text="# A\n\nContent.")]

    with pytest.raises(InvalidSearchQueryError, match="search query has no searchable terms"):
        search_documents("what is the and", documents, limit=5)
