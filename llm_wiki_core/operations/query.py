from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_wiki_core.operations.search import search_wiki
from llm_wiki_core.retrieval.lexical import InvalidSearchQueryError
from llm_wiki_core.transport.runtime import select_runtime_transport


@dataclass(frozen=True)
class QueryResult:
    operation: str
    status: str
    question: str
    answer: str
    cited_pages: list[str] = field(default_factory=list)
    gaps: list[str] = field(default_factory=list)
    suggested_save: bool = False


def query_wiki(
    vault_root: str | Path,
    question: str,
    depth: str = "standard",
    transport: object | None = None,
) -> QueryResult:
    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    _read_if_exists(active_transport, "wiki/hot.md")
    _read_if_exists(active_transport, "wiki/index.md")

    try:
        search_result = search_wiki(root, question, limit=3, transport=active_transport)
    except InvalidSearchQueryError:
        return _needs_sources_result(question)

    if not search_result.results:
        return _needs_sources_result(question)

    top_pages = [page.path for page in search_result.results]
    citations = [_wikilink(page) for page in top_pages]
    answer = (
        "Based on the current wiki, the most relevant page is "
        + ", ".join(citations)
        + ". Use the cited page content as the grounded context for this question."
    )

    return QueryResult(
        operation="query",
        status="success",
        question=question,
        answer=answer,
        cited_pages=top_pages,
        gaps=[],
        suggested_save=True,
    )


def _read_if_exists(transport: object, relative_path: str) -> str:
    try:
        return transport.read_text(relative_path)  # type: ignore[attr-defined]
    except FileNotFoundError:
        return ""
    except KeyError:
        return ""


def _needs_sources_result(question: str) -> QueryResult:
    return QueryResult(
        operation="query",
        status="needs_sources",
        question=question,
        answer=f"I don't have enough wiki coverage to answer: {question}",
        cited_pages=[],
        gaps=[f"No relevant wiki page found for: {question}"],
        suggested_save=False,
    )


def _wikilink(page: str) -> str:
    return f"[[{Path(page).stem}]]"
