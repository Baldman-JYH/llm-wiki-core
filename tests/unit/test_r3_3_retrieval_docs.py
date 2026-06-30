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
