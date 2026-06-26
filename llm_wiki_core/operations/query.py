from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

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

    candidates = _rank_pages(active_transport, question)
    if not candidates:
        return QueryResult(
            operation="query",
            status="needs_sources",
            question=question,
            answer=f"I don't have enough wiki coverage to answer: {question}",
            cited_pages=[],
            gaps=[f"No relevant wiki page found for: {question}"],
            suggested_save=False,
        )

    top_pages = [page for _, page in candidates[:3]]
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


def _rank_pages(transport: object, question: str) -> list[tuple[int, str]]:
    terms = _terms(question)
    searchable_roots = [
        "wiki/sources",
        "wiki/concepts",
        "wiki/entities",
        "wiki/questions",
        "wiki/comparisons",
    ]
    ranked: list[tuple[int, str]] = []

    for root in searchable_roots:
        for page in transport.list_markdown(root):  # type: ignore[attr-defined]
            text = transport.read_text(page).lower()  # type: ignore[attr-defined]
            score = sum(text.count(term) for term in terms)
            if score > 0:
                ranked.append((score, page))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return ranked


def _terms(question: str) -> list[str]:
    words = re.findall(r"[A-Za-z0-9]+", question.lower())
    stopwords = {"a", "an", "and", "is", "of", "the", "to", "what"}
    return [word for word in words if len(word) > 2 and word not in stopwords]


def _wikilink(page: str) -> str:
    return f"[[{Path(page).stem}]]"
