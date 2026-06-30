# R3.3 Retrieval Foundation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only local Markdown wiki search operation with deterministic BM25-style lexical ranking, then make `query` reuse it.

**Architecture:** Add a pure retrieval module under `llm_wiki_core/retrieval/`, then expose it through `llm_wiki_core.operations.search.search_wiki`. The CLI gets a `search` command, and `query_wiki` delegates ranking to the new operation while preserving current no-mutation query semantics.

**Tech Stack:** Python 3.10+, standard library only, `pytest`, existing `argparse` CLI, existing transport contract with `list_markdown()` and `read_text()`.

## Global Constraints

- The canonical abstraction is Karpathy's LLM Wiki gist: search durable `wiki/` pages first, do not bypass the compiled Markdown wiki with generic RAG.
- `AgriciDaniel/claude-obsidian` is a reference implementation, not a dependency.
- No runtime dependency may be added; `pyproject.toml` must keep `dependencies = []`.
- R3.3 is read-only retrieval; it must not mutate `.raw/` or `wiki/`.
- R3.3 must not implement vector search, embeddings, hybrid retrieval, reranking, qmd integration, public internet search, raw-source search by default, persistent indexes, or LLM synthesis.
- Default search roots are `wiki/sources`, `wiki/concepts`, `wiki/entities`, `wiki/questions`, and `wiki/comparisons`.
- `wiki/hot.md` and `wiki/index.md` remain query orientation inputs, but they are not ranked content results by default.
- Keep behavior portable on Windows PowerShell, macOS, and Linux.
- Commit messages must be written in Chinese.

---

## File Structure

- Create `llm_wiki_core/retrieval/__init__.py`: export retrieval dataclasses, ranking function, and invalid-query error.
- Create `llm_wiki_core/retrieval/lexical.py`: tokenize text, strip frontmatter, create deterministic snippets, and rank documents with BM25-style lexical scoring.
- Create `llm_wiki_core/operations/search.py`: operation-level transport integration and `SearchWikiResult` dataclass.
- Modify `llm_wiki_core/operations/query.py`: remove local term-count ranking and call `search_wiki`.
- Modify `llm_wiki_core/cli.py`: add `search` parser, execution dispatch, text output, and JSON output via existing helpers.
- Create `tests/unit/test_lexical_retrieval.py`: pure retrieval module tests.
- Create `tests/unit/test_search_operation.py`: operation tests using spy transports.
- Create `tests/unit/test_search_cli.py`: CLI text and JSON tests.
- Modify `tests/unit/test_query_save_operations.py`: add regression tests for query integration and candidate scope.
- Create or modify `tests/unit/test_r3_3_retrieval_docs.py`: documentation guard tests.
- Modify public docs: `README.md`, `docs/user-guide.md`, `docs/operation-contract.md`, `docs/roadmap-schedule.md`, and `docs/codex-command-contract.md`.

---

### Task 1: Pure Lexical Retrieval Module

**Files:**
- Create: `llm_wiki_core/retrieval/__init__.py`
- Create: `llm_wiki_core/retrieval/lexical.py`
- Test: `tests/unit/test_lexical_retrieval.py`

**Interfaces:**
- Consumes: plain document records supplied by operation code.
- Produces:
  - `InvalidSearchQueryError(ValueError)`
  - `SearchDocument(path: str, title: str, text: str)`
  - `RankedPage(path: str, title: str, score: float, matched_terms: list[str], snippet: str)`
  - `tokenize(text: str) -> list[str]`
  - `search_documents(query: str, documents: Sequence[SearchDocument], *, limit: int = 5) -> list[RankedPage]`

- [ ] **Step 1: Write failing tests for tokenization, ranking, snippets, and invalid queries**

Create `tests/unit/test_lexical_retrieval.py`:

```python
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
    assert results[0].matched_terms == ["durable", "wiki"]
    assert results[0].score > results[1].score


def test_search_documents_tie_breaks_by_path() -> None:
    from llm_wiki_core.retrieval.lexical import SearchDocument, search_documents

    documents = [
        SearchDocument(path="wiki/sources/B.md", title="B", text="# B\n\nTransport search."),
        SearchDocument(path="wiki/concepts/A.md", title="A", text="# A\n\nTransport search."),
    ]

    results = search_documents("transport", documents, limit=5)

    assert [result.path for result in results] == ["wiki/concepts/A.md", "wiki/sources/B.md"]


def test_search_documents_snippet_strips_frontmatter_and_collapses_whitespace() -> None:
    from llm_wiki_core.retrieval.lexical import SearchDocument, search_documents

    document = SearchDocument(
        path="wiki/concepts/Hot Cache.md",
        title="Hot Cache",
        text="---\ntype: concept\n---\n\n# Hot Cache\n\nRecent    context for the agent.",
    )

    results = search_documents("recent context", [document], limit=1)

    assert results[0].snippet == "Recent context for the agent."
    assert "type: concept" not in results[0].snippet


def test_search_documents_rejects_empty_or_stopword_only_query() -> None:
    from llm_wiki_core.retrieval.lexical import InvalidSearchQueryError, SearchDocument, search_documents

    documents = [SearchDocument(path="wiki/sources/A.md", title="A", text="# A\n\nContent.")]

    with pytest.raises(InvalidSearchQueryError, match="search query has no searchable terms"):
        search_documents("what is the and", documents, limit=5)
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_lexical_retrieval.py -q
```

Expected: fail with `ModuleNotFoundError: No module named 'llm_wiki_core.retrieval'`.

- [ ] **Step 3: Implement the retrieval module**

Create `llm_wiki_core/retrieval/__init__.py`:

```python
from __future__ import annotations

from llm_wiki_core.retrieval.lexical import (
    InvalidSearchQueryError,
    RankedPage,
    SearchDocument,
    search_documents,
    tokenize,
)

__all__ = [
    "InvalidSearchQueryError",
    "RankedPage",
    "SearchDocument",
    "search_documents",
    "tokenize",
]
```

Create `llm_wiki_core/retrieval/lexical.py`:

```python
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
        ranked.append(
            RankedPage(
                path=item.path,
                title=item.title,
                score=round(score, 6),
                matched_terms=matched_terms,
                snippet=_snippet(item.text, matched_terms),
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
```

- [ ] **Step 4: Run retrieval tests**

Run:

```powershell
python -m pytest tests/unit/test_lexical_retrieval.py -q
```

Expected: `5 passed`.

- [ ] **Step 5: Commit Task 1**

```powershell
git add llm_wiki_core/retrieval tests/unit/test_lexical_retrieval.py
git commit -m "实现 R3.3 词法检索模块"
```

---

### Task 2: Search Operation

**Files:**
- Create: `llm_wiki_core/operations/search.py`
- Test: `tests/unit/test_search_operation.py`

**Interfaces:**
- Consumes:
  - `SearchDocument` and `search_documents` from `llm_wiki_core.retrieval.lexical`.
  - active transport with `list_markdown(root)` and `read_text(path)`.
- Produces:
  - `SEARCH_ROOTS: tuple[str, ...]`
  - `SearchWikiResult(operation: str, status: str, query: str, limit: int, results: list[RankedPage], searched_roots: list[str], searched_pages: int, warnings: list[str])`
  - `search_wiki(vault_root: str | Path, query: str, *, limit: int = 5, transport: object | None = None) -> SearchWikiResult`

- [ ] **Step 1: Write failing operation tests**

Create `tests/unit/test_search_operation.py`:

```python
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
    assert "durable wiki keeps durable Markdown knowledge" in result.results[0].snippet
    assert ".raw/articles/source.md" not in transport.read_paths
    assert "wiki/index.md" not in transport.read_paths
    assert "wiki/hot.md" not in transport.read_paths
    assert "wiki/meta/Lint Report.md" not in transport.read_paths
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_search_operation.py -q
```

Expected: fail with `ModuleNotFoundError: No module named 'llm_wiki_core.operations.search'`.

- [ ] **Step 3: Implement `search_wiki`**

Create `llm_wiki_core/operations/search.py`:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

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
```

- [ ] **Step 4: Run operation tests**

Run:

```powershell
python -m pytest tests/unit/test_search_operation.py -q
```

Expected: `4 passed`.

- [ ] **Step 5: Commit Task 2**

```powershell
git add llm_wiki_core/operations/search.py tests/unit/test_search_operation.py
git commit -m "实现 R3.3 搜索操作"
```

---

### Task 3: CLI Search Command

**Files:**
- Modify: `llm_wiki_core/cli.py`
- Test: `tests/unit/test_search_cli.py`

**Interfaces:**
- Consumes: `search_wiki(vault_root, query, limit=5)`.
- Produces:
  - CLI command `llm-wiki search <vault> "<query>" [--limit N] [--json]`
  - text output with operation, status, query, searched pages, and result lines
  - JSON output through existing `_to_jsonable`

- [ ] **Step 1: Write failing CLI tests**

Create `tests/unit/test_search_cli.py`:

```python
from __future__ import annotations

import json


def _seed_search_vault(tmp_path) -> None:
    from llm_wiki_core.operations.init import init_vault
    from llm_wiki_core.operations.save import save_insight

    init_vault(tmp_path, purpose="Search CLI test")
    save_insight(
        tmp_path,
        content="Durable Markdown knowledge belongs in the wiki.",
        title="Durable Wiki",
        target_type="concept",
    )


def test_cli_search_prints_ranked_results(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    _seed_search_vault(tmp_path)

    exit_code = main(["search", str(tmp_path), "durable wiki knowledge", "--limit", "1"])

    assert exit_code == 0
    output = capsys.readouterr().out
    assert "search success" in output
    assert "query: durable wiki knowledge" in output
    assert "searched pages:" in output
    assert "wiki/concepts/Durable Wiki.md" in output
    assert "[[Durable Wiki]]" in output


def test_cli_search_json_output_is_machine_readable(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    _seed_search_vault(tmp_path)

    exit_code = main(["search", str(tmp_path), "durable wiki knowledge", "--limit", "1", "--json"])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["operation"] == "search"
    assert payload["status"] == "success"
    assert payload["query"] == "durable wiki knowledge"
    assert payload["limit"] == 1
    assert payload["results"][0]["path"] == "wiki/concepts/Durable Wiki.md"
    assert payload["results"][0]["title"] == "Durable Wiki"
    assert "score" in payload["results"][0]


def test_cli_search_reports_invalid_limit(tmp_path, capsys) -> None:
    from llm_wiki_core.cli import main

    _seed_search_vault(tmp_path)

    exit_code = main(["search", str(tmp_path), "durable wiki", "--limit", "0"])

    assert exit_code == 1
    error = capsys.readouterr().err
    assert "search error" in error
    assert "limit must be a positive integer" in error
```

- [ ] **Step 2: Run CLI tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_search_cli.py -q
```

Expected: fail because `argparse` does not know the `search` command.

- [ ] **Step 3: Wire CLI parser, dispatch, and text output**

Modify `llm_wiki_core/cli.py`:

```python
from llm_wiki_core.operations.search import search_wiki
```

Add parser near the existing `query` parser:

```python
    search_parser = subparsers.add_parser("search", help="Search ranked local LLM Wiki pages.")
    search_parser.add_argument("vault", help="Path to the vault root.")
    search_parser.add_argument("query", help="Search query.")
    search_parser.add_argument("--limit", type=int, default=5, help="Maximum ranked pages to return.")
    _add_json_option(search_parser)
```

Add dispatch in `_execute` before or after `query`:

```python
    if args.command == "search":
        return search_wiki(args.vault, args.query, limit=args.limit)
```

Add text output in `_print_text_result`:

```python
    if command == "search":
        print(f"{result.operation} {result.status}")
        print(f"query: {result.query}")
        print(f"searched pages: {result.searched_pages}")
        if result.results:
            print("results:")
            for page in result.results:
                print(f"- {page.path} | score: {page.score:.6f} | [[{page.title}]]")
                if page.snippet:
                    print(f"  {page.snippet}")
```

- [ ] **Step 4: Run CLI tests**

Run:

```powershell
python -m pytest tests/unit/test_search_cli.py -q
```

Expected: `3 passed`.

- [ ] **Step 5: Run existing CLI smoke coverage**

Run:

```powershell
python -m pytest tests/unit/test_cli_subprocess_entrypoints.py tests/unit/test_search_cli.py -q
```

Expected: all selected tests pass with the existing Windows POSIX dry-run skip if that file includes it.

- [ ] **Step 6: Commit Task 3**

```powershell
git add llm_wiki_core/cli.py tests/unit/test_search_cli.py
git commit -m "接入 R3.3 搜索命令"
```

---

### Task 4: Query Integration

**Files:**
- Modify: `llm_wiki_core/operations/query.py`
- Modify: `tests/unit/test_query_save_operations.py`

**Interfaces:**
- Consumes: `search_wiki(vault_root, question, limit=3, transport=active_transport)`.
- Produces: same public `QueryResult` shape as before.

- [ ] **Step 1: Add failing query integration regression tests**

Append to `tests/unit/test_query_save_operations.py`:

```python

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
```

- [ ] **Step 2: Run query tests to verify at least one new test fails**

Run:

```powershell
python -m pytest tests/unit/test_query_save_operations.py::test_query_ignores_index_only_matches_when_selecting_cited_pages tests/unit/test_query_save_operations.py::test_query_uses_retrieval_foundation_for_ranked_pages -q
```

Expected: the first test fails because current query ranking can consider index-like behavior only indirectly or the second test reveals old ranking behavior. If both pass because current behavior already matches these examples, continue and use the implementation step to remove duplicated ranking code; the full file still guards behavior.

- [ ] **Step 3: Replace local query ranking with `search_wiki`**

Modify `llm_wiki_core/operations/query.py` to:

```python
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from llm_wiki_core.operations.search import search_wiki
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

    search_result = search_wiki(root, question, limit=3, transport=active_transport)
    if not search_result.results:
        return QueryResult(
            operation="query",
            status="needs_sources",
            question=question,
            answer=f"I don't have enough wiki coverage to answer: {question}",
            cited_pages=[],
            gaps=[f"No relevant wiki page found for: {question}"],
            suggested_save=False,
        )

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


def _wikilink(page: str) -> str:
    return f"[[{Path(page).stem}]]"
```

Remove the old `_rank_pages` and `_terms` helpers from `query.py`.

- [ ] **Step 4: Run focused query tests**

Run:

```powershell
python -m pytest tests/unit/test_query_save_operations.py tests/unit/test_artifact_equivalence_verification.py -q
```

Expected: all selected tests pass.

- [ ] **Step 5: Commit Task 4**

```powershell
git add llm_wiki_core/operations/query.py tests/unit/test_query_save_operations.py
git commit -m "复用 R3.3 检索基础查询"
```

---

### Task 5: Public Documentation And Guard Tests

**Files:**
- Modify: `README.md`
- Modify: `docs/user-guide.md`
- Modify: `docs/operation-contract.md`
- Modify: `docs/roadmap-schedule.md`
- Modify: `docs/codex-command-contract.md`
- Test: `tests/unit/test_r3_3_retrieval_docs.py`

**Interfaces:**
- Consumes: public `llm-wiki search` command from Task 3.
- Produces: public docs that describe R3.3 scope, search command, read-only behavior, and deferred vector/hybrid/rerank/LLM synthesis.

- [ ] **Step 1: Write failing documentation guard tests**

Create `tests/unit/test_r3_3_retrieval_docs.py`:

```python
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_documents_r3_3_search_command_and_boundaries() -> None:
    text = _read("README.md")

    assert "R3.3" in text
    assert "llm-wiki search <vault>" in text
    assert "BM25-style" in text
    assert "vector search" in text
    assert "LLM synthesis" in text


def test_operation_contract_lists_search_operation() -> None:
    text = _read("docs/operation-contract.md")

    assert "- `search`" in text
    assert "## `search`" in text
    assert "read-only" in text
    assert "ranked wiki pages" in text


def test_user_guide_explains_search_before_query_synthesis() -> None:
    text = _read("docs/user-guide.md")

    assert "llm-wiki search <vault>" in text
    assert "Search is read-only" in text
    assert "wiki pages" in text


def test_roadmap_marks_r3_3_complete_without_claiming_hybrid_retrieval() -> None:
    text = _read("docs/roadmap-schedule.md")

    assert "### R3.3: Retrieval Foundation" in text
    assert "Status: complete" in text
    assert "hybrid retrieval" in text
    assert "remains deferred" in text
```

- [ ] **Step 2: Run docs tests to verify they fail**

Run:

```powershell
python -m pytest tests/unit/test_r3_3_retrieval_docs.py -q
```

Expected: fail because R3.3 docs are not yet updated.

- [ ] **Step 3: Update README**

Modify `README.md`:

- Change current status to say R3.3 adds local read-only wiki search on top of R3.2 URL ingest.
- Add `llm-wiki search <vault> "durable wiki knowledge"` in the query/check examples.
- Add command table row:

```markdown
| `llm-wiki search <vault> "<query>"` | Search ranked local wiki pages with dependency-free BM25-style lexical retrieval. |
```

- Add boundary bullets:

```markdown
- R3.3 search is read-only and searches durable Markdown wiki pages by default.
- R3.3 uses dependency-free BM25-style lexical retrieval.
- Vector search, hybrid retrieval, reranking, raw-source search by default, qmd integration, and LLM synthesis remain deferred.
```

- [ ] **Step 4: Update user guide**

Modify `docs/user-guide.md`:

- Add a `Search` section before `Query And Save`:

```markdown
## Search

Use search when you want to inspect the wiki evidence before asking for synthesis:

```powershell
llm-wiki search <vault> "durable wiki knowledge"
llm-wiki search <vault> "durable wiki knowledge" --limit 3 --json
```

Search is read-only. It ranks durable Markdown wiki pages and returns paths, titles, snippets, matched terms, and scores. It does not search `.raw/` by default and does not mutate the wiki.
```

- Update `What Is Ready` to include local read-only `search`.
- Update `Current Boundaries` to say vector search, hybrid retrieval, reranking, qmd integration, raw-source search by default, and LLM synthesis remain outside R3.3.

- [ ] **Step 5: Update operation contract**

Modify `docs/operation-contract.md`:

- Add `search` to the operation list between `ingest-url` and `query`.
- Add a new section before `query`:

```markdown
## `search`

### Purpose

Search ranked local wiki pages without mutating the vault.

### Input

| Field | Description |
|---|---|
| `vault_root` | Target vault root. |
| `query` | Search query. |
| `limit` | Maximum ranked pages to return. |

### Output

- ranked wiki pages
- page paths and titles
- snippets
- matched terms
- scores for ordering and debugging
- searched roots and searched page count

### Error Modes

- empty query
- query with no searchable terms
- invalid non-positive limit
- unreadable vault or page

### Validation

- read-only by default
- searches durable wiki pages, not `.raw/`, unless a later explicit mode adds raw-source search
- vector search, hybrid retrieval, reranking, and LLM synthesis are outside R3.3
```

- [ ] **Step 6: Update roadmap and Codex command contract**

Modify `docs/roadmap-schedule.md`:

```markdown
### R3.3: Retrieval Foundation

Window: 2026-06-30

Status: complete.

Scope:

- Read-only `search` operation.
- CLI command `llm-wiki search <vault> "<query>" [--limit N] [--json]`.
- Dependency-free BM25-style lexical retrieval over durable Markdown wiki pages.
- Query operation reuses the retrieval foundation.

Non-scope:

- Vector search.
- Hybrid retrieval.
- LLM reranking.
- qmd integration.
- Raw-source search by default.
- LLM synthesis save policy.

Follow-up:

- Deep retrieval, hybrid retrieval, vector search, reranking, and LLM synthesis remain deferred.
```

Modify `docs/codex-command-contract.md`:

- Add command mapping row:

```markdown
| 搜索 Wiki | `search wiki for X`、`find wiki pages about X` | `/wiki search <query>` | `search` |
```

- Add a small `search` semantics section stating search is read-only and returns ranked wiki pages before query synthesis.

- [ ] **Step 7: Run docs tests**

Run:

```powershell
python -m pytest tests/unit/test_r3_3_retrieval_docs.py -q
```

Expected: `4 passed`.

- [ ] **Step 8: Commit Task 5**

```powershell
git add README.md docs/user-guide.md docs/operation-contract.md docs/roadmap-schedule.md docs/codex-command-contract.md tests/unit/test_r3_3_retrieval_docs.py
git commit -m "补充 R3.3 检索文档"
```

---

### Task 6: Final Verification And Progress Record

**Files:**
- Modify: `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`
- No repository code changes unless verification exposes a defect.

**Interfaces:**
- Consumes: all previous R3.3 task commits.
- Produces: verified R3.3 branch state and an external progress record for the user.

- [ ] **Step 1: Run full test suite**

Run:

```powershell
python -m pytest -q
```

Expected: all tests pass, with the existing Windows POSIX shell dry-run skip allowed.

- [ ] **Step 2: Run whitespace check**

Run:

```powershell
git diff --check
```

Expected: no output and exit code 0.

- [ ] **Step 3: Confirm dependency boundary**

Run:

```powershell
Select-String -Path pyproject.toml -Pattern "dependencies = \\[\\]"
```

Expected output includes:

```text
dependencies = []
```

- [ ] **Step 4: Confirm branch diff scope**

Run:

```powershell
git status --short --branch
git log --oneline -8
```

Expected:

- current branch is the R3.3 implementation branch;
- working tree is clean before merge or review;
- recent commits are the R3.3 task commits with Chinese commit messages.

- [ ] **Step 5: Update external progress document**

Append a new stage to `D:/ai/llmWiki/codex_doc/project_understanding_progress.md`. Use the exact headings below, and write the real values from Steps 1-4 directly into the bullets before saving. The saved progress entry must not contain draft marker text.

```markdown
## 阶段 95：R3.3 Retrieval Foundation 实施完成

状态：已完成

### 本阶段目标

完成 read-only `search` operation、BM25-style lexical retrieval foundation、CLI search command、query integration、R3.3 文档同步和验证。

### 完成能力

- `llm-wiki search <vault> "<query>" [--limit N] [--json]`。
- Search 默认检索 durable Markdown wiki pages。
- Search 返回 ranked pages、path、title、snippet、matched terms、score。
- `query_wiki` 复用 retrieval foundation。
- `.raw/` 不作为默认 search scope。
- vector、hybrid retrieval、rerank、qmd integration、LLM synthesis 仍延后。

### 验证结果

- `python -m pytest -q`：
  - 结果：写入 Step 1 的实际测试摘要。
- `git diff --check`：
  - 结果：写入 Step 2 的实际检查结果。
- `pyproject.toml`：
  - `dependencies = []` 未变化。

### 当前状态

- 分支：写入 Step 4 输出中的实际分支。
- HEAD：写入 Step 4 输出中的实际最新 commit。
- 工作区：写入 Step 4 输出中的实际工作区状态。
```

- [ ] **Step 6: Report final R3.3 status to the user**

The report must include:

- branch name;
- latest commit hash;
- test result;
- whitespace check result;
- whether `pyproject.toml` still has `dependencies = []`;
- reminder that full vector/hybrid/deep retrieval remains deferred.
