from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_codex_skill_references_current_commands_and_search_mapping() -> None:
    text = _read("integrations/codex/skills/llm-wiki/SKILL.md")

    for command in [
        "llm-wiki init",
        "llm-wiki detect-transport",
        "llm-wiki status",
        "llm-wiki continue",
        "llm-wiki ingest",
        "llm-wiki ingest-batch",
        "llm-wiki ingest-url",
        "llm-wiki search",
        "llm-wiki query",
        "llm-wiki save",
        "llm-wiki lint",
    ]:
        assert command in text

    assert "search wiki for X" in text
    assert "find wiki pages about X" in text
    assert "Search is read-only" in text
    assert "artifact-level equivalence" in text


def test_codex_agents_template_references_current_workflow() -> None:
    text = _read("integrations/codex/AGENTS.template.md")

    for command in [
        "llm-wiki init",
        "llm-wiki detect-transport",
        "llm-wiki status",
        "llm-wiki continue",
        "llm-wiki ingest",
        "llm-wiki ingest-batch",
        "llm-wiki ingest-url",
        "llm-wiki search",
        "llm-wiki query",
        "llm-wiki save",
        "llm-wiki lint",
    ]:
        assert command in text

    assert ".raw/" in text
    assert "wiki/index.md" in text
    assert "wiki/log.md" in text
    assert "wiki/hot.md" in text


def test_codex_command_mapping_documents_search_and_mutation_behavior() -> None:
    text = _read("integrations/codex/COMMANDS.md")

    assert "| Natural language trigger | Target slash command | CLI command | Mutation behavior | Key files |" in text
    assert "| search wiki for X | `/wiki search <query>` | `llm-wiki search <vault> \"X\"` | read-only | `wiki/sources/`, `wiki/concepts/`, `wiki/entities/`, `wiki/questions/`, `wiki/comparisons/` |" in text
    assert "| ingest this URL | `/wiki ingest-url <url>` | `llm-wiki ingest-url <vault> <url>` | writes raw snapshot and wiki artifacts | `.raw/url/`, `.raw/.manifest.json`, `wiki/index.md`, `wiki/log.md`, `wiki/hot.md` |" in text
    assert "Natural language triggers are required; slash commands are a target UX layer." in text


def test_codex_command_mapping_table_rows_are_well_formed() -> None:
    text = _read("integrations/codex/COMMANDS.md")
    rows = [
        line
        for line in text.splitlines()
        if line.startswith("|") and not set(line.replace("|", "").strip()) <= {"-"}
    ]

    assert rows
    expected_columns = rows[0].count("|")
    for row in rows:
        assert row.endswith("|")
        assert row.count("|") == expected_columns


def test_codex_install_entrypoints_exist() -> None:
    ps1 = _read("integrations/codex/install/install.ps1")
    sh = _read("integrations/codex/install/install.sh")

    assert "llm-wiki init" in ps1
    assert "llm-wiki init" in sh
    assert "pip install -e" in ps1
    assert "pip install -e" in sh
