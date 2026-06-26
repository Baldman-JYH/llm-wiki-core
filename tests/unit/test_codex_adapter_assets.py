from __future__ import annotations

from pathlib import Path


def test_codex_skill_draft_references_mvp_commands() -> None:
    root = Path(__file__).parents[2]
    skill = root / "integrations" / "codex" / "skills" / "llm-wiki" / "SKILL.md"

    text = skill.read_text(encoding="utf-8")

    for command in ["init", "detect-transport", "status", "continue", "ingest", "query", "save", "lint"]:
        assert command in text
    assert "set up wiki" in text
    assert "check wiki status" in text
    assert "resume wiki context" in text
    assert "artifact-level equivalence" in text


def test_codex_agents_template_references_mvp_workflow() -> None:
    root = Path(__file__).parents[2]
    template = root / "integrations" / "codex" / "AGENTS.template.md"

    text = template.read_text(encoding="utf-8")

    assert "llm-wiki init" in text
    assert "llm-wiki status" in text
    assert "llm-wiki continue" in text
    assert "llm-wiki ingest" in text
    assert "llm-wiki query" in text
    assert "llm-wiki lint" in text
    assert ".raw/" in text


def test_codex_command_mapping_exists() -> None:
    root = Path(__file__).parents[2]
    mapping = root / "integrations" / "codex" / "COMMANDS.md"

    text = mapping.read_text(encoding="utf-8")

    assert "Natural language trigger" in text
    assert "check wiki status" in text
    assert "resume wiki context" in text
    assert "llm-wiki status" in text
    assert "llm-wiki continue" in text
    assert "llm-wiki save" in text
    assert "lint the wiki" in text


def test_codex_command_mapping_table_rows_are_well_formed() -> None:
    root = Path(__file__).parents[2]
    mapping = root / "integrations" / "codex" / "COMMANDS.md"

    rows = [
        line
        for line in mapping.read_text(encoding="utf-8").splitlines()
        if line.startswith("|") and not set(line.replace("|", "").strip()) <= {"-"}
    ]

    assert rows
    for row in rows:
        assert row.endswith("|")
        assert row.count("|") >= 3


def test_codex_install_entrypoints_exist() -> None:
    root = Path(__file__).parents[2]
    install = root / "integrations" / "codex" / "install"

    ps1 = (install / "install.ps1").read_text(encoding="utf-8")
    sh = (install / "install.sh").read_text(encoding="utf-8")

    assert "llm-wiki init" in ps1
    assert "llm-wiki init" in sh
    assert "pip install -e" in ps1
    assert "pip install -e" in sh
