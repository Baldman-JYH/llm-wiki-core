from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_wiki_core.retrieval.lexical import RankedPage, SearchDocument, search_documents
from llm_wiki_core.vault.routes import search_roots_for_organization
from llm_wiki_core.transport.runtime import select_runtime_transport


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
    selection = None if transport is not None else select_runtime_transport(root)
    active_transport = transport or selection.transport
    search_roots = search_roots_for_organization("generic")
    documents = _read_search_documents(active_transport, search_roots)
    results = search_documents(query, documents, limit=limit)
    status = "success" if results else "no_results"
    warnings = list(selection.warnings) if selection else []

    return SearchWikiResult(
        operation="search",
        status=status,
        query=query,
        limit=limit,
        results=results,
        searched_roots=list(search_roots),
        searched_pages=len(documents),
        warnings=warnings,
    )


def _read_search_documents(transport: object, search_roots: tuple[str, ...]) -> list[SearchDocument]:
    documents: list[SearchDocument] = []
    for root in search_roots:
        for page in transport.list_markdown(root):  # type: ignore[attr-defined]
            documents.append(
                SearchDocument(
                    path=page,
                    title=Path(page).stem,
                    text=transport.read_text(page),  # type: ignore[attr-defined]
                )
            )
    return documents
