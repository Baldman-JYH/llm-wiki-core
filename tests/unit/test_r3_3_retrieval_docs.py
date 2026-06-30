from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_documents_r3_3_search_command_and_boundaries() -> None:
    text = _read("README.md")

    assert "Current status: R3.3 adds local read-only wiki search on top of the R3.2 URL ingest flow." in text
    assert 'llm-wiki search <vault> "durable wiki knowledge"' in text
    assert '| `llm-wiki search <vault> "<query>"` | Search ranked local wiki pages with dependency-free BM25-style lexical retrieval. |' in text
    assert "R3.3 search is read-only and searches durable Markdown wiki pages by default." in text
    assert "Vector search, hybrid retrieval, reranking, raw-source search by default, qmd integration, and LLM synthesis remain deferred." in text


def test_operation_contract_lists_search_operation() -> None:
    text = _read("docs/operation-contract.md")

    assert "- `search`" in text
    assert "## `search`" in text
    assert "Search ranked local wiki pages without mutating the vault." in text
    assert "- ranked wiki pages" in text
    assert "- read-only by default" in text
    assert "- vector search, hybrid retrieval, reranking, and LLM synthesis are outside R3.3" in text


def test_user_guide_explains_search_before_query_synthesis() -> None:
    text = _read("docs/user-guide.md")

    assert "Use search when you want to inspect the wiki evidence before asking for synthesis:" in text
    assert 'llm-wiki search <vault> "durable wiki knowledge"' in text
    assert "Search is read-only. It ranks durable Markdown wiki pages and returns paths, titles, snippets, matched terms, and scores." in text
    assert "Vector search, hybrid retrieval, reranking, qmd integration, raw-source search by default, and LLM synthesis remain outside R3.3." in text


def test_roadmap_marks_r3_3_complete_without_claiming_hybrid_retrieval() -> None:
    text = _read("docs/roadmap-schedule.md")

    assert "### R3.3: Retrieval Foundation" in text
    assert "Status: complete" in text
    assert '- CLI command `llm-wiki search <vault> "<query>" [--limit N] [--json]`.' in text
    assert "- Hybrid retrieval." in text
    assert "- Deep retrieval, hybrid retrieval, vector search, reranking, and LLM synthesis remain deferred." in text


def test_codex_command_contract_documents_search_mapping_and_semantics() -> None:
    text = _read("docs/codex-command-contract.md")

    assert "| 用户意图 | 自然语言触发示例 | 目标 slash command | Core operation |" in text
    assert "| 搜索 Wiki | `search wiki for X`、`find wiki pages about X` | `/wiki search <query>` | `search` |" in text
    assert "## `search` Semantics" in text
    assert "Search is read-only and returns ranked wiki pages before query synthesis." in text
    assert "search wiki for X" in text
    assert "/wiki search <query>" in text
