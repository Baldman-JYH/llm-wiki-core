from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def _read(relative: str) -> str:
    return (ROOT / relative).read_text(encoding="utf-8")


def test_user_guide_covers_local_codex_mvp_workflow() -> None:
    guide = _read("docs/user-guide.md")

    required_terms = [
        "Karpathy",
        "claude-obsidian",
        "artifact-level equivalence",
        "Codex App",
        "Codex CLI",
        "filesystem",
        "Obsidian CLI",
        ".raw/",
        "wiki/index.md",
        "wiki/log.md",
        "wiki/hot.md",
    ]
    for term in required_terms:
        assert term in guide

    required_commands = [
        "python -m pip install -e .",
        "python -m llm_wiki_core",
        "llm-wiki init",
        "llm-wiki detect-transport",
        "llm-wiki ingest",
        "llm-wiki status",
        "llm-wiki continue",
        "llm-wiki query",
        "llm-wiki save",
        "llm-wiki lint",
    ]
    for command in required_commands:
        assert command in guide


def test_release_checklist_states_mvp_readiness_and_boundaries() -> None:
    checklist = _read("docs/release-readiness-checklist.md")

    required_terms = [
        "Ready for MVP local use",
        "not ready for full claude-obsidian parity",
        "Karpathy",
        "artifact-level equivalence",
        "Codex App",
        "Codex CLI",
        "PowerShell",
        "filesystem",
        "Obsidian CLI",
    ]
    for term in required_terms:
        assert term in checklist


def test_readme_links_release_readiness_docs() -> None:
    readme = _read("README.md")

    assert "docs/user-guide.md" in readme
    assert "docs/release-readiness-checklist.md" in readme
