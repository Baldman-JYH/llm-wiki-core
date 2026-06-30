from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import math
import re
from typing import Sequence


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "how",
    "in",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "what",
    "when",
    "where",
    "which",
    "who",
    "why",
    "with",
}


class InvalidSearchQueryError(ValueError):
    """Raised when a search query has no searchable terms."""


@dataclass(frozen=True)
class SearchDocument:
    path: str
    title: str
    text: str


@dataclass(frozen=True)
class RankedPage:
    path: str
    title: str
    score: float
    matched_terms: list[str]
    snippet: str


def tokenize(text: str) -> list[str]:
    tokens = re.findall(r"[\w]+", text.casefold(), flags=re.UNICODE)
    return [token for token in tokens if _is_searchable_token(token)]


def search_documents(
    query: str,
    documents: Sequence[SearchDocument],
    *,
    limit: int = 5,
) -> list[RankedPage]:
    query_terms = list(dict.fromkeys(tokenize(query)))
    if not query_terms:
        raise InvalidSearchQueryError("search query has no searchable terms")
    if limit < 1:
        raise ValueError("limit must be a positive integer")

    indexed = [_IndexedDocument.from_document(document) for document in documents]
    if not indexed:
        return []

    average_length = sum(item.length for item in indexed) / len(indexed)
    document_frequency = {
        term: sum(1 for item in indexed if term in item.term_counts)
        for term in query_terms
    }

    ranked: list[RankedPage] = []
    for item in indexed:
        score = _bm25_score(item, query_terms, document_frequency, len(indexed), average_length)
        if score <= 0:
            continue
        matched_terms = [term for term in query_terms if term in item.term_counts]
        snippet = _snippet(item.text, query_terms)
        ranked.append(
            RankedPage(
                path=item.path,
                title=item.title,
                score=round(score, 6),
                matched_terms=matched_terms,
                snippet=snippet,
            )
        )

    ranked.sort(key=lambda page: (-page.score, page.path, page.title))
    return ranked[:limit]


@dataclass(frozen=True)
class _IndexedDocument:
    path: str
    title: str
    text: str
    term_counts: Counter[str]
    length: int

    @classmethod
    def from_document(cls, document: SearchDocument) -> "_IndexedDocument":
        terms = tokenize(document.text)
        return cls(
            path=document.path,
            title=document.title,
            text=document.text,
            term_counts=Counter(terms),
            length=max(len(terms), 1),
        )


def _is_searchable_token(token: str) -> bool:
    if token in STOPWORDS:
        return False
    if token.isdigit():
        return True
    return len(token) > 1


def _bm25_score(
    document: _IndexedDocument,
    query_terms: Sequence[str],
    document_frequency: dict[str, int],
    document_count: int,
    average_length: float,
) -> float:
    k1 = 1.5
    b = 0.75
    score = 0.0
    for term in query_terms:
        frequency = document.term_counts.get(term, 0)
        if frequency == 0:
            continue
        containing_docs = document_frequency[term]
        inverse_document_frequency = math.log(1 + (document_count - containing_docs + 0.5) / (containing_docs + 0.5))
        denominator = frequency + k1 * (1 - b + b * (document.length / average_length))
        score += inverse_document_frequency * ((frequency * (k1 + 1)) / denominator)
    return score


def _snippet(text: str, matched_terms: Sequence[str], *, max_length: int = 180) -> str:
    body = _strip_frontmatter(text)
    lines = [line.strip() for line in body.splitlines() if line.strip()]
    folded_terms = [term.casefold() for term in matched_terms]
    selected = lines[0] if lines else ""
    for line in lines:
        folded_line = line.casefold()
        if any(term in folded_line for term in folded_terms):
            selected = line
            break
    collapsed = re.sub(r"\s+", " ", selected).strip()
    if len(collapsed) <= max_length:
        return collapsed
    return collapsed[: max_length - 3].rstrip() + "..."


def _strip_frontmatter(text: str) -> str:
    if not text.startswith("---\n"):
        return text
    end = text.find("\n---\n", 4)
    if end == -1:
        return text
    return text[end + len("\n---\n") :]
