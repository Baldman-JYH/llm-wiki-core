from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_readme_documents_r3_3_search_command_and_boundaries() -> None:
    text = _read("README.md")

    assert "R3.3 retrieval foundation" in text or "R3.3 search" in text
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

    assert "| User intent | Natural-language examples | Target slash command | Core operation |" in text
    assert "| Search Wiki | `search wiki for X`, `find wiki pages about X` | `/wiki search <query>` | `search` |" in text
    assert "## `search` Semantics" in text
    assert "Search is read-only and returns ranked durable wiki pages before query synthesis." in text
    assert "Search does not mutate wiki content." in text
    assert "Keep `.raw/` out of the default search scope." in text


def test_codex_command_contract_documents_existing_core_command_semantics() -> None:
    text = _read("docs/codex-command-contract.md")

    assert "## `/wiki` Semantics" in text
    assert "When the vault is not initialized:" in text
    assert "Ask for the vault purpose." in text
    assert "Create `.raw/.manifest.json`." in text
    assert "Run `detect-transport`." in text
    assert "When the vault is initialized:" in text
    assert "Read `wiki/hot.md`." in text
    assert "Read `wiki/index.md`." in text
    assert "Suggest the next action: `ingest`, `search`, `query`, `lint`, or `save`." in text

    assert "## `ingest` Semantics" in text
    assert "Confirm the target is under `.raw/`." in text
    assert "Read the raw source but do not modify it." in text
    assert "Check `.raw/.manifest.json`." in text
    assert "If the source was already ingested and the fingerprint is unchanged, ask whether to skip or force re-ingest." in text
    assert "Update `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`." in text

    assert "## `query` Semantics" in text
    assert "Read `wiki/hot.md`." in text
    assert "Read `wiki/index.md`." in text
    assert "Select only the necessary relevant pages." in text
    assert "Cite wiki pages in the answer." in text
    assert "If the answer has durable value, suggest saving it to `wiki/questions/`." in text

    assert "## `lint` Semantics" in text
    assert "Check frontmatter." in text
    assert "Check dead wikilinks." in text
    assert "Check orphan pages." in text
    assert "Output or write a lint report." in text

    assert "## `save` Semantics" in text
    assert "Decide whether the current content has durable knowledge value." in text
    assert "Choose whether to save as a question, concept, source note, or session note." in text
    assert "Create or update the corresponding wiki page." in text
    assert "Update `wiki/index.md`, `wiki/log.md`, and `wiki/hot.md`." in text

    assert "## `detect-transport` Semantics" in text
    assert "Detect filesystem transport." in text
    assert "Detect Obsidian CLI transport." in text
    assert "Write a transport snapshot." in text
    assert "Report the active available transport." in text


def test_r3_3_plan_has_no_mojibake_templates() -> None:
    text = _read("docs/superpowers/plans/2026-06-30-r3-3-retrieval-foundation.md")

    mojibake_markers = ["\ufffd", "鈧", "锟", "鎼", "銆", "乣", "琛", "闃", "鐘", "鍒"]

    assert not [marker for marker in mojibake_markers if marker in text]
