from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from llm_wiki_core.retrieval.lexical import RankedPage, SearchDocument, search_documents
from llm_wiki_core.transport.runtime import select_runtime_transport


SEARCH_ROOTS = (
    "wiki/sources",
    "wiki/concepts",
    "wiki/entities",
    "wiki/questions",
    "wiki/comparisons",
)


@dataclass(frozen=True)
class SearchWikiResult:
    operation: str
    status: str
    query: str
    limit: int
    results: list[RankedPage] = field(default_factory=list)
    searched_roots: list[str] = field(default_factory=list)
    searched_pages: int = 0
    warnings: list[str] = field(default_factory=list)


def search_wiki(
    vault_root: str | Path,
    query: str,
    *,
    limit: int = 5,
    transport: object | None = None,
) -> SearchWikiResult:
    if limit < 1:
        raise ValueError("limit must be a positive integer")

    root = Path(vault_root)
    active_transport = transport or select_runtime_transport(root).transport
    documents = _read_search_documents(active_transport)
    results = search_documents(query, documents, limit=limit)
    results = _refresh_snippets(active_transport, results)
    status = "success" if results else "no_results"

    return SearchWikiResult(
        operation="search",
        status=status,
        query=query,
        limit=limit,
        results=results,
        searched_roots=list(SEARCH_ROOTS),
        searched_pages=len(documents),
        warnings=[],
    )


def _read_search_documents(transport: object) -> list[SearchDocument]:
    documents: list[SearchDocument] = []
    for root in SEARCH_ROOTS:
        for page in transport.list_markdown(root):  # type: ignore[attr-defined]
            documents.append(
                SearchDocument(
                    path=page,
                    title=Path(page).stem,
                    text=transport.read_text(page),  # type: ignore[attr-defined]
                )
            )
    return documents


def _refresh_snippets(transport: object, pages: list[RankedPage]) -> list[RankedPage]:
    refreshed: list[RankedPage] = []
    for page in pages:
        text = transport.read_text(page.path)  # type: ignore[attr-defined]
        refreshed.append(
            RankedPage(
                path=page.path,
                title=page.title,
                score=page.score,
                matched_terms=page.matched_terms,
                snippet=_snippet_without_header(text, page.matched_terms),
            )
        )
    return refreshed


def _snippet_without_header(text: str, terms: list[str], *, max_length: int = 180) -> str:
    lines = [line.strip() for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines() if line.strip()]
    folded_terms = [term.casefold() for term in terms]
    selected = lines[1] if len(lines) > 1 else (lines[0] if lines else "")
    for line in lines[1:]:
        folded_line = line.casefold()
        if any(term in folded_line for term in folded_terms):
            selected = line
            break
    collapsed = re.sub(r"\s+", " ", selected).strip()
    if len(collapsed) <= max_length:
        return collapsed
    return collapsed[: max_length - 3].rstrip() + "..."
